const { chromium } = require('playwright');
const fs = require("fs");

(async () => {
    const browser = await chromium.launch({ headless: false });
    const page = await browser.newPage();
    await page.goto('https://repositorio.ipl.pt');
    const results = [];
    let globalId = 0;
    //const scrapped = [];

    while(true) {
        const reviewsSelector = '.mt-4.mb-4.d-flex';
        while (true) {
            const buttonLoadMore = page.locator('button:has-text("Carregar mais ...")');
            if (!(await buttonLoadMore.isVisible())) {
                //console.log('Botão desapareceu. fim');
                break;
            }

            const before = await page.locator(reviewsSelector).count();

            await buttonLoadMore.scrollIntoViewIfNeeded();
            await buttonLoadMore.click();

            //console.log('ANTES:', before);
            await page.waitForTimeout(2000);
            //console.log('DEPOIS:', await page.locator('.mt-4.mb-4.d-flex.ng-tns-c62-30.ng-star-inserted').count());

            await page.waitForFunction(
                (selector, beforeCount) =>
                    document.querySelectorAll(selector).length > beforeCount,
                reviewsSelector,
                before
            ).catch(() => {});
        }

        //const reviews = page.locator(reviewsSelector);
        //const data = await reviews.evaluateAll(els => els.map(el => el.innerText) );

        const currentDate = new Date();
        const data = await page.$$eval(reviewsSelector, (els, args) =>
            els.map((el, idx) => ({
                id: args.startId + idx,
                titulo: el.querySelector('a')?.innerText.trim(),
                autores: el.querySelector('.clamp-default-2 .item-list-authors')?.innerText.trim(),
                dataPublicacao: el.querySelector('.tag_elements a')?.innerText.trim(),
                texto: el.querySelector('.clamp-default-3 span')?.innerText.trim(),
                tipo: el.querySelectorAll('.tag_elements a')?.[1]?.innerText.trim(),
                acesso: el.querySelector('.access-status-list-element-badge a')?.innerText.trim(),
                dataAcessada: args.currentDate
            })),
            {
                startId: globalId,
                currentDate: currentDate
            }
        );
        globalId += data.length;

        //garantir que ele so da push quando faz um scrap novo, evitando duplicados por falta de load
        const seen = new Set();
        const newData = data.filter(item => {
            if (seen.has(item.titulo)) return false;
            seen.add(item.titulo);
            return true;
        });

        results.push(...newData);
        //console.log('Página capturada:', data.length)

        const buttonNextPage = page.locator('.page-item:has-text("»")');
        //console.log(buttonNextPage.count());
        /*if (!(await buttonNextPage.isVisible()) || !(await buttonNextPage.isEnabled())) {
            console.log('Fim da paginação');
            break;
        }*/
        if (!await buttonNextPage.isVisible()) {
            //console.log('Fim da paginação visible');
            break;
        }

        if (!await buttonNextPage.isEnabled()) {
            //console.log('Fim da paginação enabled');
            break;
        }

        //const firstBefore = await reviews.first().innerText();

        const snapshotBefore = await page.$$eval(
            reviewsSelector,
            els => els.map(e => e.innerText).join('|')
        );

        //await buttonNextPage.scrollIntoViewIfNeeded();
        await buttonNextPage.click(); // esperar mudança real no DOM

        /*
        await page.waitForFunction(
            (selector, oldSnapshot) => {
                const now = Array.from(document.querySelectorAll(selector))
                    .map(e => e.innerText)
                    .join('|');

                return now !== oldSnapshot;
            },
            reviewsSelector,
            snapshotBefore
        );*/
        await page.waitForFunction(
            (selector) => {
                const items = document.querySelectorAll(selector);
                return items.length >= 10; // ou número esperado
            },
            reviewsSelector
        );
    }
    //console.log('TOTAL:', results.length);
    //console.log(results[30]);
    //console.log(results[9]);
    //if(results[11] !== null) console.log(results[11]);

    await browser.close();
    fs.writeFileSync("repoCientifico.json", JSON.stringify(results, null, 2));
    console.log("Repositorio Cientifico saved!");
})();