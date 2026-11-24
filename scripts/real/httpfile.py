import io, urllib.request
class HTTPFile(io.RawIOBase):
    def __init__(self, url):
        self.url=url; self.pos=0; self.fetched=0
        req=urllib.request.Request(url, method='HEAD')
        with urllib.request.urlopen(req) as r: self.size=int(r.headers['Content-Length']); self.url=r.url
    def seekable(self): return True
    def readable(self): return True
    def tell(self): return self.pos
    def seek(self, off, whence=0):
        self.pos = off if whence==0 else (self.pos+off if whence==1 else self.size+off); return self.pos
    def read(self, n=-1):
        if n<0: n=self.size-self.pos
        if n==0 or self.pos>=self.size: return b''
        end=min(self.size, self.pos+n)-1
        req=urllib.request.Request(self.url, headers={'Range':f'bytes={self.pos}-{end}'})
        with urllib.request.urlopen(req) as r: b=r.read()
        self.pos+=len(b); self.fetched+=len(b); return b
    def readinto(self, buf):
        b=self.read(len(buf)); buf[:len(b)]=b; return len(b)
