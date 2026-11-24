# usage: ami.py ann_dir meeting win_start win_len out_truth id
import sys, json, re, glob, os, xml.etree.ElementTree as ET
ann, mtg, ws, wl, out, sid = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4]), sys.argv[5], sys.argv[6]
NS='{http://nite.sourceforge.net/}'
turns=[]
for wf in sorted(glob.glob(f'{ann}/words/{mtg}.*.words.xml')):
    spk=wf.split('.')[-3]
    words={}; order=[]
    for el in ET.parse(wf).getroot():
        i=el.get(NS+'id'); order.append(i)
        if el.tag=='w': words[i]=(el.text or '', el.get('punc')=='true', el.get('starttime'), el.get('endtime'))
    idx={k:n for n,k in enumerate(order)}
    for seg in ET.parse(f'{ann}/segments/{mtg}.{spk}.segments.xml').getroot():
        s=float(seg.get('transcriber_start')); e=float(seg.get('transcriber_end'))
        if s<ws or e>ws+wl: continue
        toks=[]
        for ch in seg:
            m=re.findall(r'id\(([^)]+)\)', ch.get('href'))
            a=idx[m[0]]; b=idx[m[-1]]
            for k in order[a:b+1]:
                if k in words: toks.append(words[k])
        text=''
        for t,p,_,_ in toks: text += t if (p or not text) else ' '+t
        if not text.strip(): continue
        turns.append({'start':round(s-ws,2),'end':round(e-ws,2),'lang':'en','speaker':spk,'text':text.strip()})
turns.sort(key=lambda t:(t['start'],t['end']))
json.dump({'id':sid,'duration_sec':wl,'source':f'AMI Meeting Corpus, meeting {mtg}, Mix-Headset, window {ws:.0f}s-{ws+wl:.0f}s (University of Edinburgh / AMI Consortium)','license':'CC BY 4.0 (https://groups.inf.ed.ac.uk/ami/corpus/license.shtml)','turns':turns}, open(out,'w'), ensure_ascii=False, indent=1)
print(sid, len(turns), 'turns', sorted({t['speaker'] for t in turns}))
