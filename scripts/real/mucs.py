# usage: mucs.py transcripts_dir wav_dir rec out_dir id
import sys, json, re, subprocess
td, wd, rec, outd, sid = sys.argv[1:6]
text=dict(l.rstrip('\n').split(' ',1) for l in open(f'{td}/text') if ' ' in l)
u2s=dict(l.split() for l in open(f'{td}/utt2spk'))
turns=[]
for l in open(f'{td}/segments'):
    u,w,s,e=l.split()
    if w!=rec: continue
    t=text.get(u,'').strip()
    if not t: continue
    lat=bool(re.search(r'[A-Za-z]',t)); dev=bool(re.search(r'[ऀ-ॿ]',t))
    turns.append({'start':float(s),'end':float(e),'lang':'hi+en' if lat and dev else ('en' if lat else 'hi'),'speaker':u2s[u],'text':t,'segment':u})
turns.sort(key=lambda x:x['start'])
end=turns[-1]['end']
subprocess.run(['ffmpeg','-v','error','-y','-i',f'{wd}/{rec}.wav','-t',str(end),'-ac','1','-ar','16000','-c:a','pcm_s16le',f'{outd}/audio/{sid}.wav'],check=True)
json.dump({'id':sid,'duration_sec':round(end,2),'source':f'MUCS 2021 sub-task 2, Hindi-English test set (OpenSLR SLR104; IIT Madras Spoken Tutorial lecture), recording {rec}, continuous unedited audio with original segment timestamps','license':'CC BY-SA 4.0 (https://www.openslr.org/104/)','turns':turns}, open(f'{outd}/truth/{sid}.json','w'), ensure_ascii=False, indent=1)
import collections; print(sid, len(turns), round(end/60,1),'min', collections.Counter(x['lang'] for x in turns))
