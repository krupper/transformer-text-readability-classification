//requiring path and fs modules
const path = require('path');
const fs = require('fs');


//joining path of directory 
const directoryPath = path.join(__dirname, '../', 'raw_data', 'APA_sentence-aligned_LHA', 'A2-OR');

const output = "../plain/APAC/";

function uniq_fast(a) {
    var seen = {};
    var out = [];
    var len = a.length;
    var j = 0;
    for(var i = 0; i < len; i++) {
         var item = a[i];
         if(seen[item] !== 1) {
               seen[item] = 1;
               out[j++] = item;
         }
    }
    return out;
}

let i = 0;
fs.readdir(directoryPath, function (err, files) {
    //handling error
    if (err) {
        return console.log('Unable to scan directory: ' + err);
    } 

    files.forEach(function (file) {
        if (path.extname(file) == ".simpde"){
            let data = fs.readFileSync(directoryPath + "/" + file, 'utf8');

            let sentences = uniq_fast(data.split("\n"));
            let content = "";

            for (const sentence of sentences) {
                let temp = sentence.replace("    ", "");
                temp = temp.replace("    ", "");
                temp = temp.replace("    ", "");
                temp = temp.replace("    ", "");
                temp = temp.replace(" ,", ",");
                temp = temp.replace(" .", ".");
                
                content += temp + "\n";
            }

            fs.writeFileSync(output+i+".txt", content);
            console.log(i);
            i++;
        }

    });
});