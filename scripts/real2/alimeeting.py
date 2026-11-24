# usage: alimeeting.py textgrid out_truth id duration
import sys, json, re
tg, out, sid, dur = sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4])
turns=[]; spk=None; cur={}
for line in open(tg, encoding='utf-8'):
    l=line.strip()
    m=re.match(r'name = "(.*)"', l)
    if m: spk=m.group(1).replace('N_',''); continue
    m=re.match(r'xmin = ([\d.]+)', l)
    if m and spk: cur={'start':float(m.group(1))}; continue
    m=re.match(r'xmax = ([\d.]+)', l)
    if m and 'start' in cur: cur['end']=float(m.group(1)); continue
    m=re.match(r'text = "(.*)"$', l)
    if m and 'end' in cur:
        t=m.group(1).strip()
        if t: turns.append({'start':round(cur['start'],2),'end':round(cur['end'],2),'lang':'zh','speaker':spk,'text':t})
        cur={}
turns.sort(key=lambda t:(t['start'],t['end']))
s=sorted({t['speaker'] for t in turns})
json.dump({'id':sid,'duration_sec':dur,'speakers':len(s),'source':'AliMeeting Eval set (Alibaba DAMO / OpenSLR SLR119), meeting R8001_M8004, far-field 8-mic array, channel 1 only, full length; labels from the official far-field TextGrid','license':'CC BY-SA 4.0 (https://www.openslr.org/119/)','turns':turns}, open(out,'w'), ensure_ascii=False, indent=1)
print(sid,len(turns),'turns',s)
