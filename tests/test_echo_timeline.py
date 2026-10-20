import unittest
from libraries.echo_timeline import TimelineIndexer,utc_time
class Tests(unittest.TestCase):
 def source(self,id='s'):return {'source_id':id,'sha256':'a'*64}
 def convo(self):return {'id':'c','title':'Private title','current_node':'b','mapping':{'a':{'message':{'create_time':1704067200,'author':{'role':'user'},'content':{'parts':['future 2030-01-01']}}},'b':{'parent':'a','message':{'create_time':1704067201,'author':{'role':'assistant'}}},'z':{'parent':'a','message':{'author':{'role':'assistant'}}}}}
 def test_seconds_milliseconds_equal(self):self.assertEqual(utc_time(1704067200),utc_time(1704067200000))
 def test_naive_date_unresolved(self):self.assertIsNone(utc_time('2024-01-01'))
 def test_invalid_unresolved(self):
  for v in [True,float('nan'),'bad',None]:self.assertIsNone(utc_time(v))
 def test_timezone(self):self.assertEqual(utc_time('2024-01-01T01:00:00+01:00'),'2024-01-01T00:00:00Z')
 def test_branches_preserved(self):
  i=TimelineIndexer();i.add('openai',self.convo(),self.source());r=i.report();self.assertEqual(len(r['events']),2);self.assertEqual(len(r['unresolved']),1)
  self.assertEqual(r['events'][0]['references'][0]['branch'],'selected-path');self.assertEqual(r['unresolved'][0]['references'][0]['branch'],'other-recorded-branch')
 def test_duplicate_merges_source_refs(self):
  i=TimelineIndexer();i.add('openai',self.convo(),self.source());i.add('openai',self.convo(),self.source('s2'));r=i.report();self.assertEqual(len(r['events']),2);self.assertEqual(len(r['events'][0]['references']),2)
 def test_provider_namespaces(self):
  i=TimelineIndexer();i.add('openai',self.convo(),self.source());i.add('claude',{'uuid':'c','name':'Claude','chat_messages':[{'uuid':'a','sender':'human','created_at':'2024-01-01T00:00:00Z'}]},self.source('s2'));self.assertEqual(i.report()['summary']['dated_messages'],3)
 def test_text_dates_not_timeline_positions(self):
  i=TimelineIndexer();i.add('openai',self.convo(),self.source());r=i.report();self.assertEqual(r['events'][0]['date_mentions'][0]['date'],'2030-01-01');self.assertTrue(r['events'][0]['time'].startswith('2024'))
 def test_private_text_not_copied(self):
  i=TimelineIndexer();c=self.convo();c['mapping']['a']['message']['content']['parts']=['SECRET TEXT'];i.add('openai',c,self.source());self.assertNotIn('SECRET TEXT',str(i.report()))
 def test_conflict_retained(self):
  i=TimelineIndexer();i.add('openai',self.convo(),self.source());c=self.convo();c['title']='different';i.add('openai',c,self.source('s2'));self.assertTrue(i.report()['conflicts'])
