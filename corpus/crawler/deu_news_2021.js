const fs = require('fs/promises');

let i = 0;
(async () => {
    try {
        const data = await fs.readFile('../raw_data/deu_news_2021_1M-sentences.txt', { encoding: 'utf8' });

        let output = ""
        for (const line of data.split("\n")) {
            let temp = line.split("\t")[1];

            if(output.length < 100000){
                output += temp + "\n";
            }else {
                console.log(output);
                console.log("------------");
                console.log(" ");

                // Write output to file
                await fs.writeFile(`../everyday/deu_news_2021/${i}.txt`, output);
                i++;
                output = "";
            }
        }

        // Write output to file
        if(output != "")
            await fs.writeFile(`../everyday/deu_news_2021/${i}.txt`, output);
    } catch (err) {
        console.log(err);
    }

})()