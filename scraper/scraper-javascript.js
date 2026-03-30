const cheerio = require('cheerio');
const fs = require('fs');

const baseUrl = 'https://www.ipl.pt/en/politecnico/comunicacao/newsletter';

const news = {};

async function scrapeAll() {
    let page = 0;
    let hasMore = true;

    const currentDate = new Date();

    while (hasMore) {
        const url = `${baseUrl}?page=${page}`;
        const response = await fetch(url);
        const html = await response.text();
        const $ = cheerio.load(html);

        const items = $(".view-content-wrap .item");

        if (items.length === 0) {
            hasMore = false;
            break;
        }

        items.each((i, element) => {
            const titulo = $(element)
                .find(".views-field-title a")
                .text()
                .trim();

            if (!titulo) return;

            const data = $(element)
                .find(".views-field-field-data-envio")
                .text()
                .trim();

            const href = $(element)
                .find(".views-field-title a")
                .attr("href");

            const link = new URL(href, "https://www.ipl.pt").href;

            news[titulo] = {
                date: data,
                link: link,
                dateChecked: currentDate
            };
        });

        console.log(`Scraped page ${page}`);
        page++;
    }

    fs.writeFileSync("newsletter.json", JSON.stringify(news, null, 2));
    console.log("Newsletter saved!");
}

scrapeAll().then(r => console.log("Scraping completed!")).catch(err => console.error("Error:", err));
