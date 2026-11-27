#!/usr/bin/env python3
"""Local-only preview with project-path simulation; never expose repository sources."""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlsplit
import argparse

parser=argparse.ArgumentParser()
parser.add_argument('--port',type=int,default=8765)
parser.add_argument('--directory',type=Path,default=Path(__file__).resolve().parents[1]/'dist')
args=parser.parse_args()

class PreviewHandler(SimpleHTTPRequestHandler):
    def __init__(self,*a,**kw): super().__init__(*a,directory=str(args.directory.resolve()),**kw)
    def do_GET(self):
        prefix='/almeida-e-mileski-advocacia'
        if urlsplit(self.path).path==prefix:
            self.send_response(301);self.send_header('Location',prefix+'/');self.end_headers();return
        if self.path.startswith(prefix+'/'): self.path=self.path[len(prefix):]
        super().do_GET()
    def end_headers(self):
        self.send_header('X-Robots-Tag','noindex, nofollow')
        self.send_header('X-Content-Type-Options','nosniff')
        super().end_headers()
    def send_error(self,code,message=None,explain=None):
        page=args.directory/'404.html'
        if code==404 and page.is_file():
            body=page.read_bytes();self.send_response(404);self.send_header('Content-Type','text/html; charset=utf-8');self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
        else: super().send_error(code,message,explain)
    def log_message(self,*args): pass

print(f'Local preview: http://127.0.0.1:{args.port}',flush=True)
ThreadingHTTPServer(('127.0.0.1',args.port),PreviewHandler).serve_forever()
