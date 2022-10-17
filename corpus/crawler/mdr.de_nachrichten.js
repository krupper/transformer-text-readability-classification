const puppeteer = require('puppeteer');
const cheerio = require('cheerio');
const fs = require('fs');

const urls = [];

async function fetchUrls(page, url, urls){
    await page.goto(url);

    let html = await page.content();
    const $ = cheerio.load(html);
    $('a.linkAll').each((index, element) => {
        let article_url = new URL($(element).attr('href'), url).href;
        urls.push(article_url);
    })
}

(async () => {
    const browser = await puppeteer.launch({ headless: true });
    const page = await browser.newPage();

    await fetchUrls(page, 'https://www.mdr.de/nachrichten-leicht/rueckblick/leichte-sprache-rueckblick-buendelgruppe-sachsen-anhalt-100.html', urls);
    await fetchUrls(page, 'https://www.mdr.de/nachrichten-leicht/index.html', urls);


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
            content += cheerio.load(temp).text().replace(/\xA0/g,' ') + "\n";
            // content += cheerio.load(temp).text().replaceAll('#RETURN#', '\n').replace(/\xA0/g,' ') + "\n";
        });

        if(content == '')
            continue;

        try {
            fs.writeFileSync(`../easy_to_read/mdr.de_nachrichten/${i}.txt`, content);
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
