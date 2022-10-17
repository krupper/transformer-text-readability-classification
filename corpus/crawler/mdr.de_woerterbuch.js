const puppeteer = require('puppeteer');
const cheerio = require('cheerio');
const fs = require('fs');

const urls = [];

async function fetchUrls(page, urls){
    const url = 'https://www.mdr.de/nachrichten-leicht/woerterbuch/index.html';
    await page.goto(url);

    let html = await page.content();
    const $ = cheerio.load(html);
    const category_urls = [];

    $('.dokumentSpezifischeAnfasserSendungenAZ a.pageItem').each((index, element) => {
        let category_url = new URL($(element).attr('href'), url).href;
        category_urls.push(category_url);
    });

    for (const url of category_urls) {
        await page.goto(url);

        let html = await page.content();
        const $ = cheerio.load(html);

        $('.teaser a.linkAll').each((index, element) => {
            let article_url = new URL($(element).attr('href'), url).href;
            urls.push(article_url);
        });
    }
}

(async () => {
    const browser = await puppeteer.launch({ headless: true });
    const page = await browser.newPage();

    await fetchUrls(page, urls);

    // Get detail texts
    let i = 0;
    for (const url of urls) {
        console.log(url);

        await page.goto(url);

        let html = await page.content();
        const $ = cheerio.load(html);
        let content = '';
        $('p.text').each((index, element) => {
            const temp = $(element).html().replaceAll('<br>', '#P#\n');
            // content += cheerio.load(temp).text().replaceAll('#RETURN#', '\n').replace(/\xA0/g,' ') + "\n";
            content += cheerio.load(temp).text().replace(/\xA0/g,' ') + "\n";
        });

        if(content == '')
            continue;

        try {
            fs.writeFileSync(`../easy_to_read/mdr.de_woerterbuch/${i}.txt`, content);
            // file written successfully
            let progress = Math.round((i / urls.length) * 100);
            console.log(`${progress}%`);
        } catch (err) {
            console.error(err);
        }
        i++;
    }

    browser.close()
})()
