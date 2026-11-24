# usage: earnings21.py nlp rttm out_truth id duration
import sys, json
nlp, rttm, out, sid, dur = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], float(sys.argv[5])
rows=[l.rstrip('\n').split('|') for l in open(nlp)][1:]
runs=[]
for r in rows:
    tok,spk,punc=r[0],r[1],r[4]
    if not runs or runs[-1]['speaker']!=spk: runs.append({'speaker':spk,'toks':[]})
    runs[-1]['toks'].append(tok+punc)
segs=[l.split() for l in open(rttm) if l.startswith('SPEAKER')]
sruns=[]
for x in segs:
    s=float(x[3]); e=s+float(x[4]); spk=x[7]
    if not sruns or sruns[-1]['speaker']!=spk: sruns.append({'speaker':spk,'start':s,'end':e})
    else: sruns[-1]['end']=e
assert len(runs)==len(sruns) and all(a['speaker']==b['speaker'] for a,b in zip(runs,sruns)), 'run mismatch'
turns=[{'start':round(b['start'],2),'end':round(b['end'],2),'lang':'en','speaker':'S'+a['speaker'],'text':' '.join(a['toks'])} for a,b in zip(runs,sruns)]
spk=sorted({t['speaker'] for t in turns})
json.dump({'id':sid,'duration_sec':dur,'speakers':len(spk),'source':'Earnings-21 (Rev.com), file 4366893 (Earthstone Energy Q2 earnings call), full length; turn times from the official RTTM, text from the speaker-labelled NLP reference (runs matched 1:1)','license':'CC BY-SA 4.0 per repo LICENSE.md (which names transcripts/text files explicitly; audio is earnings-call content distributed in the same CC BY-SA repo)','turns':turns}, open(out,'w'), ensure_ascii=False, indent=1)
print(sid,len(turns),'turns',len(spk),'speakers')
