//const cheerio = require('cheerio');
//const fs = require('fs');
//const puppeteer = require('puppeteer');

const baseUrl = 'https://repositorio.ipl.pt';

const articles = {};

import { chromium } from 'playwright';
(async () => {
    const browser = await chromium.launch({ headless: true });
    const page = await browser.newPage();

    // Vai ao home
    await page.goto(`${baseUrl}/home`);

    // Espera requests carregarem
    await page.waitForLoadState('networkidle');

    // Intercepta cookies
    const cookies = await page.context().cookies();
    console.log("COOKIES:", cookies);

    // Agora podes clicar no botão ou chamar APIs internas
    // await page.click('selector-do-botao');

    await browser.close();
})();
/*
async function scrapeAll() {
    const browser = await puppeteer.launch({headless: true});
    const page = await browser.newPage();
    await page.goto(baseUrl, {waitUntil: "networkidle2"});
    await page.click("button.search-button");
    //await page.waitForTimeout(3000);
    await page.screenshot({path: "debug.png", fullPage: true});
    await page.waitForSelector("ng-tns-c201-0", {timeout: 10000});
    let pageNumber = 1; //obrigatorio comecar em 1. nao existe pagina com indice 0
    //let hasMore = true;

    const currentDate = new Date();

    //while (hasMore) {
        const url = `${baseUrl}/search?spc.page=${pageNumber}&spc.sf=dc.date.accessioned&spc.sd=DESC`;
        const response = await fetch(url);
        const html = await response.text();
        const $ = cheerio.load(html);

        const items = $(".list-unstyled");
        console.log(items.length);
        //console.log(items)
        /*
        if (items.length === 0) {
            hasMore = false;
            break;
        }


        items.each((i, element) => {
            const titulo = $(element)
                .find(".ng-star-inserted a")
                .text()
                .trim();

            if (!titulo) return;

            const autores = $(element)
                .find(".clamp-default-2")
                .text()
                .trim();

            const texto = $(element)
                .find(".min-3 .clamp-default-none span")
                .text()
                .trim();

            const data = $(element)
                .find(".tag_elements .ng-star-inserted a")
                .text()
                .trim();

            const tipo = $(element)
                .find(".tag_elements .ng-star-inserted a")
                .text()
                .trim();

            const acesso = $(element)
                .find(".tag_elements .access-status-list-element-badge a")
                .text()
                .trim();

            const href = $(element)
                .find(".ng-star-inserted a")
                .attr("href");

            const link = new URL(href, "https://repositorio.ipl.pt").href;

            articles[titulo] = {
                autores: autores,
                texto: texto,
                dataDePublicacao: data,
                tipo: tipo,
                acesso: acesso,
                link: link,
                dateChecked: currentDate
            };
        });

        console.log(`Scraped page ${pageNumber}`);
        pageNumber++;
    //}

    fs.writeFileSync("repoCientifico.json", JSON.stringify(articles, null, 2));
    console.log("Repositorio Cientifico saved!");
}

scrapeAll().then(r => console.log("Scraping completed!")).catch(err => console.error("Error:", err));
*/