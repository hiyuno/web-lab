#!/usr/bin/env python3
"""Local optimizer app: lists the audited assets and converts them on demand.

Reads <audit>/report.json (from the assets-web-audit skill). Optimized files go to the output
folder chosen in the UI (default <audit>/optimized), one sub-folder per page. The output folder
is remembered in optimizer/settings.json; conversion results in <audit>/optimizer-jobs.json.

Usage:  server.py --audit assets-audit --port 8770
"""
import argparse, json, mimetypes, os, queue, shutil, subprocess, sys, threading, time, urllib.parse
import tempfile, zipfile
import glob
import copy
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import convert as C
from workflow import Versions, page_summaries
from responsive import Responsive

STATIC = os.path.join(HERE, "static")
SETTINGS_PATH = os.path.join(HERE, "settings.json")
ASSET_FIELDS = ("id", "file", "folder", "type", "kind", "bytes", "severity", "issues", "info",
                "rendered", "dpr", "pages", "video", "recommended", "defaults", "external", "retina", "responsive")


class State:
    def __init__(self, audit):
        self.audit = os.path.abspath(audit)
        self.default_out = os.path.join(self.audit, "optimized")
        self.out = self.default_out
        self.thumbs = os.path.join(self.audit, ".thumbs")
        os.makedirs(self.thumbs, exist_ok=True)
        with open(os.path.join(self.audit, "report.json")) as f:
            rep = json.load(f)
        self.assets = [a for a in rep["assets"] if a.get("file")]
        self.by_id = {a["id"]: a for a in self.assets}
        measurements = {}
        for path in glob.glob(os.path.join(self.audit, 'inventory', '*.json')):
            with open(path) as f:
                inventory = json.load(f)
            for item in inventory.get('assets', []):
                if item.get('rendered'):
                    measurements.setdefault(item.get('url'), []).append(item['rendered'])
        for a in self.assets:
            a['retina'] = C.retina_size(a, measurements.get(a.get('original_url')))
            a["recommended"] = C.recommended_preset(a)
            a["defaults"] = C.default_options(a)
            a["external"] = "framerusercontent.com" not in (a.get("original_url") or "")
        self.lock = threading.Lock()
        self.thumb_sem = threading.Semaphore(3)   # don't spawn dozens of ffmpeg at once
        self.jobs = {}
        self.results = {}
        self.covers = {}
        self.names = {}
        self.q = queue.Queue()
        self.seq = 0
        self.jobs_path = os.path.join(self.audit, "optimizer-jobs.json")
        self.load_settings()
        self.load_results()
        self.versions = Versions(os.path.join(self.audit, '.versions'))
        self.responsive = Responsive(self)
        threading.Thread(target=self.worker, daemon=True).start()

    # settings ----------------------------------------------------------------
    def load_settings(self):
        try:
            s = json.load(open(SETTINGS_PATH))
            out = os.path.expanduser(s.get("out_dir") or "")
            if out and os.path.isdir(out):
                self.out = out
        except Exception:
            pass

    def set_out_dir(self, path):
        path = os.path.abspath(os.path.expanduser((path or "").strip())) if (path or "").strip() else self.default_out
        os.makedirs(path, exist_ok=True)
        if not os.access(path, os.W_OK):
            raise PermissionError(f"Sin permiso de escritura en {path}")
        with self.lock:
            self.out = path
        with open(SETTINGS_PATH, "w") as f:
            json.dump({"out_dir": path}, f, indent=1)
        return path

    def settings(self):
        return {"out_dir": self.out, "default_out": self.default_out, "is_default": self.out == self.default_out}

    def archive_current(self, aid, reason='before_change'):
        result = self.results.get(aid)
        if result:
            return self.versions.capture(aid, self.by_id[aid], result, self.covers.get(aid), self.export_name(aid), reason)

    def restore(self, aid, vid):
        with self.lock:
            if any(j['asset']==aid and j['status'] in ('queued','running') for j in self.jobs.values()):
                raise ValueError('Espera a que termine la optimización.')
            v = self.versions.get(aid, vid)
            if not v['result'] or not os.path.isfile(v['result']['abs']):
                raise ValueError('El archivo de esta versión no está disponible.')
            name = v['export_name']
            for other in self.assets:
                if other['id'] != aid and self.export_name(other['id']).casefold() == name.casefold():
                    raise ValueError('Otro asset utiliza el nombre de esta versión.')
            self.archive_current(aid, 'before_restore')
            self.publish(aid, v['result'], v.get('cover'), name, self.out)
            a = self.by_id[aid]
            self.names[aid] = {'export_name':name,'original_file':a['file'],'original_name':os.path.basename(a['file']),'updated_at':time.time()}
            self.jobs = {jid:j for jid,j in self.jobs.items() if j['asset'] != aid}
            self.save_results()
        return {'ok':True}

    def publish(self, aid, result, cover, name, out):
        """Publish a complete pair, rolling back overwritten files on failure."""
        folder = os.path.join(out, self.by_id[aid]['folder'])
        os.makedirs(folder, exist_ok=True)
        records = {}
        current_paths = {r['abs'] for r in (self.results.get(aid),self.covers.get(aid)) if r}
        with tempfile.TemporaryDirectory(prefix='.publish-', dir=folder) as tmp:
            changes = []
            for key, record in [('result',result),('cover',cover)]:
                if not record: continue
                ext = os.path.splitext(record['abs'])[1]
                suffix = '_cover' if key=='cover' else '_video' if record.get('kind')=='video' else ''
                target = os.path.join(folder,name+suffix+ext)
                if os.path.exists(target) and target not in current_paths:
                    raise ValueError('La carpeta ya contiene otro archivo llamado '+os.path.basename(target))
                staged = os.path.join(tmp,key+ext)
                shutil.copy2(record['abs'], staged)
                backup = None
                if os.path.exists(target):
                    backup = os.path.join(tmp,key+'.backup')
                    shutil.copy2(target,backup)
                changes.append((target,staged,backup))
                records[key] = {**copy.deepcopy(record),'abs':target,'file':os.path.basename(target),'out_dir':folder,'export_name':name}
            completed=[]
            try:
                for target, staged, backup in changes:
                    os.replace(staged,target)
                    completed.append((target,backup))
            except Exception:
                for target, backup in reversed(completed):
                    if backup: os.replace(backup,target)
                    else: os.unlink(target)
                raise
        self.results[aid] = records['result']
        if records.get('cover'): self.covers[aid]=records['cover']
        else: self.covers.pop(aid,None)

    # persistence -------------------------------------------------------------
    def load_results(self):
        legacy = os.path.join(self.default_out, "jobs.json")
        path = self.jobs_path if os.path.exists(self.jobs_path) else legacy
        try:
            data = json.load(open(path))
        except Exception:
            return
        self.names = {aid: value for aid, value in data.get("names", {}).items() if aid in self.by_id}
        for aid, r in data.get("results", {}).items():
            if aid not in self.by_id:
                continue
            r.setdefault("abs", os.path.join(self.audit, r["file"]))
            if os.path.exists(r["abs"]):
                r["file"] = os.path.basename(r["abs"])
                r["out_dir"] = os.path.dirname(r["abs"])
                self.results[aid] = r
        for aid, r in data.get("covers", {}).items():
            # Preserve existing exports as importable history, including legacy JPGs.
            if aid in self.by_id and os.path.exists(r.get("abs", "")):
                self.covers[aid] = r

    def save_results(self):
        tmp = self.jobs_path + ".tmp"
        with open(tmp, "w") as f:
            json.dump({"results": self.results, "covers": self.covers, "names": self.names}, f, indent=1)
        os.replace(tmp, self.jobs_path)

    def export_name(self, aid):
        return self.names.get(aid, {}).get("export_name") or os.path.splitext(os.path.basename(self.by_id[aid]["file"]))[0]

    def set_name(self, aid, name):
        if not isinstance(name, str):
            raise ValueError("Introduce un nombre válido.")
        name = name.strip()
        if not name or len(name) > 160 or name.startswith('.') or any(c in name for c in '/\\:*?"<>|') or any(ord(c) < 32 for c in name):
            raise ValueError("Usa un nombre sin rutas ni caracteres especiales (máximo 160 caracteres).")
        if os.path.splitext(name)[1].lower() in ('.jpg', '.jpeg', '.png', '.webp', '.mp4', '.webm', '.gif', '.svg', '.mov', '.m4v'):
            name = os.path.splitext(name)[0]
        if not name:
            raise ValueError("Introduce un nombre sin extensión.")
        with self.lock:
            if any(j['asset'] == aid and j['status'] in ('queued', 'running') for j in self.jobs.values()):
                raise ValueError("Espera a que termine la conversión antes de cambiar el nombre.")
            for other in self.assets:
                if other['id'] != aid:
                    other_name = self.export_name(other['id']).casefold()
                    suffixes = ('', '_video', '_cover')
                    if {name.casefold() + s for s in suffixes} & {other_name + s for s in suffixes}:
                        raise ValueError("Otro archivo ya usa ese nombre. Elige uno diferente.")
            a = self.by_id[aid]
            moves = []
            for record, suffix in ((self.results.get(aid), '_video' if a.get('type') == 'video' else ''), (self.covers.get(aid), '_cover')):
                if not record or not os.path.isfile(record.get('abs', '')):
                    continue
                old = record['abs']
                new = os.path.join(os.path.dirname(old), name + suffix + os.path.splitext(old)[1])
                if old != new and os.path.exists(new):
                    raise ValueError('Ya existe un archivo con ese nombre en la carpeta de salida.')
                moves.append((record, old, new, dict(record)))
            previous_name = self.names.get(aid)
            if name != self.export_name(aid):
                self.archive_current(aid, 'before_rename')
            completed = []
            try:
                for record, old, new, previous in moves:
                    if old != new:
                        os.rename(old, new)
                    completed.append((record, old, new, previous))
                    record.update(abs=new, file=os.path.basename(new), original_file=a['file'])
                    record['export_name'] = name
                self.names[aid] = {"export_name": name, "original_file": a['file'], "original_name": os.path.basename(a['file']), "updated_at": time.time()}
                self.save_results()
            except Exception:
                for record, old, new, previous in reversed(completed):
                    if old != new:
                        os.rename(new, old)
                    record.clear()
                    record.update(previous)
                if previous_name is None:
                    self.names.pop(aid, None)
                else:
                    self.names[aid] = previous_name
                raise
        return self.names[aid]

    def make_cover(self, aid):
        a = self.by_id[aid]
        # Generate the poster from the selected optimized video when available,
        # so its dimensions and compression follow the chosen 1080/720/480 preset.
        result = self.results.get(aid)
        src = result["abs"] if result and os.path.exists(result.get("abs", "")) else os.path.join(self.audit, a["file"])
        source_info = C.probe(src)
        max_width = source_info.get("w") or 2048
        res = C.extract_cover(src, os.path.join(self.out, a["folder"]), max_width=max_width, export_name=self.export_name(aid))
        res["original_file"] = a["file"]
        res["target_width"] = max_width
        res["abs"] = res["file"]
        res["file"] = os.path.basename(res["abs"])
        res["out_dir"] = os.path.dirname(res["abs"])
        res["at"] = time.time()
        with self.lock:
            self.covers[aid] = res
            self.save_results()
        return res

    # queue -------------------------------------------------------------------
    def enqueue(self, aid, preset=None, options=None):
        a = self.by_id[aid]
        if preset not in (None,'retina',*C.IMAGE_PRESETS,*C.VIDEO_PRESETS):
            raise ValueError('Tamaño no válido.')
        options = {k: v for k, v in (options or {}).items() if k in ('strip_audio', 'trim')}
        if preset == 'retina':
            if not a.get('retina'):
                raise ValueError('No hay medidas disponibles para Retina.')
            options['_retina'] = a['retina']
        with self.lock:
            for j in self.jobs.values():
                if j["asset"] == aid and j["status"] in ("queued", "running"):
                    return j["id"]
            self.seq += 1
            jid = f"j{self.seq}"
            self.jobs[jid] = {"id": jid, "asset": aid, "preset": 'retina' if preset == 'retina' else int(preset or a["recommended"]),
                              'export_name':self.export_name(aid), 'out':self.out,
                              "options": {**a["defaults"], **(options or {})},
                              "status": "queued", "progress": 0, "error": None, "created": time.time()}
        self.q.put(jid)
        return jid

    def worker(self):
        while True:
            jid = self.q.get()
            job = self.jobs[jid]
            a = self.by_id[job["asset"]]
            job["status"], job["started"] = "running", time.time()
            src = os.path.join(self.audit, a["file"])

            def prog(p, job=job):
                job["progress"] = p

            try:
                resolved_preset = job['options']['_retina']['w'] if job['preset'] == 'retina' else job['preset']
                with tempfile.TemporaryDirectory(prefix='walo-export-') as staging:
                    res = C.convert_file(src, staging, resolved_preset, job["options"], prog, export_name=job['export_name'])
                    res.update(original_file=a['file'], abs=res['file'], preset=job['preset'], options=job['options'], original_bytes=a['bytes'], at=time.time(), export_name=job['export_name'])
                    cover = None
                    if res['kind']=='video':
                        cover=C.extract_cover(res['abs'],staging,max_width=res['w'],export_name=job['export_name'])
                        cover.update(abs=cover['file'],at=res['at'],original_file=a['file'])
                    with self.lock:
                        self.archive_current(a['id'])
                        self.publish(a['id'],res,cover,job['export_name'],job['out'])
                        self.save_results()
                        self.archive_current(a['id'],'optimized')
                job["status"], job["progress"] = "done", 100
            except Exception as e:
                job["status"], job["error"] = "error", str(e)[-400:]
            job["finished"] = time.time()

    def snapshot(self):
        with self.lock:
            latest = {}
            for j in sorted(self.jobs.values(), key=lambda j: j["created"]):
                latest[j["asset"]] = j
            counts = {s: sum(j["status"] == s for j in self.jobs.values()) for s in ("queued", "running", "done", "error")}
            out = [{**{k: a.get(k) for k in ASSET_FIELDS}, "result": self.results.get(a["id"]),
                    "cover": self.covers.get(a["id"]), "job": latest.get(a["id"])} for a in self.assets]
        for a in out:
            a['export_name'] = self.export_name(a['id'])
        return {"assets": out, "jobs": counts, "settings": self.settings(), 'pages':page_summaries(self.assets,self.results,self.covers), 'audit':self.responsive.public()}

    # thumbnails --------------------------------------------------------------
    def thumb(self, aid):
        a = self.by_id[aid]
        src = os.path.join(self.audit, a["file"])
        ext = os.path.splitext(src)[1].lower()
        if ext == ".svg":
            return src
        dst = os.path.join(self.thumbs, aid + ".jpg")
        if os.path.exists(dst):
            return dst
        with self.thumb_sem:
            if os.path.exists(dst):
                return dst
            try:
                if ext in C.VIDEO_EXT:
                    for ss in ("1", "0"):
                        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", ss, "-i", src, "-frames:v", "1",
                                        "-vf", "scale=320:-2", dst], timeout=60)
                        if os.path.exists(dst):
                            break
                else:
                    from PIL import Image, ImageOps
                    with Image.open(src) as im:
                        im = ImageOps.exif_transpose(im).convert("RGBA")
                        im.thumbnail((320, 320))
                        bg = Image.new("RGB", im.size, (30, 30, 34))
                        bg.paste(im, mask=im.split()[3])
                        bg.save(dst, "JPEG", quality=80)
            except Exception:
                return None
        return dst if os.path.exists(dst) else None


def pick_folder(start):
    """Native macOS folder dialog. Returns the chosen POSIX path or None if cancelled."""
    script = f'POSIX path of (choose folder with prompt "Carpeta para los archivos optimizados" default location POSIX file "{start}")'
    r = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, timeout=300)
    return r.stdout.strip() or None


class Handler(BaseHTTPRequestHandler):
    state: State = None

    def log_message(self, *a):
        pass

    def _send(self, code, body, ctype="application/json"):
        if isinstance(body, (dict, list)):
            body = json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _file(self, path, download=False, cache=False):
        if not path or not os.path.isfile(path):
            return self._send(404, {"error": "not found"})
        ctype = mimetypes.guess_type(path)[0] or "application/octet-stream"
        size = os.path.getsize(path)
        start, end = 0, size - 1
        requested = self.headers.get('Range')
        if requested:
            try:
                units, span = requested.split('=',1)
                left,right = span.split('-',1)
                if units != 'bytes' or ',' in span: raise ValueError()
                start = int(left) if left else max(0,size-int(right))
                end = min(size-1,int(right)) if right and left else size-1
                if start<0 or start>end: raise ValueError()
            except ValueError:
                self.send_response(416)
                self.send_header('Content-Range',f'bytes */{size}')
                self.end_headers()
                return
        self.send_response(206 if requested else 200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(end-start+1))
        self.send_header('Accept-Ranges','bytes')
        if requested: self.send_header('Content-Range',f'bytes {start}-{end}/{size}')
        self.send_header("Cache-Control", "max-age=3600" if cache else "no-store")
        if download:
            self.send_header("Content-Disposition", "attachment; filename=export; filename*=UTF-8''"+urllib.parse.quote(os.path.basename(path),safe=''))
        self.end_headers()
        try:
            with open(path, "rb") as f:
                f.seek(start)
                remaining=end-start+1
                while remaining>0:
                    chunk=f.read(min(1024*1024,remaining))
                    if not chunk: break
                    self.wfile.write(chunk)
                    remaining-=len(chunk)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def do_GET(self):
        u = urllib.parse.urlsplit(self.path)
        path = urllib.parse.unquote(u.path)
        qs = urllib.parse.parse_qs(u.query)
        S = self.state
        if path == "/":
            return self._file(os.path.join(STATIC, "index.html"))
        if path in ('/workflow.js','/workflow.css'):
            return self._file(os.path.join(STATIC,path[1:]))
        if path.startswith('/api/history/'):
            aid=path.split('/')[-1]
            if aid not in S.by_id: return self._send(404,{'error':'unknown asset'})
            with S.lock:
                versions=S.versions.list(aid)
                if not versions and S.results.get(aid):
                    S.archive_current(aid,'imported')
                    versions=S.versions.list(aid)
            return self._send(200,{'versions':versions})
        if path.startswith('/version/'):
            try:
                _,_,aid,vid,kind=path.split('/')
                v=S.versions.get(aid,vid)
                return self._file(v.get(kind,{}).get('abs'),download='download' in qs)
            except (ValueError,AttributeError):
                return self._send(404,{'error':'Versión no encontrada'})
        if path == "/api/assets":
            return self._send(200, S.snapshot())
        if path == "/api/settings":
            return self._send(200, S.settings())
        if path.startswith('/bundle/'):
            aid = path[len('/bundle/'):]
            with S.lock:
                records = [S.results.get(aid), S.covers.get(aid)]
                records = [r for r in records if r and os.path.isfile(r.get('abs', ''))]
                if not records:
                    return self._send(404, {'error': 'No hay archivos generados.'})
                with tempfile.TemporaryFile() as bundle:
                    with zipfile.ZipFile(bundle, 'w', compression=zipfile.ZIP_STORED) as archive:
                        for record in records:
                            archive.write(record['abs'], os.path.basename(record['abs']))
                    size = bundle.tell()
                    bundle.seek(0)
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/zip')
                    self.send_header('Content-Length', str(size))
                    filename = urllib.parse.quote(S.export_name(aid) + '.zip', safe='')
                    self.send_header('Content-Disposition', "attachment; filename=export.zip; filename*=UTF-8''" + filename)
                    self.end_headers()
                    shutil.copyfileobj(bundle, self.wfile)
            return
        if path.startswith("/files/"):
            full = os.path.abspath(os.path.join(S.audit, path[len("/files/"):]))
            if not full.startswith(S.audit + os.sep):
                return self._send(403, {"error": "forbidden"})
            return self._file(full, download="download" in qs)
        if path.startswith("/result/"):
            r = S.results.get(path[len("/result/"):])
            return self._file(r["abs"] if r else None, download="download" in qs)
        if path.startswith("/cover/"):
            r = S.covers.get(path[len("/cover/"):])
            return self._file(r["abs"] if r else None, download="download" in qs)
        if path.startswith("/thumb/"):
            aid = path[len("/thumb/"):]
            if aid not in S.by_id:
                return self._send(404, {"error": "unknown asset"})
            return self._file(S.thumb(aid), cache=True)
        return self._send(404, {"error": "not found"})

    def do_POST(self):
        n = int(self.headers.get("Content-Length") or 0)
        try:
            body = json.loads(self.rfile.read(n) or b"{}")
        except ValueError:
            return self._send(400, {"error": "bad json"})
        S = self.state
        if self.path == '/api/audit':
            return self._send(200,S.responsive.start(body.get('password') or ''))
        if self.path == '/api/restore':
            if body.get('id') not in S.by_id: return self._send(404,{'error':'unknown asset'})
            try: return self._send(200,S.restore(body['id'],body.get('version')))
            except (ValueError,OSError) as e: return self._send(400,{'error':str(e)})
        if self.path == "/api/convert":
            aid = body.get("id")
            if aid not in S.by_id:
                return self._send(404, {"error": "unknown asset"})
            try:
                return self._send(200, {"job": S.enqueue(aid, body.get("preset"), body.get("options"))})
            except ValueError as e:
                return self._send(400, {'error':str(e)})
        if self.path == "/api/name":
            if body.get('id') not in S.by_id:
                return self._send(404, {"error": "unknown asset"})
            try:
                return self._send(200, S.set_name(body['id'], body.get('name')))
            except (ValueError, OSError) as e:
                return self._send(400, {"error": str(e)})
        if self.path == "/api/convert-batch":
            jobs = [S.enqueue(i) for i in body.get("ids") or [] if i in S.by_id]
            return self._send(200, {"jobs": jobs})
        if self.path == "/api/settings":
            try:
                S.set_out_dir(body.get("out_dir"))
            except Exception as e:
                return self._send(400, {"error": str(e)})
            return self._send(200, S.settings())
        if self.path == "/api/pick-folder":
            try:
                chosen = pick_folder(S.out)
            except Exception as e:
                return self._send(500, {"error": str(e)})
            return self._send(200, {"out_dir": chosen})
        if self.path == "/api/open-out":
            os.makedirs(S.out, exist_ok=True)
            subprocess.Popen(["open", S.out])
            return self._send(200, {"ok": True})
        if self.path == "/api/cover":
            aid = body.get("id")
            if aid not in S.by_id:
                return self._send(404, {"error": "unknown asset"})
            try:
                return self._send(200, S.make_cover(aid))
            except Exception as e:
                return self._send(500, {"error": str(e)})
        if self.path == "/api/reveal":
            r = (S.covers if body.get("kind") == "cover" else S.results).get(body.get("id"))
            if not r or not os.path.exists(r["abs"]):
                return self._send(404, {"error": "no result"})
            subprocess.Popen(["open", os.path.dirname(r["abs"])])
            return self._send(200, {"ok": True})
        return self._send(404, {"error": "not found"})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--audit", default="assets-audit")
    ap.add_argument("--port", type=int, default=8770)
    a = ap.parse_args()
    Handler.state = State(a.audit)
    srv = ThreadingHTTPServer(("127.0.0.1", a.port), Handler)
    print(f"optimizer: http://localhost:{a.port}  ({len(Handler.state.assets)} assets, salida: {Handler.state.out})", flush=True)
    srv.serve_forever()


if __name__ == "__main__":
    main()
