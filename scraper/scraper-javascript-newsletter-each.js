const fs = require('fs');
const cheerio = require("cheerio");

const data = fs.readFileSync('newsletter.json', 'utf-8');
const json = JSON.parse(data);
const baseUrls = Object.values(json).map(item => item.link);
const baseUrl = "https://www.ipl.pt/newsletter/1"
//console.log(json, "type: ", typeof json)
//const maxIndex = Object.keys(json).length;
//const maxIndex = 1
//console.log("Max index: ", maxIndex)
//const baseUrl = 'https://www.ipl.pt/newsletter/';

const news = {}

async function scrapeAll() {
    const currentDate = new Date();

    //for (const baseUrl of baseUrls) {
    for(let i = 0; i < 1; i++) {
        const response = await fetch(baseUrl);
        const html = await response.text();
        const url = new URL(baseUrl);
        const lastPart = url.pathname.split("/").filter(Boolean).pop();
        const $ = cheerio.load(html);

        const items = $(".content-main");
        //console.log("Item found:", items.length);
        items.each((_, element) => {
            //console.log("Processing newsletter:", link);
            const titulo = `Newsletter: ${lastPart}`
            // primeiro texto da newsletter é sempre algo referente ao politecnico
            const politecnicoTitulo = $(element)
                .find(".title-body h1")
                .text()
                .trim()
            const politecnicoTexto = $(element)
                .find(".title-body p")
                .text()
                .trim()
            const href = $(element)
                .find(".title-body a")
                .attr("href");
            console.log("Href found:", href, href.length);

            let link
            if(href) {
                link = new URL(href, "https://www.ipl.pt").href
            } else link = "No links found";
            const campoAberto = [];

            const container = $(element).find(".field--name-field-campo-aberto-grupo-3");

            container.find("h2").each((i, el) => {
                const titulo = $(el).text().trim();

                // get the NEXT <p> after this h2
                const texto = $(el)
                    .nextUntil("h2", "p")
                    .map((_, p) => $(p).text().trim())
                    .get()
                    .join(" ");

                const hrefCa = $(el)
                    .find("a")
                    .attr("href");
                //console.log("Campo Aberto Href found:", hrefCa);

                const linkCa = new URL(hrefCa, "https://www.ipl.pt").href;

                campoAberto.push({
                    titulo: titulo,
                    texto: texto,
                    link: linkCa
                });
            });

            //console.log(campoAberto);

            //console.log(campoAberto);
            /*const campoAbertoTitulo  = $(element)
                .find(".field.field--name-field-campo-aberto-grupo-3 h2")
                .text()
                .trim()
            console.log("Campo Aberto Título:", campoAbertoTitulo, campoAbertoTitulo.length)
            const campoAbertoTexto = $(element)
                .find(".field--name-field-campo-aberto-grupo-3 p")
                .text()
                .trim()
            console.log("Campo Aberto Texto:", campoAbertoTexto, campoAbertoTexto.length)*/
            /*

        //const link = new URL()
         */
            news[titulo] = {
                politecnicoTitulo: politecnicoTitulo,
                politecnicoTexto: politecnicoTexto,
                links: link,
                noticias: campoAberto,
                //campoAbertoTitulo: campoAbertoTitulo,
                //campoAbertoTexto: campoAbertoTexto,
                //text: text,
                dateChecked: currentDate
            };
        });
    }

    fs.writeFileSync("newsletter-content.json", JSON.stringify(news, null, 2));
    console.log("Newsletter-content saved!");
}

scrapeAll().then(r => console.log("Scraping completed!")).catch(err => console.error("Error:", err));
