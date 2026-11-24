# usage: ascend.py parquet out_dir id session per_speaker_sec
import sys, json, wave, subprocess, collections, pyarrow.parquet as pq
pqf, outd, sid, sess, per = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], float(sys.argv[5])
rows=[r for r in pq.read_table(pqf).to_pylist() if str(r['session_id'])==sess]
rows.sort(key=lambda r:r['id'])
used=collections.Counter(); pcm=b''; turns=[]; t0=0.0; gap=b'\x00\x00'*4800
L={'zh':'zh','en':'en','mixed':'zh+en'}
for r in rows:
    spk=str(r['original_speaker_id'])
    if used[spk]>=per: continue
    p=subprocess.run(['ffmpeg','-v','error','-i','pipe:0','-ac','1','-ar','16000','-f','s16le','pipe:1'],input=r['audio']['bytes'],capture_output=True,check=True).stdout
    d=len(p)/32000; used[spk]+=d
    turns.append({'start':round(t0,2),'end':round(t0+d,2),'lang':L.get(r['language'],r['language']),'speaker':spk,'text':r['transcription'],'segment':r['id']})
    pcm+=p+gap; t0+=d+0.3
pcm=pcm[:-len(gap)]; dur=round(len(pcm)/32000,2)
w=wave.open(f'{outd}/audio/{sid}.wav','wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(16000); w.writeframes(pcm); w.close()
json.dump({'id':sid,'duration_sec':dur,'source':f'ASCEND (HKUST CAiRE) test split, session {sess} ({rows[0]["topic"]}), spontaneous Mandarin-English code-switched conversation; utterances in dataset order (grouped by speaker, not original interleaving), joined with 0.3 s silence','license':'CC BY-SA 4.0 (https://huggingface.co/datasets/CAiRE/ASCEND)','turns':turns}, open(f'{outd}/truth/{sid}.json','w'), ensure_ascii=False, indent=1)
print(sid,len(turns),'turns',dur,'s',dict(used),collections.Counter(t['lang'] for t in turns))
