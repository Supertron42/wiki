"""Shared guide/card regressions for source-verified software documentation.
WIRING: projects.json drives cards; project-guide.css owns software page layout.
"""
from pathlib import Path
from html.parser import HTMLParser
import importlib.util,json,re,unittest
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('guide_site_tools',ROOT/'tools/site_tools.py');tools=importlib.util.module_from_spec(spec);spec.loader.exec_module(tools)
REQUIRED={'collectionsmanager','clibdt','simplecustomweights','morecolorfului','dynamiccontainerloot','dynamicleveledlists','npcspawner','dynamicformlists','dynamicmusicandsounds','dynamicnpcs','arcanearchery','armornormalizer','prismauisettingsmenu','runtimesanitychecker','tomeandspellidentifier','adjustable-prices','auto-arrow-retrieval','dynamic-location-discovery','location-discovery','stability-tester','tk-dodge-ng','weapon-and-armor-material-mod','what-is-my-name'}

class Markup(HTMLParser):
 def __init__(self,text):
  super().__init__();self.ids=[];self.h1=0;self.styles=[];self.inline=0;self.body={};self.cards=0;self.feed(text)
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if 'id' in a:self.ids.append(a['id'])
  if tag=='h1':self.h1+=1
  if tag=='link' and a.get('rel')=='stylesheet':self.styles.append(a['href'])
  if tag=='style':self.inline+=1
  if tag=='body':self.body=a
  if tag=='article' and 'project-card' in a.get('class','').split():self.cards+=1

class GuideTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.registry=tools.read_registry(ROOT)
 def test_all_prepared_projects_have_registered_guides(self):
  registered={p['slug'] for p in self.registry['projects']}
  self.assertTrue(REQUIRED<=registered)
  for slug in REQUIRED:self.assertTrue((ROOT/'site'/slug/'index.html').is_file(),slug)
 def test_rewritten_guides_share_one_layout_and_share_controls(self):
  for slug in REQUIRED:
   for path in (ROOT/'site'/slug).glob('*.html'):
    text=path.read_text(encoding='utf-8');page=tools.Page(text)
    if page.redirect:continue
    with self.subTest(page=str(path)):
     parsed=Markup(text)
     self.assertEqual(parsed.styles,['../assets/css/project-guide.css'])
     self.assertIn('guide',parsed.body.get('class','').split())
     self.assertIn('nav',parsed.ids);self.assertIn('content',parsed.ids)
     self.assertEqual(parsed.h1,1);self.assertEqual(parsed.inline,0)
     self.assertIn('guide-md-text',parsed.ids);self.assertIn('guide-bb-text',parsed.ids)
 def test_registry_cards_have_complete_identical_coverage(self):
  expected=[p for p in self.registry['projects'] if p['category']=='skyrim']
  cards=tools.project_cards(self.registry,'skyrim')
  self.assertEqual(Markup(cards).cards,len(expected))
  for name in ('index.html','skyrim.html'):
   text=(ROOT/'site'/name).read_text(encoding='utf-8')
   block=text.split('<!-- PROJECT-CARDS:START -->')[1].split('<!-- PROJECT-CARDS:END -->')[0]
   self.assertEqual(Markup(block).cards,len(expected))
   for project in expected:self.assertEqual(block.count('href="'+project['entry']+'"'),1)
   self.assertIn(cards,block)
 def test_no_guessed_source_repositories(self):
  for project in self.registry['projects']:
   if project['slug'] in REQUIRED:self.assertIsNone(project['source_url'])
 def test_critical_legacy_anchors_and_new_programs_guide(self):
  anchors={'dynamicnpcs':{'settings','reports','specifics','compact-reports-editor','spreadsheet-rules'},'dynamiccontainerloot':{'container-editor','settings','reports'},'dynamicleveledlists':{'settings','reports'},'clibdt':{'skyrim-17104'},'prismauisettingsmenu':{'menu-control-api','spreadsheet-rules'}}
  for slug,required in anchors.items():self.assertTrue(required<=tools.Page((ROOT/'site'/slug/'index.html').read_text(encoding='utf-8')).ids,slug)
  self.assertIn('library',tools.Page((ROOT/'site/collectionsmanager/programs.html').read_text(encoding='utf-8')).ids)
 def test_metadata_is_escaped_and_sources_stay_optional(self):
  data={'projects':[dict(name='<Example>',description='A & B',category='skyrim',color='#4ec9b0',entry='example/index.html',source_url=None)]}
  cards=tools.project_cards(data,'skyrim');self.assertIn('&lt;Example&gt;',cards);self.assertIn('A &amp; B',cards);self.assertNotIn('Source code',cards)
  self.assertEqual(tools.project_cards(data,'wow'),'')
 def test_stubs_and_mit_port_are_not_misrepresented(self):
  for slug in ('adjustable-prices','weapon-and-armor-material-mod'):
   text=(ROOT/'site'/slug/'index.html').read_text(encoding='utf-8');self.assertIn('Unfinished project scaffold',text)
  text=(ROOT/'site/tk-dodge-ng/index.html').read_text(encoding='utf-8');self.assertIn('MIT',text);self.assertIn('Itamar Holtzman',text)
 def test_unfinished_cm_features_remain_labeled(self):
  text=(ROOT/'site/collectionsmanager/programs.html').read_text(encoding='utf-8')
  self.assertIn('not validated',text);self.assertIn('revision isolation remain unfinished',text)

if __name__=='__main__':unittest.main()
