"""Responsive audit orchestration and provenance for Retina."""
import glob
import json
import os
import shutil
import subprocess
import threading
import time
from urllib.parse import urlsplit
import convert as C


def url_key(url):
    parts = urlsplit(url or '')
    return parts.netloc + parts.path


class Responsive:
    def __init__(self, state):
        self.state = state
        self.path = os.path.join(state.audit, 'responsive.json')
        self.status = {'status':'idle','completed':0,'total':0,'failures':[],'measurements':[]}
        if os.path.isfile(self.path):
            with open(self.path) as f:
                self.status = json.load(f)
            if self.status['status'] == 'running':
                self.status['status'] = 'interrupted'
        self.apply()

    def apply(self):
        by_url = {}
        for measurement in self.status.get('measurements', []):
            for item in measurement['assets']:
                by_url.setdefault(url_key(item['url']), []).append({**item,'page':measurement['page'],'viewport':measurement['width']})
        for a in self.state.assets:
            boxes = []
            for url in set([a.get('original_url', '')] + a.get('served_urls', [])):
                boxes.extend(by_url.get(url_key(url), []))
            if boxes:
                retina = C.retina_size(a, boxes)
                if retina:
                    retina.update(basis='responsive', viewports=sorted({b['viewport'] for b in boxes}), measured_at=self.status.get('at'))
                    a['retina'] = retina
                a['responsive'] = boxes

    def public(self):
        return {k:v for k,v in self.status.items() if k != 'measurements'} | {'measured_assets':sum(bool(a.get('responsive')) for a in self.state.assets)}

    def start(self, password=''):
        with self.state.lock:
            if self.status['status'] == 'running':
                return self.public()
            self.status = {**self.status,'status':'running','completed':0,'total':0,'failures':[],'at':time.time()}
            self.status.pop('error',None)
        threading.Thread(target=self.run, args=(password,), daemon=True).start()
        return self.public()

    def run(self, password=''):
        env = os.environ.copy()
        # Prefer configured dependencies; otherwise use the desktop bundled runtime.
        if not env.get('NODE_PATH'):
            matches = glob.glob(os.path.expanduser('~/.cache/codex-runtimes/*/dependencies/node/node_modules'))
            if matches:
                env['NODE_PATH'] = matches[0]
        process = None
        try:
            node = shutil.which('node')
            if not node:
                raise RuntimeError('Node.js is not available to measure the site.')
            process = subprocess.Popen([node, os.path.join(os.path.dirname(__file__),'responsive.cjs'), self.state.audit], env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            process.stdin.write(json.dumps({'password':password}))
            process.stdin.close()
            password = ''
            errors = []
            def drain():
                for line in process.stderr:
                    errors.append(line)
                    if len(errors)>30: errors.pop(0)
            threading.Thread(target=drain,daemon=True).start()
            for line in process.stdout:
                event = json.loads(line)
                with self.state.lock:
                    if event['type']=='measurement':
                        self.status['measurements'] = [m for m in self.status['measurements'] if (m['page'],m['width']) != (event['page'],event['width'])] + [event]
                    elif event['type']=='failure':
                        self.status['failures'].append(event)
                    elif event['type']=='progress':
                        self.status.update(completed=event['completed'],total=event['total'])
            process.wait()
            if process.returncode:
                raise RuntimeError(''.join(errors)[-1200:] or 'No se pudo iniciar el navegador.')
            self.status['status'] = 'partial' if self.status['failures'] else 'done'
        except Exception as e:
            self.status.update(status='error',error=str(e))
        finally:
            with self.state.lock:
                self.apply()
                with open(self.path+'.tmp','w') as f: json.dump(self.status,f)
                os.replace(self.path+'.tmp',self.path)
