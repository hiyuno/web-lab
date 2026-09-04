import json
import os
import tempfile
import time
import unittest
from unittest.mock import patch
from PIL import Image
import server
from workflow import page_summaries


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='walo-workflow-')
        self.root = self.temp.name
        src = os.path.join(self.root,'original.png')
        Image.new('RGB',(1200,900),'#d98122').save(src)
        self.asset = {'id':'sample','file':'original.png','folder':'home','type':'image','bytes':os.path.getsize(src),'pages':['home','project'],'info':{'w':1200,'h':900},'rendered':{'w':300,'h':225}}
        with open(os.path.join(self.root,'report.json'),'w') as f:json.dump({'assets':[self.asset]},f)
        with patch.object(server.State,'load_settings',lambda s:None): self.state=server.State(self.root)

    def tearDown(self): self.temp.cleanup()

    def optimize(self,preset):
        jid=self.state.enqueue('sample',preset)
        end=time.monotonic()+20
        while self.state.jobs[jid]['status'] in ('queued','running') and time.monotonic()<end:time.sleep(.02)
        self.assertEqual(self.state.jobs[jid]['status'],'done',self.state.jobs[jid])

    def test_versions_restore_and_name_provenance(self):
        self.state.set_name('sample','primero')
        self.optimize(1024)
        initial=self.state.versions.list('sample')[0]
        self.state.set_name('sample','segundo')
        self.optimize('retina')
        self.assertEqual(self.state.results['sample']['w'],600)
        self.state.restore('sample',initial['id'])
        r=self.state.results['sample']
        self.assertEqual(r['w'],1024)
        self.assertEqual(r['file'],'primero.webp')
        self.assertEqual(self.state.export_name('sample'),'primero')
        self.assertTrue(os.path.isfile(os.path.join(self.root,'original.png')))
        with open(self.state.jobs_path) as f:data=json.load(f)
        self.assertEqual(data['names']['sample']['original_file'],'original.png')
        self.assertGreaterEqual(len(self.state.versions.list('sample')),2)

    def test_restore_collision_does_not_overwrite(self):
        self.optimize(1024)
        version=self.state.versions.list('sample')[0]
        self.state.set_name('sample','renamed')
        target=os.path.join(self.state.out,'home','original.webp')
        with open(target,'wb') as f:f.write(b'unrelated')
        with self.assertRaises(ValueError):self.state.restore('sample',version['id'])
        with open(target,'rb') as f:self.assertEqual(f.read(),b'unrelated')
        self.assertEqual(self.state.export_name('sample'),'renamed')

    def test_shared_assets_count_once_and_unoptimized_retained(self):
        self.optimize(1024)
        summaries=page_summaries(self.state.assets,self.state.results,self.state.covers)
        self.assertEqual(len(summaries),3)
        self.assertTrue(all(s['count']==1 for s in summaries))
        self.assertEqual(summaries[0]['current_bytes'],self.state.results['sample']['bytes'])

    def test_conversion_failure_preserves_result(self):
        self.optimize(1024)
        original=dict(self.state.results['sample'])
        with patch.object(server.C,'convert_file',side_effect=RuntimeError('fixture failure')):
            jid=self.state.enqueue('sample','retina')
            end=time.monotonic()+10
            while self.state.jobs[jid]['status'] in ('queued','running') and time.monotonic()<end:time.sleep(.02)
        self.assertEqual(self.state.jobs[jid]['status'],'error')
        self.assertEqual(self.state.results['sample'],original)
        self.assertTrue(os.path.isfile(original['abs']))

    def test_video_cover_versions_are_paired(self):
        src=os.path.abspath(os.path.join(os.path.dirname(__file__),'..','assets-audit','home','XmfPKW4aGFwN0JztJbJTUl8QSug.mp4'))
        if not os.path.isfile(src): self.skipTest('Real video fixture unavailable')
        self.asset.update(file=src,type='video',info={'w':1080,'h':1350},bytes=os.path.getsize(src),defaults={},recommended=720)
        self.state.by_id['sample']=self.asset
        for preset in (480,720):
            jid=self.state.enqueue('sample',preset,{'trim':.1,'strip_audio':True})
            end=time.monotonic()+20
            while self.state.jobs[jid]['status'] in ('queued','running') and time.monotonic()<end:time.sleep(.02)
            self.assertEqual(self.state.jobs[jid]['status'],'done',self.state.jobs[jid])
        versions=self.state.versions.list('sample')
        initial=versions[-1]
        self.state.restore('sample',initial['id'])
        self.assertEqual(self.state.results['sample']['w'],480)
        self.assertEqual(self.state.covers['sample']['w'],480)
        self.assertTrue(self.state.covers['sample']['file'].endswith('_cover.webp'))


if __name__=='__main__':unittest.main()
