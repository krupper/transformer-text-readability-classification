const fs = require('fs');
const path = require('path');
const csv = require('fast-csv');


let i = 0;
let output = '../everyday/open-discourse/';

fs.createReadStream(path.resolve(__dirname, '..', 'raw_data', 'open_discourse', 'speeches.csv'))
    .pipe(csv.parse({ headers: true }))
    .on('error', error => console.error(error))
    .on('data', row => {
        let content = row.speechContent;
        content = content.replace(/\({[0-9]+}\)/g, "") 
        let date = new Date(row.date);


        let size = content.split(" ").length;

        // save all speeches from 2012 to now with more than 50 words.
        if(date.getFullYear() > 2011 && size > 50){
            fs.writeFile(output+i+".txt", content, (err) => {
                if (err) throw err;
            });

            console.log(i);
            
            i++;
        }
    })
    .on('end', rowCount => console.log(`Parsed ${rowCount} rows`));