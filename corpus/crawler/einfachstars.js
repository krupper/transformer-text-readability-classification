const puppeteer = require('puppeteer');
const cheerio = require('cheerio');
const fs = require('fs');

const urls = [];

(async () => {
    const browser = await puppeteer.launch({ headless: true });
    const page = await browser.newPage();

    const url = 'https://einfachstars.info/lexikon/index.html';
    await page.goto(url);

    let html = await page.content();
    const $ = cheerio.load(html);

    $('a.glossary-list-link').each((index, element) => {
        let article_url = new URL($(element).attr('href'), url).href;
        urls.push(article_url);
    });

    // Get detail texts
    let i = 0;
    for (const url of urls) {
        console.log(url);

        await page.goto(url);

        let html = await page.content();
        const $ = cheerio.load(html);
        let content = '';
        $('.body p:not(.image-source)').each((index, element) => {
            const temp = $(element).html().replaceAll('<br>', '#RETURN#');
            content += cheerio.load(temp).text().replaceAll('#RETURN#', '\n').replace(/\xA0/g,' ') + "\n";

            // content += $(element).text() +  "\n";
        });

        if(content == '')
            continue;

        try {
            console.log(content);
            
            fs.writeFileSync(`../easy_to_read/einfachstars/${i}.txt`, content);
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

