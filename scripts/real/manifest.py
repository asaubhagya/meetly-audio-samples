import sys, json, glob, os, hashlib
root=sys.argv[1]; titles=json.loads(open(sys.argv[2]).read())
out=[]
for tf in sorted(glob.glob(f'{root}/truth/*.json')):
    t=json.load(open(tf)); sid=t['id']; a=f'{root}/audio/{sid}.wav'
    b=open(a,'rb').read()
    langs=[]
    for x in t['turns']:
        for l in x['lang'].split('+'):
            if l not in langs: langs.append(l)
    d=t['duration_sec']; length='short' if d<90 else ('medium' if d<300 else 'long')
    out.append({'id':sid,'title':titles.get(sid,sid),'languages':langs,'duration_sec':round(d,1),'turns':len(t['turns']),'length':length,
      'audio':f'audio/{sid}.wav','truth':f'truth/{sid}.json','bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'enabled':True,
      'source':t['source'],'license':t['license'],'speakers':len({x['speaker'] for x in t['turns']})})
json.dump(out, open(f'{root}/manifest-entries.json','w'), ensure_ascii=False, indent=1)
for e in out: print(e['id'],e['duration_sec'],e['turns'],e['speakers'],e['languages'],e['bytes'])
print('total MB', round(sum(e['bytes'] for e in out)/1e6,1))
