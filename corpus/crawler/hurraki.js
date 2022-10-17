const fetch = require("node-fetch");
const fs = require('fs');

function addUrls(current_urls, urls){
    for (const page of current_urls) {
        urls.push(`https://hurraki.de/w/api.php?action=query&format=json&titles=${encodeURIComponent(page.title)}&prop=extracts&exintro&explaintext`);
    }
}

async function sleep(ms) {
  return new Promise((resolve) => {
    setTimeout(resolve, ms);
  });
}

(async () => {
    const all_articles_url = 'https://hurraki.de/w/api.php?action=query&list=allpages&format=json&aplimit=500';

    const urls = [];

    let res = await fetch(all_articles_url);
    let data = await res.json();
    addUrls(data.query.allpages, urls);
    
    while(data.continue){
        let continue_params = '&apcontinue=' + data.continue.apcontinue + '&continue=' + data.continue.continue;
        res = await fetch(all_articles_url+continue_params);
        data = await res.json();
        addUrls(data.query.allpages, urls);
    }

    let i = 0;
    for (const url of urls) {

        // Prevent a firewall block due to a too high load per IP address
        let run = true;
        while(run){
            try {

                res = await fetch(url);
                data = await res.json();
                run = false;
            } catch(FetchError){
                await sleep(Math.floor(Math.random() * 10) * 1000);
                console.log("Wait");
            }
        }

        let content = data.query.pages[Object.keys(data.query.pages)[0]].extract;

        if (content == ''){
            continue;
        }

        try {
            fs.writeFileSync(`../easy_to_read/hurraki/${i}.txt`, content);
            // file written successfully
            let progress = Math.round((i / urls.length) * 100);
            console.log(`${progress}%`);
        } catch (err) {
            console.error(err);
        }
        i++;
    }
})()