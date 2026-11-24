import sys, collections, pyarrow.parquet as pq
sys.path.insert(0, sys.argv[2]); from httpfile import HTTPFile
p=pq.ParquetFile(HTTPFile(sys.argv[1]))
t=p.read(columns=['audio_id','speaker_id']).to_pylist()
s=collections.defaultdict(lambda:[0,set()])
for r in t:
    k=r['audio_id'].rsplit('_',2)[0]; s[k][0]+=1; s[k][1].add(r['speaker_id'])
for k,(n,sp) in sorted(s.items(), key=lambda kv:(-len(kv[1][1]),-kv[1][0]))[:4]: print(k,n,len(sp))
