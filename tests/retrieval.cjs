const fs=require('fs'),vm=require('vm'),assert=require('assert');const h=fs.readFileSync(__dirname+'/../index.html','utf8');const scripts=[...h.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(x=>x[1]);const c={};vm.createContext(c);vm.runInContext(scripts[0],c);vm.runInContext(scripts[2],c);const ec={module:{exports:{}}};vm.createContext(ec);vm.runInContext(scripts[1],ec);const e=ec.module.exports;const rows=Object.entries(c.fdty_database).map(([key,answer],id)=>{const d=c.fdty_details[key]||{};return {id,text:key,display:d.text||key,normalized:e.normalize(d.text||key),type:typeof answer==='boolean'?'boolean':'choice',options:d.options||[]}});const data=JSON.parse(fs.readFileSync(__dirname+'/../data/mulan-outline.json')).entries;rows.push(...data.map((x,i)=>({id:6501+i,text:x.id,display:x.topic+' 原第'+x.number+'条',content:x.text,type:'knowledge',options:[],normalized:e.normalize(x.text)})));const textbook=JSON.parse(fs.readFileSync(__dirname+'/../data/university-pe-textbook.json')).entries;rows.push(...textbook.map((x,i)=>({id:6616+i,text:x.id,display:x.topic+' · 书页 '+x.bookPage,content:x.text,type:'textbook',options:[]})));assert.equal(rows.length,7266);const cases=[['木兰拳的创始人是谁','杨文娣'],['木兰源的创始人是人谁','杨文娣'],['八段锦第三式叫什么','调理脾胃须单举'],['木兰拳规定套路有多少式','28式'],['木兰拳比赛场地长宽','长14米'],['平衡不足2秒扣多少分','不足2秒扣0.1'],['木兰拳采用什么呼吸','胸式呼吸']];let failures=0;for(const [q,want]of cases){const got=e.search(rows,q,'all',new Set());const rank=got.findIndex(r=>(r.content||r.display).includes(want));console.log(q,'target rank',rank+1,'top:',got.slice(0,3).map(r=>(r.content||r.display).slice(0,100)));if(rank<0||rank>=8)failures++;}assert.equal(failures,0);assert.equal(e.search(rows,'zzzzqwerty123','all',new Set()).length,0);assert.equal(e.search(rows,'杨文娣','knowledge',new Set(),'exact').length,1);assert(e.search(rows,'八段锦','boolean',new Set()).every(r=>r.type==='boolean'));assert.equal(e.search(rows,'','saved',new Set(['mulan-001'])).length,1);console.log('Retrieval checks passed');

const ids=q=>Array.from(e.search(rows,q,'all',new Set()),r=>r.id);
for(const q of ['8断锦','8段锦','八断锦','８断锦'])assert.deepStrictEqual(ids(q),ids('八段锦'),q);
const sample=['木兰拳具有舒展的动作特点，传统健身项目八段锦也受到欢迎。','八段锦的动作与木兰拳的动作各有特点。','木兰拳动作舒展。','八段锦动作柔和。'].map((display,id)=>({id,text:String(id),display,normalized:e.normalize(display),type:'boolean',options:[]}));
for(const q of ['木兰拳 八段锦','木兰拳和八段锦','木兰拳和8断锦','八段锦 木兰拳','木兰拳、八段锦'])assert.deepStrictEqual(Array.from(e.search(sample,q,'all',new Set()),r=>r.id),[0,1],q);
assert.equal(e.search(sample,'木兰拳 不存在的词','all',new Set()).length,0);
assert.equal(e.search(sample,'8断锦','all',new Set(),'exact').length,0);
assert.deepStrictEqual(Array.from(e.search(sample,'木兰拳 八段锦','all',new Set(),'exact'),r=>r.id),[0,1]);
console.log('Alias and separated-keyword checks passed');

assert.equal(textbook.length,650);
assert.equal(new Set(rows.map(r=>r.text)).size,rows.length);
assert.equal(e.search(rows,'','textbook',new Set()).length,650);
const textbookMatches=e.search(rows,'木兰拳','textbook',new Set(),'exact');
assert(textbookMatches.length>0);
assert(textbookMatches.every(r=>r.type==='textbook'));
assert(textbookMatches.some(r=>r.display.includes('书页 385')));
assert.equal(e.search(rows,'','saved',new Set(['textbook-p396'])).length,1);
assert(e.search(rows,'心肺耐力','textbook',new Set(),'exact').length>0);
for(const entry of textbook){assert.equal(entry.pdfPage-entry.bookPage,11);assert(entry.text.trim());}
const embedded=JSON.parse(h.match(/const textbook=(.*);\n/)[1]);
assert.deepStrictEqual(embedded,textbook);
console.log('Textbook retrieval, source pages, favorites and offline data checks passed');
