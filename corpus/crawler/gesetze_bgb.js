const fs = require('fs/promises');
const {XMLParser, XMLBuilder, XMLValidator} = require('fast-xml-parser');


let i = 0;
(async () => {
    try {
        const data = await fs.readFile('../raw_data/Gesetze/BGB/data.xml', { encoding: 'utf8' });
        let output = "";

        const parser = new XMLParser();
        let jsonObj = parser.parse(data);


        // console.log(jsonObj.dokumente.norm);


        for (const item of jsonObj.dokumente.norm) {
            
            // skip item if it does not include a text
            // if(!item.textdaten.text.TOC){
            //     continue;
            // }
            
            // console.log(item);
            // console.log("--------");
            try {
                let temp = item.textdaten.text.Content.P;

                // skip removed paragraphs
                if(temp == "-"){
                    continue;
                }

                // skip empty paragraphs
                if(temp == ""){
                    continue;
                }
               
                // if item is a string
                if(typeof temp == "string"){
                    temp = temp.replaceAll(/\([0-9]+\)\s/g, ""); 
                    output += temp + "\n";
                    continue;
                }

                // if item is an array
                if(Array.isArray(temp)){
                    for (let line of temp) {

                        if(typeof line == "string"){
                            // Remove line numbers
                            line = line.replaceAll(/\([0-9]+\)\s/g, ""); 
                            output += line + "\n";
                        }
                    }
                    continue;
                }

                console.log(temp);
                
            }catch {
                //console.log(item);
            }
        }



        // Write output to file
        if(output != "")
            console.log(output);    
            await fs.writeFile(`../special/gesetze_bgb/${i}.txt`, output);
    } catch (err) {
        console.log(err);
    }

})()