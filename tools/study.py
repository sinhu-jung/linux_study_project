#!/usr/bin/env python3
"""Local, dependency-free Linux source reader. Sources come from Git, not checkout."""
import argparse
import errno
import json
import os
import sqlite3
import subprocess
import threading
from collections import Counter
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse
from urllib.request import urlopen
from course import Course
from knowledge import Knowledge

ROOT = Path(__file__).resolve().parent.parent
REPO = ROOT / 'linux'
DB = ROOT / 'data' / 'progress.sqlite3'
FILES = []
FILESET = set()
SHA = ''
LOCK = threading.Lock()
COURSE = None
KNOWLEDGE = None

def git(*args, timeout=30):
    return subprocess.run([os.environ.get('STUDY_GIT', 'git'), '-C', str(REPO), *args], capture_output=True, check=True, timeout=timeout).stdout

def connection():
    return sqlite3.connect(DB)

def initialize():
    global FILES, FILESET, SHA, COURSE, KNOWLEDGE
    SHA = git('rev-parse', 'HEAD').decode().strip()
    FILES = sorted(git('ls-tree', '-r', '--name-only', '-z', 'HEAD').decode().split('\0')[:-1])
    FILESET = set(FILES)
    DB.parent.mkdir(exist_ok=True)
    with connection() as db:
        db.execute('CREATE TABLE IF NOT EXISTS progress(path TEXT PRIMARY KEY, status TEXT NOT NULL, note TEXT NOT NULL, updated TEXT DEFAULT CURRENT_TIMESTAMP)')
    COURSE = Course(ROOT, connection, git, LOCK)
    KNOWLEDGE = Knowledge(ROOT, SHA)

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass
    def send(self, value, code=200):
        body = json.dumps(value, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.end_headers()
        self.wfile.write(body)
    def do_GET(self):
        if self.headers.get('Host') not in (f'127.0.0.1:{self.server.server_port}', f'localhost:{self.server.server_port}'):
            return self.send({'error': 'Invalid host'}, 403)
        url = urlparse(self.path)
        q = {k: v[0] for k, v in parse_qs(url.query).items()}
        try:
            if url.path == '/api/knowledge':
                return self.send(KNOWLEDGE.handle(q))
            if url.path.startswith('/api/course'):
                value, status = COURSE.handle('GET', url.path, q)
                return self.send(value, status)
            if url.path in ('/', '/explorer', '/knowledge'):
                body = (ROOT / 'tools' / ({'/':'index.html','/explorer':'explorer.html','/knowledge':'knowledge.html'}[url.path])).read_bytes()
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.send_header('X-Content-Type-Options', 'nosniff')
                self.end_headers()
                self.wfile.write(body)
            elif url.path == '/api/meta':
                with connection() as db:
                    counts = dict(db.execute('SELECT status, COUNT(*) FROM progress GROUP BY status'))
                    recent = list(db.execute('SELECT path,status FROM progress ORDER BY updated DESC LIMIT 15'))
                self.send({'sha': SHA, 'version': 'v6.12', 'total': len(FILES), 'counts': counts, 'recent': recent, 'groups': dict(Counter(p.split('/')[0] for p in FILES))})
            elif url.path == '/api/tree':
                prefix, search = q.get('prefix', ''), q.get('q', '').lower()
                offset = max(0, int(q.get('offset', 0)))
                if search:
                    paths = [p for p in FILES if search in p.lower()]
                    entries = [{'path': p, 'dir': False} for p in paths]
                else:
                    entries_map = {}
                    for p in FILES:
                        if not p.startswith(prefix): continue
                        tail = p[len(prefix):]
                        child = tail.split('/')[0]
                        isdir = '/' in tail
                        path = prefix + child + ('/' if isdir else '')
                        entries_map[path] = {'path': path, 'dir': isdir}
                    entries = sorted(entries_map.values(), key=lambda e: (not e['dir'], e['path']))
                with connection() as db:
                    states = dict(db.execute('SELECT path,status FROM progress'))
                for e in entries: e['status'] = states.get(e['path'], 'new')
                self.send({'entries': entries[offset:offset+250], 'total': len(entries), 'offset': offset})
            elif url.path == '/api/file':
                path = q.get('path', '')
                if path not in FILESET: return self.send({'error': '파일을 찾을 수 없습니다.'}, 404)
                data = git('show', 'HEAD:' + path)
                with connection() as db:
                    row = db.execute('SELECT status,note FROM progress WHERE path=?', (path,)).fetchone()
                binary = b'\0' in data[:8192]
                self.send({'path': path, 'text': '[바이너리 파일: 코드 본문을 표시하지 않습니다.]' if binary else data.decode('utf-8', 'replace'), 'bytes': len(data), 'status': row[0] if row else 'new', 'note': row[1] if row else '', 'binary': binary})
            elif url.path == '/api/search':
                term = q.get('q', '')
                if not term or len(term) > 200: return self.send({'matches': []})
                result = subprocess.run([os.environ.get('STUDY_GIT', 'git'), '-C', str(REPO), 'grep', '-n', '-I', '-m', '3', '-F', '-e', term, 'HEAD', '--'], capture_output=True, timeout=30)
                if result.returncode not in (0, 1): raise ValueError(result.stderr.decode())
                lines = result.stdout.decode('utf-8', 'replace').splitlines()
                matches = []
                for line in lines[:200]:
                    path, number, text = line[5:].split(':', 2)
                    matches.append({'path': path, 'line': int(number), 'text': text})
                self.send({'matches': matches, 'truncated': len(lines) > 200})
            else: self.send({'error': 'Not found'}, 404)
        except subprocess.TimeoutExpired:
            self.send({'error': '검색 시간이 초과되었습니다. 더 구체적인 문자열로 검색하세요.'}, 408)
        except (ValueError, subprocess.CalledProcessError) as e:
            self.send({'error': str(e)}, 400)
    def do_POST(self):
        origin = self.headers.get('Origin')
        if self.headers.get('Host') not in (f'127.0.0.1:{self.server.server_port}', f'localhost:{self.server.server_port}') or origin not in (None, f'http://127.0.0.1:{self.server.server_port}', f'http://localhost:{self.server.server_port}'):
            return self.send({'error': 'Invalid origin'}, 403)
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if length > 200000: return self.send({'error': '메모가 너무 큽니다.'}, 413)
            payload = json.loads(self.rfile.read(length))
            if not isinstance(payload, dict):
                return self.send({'error': 'Invalid request'}, 400)
            if self.path.startswith('/api/course'):
                value, status = COURSE.handle('POST', self.path, {}, payload)
                return self.send(value, status)
            if self.path != '/api/progress' or payload.get('path') not in FILESET or payload.get('status') not in ('new', 'reading', 'done', 'revisit'):
                return self.send({'error': 'Invalid entry'}, 400)
            with LOCK, connection() as db:
                db.execute('INSERT INTO progress(path,status,note) VALUES(?,?,?) ON CONFLICT(path) DO UPDATE SET status=excluded.status,note=excluded.note,updated=CURRENT_TIMESTAMP', (payload['path'], payload['status'], str(payload.get('note', ''))))
            self.send({'ok': True})
        except (ValueError, TypeError): self.send({'error': 'Invalid request'}, 400)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8765)
    args = parser.parse_args()
    initialize()
    address = f'http://127.0.0.1:{args.port}'
    try:
        server = ThreadingHTTPServer(('127.0.0.1', args.port), Handler)
    except OSError as error:
        if error.errno != errno.EADDRINUSE:
            raise
        try:
            with urlopen(address + '/api/meta', timeout=2) as response:
                existing = json.load(response)
            same_source = existing.get('sha') == SHA and existing.get('total') == len(FILES)
        except (OSError, ValueError, AttributeError):
            same_source = False
        if same_source:
            print(f'학습 서버가 이미 실행 중입니다. 브라우저에서 {address} 를 열어주세요.', flush=True)
            raise SystemExit(0)
        print(f'{args.port} 포트를 다른 프로그램이 사용 중입니다.\n'
              '실행 명령 뒤에 --port 8766 을 붙여 다른 포트에서 실행하세요.', flush=True)
        raise SystemExit(1)
    print(f'Linux v6.12 · {len(FILES):,} files · {address}\n종료: Ctrl+C', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\n학습 서버를 종료했습니다.', flush=True)
    finally:
        server.server_close()
