//https://aug.dguv.de/wp-json/arbeitge/v2/leichte-sprache?postPage=7

const puppeteer = require('puppeteer');
const cheerio = require('cheerio');
const fs = require('fs');
const fetch = require("node-fetch");

const urls = [];

(async () => {
    for (let i = 0; i <= 7; i++) {
        let url = `https://aug.dguv.de/wp-json/arbeitge/v2/leichte-sprache?postPage=${i}`;
        let res = await fetch(url);
        let data = await res.json();

        for (const url of data) {
            urls.push(url.link);
        }
    }

    const browser = await puppeteer.launch({ headless: true });
    const page = await browser.newPage();

    // Get detail texts
    let i = 0;
    for (const url of urls) {
        console.log(url);

        await page.goto(url);

        let html = await page.content();
        const $ = cheerio.load(html);
        let content = '';

        let copyrightText = $('div.article-item__text').last().text();

        $('div.article-item__text').each((index, element) => {
            let elements = $(element).find("p, li");

            // remove copyright texts
            let text = $(element).text();
            if (text == copyrightText){
                return false;
            }

            elements.each((index, element) => {
                let text = $(element).text();

                if(text == ""){
                    return false;
                }
                
                content += text.trim() + "#P#\n";

                console.log(text);
                console.log("---------");
            });
        });

        if(content == '')
            continue;

        try {
            fs.writeFileSync(`../easy_to_read/dguv/${i}.txt`, content);
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

