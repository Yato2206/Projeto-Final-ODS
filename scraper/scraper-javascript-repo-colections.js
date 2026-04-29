const { chromium } = require('playwright');
const fs = require("fs");

/**
 * SCRAPER CLARO E PRECISO:
 * 1. Aceder a https://repositorio.ipl.pt
 * 2. Scroll + "Carregar mais"
 * 3. Ir para última página
 * 4. Scrape items COM badge-info
 * 5. Ir página anterior
 * 6. Repetir até encontrar página SEM badge-info
 * 7. Nessa página final, scrape APENAS items COM badge-info
 * 8. Guardar results_links.json
 */

async function main() {
    const browser = await chromium.launch({ headless: false });
    const page = await browser.newPage();

    try {
        console.log('\n' + '='.repeat(80));
        console.log('SCRAPER - REPOSITORIO IPL');
        console.log('='.repeat(80) + '\n');

        const BASE_URL = 'https://repositorio.ipl.pt';
        const ITEMS_SELECTOR = '.mt-4.mb-4.d-flex';
        const BADGE_SELECTOR = '.badge-info';

        console.log('Passo 1: Navegando para página base...');
        await page.goto(BASE_URL, { waitUntil: 'networkidle' });
        console.log('Página carregada\n');

        console.log('Passo 2: Clicando "Carregar mais"...');

        let loadMoreCount = 0;
        while (true) {
            await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
            await page.waitForTimeout(2500);

            const btn = await page.$('button:has-text("Carregar mais")');

            if (!btn || !(await btn.isVisible())) {
                console.log(`Botão desapareceu (${loadMoreCount} cliques)\n`);
                break;
            }

            await btn.scrollIntoViewIfNeeded();
            await page.waitForTimeout(300);
            await btn.click();
            loadMoreCount++;
            console.log(`  Clique ${loadMoreCount}...`);

            await page.waitForTimeout(1500);
        }

        console.log('Passo 3: Procurando última página...');

        const lastPageNum = await page.evaluate(() => {
            const buttons = Array.from(document.querySelectorAll('.pagination button, .pagination a'));
            let maxNum = 1;

            for (const btn of buttons) {
                const text = btn.textContent.trim();
                const num = parseInt(text);
                if (!isNaN(num) && text !== '«' && text !== '»') {
                    maxNum = Math.max(maxNum, num);
                }
            }

            return maxNum;
        });

        console.log(`Última página: ${lastPageNum}\n`);

        console.log('Passo 4: Começando scrape regressivo...\n');

        const extractedLinks = {};
        let currentPage = lastPageNum;
        let shouldStop = false;

        while (!shouldStop && currentPage >= 1) {
            console.log(`Página ${currentPage}:`);

            if (Object.keys(extractedLinks).length > 0) {
                const prevBtn = await page.$('.pagination button:has-text("«"), .pagination a:has-text("«")');
                if (prevBtn && await prevBtn.isVisible()) {
                    await prevBtn.click();
                    await page.waitForTimeout(1000);
                } else {
                    console.log(`  → Botão « não encontrado, parando`);
                    break;
                }
            } else {
                const lastPageBtn = await page.evaluate(({ num }) => {
                    const buttons = Array.from(document.querySelectorAll('.pagination button, .pagination a'));
                    for (const btn of buttons) {
                        if (btn.textContent.trim() === num.toString()) {
                            btn.click();
                            return true;
                        }
                    }
                    return false;
                }, { num: currentPage });

                if (lastPageBtn) {
                    await page.waitForTimeout(1000);
                }
            }

            const itemCount = await page.locator(ITEMS_SELECTOR).count();
            console.log(`  → ${itemCount} items encontrados`);

            if (itemCount === 0) {
                console.log(`  →Página vazia! Parando.\n`);
                break;
            }

            const itemsWithBadgeCount = await page.evaluate(({ selector, badge }) => {
                const items = document.querySelectorAll(selector);
                let count = 0;
                for (const item of items) {
                    const badgeEl = item.querySelector(badge);
                    if (badgeEl) {
                        count++;
                    }
                }
                return count;
            }, { selector: ITEMS_SELECTOR, badge: BADGE_SELECTOR });

            const itemsWithoutBadgeCount = itemCount - itemsWithBadgeCount;
            console.log(`  → COM badge-info: ${itemsWithBadgeCount}`);
            console.log(`  → SEM badge-info: ${itemsWithoutBadgeCount}`);

            const pageLinks = await page.$$eval(ITEMS_SELECTOR, (els) =>
                els.map((el) => {
                    const badgeEl = el.querySelector('.badge-info');

                    if (!badgeEl || badgeEl.textContent.includes("Comunidade")) {
                        return null;
                    }

                    const link = el.querySelector('a')?.href || '';
                    const titulo = el.querySelector('a')?.innerText.trim() || '';

                    if (titulo === "Sem título" || titulo === "Pessoas" || titulo === "Financiadores") {
                        return null;
                    }

                    return { link, titulo };
                }).filter(item => item !== null && item.link !== '')
            );

            console.log(`  → ${pageLinks.length} links COM badge extraídos`);

            for (const item of pageLinks) {
                if (item.link && !extractedLinks[item.link]) {
                    extractedLinks[item.link] = {
                        titulo: item.titulo,
                        dateScraped: new Date().toISOString()
                    };
                }
            }

            if (itemsWithoutBadgeCount > 0) {
                console.log(`  → Encontrados items SEM badge-info!`);
                console.log(`  → Esta é a página FINAL. Parando.\n`);
                shouldStop = true;
            } else {
                console.log(`  → Ir para página anterior\n`);
                currentPage--;
            }
        }

        console.log('Passo 5: Guardando resultados...\n');

        fs.writeFileSync('results_links.json', JSON.stringify(extractedLinks, null, 2), 'utf-8');

        console.log('='.repeat(80));
        console.log(' SCRAPER COMPLETO!');
        console.log('='.repeat(80));
        console.log(`\nTotal de links: ${Object.keys(extractedLinks).length}`);
        console.log('Ficheiro: results_links.json\n');

    } catch (error) {
        console.error('Erro:', error.message);
    } finally {
        await browser.close();
    }
}

main();

