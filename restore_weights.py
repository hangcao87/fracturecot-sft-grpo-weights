#!/usr/bin/env python3
"""Restore and verify downloaded release assets. Python 3.9+; standard library only."""
import argparse
import hashlib
import json
from pathlib import Path
import tarfile

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda: f.read(8 * 1024 * 1024), b''): h.update(b)
    return h.hexdigest()

def verify(path, item):
    if not path.is_file() or path.stat().st_size != item['bytes'] or sha(path) != item['sha256']:
        raise RuntimeError('Missing or corrupt file: ' + str(path))

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--assets',type=Path,default=Path('assets'))
    p.add_argument('--output',type=Path,default=Path('weights'))
    p.add_argument('--manifest',type=Path,default=Path(__file__).with_name('release_manifest.json'))
    p.add_argument('--model',choices=['all','initial_sft','grpo'],default='all')
    a=p.parse_args(); m=json.loads(a.manifest.read_text())
    models = list(m['models']) if a.model=='all' else [a.model]
    meta=m['metadata_asset']; archive=a.assets/meta['name']; verify(archive,meta)
    a.output.mkdir(parents=True,exist_ok=True)
    with tarfile.open(archive,'r:gz') as tar:
        allowed={model+'/'+item['path'] for model in models for item in m['models'][model]['files'] if not item.get('assets')}
        for member in tar.getmembers():
            if member.name not in allowed: continue
            if not member.isfile(): raise RuntimeError('Non-regular archive member')
            dest=a.output/member.name
            if dest.exists():
                expected=next(i for i in m['models'][member.name.split('/')[0]]['files'] if i['path']==Path(member.name).name)
                verify(dest,expected); continue
            dest.parent.mkdir(parents=True,exist_ok=True)
            source=tar.extractfile(member)
            with dest.open('xb') as f:
                for b in iter(lambda: source.read(8*1024*1024),b''): f.write(b)
    for model in models:
        for item in m['models'][model]['files']:
            dest=a.output/model/item['path']
            if item.get('assets') and not dest.exists():
                dest.parent.mkdir(parents=True,exist_ok=True)
                temp=dest.with_suffix(dest.suffix+'.restoring')
                with temp.open('xb') as output:
                    for part in item['assets']:
                        source=a.assets/part['name']; verify(source,part)
                        with source.open('rb') as f:
                            for b in iter(lambda:f.read(8*1024*1024),b''): output.write(b)
                verify(temp,item); temp.replace(dest)
            verify(dest,item)
            print('VERIFIED',model+'/'+item['path'],flush=True)
    print('All selected original files restored and SHA256 verified.')

if __name__=='__main__':main()
