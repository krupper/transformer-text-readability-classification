const puppeteer = require('puppeteer');
const cheerio = require('cheerio');
const fs = require('fs');

let url = 'https://www.nachrichtenleicht.de/nachrichtenleicht-nachrichten-100.html';

const numberOfPages = 100; // * 100
const urls = [];

(async () => {
    const browser = await puppeteer.launch({ headless: true });
    const page = await browser.newPage();

    for (let i = 0; i < numberOfPages; i++) {
        url = `https://www.nachrichtenleicht.de/api/partials/PaginatedArticles_NL?drsearch:currentItems=${i*100}&drsearch:itemsPerLoad=100&drsearch:partialProps={%22sophoraId%22:%22nachrichtenleicht-nachrichten-100%22}&drsearch:_ajax=1`;

        await page.goto(url);
        // await page.waitForSelector('button.content-loader-btn-more.js-load-more-button')

        let html = await page.content();
        const $ = cheerio.load(html);
        $('article a').each((index, element) => {
            urls.push($(element).attr('href'));
        })
        
    }


    // Get detail texts
    let i = 0;
    for (const url of urls) {
        console.log(url);

        await page.goto(url);

        let html = await page.content();
        const $ = cheerio.load(html);
        let content = '';
        $('.article-details-text').each((index, element) => {
            content += $(element).text()+ "#P#\n";
        });

        try {
            fs.writeFileSync(`../plain/nachrichtenleicht.de/${i}.txt`, content);
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


