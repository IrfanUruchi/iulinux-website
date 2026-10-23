#!/usr/bin/env python3
"""Build Handbook HTML and PDF from the authoritative Markdown source."""
from pathlib import Path
import html as htmlmod, re
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer, Preformatted, Image, Table, TableStyle, PageBreak, KeepTogether, CondPageBreak
from reportlab.platypus.tableofcontents import TableOfContents

ROOT=Path(__file__).resolve().parents[1]; SOURCE=ROOT/'docs/handbook.md'; PDF=ROOT/'assets/downloads/IULinux-0.1-Alpha-Handbook.pdf'; HTML=ROOT/'handbook.html'
def parse_md(text):
    lines=text.splitlines(); out=[]; i=0
    while i<len(lines):
        line=lines[i]
        if not line.strip(): i+=1; continue
        if line.startswith('```'):
            lang=line[3:].strip(); i+=1; buf=[]
            while i<len(lines) and not lines[i].startswith('```'): buf.append(lines[i]); i+=1
            out.append(('code',lang,'\n'.join(buf))); i+=1; continue
        if line.startswith('|'):
            rows=[]
            while i<len(lines) and lines[i].startswith('|'):
                cells=[c.strip() for c in lines[i].strip('|').split('|')]
                if not all(set(c)<=set('-: ') for c in cells): rows.append(cells)
                i+=1
            out.append(('table',rows)); continue
        m=re.match(r'^(#{1,6})\s+(.*)$',line)
        if m: out.append(('h',len(m.group(1)),m.group(2))); i+=1; continue
        if line.startswith('> '):
            buf=[]
            while i<len(lines) and lines[i].startswith('> '): buf.append(lines[i][2:]); i+=1
            out.append(('callout',' '.join(buf))); continue
        if line.startswith('!['):
            m=re.match(r'!\[([^]]*)\]\(([^)]+)\)',line)
            if m: out.append(('image',m.group(1),m.group(2))); i+=1; continue
        if re.match(r'^[-*] ',line) or re.match(r'^\d+\. ',line):
            ordered=bool(re.match(r'^\d+\. ',line)); items=[]
            while i<len(lines) and ((ordered and re.match(r'^\d+\. ',lines[i])) or (not ordered and re.match(r'^[-*] ',lines[i]))): items.append(re.sub(r'^(-|\*|\d+\.)\s+','',lines[i])); i+=1
            out.append(('list',ordered,items)); continue
        buf=[line]; i+=1
        while i<len(lines) and lines[i].strip() and not re.match(r'^(#{1,6})\s|^```|^> |^[-*] |^\d+\. |^\||^!\[',lines[i]): buf.append(lines[i]); i+=1
        out.append(('p',' '.join(buf)))
    return out
def inline(s):
    s=htmlmod.escape(s,quote=False); s=re.sub(r'`([^`]+)`',r'<font name="Courier">\1</font>',s); s=re.sub(r'\*\*([^*]+)\*\*',r'<b>\1</b>',s); return re.sub(r'\[([^]]+)\]\(([^)]+)\)',r'<link href="\2" color="#3c6b37">\1</link>',s)
def slug(s): return re.sub(r'[^a-z0-9]+','-',s.lower()).strip('-')
CSS='''.handbook-hero{background:var(--green-dark);color:#edf4ec;padding:70px 0 62px}.handbook-hero h1{font-size:clamp(2.8rem,6vw,5.2rem);max-width:850px}.handbook-hero p{max-width:720px;color:#b6cbb9;font-size:1.12rem}.handbook-layout{display:grid;grid-template-columns:220px 1fr;gap:60px;padding:64px 0}.toc{position:sticky;top:20px;align-self:start;border-top:2px solid var(--green);padding-top:16px}.toc strong{display:block;margin-bottom:10px}.toc a{display:block;color:var(--muted);font-size:.83rem;text-decoration:none;padding:6px 0}.handbook-content{min-width:0}.handbook-content h2{font-size:2.35rem;margin-top:4.4rem;padding-top:1rem;border-top:1px solid var(--line)}.handbook-content h3{font-size:1.45rem;margin-top:2.4rem}.handbook-content p,.handbook-content li{max-width:820px;color:#4f5d55}.handbook-content li{margin:7px 0}.handbook-content a{color:var(--green-deep);font-weight:650}.handbook-content pre{max-width:820px;background:#17201d;color:#d9e7db;padding:17px 20px;overflow:auto;border-radius:5px;font:.82rem/1.6 ui-monospace,SFMono-Regular,Menlo,monospace}.handbook-content code{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;background:#e8f0e7;padding:.12em .3em;border-radius:3px}.handbook-content pre code{background:transparent;padding:0}.callout{max-width:820px;background:#fff5d9;border-left:4px solid #a77914;padding:16px 18px;margin:20px 0}.handbook-content figure{max-width:820px;margin:24px 0}.handbook-content figure img{display:block;max-width:100%;height:auto;border:1px solid var(--line)}.handbook-content figcaption{font-size:.8rem;color:var(--muted);padding-top:7px}.table-wrap{overflow:auto;max-width:900px;margin:20px 0}.handbook-content table{border-collapse:collapse;width:100%;font-size:.9rem;background:#fff}.handbook-content th,.handbook-content td{border:1px solid var(--line);padding:10px;text-align:left;vertical-align:top}.handbook-content th{background:#e8f0e7;color:var(--ink)}@media(max-width:800px){.handbook-layout{grid-template-columns:1fr;gap:25px}.toc{position:static}.handbook-content h2{font-size:2rem}}'''
def build_html(bs):
    toc=[]; body=[]
    for b in bs:
        if b[0]=='h' and b[1]==1 and not body:
            continue
        if b[0]=='h':
            ident=slug(b[2]); body.append(f'<h{b[1]} id="{ident}">{inline(b[2])}</h{b[1]}>'); toc.append((b[1],b[2],ident))
        elif b[0]=='p': body.append(f'<p>{inline(b[1])}</p>')
        elif b[0]=='code': body.append(f'<pre><code>{htmlmod.escape(b[2])}</code></pre>')
        elif b[0]=='callout': body.append(f'<aside class="callout"><strong>Important:</strong> {inline(b[1])}</aside>')
        elif b[0]=='image': body.append(f'<figure><img src="{b[2].replace("../","")}" alt="{htmlmod.escape(b[1])}"><figcaption>{inline(b[1])}</figcaption></figure>')
        elif b[0]=='list': body.append(('<ol>' if b[1] else '<ul>')+''.join('<li>'+inline(x)+'</li>' for x in b[2])+('</ol>' if b[1] else '</ul>'))
        elif b[0]=='table': body.append('<div class="table-wrap"><table><thead><tr>'+''.join('<th>'+inline(x)+'</th>' for x in b[1][0])+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+inline(x)+'</td>' for x in row)+'</tr>' for row in b[1][1:])+'</tbody></table></div>')
    nav=''.join(f'<a href="#{i}">{inline(t)}</a>' for l,t,i in toc if l==2)
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="IULinux 0.1 Alpha 1 technical and user handbook"><title>IULinux Handbook — 0.1 Alpha 1</title><link rel="icon" href="assets/iulinux-mark.png" type="image/png"><link rel="stylesheet" href="styles.css"><link rel="stylesheet" href="overrides.css"><style>{CSS}</style></head><body><a class="skip-link" href="#handbook">Skip to handbook</a><header class="site-header"><a class="brand" href="index.html"><img class="brand-image" src="assets/iulinux-mark.png" alt=""><span>IULinux</span></a><nav class="site-nav" aria-label="Handbook navigation"><a href="index.html">Website</a><a href="assets/downloads/IULinux-0.1-Alpha-Handbook.pdf">Download PDF</a><a href="https://github.com/IrfanUruchi/IULinux">GitHub ↗</a></nav></header><section class="handbook-hero"><div class="section-wrap"><p class="eyebrow eyebrow-green">Technical Handbook / 0.1 Alpha 1</p><h1>Install, use, understand, contribute.</h1><p>A practical reference for installing, using, troubleshooting, and maintaining IULinux Alpha 1.</p></div></section><main id="handbook" class="section-wrap handbook-layout"><aside class="toc"><strong>Contents</strong>{nav}</aside><article class="handbook-content">{''.join(body)}</article></main><footer class="site-footer"><div class="section-wrap footer-inner"><a class="brand" href="index.html"><img class="brand-image" src="assets/iulinux-mark.png" alt=""><span>IULinux</span></a><p>Technical Handbook — 0.1 Alpha 1</p><a href="index.html">Website</a></div></footer></body></html>'''
class Doc(BaseDocTemplate):
    def __init__(self,*a,**kw):
        super().__init__(*a,**kw); self.addPageTemplates([PageTemplate(id='main',frames=Frame(18*mm,22*mm,174*mm,245*mm,id='normal'),onPage=self.footer)])
    def footer(self,c,d):
        c.saveState(); c.setStrokeColor(colors.HexColor('#dce3dc')); c.line(18*mm,16*mm,192*mm,16*mm); c.setFont('Helvetica',8); c.setFillColor(colors.HexColor('#5e6a65')); c.drawString(18*mm,10*mm,'IULinux 0.1 Alpha — Technical Handbook'); c.drawRightString(192*mm,10*mm,str(d.page)); c.restoreState()
    def afterFlowable(self,f):
        if isinstance(f,Paragraph) and f.style.name in ('H1','H2'):
            key=slug(f.getPlainText()); title=f.getPlainText(); level=0 if f.style.name=='H1' else 1
            self.canv.bookmarkPage(key); self.canv.addOutlineEntry(title,key,level=level,closed=False)
            if title not in ('Contents','IULinux 0.1 Alpha 1 — Technical and User Handbook'):
                self.notify('TOCEntry',(level,title,self.page,key))
def build_pdf(bs):
    ss=getSampleStyleSheet(); ss.add(ParagraphStyle(name='H1',parent=ss['Heading1'],fontSize=20,leading=24,textColor=colors.HexColor('#3c6b37'),spaceBefore=16,spaceAfter=8)); ss.add(ParagraphStyle(name='H2',parent=ss['Heading2'],fontSize=14,leading=18,textColor=colors.HexColor('#3c6b37'),spaceBefore=14,spaceAfter=6)); ss.add(ParagraphStyle(name='H3',parent=ss['Heading3'],fontSize=11,leading=14,spaceBefore=10,spaceAfter=4)); ss.add(ParagraphStyle(name='BodyX',parent=ss['BodyText'],fontSize=9.2,leading=13,spaceAfter=6,textColor=colors.HexColor('#26332c'))); ss.add(ParagraphStyle(name='TableCell',parent=ss['BodyText'],fontSize=7.5,leading=9.2,spaceAfter=0,textColor=colors.HexColor('#26332c'))); ss.add(ParagraphStyle(name='CodeX',fontName='Courier',fontSize=7.2,leading=9.5,backColor=colors.HexColor('#eef3ed'),borderColor=colors.HexColor('#d2ddd1'),borderWidth=.5,borderPadding=6)); ss.add(ParagraphStyle(name='Caption',parent=ss['BodyText'],fontSize=7.8,leading=9.5,textColor=colors.HexColor('#5e6a65')))
    story=[Paragraph('IULinux 0.1 Alpha 1',ss['Title']),Paragraph('Technical and user handbook',ss['BodyX']),Paragraph('Revision 2026-10-23 · Source-backed Alpha documentation',ss['Caption']),Spacer(1,8*mm),Paragraph('Contents',ss['H1'])]; toc=TableOfContents(); toc.levelStyles=[ParagraphStyle(name='TOC1',fontSize=9,leftIndent=0,leading=12),ParagraphStyle(name='TOC2',fontSize=8,leftIndent=10,leading=10)]; story += [toc,PageBreak()]
    for b in bs:
        if b[0]=='h' and b[1]==1 and b[2].startswith('IULinux 0.1 Alpha 1'):
            continue
        if b[0]=='h':
            if 'diagram' in b[2].lower() or 'workflow reference' in b[2].lower(): story.append(CondPageBreak(65*mm))
            story.append(Paragraph(inline(b[2]),ss['H1' if b[1]<=2 else 'H3']))
        elif b[0]=='p': story.append(Paragraph(inline(b[1]),ss['BodyX']))
        elif b[0]=='code': story.append(KeepTogether([Preformatted(b[2],ss['CodeX'])]))
        elif b[0]=='callout': story.append(Paragraph('<b>Important:</b> '+inline(b[1]),ss['BodyX']))
        elif b[0]=='image':
            p=ROOT/b[2].replace('../','')
            if p.exists(): story += [Image(str(p),width=150*mm,height=92*mm),Paragraph(inline(b[1]),ss['Caption'])]
        elif b[0]=='list':
            for n,x in enumerate(b[2],1): story.append(Paragraph((f'{n}. ' if b[1] else '• ')+inline(x),ss['BodyX']))
        elif b[0]=='table':
            if len(b[1]) >= 20: story.append(PageBreak())
            data=[[Paragraph(inline(x),ss['TableCell']) for x in row] for row in b[1]]; t=Table(data,repeatRows=1,splitByRow=1,hAlign='LEFT'); t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e8f0e7')),('GRID',(0,0),(-1,-1),.4,colors.HexColor('#dce3dc')),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),4),('RIGHTPADDING',(0,0),(-1,-1),4)])); story += [t,Spacer(1,4)]
    Doc(str(PDF),pagesize=A4,title='IULinux 0.1 Alpha 1 Technical Handbook',author='IULinux Project').multiBuild(story)
if __name__=='__main__':
    bs=parse_md(SOURCE.read_text()); HTML.write_text(build_html(bs)); PDF.parent.mkdir(parents=True,exist_ok=True); build_pdf(bs); print(HTML); print(PDF)
