"""Import uploaded OCR PDF. Usage: python scripts/import-textbook.py /path/to/source.pdf"""
import bisect, hashlib, json, re, sys
from pathlib import Path
import fitz
root = Path(__file__).resolve().parents[1]
pdf = Path(sys.argv[1])
doc = fitz.open(pdf)
# Printed page starts transcribed from the book's contents (PDF pages 8–10).
sections = [(3,'体育概论与体育锻炼','体育的概述'),(8,'体育概论与体育锻炼','体育的功能与奥林匹克精神'),(11,'体育概论与体育锻炼','高等学校体育'),(13,'体育概论与体育锻炼','体育锻炼与心理健康'),(16,'体育概论与体育锻炼','体育锻炼与社会适应能力'),(20,'体育锻炼与健康体能','健康体能概述'),(24,'体育锻炼与健康体能','体育锻炼与身体成分'),(25,'体育锻炼与健康体能','体育锻炼对心肺耐力的提高'),(29,'体育锻炼与健康体能','体育锻炼对肌肉力量与肌肉耐力的提高'),(33,'体育锻炼与健康体能','体育锻炼对柔韧性的提高'),(38,'体质健康与运动性疲劳','体质健康状态评测'),(44,'体质健康与运动性疲劳','体育锻炼与健康生活方式'),(52,'体质健康与运动性疲劳','体育锻炼与营养膳食'),(56,'体质健康与运动性疲劳','运动性疲劳的成因与恢复'),(62,'体育卫生保健与运动性疾病的预防','体育锻炼中常见的生理反应'),(65,'体育卫生保健与运动性疾病的预防','体育锻炼中的卫生常识与安全'),(69,'体育卫生保健与运动性疾病的预防','运动性疾病的预防、处理和康复'),(74,'体育卫生保健与运动性疾病的预防','运动处方的制订与应用'),(81,'田径','概述'),(82,'田径','项目群简介'),(86,'田径','大学生体质健康测试内容精要'),(98,'球类运动','篮球'),(122,'球类运动','排球'),(141,'球类运动','足球'),(162,'球类运动','羽毛球'),(182,'球类运动','网球'),(203,'球类运动','乒乓球'),(216,'球类运动','棒、垒球'),(234,'球类运动','手球'),(264,'球类运动','板球'),(285,'球类运动','气排球'),(317,'球类运动','高尔夫球'),(327,'民族传统体育与武术','长拳'),(337,'民族传统体育与武术','咏春拳'),(349,'民族传统体育与武术','太极拳'),(362,'民族传统体育与武术','剑术'),(370,'民族传统体育与武术','龙舞运动'),(385,'民族传统体育与武术','木兰拳'),(427,'民族传统体育与武术','传统体育养生'),(443,'民族传统体育与武术','防身术'),(457,'民族传统体育与武术','射艺'),(462,'形体运动','健美操'),(470,'形体运动','艺术体操'),(504,'形体运动','体育舞蹈'),(544,'形体运动','形体健美'),(562,'形体运动','有氧塑身'),(598,'形体运动','健美'),(615,'游泳与救生','游泳'),(633,'游泳与救生','游泳救生'),(641,'击剑','概述'),(644,'击剑','基本技术'),(648,'击剑','击剑战术'),(651,'击剑','击剑运动身体素质练习方法')]
entries=[]
for page in range(14,665):
    printed=page-11
    raw=doc[page-1].get_text()
    if not raw.strip(): continue
    # Remove OCR's artificial whitespace between Chinese characters; no factual corrections.
    text=re.sub(r'(?<=[\u3400-\u9fff])\s+(?=[\u3400-\u9fff])','',raw)
    text=re.sub(r'\n\s*\n+','\n',text).strip()
    _,chapter,section=sections[bisect.bisect_right([s[0] for s in sections],printed)-1]
    entries.append(dict(id=f'textbook-p{page:03}',topic=chapter+' · '+section,text=text,pdfPage=page,bookPage=printed,source=pdf.name))
data=dict(title='大学体育',editor='马祖勤',edition='2023年6月第1版',isbn='978-7-309-16591-3',source=pdf.name,sha256=hashlib.sha256(pdf.read_bytes()).hexdigest(),pdfPages=len(doc),note='正文按页提取OCR文字，未逐字校订；插图和表格请核对原PDF。章节按目录起始页归属。书页=PDF页-11。',entries=entries)
(root/'data/university-pe-textbook.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
h=(root/'index.html').read_text()
start='// BEGIN TEXTBOOK DATA\n'
end='// END TEXTBOOK DATA\n'
block=start+'const textbook='+json.dumps(entries,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+';\n'+end
if start in h: h=h[:h.index(start)]+block+h[h.index(end)+len(end):]
else: h=h.replace('let saved=new Set();',block+"rows.push(...textbook.map((entry,i)=>({id:6501+knowledge.length+i,text:entry.id,display:entry.topic+' · 书页 '+entry.bookPage,content:entry.text,original:entry.text,type:'textbook',options:[],source:entry.source,pdfPage:entry.pdfPage,bookPage:entry.bookPage})));\nlet saved=new Set();")
(root/'index.html').write_text(h)
print(f'Imported {len(entries)} pages; {sum(len(x["text"]) for x in entries)} characters')
