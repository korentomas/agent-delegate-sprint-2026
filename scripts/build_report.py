"""Build report using styles/page setup from the official Apart DOCX template.
Requires python-docx==1.2.0. The third-party template is not redistributed.
Usage: python3 scripts/build_report.py --template /path/to/template.docx
Then export DOCX with LibreOffice or Word. No network performed here.
"""
import argparse,json
from pathlib import Path
from docx import Document
from docx.shared import Inches,Pt,RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--template',type=Path,required=True);a=p.parse_args()
doc=Document(a.template)
# Keep native styles and section properties, replace instructional body.
for child in list(doc._element.body):
 if child.tag!=qn('w:sectPr'):doc._element.body.remove(child)
style=doc.styles['normal'];style.font.name='Arial';style.font.size=Pt(10)
style.paragraph_format.space_after=Pt(7);style.paragraph_format.line_spacing=1.08
for key in ['Heading 2','Heading 3']:
 doc.styles[key].font.name='Arial';doc.styles[key].font.size=Pt(13 if key=='Heading 2' else 11)
 doc.styles[key].font.color.rgb=RGBColor.from_string('163A54')
 doc.styles[key].paragraph_format.space_before=Pt(8)
 doc.styles[key].paragraph_format.space_after=Pt(7)
pages=json.loads((ROOT/'report/content.json').read_text())
for idx,page in enumerate(pages):
 if idx:doc.add_page_break()
 for kind,text in page:
  if kind=='image':doc.add_picture(str(ROOT/text),width=Inches(6.4))
  elif kind=='table':
   t=doc.add_table(rows=0,cols=len(text[0]));t.autofit=True
   for i,row in enumerate(text):
    cells=t.add_row().cells
    for c,txt in zip(cells,row):
     c.text=txt
     for r in c.paragraphs[0].runs:r.font.size=Pt(9);r.bold=i==0
  elif kind in ['h2','h3']:doc.add_paragraph(text,style='Heading 2' if kind=='h2' else 'Heading 3')
  else:
   paragraph=doc.add_paragraph(style='normal');r=paragraph.add_run(text)
   if kind=='title':r.font.size=Pt(20);r.bold=True;r.font.color.rgb=RGBColor.from_string('163A54')
   if kind=='subtitle':r.font.size=Pt(11);r.italic=True
   if kind=='caption':r.font.size=Pt(8);r.italic=True
# Page footer with field; no claim of acceptance or sponsorship.
for section in doc.sections:
 fp=section.footer.paragraphs[0];fp.text='Agent Delegate • Apart Research AI Incident Response Sprint • '
 field=OxmlElement('w:fldSimple');field.set(qn('w:instr'),'PAGE');fp._p.append(field)
 for r in fp.runs:r.font.size=Pt(8)
doc.core_properties.title='Agent Delegate: A Protected Escalation Channel for Multi-Agent Containment'
doc.core_properties.author='Matías Podeley — BAISH (Buenos Aires AI Safety Hub)'
doc.core_properties.subject='Apart Research AI Incident Response Sprint, Track 1 — Containment'
doc.save(ROOT/'report/agent-delegate.docx')
print(ROOT/'report/agent-delegate.docx')
