# usage: vp.py parquet lang out_dir id maxsec
import sys, json, io, wave, collections, subprocess, pyarrow.parquet as pq
pqf, lang, outd, sid, maxsec, want = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], float(sys.argv[5]), sys.argv[6]
t=pq.read_table(pqf, columns=['audio_id','speaker_id','raw_text','normalized_text','gender'])
rows=t.to_pylist()
by=collections.defaultdict(list)
for i,r in enumerate(rows): by[r['audio_id'].rsplit('_',2)[0]].append(i)
sess=want; idxs=by[want]
def key(i):
    a=rows[i]['audio_id'].rsplit('_',2); return (a[1], int(a[2]))
idxs.sort(key=key)
aud=pq.read_table(pqf, columns=['audio']).column('audio').to_pylist()
pcm=b''; turns=[]; t0=0.0; gap=b'\x00\x00'*8000
for i in idxs:
    b=aud[i]['bytes']
    p=subprocess.run(['ffmpeg','-v','error','-i','pipe:0','-ac','1','-ar','16000','-f','s16le','pipe:1'],input=b,capture_output=True,check=True).stdout
    d=len(p)/32000
    if t0+d>maxsec: break
    r=rows[i]
    turns.append({'start':round(t0,2),'end':round(t0+d,2),'lang':lang,'speaker':r['speaker_id'],'text':r['raw_text'] or r['normalized_text'],'segment':r['audio_id']})
    pcm+=p+gap; t0+=d+0.5
pcm=pcm[:-len(gap)]; dur=round(len(pcm)/32000,2)
w=wave.open(f'{outd}/audio/{sid}.wav','wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(16000); w.writeframes(pcm); w.close()
json.dump({'id':sid,'duration_sec':dur,'speakers':len({t['speaker'] for t in turns}),'source':f'VoxPopuli transcribed test split (Meta), European Parliament plenary session {sess}; consecutive segments in original order, joined with 0.5 s silence (inter-segment gaps removed)','license':'CC0 1.0 (VoxPopuli transcribed data; https://github.com/facebookresearch/voxpopuli#license)','turns':turns}, open(f'{outd}/truth/{sid}.json','w'), ensure_ascii=False, indent=1)
print(sid, sess, len(turns),'turns', dur,'s', len({t['speaker'] for t in turns}),'speakers')
