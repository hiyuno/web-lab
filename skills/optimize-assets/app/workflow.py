"""Immutable export versions and aggregate inventory statistics."""
import copy
import json
import os
import shutil
import time
import uuid


class Versions:
    def __init__(self, root):
        self.root = root
        os.makedirs(root, exist_ok=True)

    def list(self, aid):
        folder = os.path.join(self.root, aid)
        if not os.path.isdir(folder):
            return []
        records = []
        for entry in os.scandir(folder):
            path = os.path.join(entry.path, 'version.json')
            if not os.path.isfile(path):
                continue
            with open(path) as f:
                record = json.load(f)
            records.append(record)
        return sorted(records, key=lambda r: r['at'], reverse=True)

    def capture(self, aid, asset, result, cover, name, reason='optimized'):
        existing = self.list(aid)
        if existing:
            last = existing[0]
            if (last['export_name'] == name and last.get('result',{}).get('at') == (result or {}).get('at')
                    and (last.get('cover') or {}).get('at') == (cover or {}).get('at')):
                return last
        version = uuid.uuid4().hex
        folder = os.path.join(self.root, aid, version)
        os.makedirs(folder)
        record = {'id': version, 'asset': aid, 'at': time.time(), 'reason': reason,
                  'original_file': asset['file'], 'original_url': asset.get('original_url'),
                  'export_name': name, 'result': None, 'cover': None}
        for key, source in [('result', result), ('cover', cover)]:
            if source and os.path.isfile(source.get('abs', '')):
                stored = copy.deepcopy(source)
                # Prefix avoids accidental collisions between result and cover.
                stored['abs'] = os.path.join(folder, key + os.path.splitext(source['abs'])[1])
                shutil.copy2(source['abs'], stored['abs'])
                record[key] = stored
        tmp = os.path.join(folder, 'version.json.tmp')
        with open(tmp, 'w') as f:
            json.dump(record, f, indent=2)
        os.replace(tmp, os.path.join(folder, 'version.json'))
        return record

    def get(self, aid, vid):
        for record in self.list(aid):
            if record['id'] == vid:
                return record
        raise ValueError('Versión no encontrada.')


def page_summaries(assets, results, covers):
    pages = sorted({p for a in assets for p in a.get('pages', [])})
    rows = []
    for page in [None] + pages:
        subset = {a['id']: a for a in assets if page is None or page in a.get('pages', [])}.values()
        before = current = poster = done = count = 0
        for a in subset:
            count += 1
            before += a['bytes']
            r = results.get(a['id'])
            current += r['bytes'] if r else a['bytes']
            done += bool(r)
            poster += covers.get(a['id'], {}).get('bytes', 0)
        rows.append({'page': page or '', 'count': count, 'optimized': done,
                     'original_bytes': before, 'current_bytes': current,
                     'cover_bytes': poster, 'saved_bytes': before - current})
    return rows
