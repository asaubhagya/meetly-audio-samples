# usage: icsi.py ann_dir meeting out_truth id duration
import sys, json, re, glob, xml.etree.ElementTree as ET
ann, mtg, out, sid, dur = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], float(sys.argv[5])
NS='{http://nite.sourceforge.net/}'
turns=[]
for wf in sorted(glob.glob(f'{ann}/Words/{mtg}.*.words.xml')):
    ch=wf.split('.')[-3]; order=[]; words={}
    for el in ET.parse(wf).getroot():
        i=el.get(NS+'id'); order.append(i)
        if el.tag=='w': words[i]=el.text or ''
    idx={k:n for n,k in enumerate(order)}
    for seg in ET.parse(f'{ann}/Segments/{mtg}.{ch}.segs.xml').getroot():
        s=float(seg.get('starttime')); e=float(seg.get('endtime')); spk=seg.get('participant')
        toks=[]
        for c in seg:
            m=re.findall(r'id\(([^)]+)\)', c.get('href','')); 
            if not m: continue
            for k in order[idx[m[0]]:idx[m[-1]]+1]:
                if k in words: toks.append(words[k])
        text=''
        for t in toks:
            punc=not re.search(r'\w', t)
            text += t if (punc or not text) else ' '+t
        if not re.search(r'\w', text): continue
        turns.append({'start':round(s,2),'end':round(e,2),'lang':'en','speaker':spk,'text':text.strip()})
turns.sort(key=lambda t:(t['start'],t['end']))
spk=sorted({t['speaker'] for t in turns})
json.dump({'id':sid,'duration_sec':dur,'speakers':len(spk),'source':f'ICSI Meeting Corpus, meeting {mtg}, headset mix (full length); speaker labels are ICSI participant ids','license':'CC BY 4.0 (https://groups.inf.ed.ac.uk/ami/icsi/license.shtml)','turns':turns}, open(out,'w'), ensure_ascii=False, indent=1)
print(sid, len(turns),'turns', len(spk),'speakers', spk)
