const fs = require('fs');
const path = require('path');

function walk(dir) {
    let results = [];
    const list = fs.readdirSync(dir);
    list.forEach(file => {
        file = path.join(dir, file);
        const stat = fs.statSync(file);
        if (stat && stat.isDirectory()) {
            if (!file.includes('pages_legacy')) {
                results = results.concat(walk(file));
            }
        } else {
            if (file.endsWith('.astro') || file.endsWith('.md') || file.endsWith('.jsx')) {
                results.push(file);
            }
        }
    });
    return results;
}

const files = walk('g:/0_RAFAL/Antigravity/subterra-project/injector/src');
let count = 0;
files.forEach(f => {
    let content = fs.readFileSync(f, 'utf-8');
    if (content.includes('SubTerra')) {
        content = content.replace(/SubTerra Data/g, 'Foundation Pricing Data');
        content = content.replace(/SubTerra Analytics/g, 'Foundation Pricing Data');
        content = content.replace(/SubTerra/g, 'Foundation Pricing');
        fs.writeFileSync(f, content, 'utf-8');
        console.log('Updated', f);
        count++;
    }
});
console.log('Total files updated:', count);
