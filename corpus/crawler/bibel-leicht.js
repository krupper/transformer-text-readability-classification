// https://www.evangelium-in-leichter-sprache.de/bibelstellen?page=0

const puppeteer = require('puppeteer');
const cheerio = require('cheerio');
const fs = require('fs');

const urls = [];

(async () => {
    const browser = await puppeteer.launch({ headless: true });
    const page = await browser.newPage();

    for (let i = 0; i < 19; i++) {
        const url = 'https://www.evangelium-in-leichter-sprache.de/bibelstellen?page=' + i;
        await page.goto(url);

        let html = await page.content();
        const $ = cheerio.load(html);

        $('.view-content a').each((index, element) => {
            let article_url = new URL($(element).attr('href'), url).href;
            urls.push(article_url);
        });
    }

    // Get detail texts
    let i = 0;
    for (const url of urls) {
        console.log(url);

        await page.goto(url);

        let html = await page.content();
        const $ = cheerio.load(html);
        let content = '';
        $('.field-type-text-with-summary p, .field-type-text-with-summary div.rteindent1').each((index, element) => {
            content += $(element).text() + "#P#\n";
        });

        if(content == '')
            continue;

        try {
            fs.writeFileSync(`../easy_to_read/bibel/${i}.txt`, content);
            // file written successfully
            let progress = Math.round((i / urls.length) * 100);
            console.log(`${progress}%`);
            console.log("-------------------------------------");
        } catch (err) {
            console.error(err);
        }
        i++;
    }

    browser.close()
})()

