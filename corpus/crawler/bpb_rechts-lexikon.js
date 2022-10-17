const puppeteer = require('puppeteer');
const cheerio = require('cheerio');
const fs = require('fs');

const urls = [];

(async () => {
    const browser = await puppeteer.launch({ headless: true });
    const page = await browser.newPage();

    const url = 'https://www.bpb.de/kurz-knapp/lexika/recht-a-z/';
    await page.goto(url);

    let html = await page.content();
    const $ = cheerio.load(html);

    $('a.topic-list__link').each((index, element) => {
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
        $('.text-content.spacer-horizontal__inset-narrow > p').each((index, element) => {
            
            let temp = $(element).html().replaceAll('<br>', '#P#\n');
            temp = cheerio.load(temp).text().replace(/\xA0/g,' ') + "\n";
            // temp = cheerio.load(temp).text().replaceAll('#RETURN#', '\n').replace(/\xA0/g,' ') + "\n";

            temp = temp.replaceAll("Interner Link: ", "");
            temp = temp.replaceAll("Externer Link: ", "");
            temp = temp.replaceAll("  ", " ");

            if(!temp.includes("Quelle:") && !temp.includes("Das Lexikon als barrierefreie PDF herunterladen") && !temp.includes(" Artikel als PDF zum Download") && !temp.includes("Siehe auch:") && !temp.includes("Duden Wirtschaft"))
                content += temp;
        });

        if(content == '')
            continue;

        try {
            console.log(content);
            
            fs.writeFileSync(`../everyday/bpb_rechts-lexikon/${i}.txt`, content);
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

