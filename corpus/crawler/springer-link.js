const puppeteer = require('puppeteer');
const cheerio = require('cheerio');
const fs = require('fs');
const fetch = require("node-fetch");


function isHeading(text){
    if(!['.', '!', ';', '?'].some(el => text[text.length-1] == el)){
        if(text.split(" ").length < 4){
            console.log("HEADING WARNING: ", text);    
        }

        return true; 
    }
    return false;
}

(async () => {
    const apiKey = "7c5e530b758e44f7df845aba64cfb454";

    let i = 0;
    for (let j = 0; j < 500; j++) {
        const start = (j * 100) + 1;
        const url = `https://api.springernature.com/meta/v2/json?api_key=${apiKey}&q=language%3Ade+-(subject:%22Medicine%22)&s=${start}&p=100`;
        console.log(url);

        let res = await fetch(url);
        let data = await res.json();
        data = data.records;

        
        for (const article of data) {
            let content = '';

            // skip empty paragraphs
            if(article.abstract == ""){
                continue;
            }

            if(typeof article.abstract == "string" && !isHeading(article.abstract)){
                content = article.abstract + "\n";
            }

            if(Array.isArray(article.abstract)){
                for (const line of article.abstract) {
                    if(!isHeading(line)){
                        content += line + "\n";
                    }
                }
            }

            if(content == ""){
                continue;
            }

            try {
                fs.writeFileSync(`../special/springer-link/${i}.txt`, content);
                // file written successfully
                let progress = Math.round((i / data.length) * 100);
                console.log(`${progress}%`);
            } catch (err) {
                console.error(err);
            }
            i++;
            console.log(content);
        }    
    }
})()