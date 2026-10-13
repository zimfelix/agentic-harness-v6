#!/usr/bin/env python3
"""Independent stdlib verification; copies products so demos/tests cannot alter originals.
Run: python3 verify.py. Compact evidence: verification.json. No network/packages.
Each executable outcome uses its own fresh persistent store. Temporary copies deleted.
"""
import argparse, concurrent.futures, hashlib, json, os, pathlib, platform, re, shutil, subprocess, sys, tempfile
ROOT=pathlib.Path(__file__).resolve().parent
PRODUCTS={
 'A':ROOT/'fixtures/autonomy/sol-autonomy-r1-lean',
 'B':ROOT/'fixtures/autonomy/opus-native-autonomy-r2-baseline',
 'C':ROOT/'fixtures/autonomy/sol-autonomy-r1-baseline',
 'D':ROOT/'fixtures/autonomy/opus-native-autonomy-r2-lean',
}
NAMES=['entrypoint_and_demo','fresh_process_persistence','dependency_block','cycle_rejection','deterministic_next_and_completed_exclusion','malformed_import_preservation','export_import_roundtrip','backup_restore','deletion_integrity','own_behavior_suite']
CONFIG={
'A':dict(flag='--db', fixture='examples/synthetic.json', imp=['--replace'], demo=[sys.executable,'examples/demo.py'], blocked='a3', ready='a2', deps='dependencies', cycle=['depend','a2','a4'], delete=['task-delete','a2'], done=['done','a2']),
'B':dict(flag='--db', fixture='examples/synthetic-portfolio.json',imp=[],demo=['sh','scripts/demo.sh'],blocked=3,ready=2,deps='depends_on',cycle=['dep','add','2','4'],delete=['task','delete','2'],done=['task','done','2']),
'C':dict(flag='--state',fixture='fixtures/demo.json',imp=['--yes'],demo=[sys.executable,'examples/demo.py'],blocked='a3',ready='a2',deps='depends_on',cycle=['task','update','a2','--depends-on','a3'],delete=['task','delete','a2','--yes'],done=['task','done','a2']),
'D':dict(flag='--data',fixture='examples/sample-project.json',imp=['--replace'],demo=['sh','examples/demo.sh'],blocked='t4',ready='t6',deps='depends_on',cycle=['task','depend','t2','t5'],delete=['task','delete','t2'],done=['task','done','t6'])}
def digest(x): return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def review(label):
 c=CONFIG[label]; results=[]; logs=[]
 with tempfile.TemporaryDirectory(prefix='planner-review-') as tmp:
  product=pathlib.Path(tmp)/label; shutil.copytree(PRODUCTS[label],product)
  def run(args, cwd=product):
   p=subprocess.run(list(map(str,args)),cwd=cwd,capture_output=True,text=True,timeout=65)
   text=p.stdout+p.stderr
   logs.append({'command':' '.join(map(str,args)).replace(str(product),'<copy>'),'exit':p.returncode,'output_sha256':hashlib.sha256(text.encode()).hexdigest(),'observation':text[-650:]})
   return p
  def check(v,msg):
   if not v: raise AssertionError(msg)
  for idx in [9]+list(range(9)):
   name=NAMES[idx]
   start=len(logs); observations={}; status='pass'
   try:
    folder=product/('review-'+str(idx)); folder.mkdir(); state=folder/'state'; counter=[0]
    base=([sys.executable,str(product/'planner')] if label=='B' else [sys.executable,str(product/'planner.py')])+[c['flag'],str(state)]
    def cli(*args,ok=True):
     p=run(base+list(args)); check((p.returncode==0)==ok, 'unexpected exit: '+p.stderr[-400:]); return p.stdout
    def export():
     counter[0]+=1; path=folder/('export-'+str(counter[0])+'.json')
     cli('export',*(['--out',str(path)] if label=='D' else [str(path)]))
     d=json.loads(path.read_text()); d.pop('exported_at',None); return d
    def seed(): cli('import',str(product/c['fixture']),*c['imp'])
    def nextwork(): return cli('next',*(['--today','2026-10-10','--limit','20'] if label=='B' else ['--limit','20'] if label=='D' else []))
    def ids_next(out):
     if label in 'AC':
      d=json.loads(out); t=d['task' if label=='A' else 'next']; return [] if t is None else [t['id']]
     return [int(x) for x in re.findall(r'^\s*\d+\.\s+#(\d+)',out,re.M)] if label=='B' else re.findall(r'^\s*\d+\.\s+(t\d+)',out,re.M)
    def done(t): return cli(*(['done',str(t)] if label=='A' else ['task','done',str(t)]),ok=False)
    if idx==0:
     if label=='B':
      try: run([str(product/'planner'),'--help'])
      except PermissionError as exc: observations['documented_entrypoint_error']=str(exc)
     cli('--help'); p=run(c['demo']); seed(); d=export(); check(len(d['projects'])==2 and len(d['tasks'])>=6,'fixture counts'); observations.update(projects=len(d['projects']),tasks=len(d['tasks']),demo_exit=p.returncode)
     check(p.returncode==0 and 'documented_entrypoint_error' not in observations,'documented entrypoint/demo fails; Python interpreter fallback works')
    elif idx==1:
     if label=='A': cli('project-add','Independent synthetic','--id','p'); cli('task-add','p','Independent task','--id','x','--estimate','12')
     elif label=='B': cli('project','add','p','Independent synthetic'); cli('task','add','p','Independent task','--estimate','12m')
     elif label=='C': cli('project','add','p','Independent synthetic'); cli('task','add','x','--project','p','--title','Independent task','--estimate','12')
     else: cli('project','add','Independent synthetic'); cli('task','add','p1','Independent task','--estimate','12m')
     cli('overview'); d=export(); check(len(d['tasks'])==1 and d['tasks'][0]['title']=='Independent task','fresh read mismatch'); observations={'state_hash':digest(d),'task_count':1}
    elif idx in (2,3,4,5,8):
     seed(); before=export()
     if idx==2:
      done(c['blocked']); check(export()==before,'blocked completion changed state'); selected=ids_next(nextwork()); check(selected and c['blocked'] not in selected,'blocked next or parse failure'); observations={'selected':selected,'preserved':True}
     elif idx==3:
      cli(*c['cycle'],ok=False); check(export()==before,'cycle changed state'); observations={'before_hash':digest(before),'after_hash':digest(export())}
     elif idx==4:
      outputs=[nextwork() for _ in range(3)]; check(len(set(outputs))==1,'nondeterministic'); selected=ids_next(outputs[0]); check(selected,'next parse empty');
      tasks={t['id']:t for t in before['tasks']}
      for t in selected:
       x=tasks[t]; isdone=x.get('done',False) or x.get('done_at') is not None or x.get('status')=='done'; check(not isdone,'suggested done'); check(all(tasks[p].get('done',False) or tasks[p].get('done_at') is not None or tasks[p].get('status')=='done' for p in x[c['deps']]),'suggested blocked')
      cli(*c['done']); after=ids_next(nextwork()); check(c['ready'] not in after,'newly completed suggested'); observations={'repeated_order':selected,'after_completion':after}
     elif idx==5:
      for kind in ['syntax','dangling','cycle']:
       bad=folder/'bad.json'
       if kind=='syntax': bad.write_text('{broken')
       else:
        d=json.loads(json.dumps(before)); target=d['tasks'][1]; target[c['deps']]=['missing' if label!='B' else 999] if kind=='dangling' else [d['tasks'][2]['id'] if label!='D' else 't5']; bad.write_text(json.dumps(d))
       cli('import',str(bad),*c['imp'],ok=False); check(export()==before,'invalid import damaged state')
      observations={'rejections':['syntax','dangling','cycle'],'preserved_hash':digest(before)}
     else:
      cli(*c['delete'],ok=False); check(export()==before,'refused deletion changed state')
      if label in 'BD': cli(*c['delete'],'--detach')
      elif label=='A': cli('task-delete','b3')
      else: cli('task','delete','b3','--yes')
      d=export(); ids={t['id'] for t in d['tasks']}; check(all(set(t[c['deps']])<=ids for t in d['tasks']),'dangling refs'); check(len(d['tasks'])==len(before['tasks'])-1,'no deletion'); observations={'tasks_after':len(ids),'dangling_references':0}
    elif idx in (6,7):
     seed(); before=export(); path=folder/'transfer.json'
     if idx==6:
      cli('export',*(['--out',str(path)] if label=='D' else [str(path)])); base[base.index(str(state))]=str(folder/'other-state'); cli('import',str(path),*c['imp'])
     else:
      if label=='D': cli('backup'); path=sorted((folder/'backups').glob('*.json'))[-1]
      else: cli('backup',str(path))
      cli(*c['done']); check(export()!=before,'mutation missing'); cli('restore',str(path),*(['--replace'] if label=='A' else ['--yes'] if label in 'BC' else []))
     after=export(); check(after==before,'roundtrip differs'); observations={'before_hash':digest(before),'after_hash':digest(after),'equal':True}
    else:
     p=run([sys.executable,'-m','unittest','discover','-s','tests','-v']); check(p.returncode==0,'own suite failed'); observations={'summary':(p.stdout+p.stderr)[-160:]}
   except Exception as exc:
    status='fail' if isinstance(exc,AssertionError) else 'unverified'; observations.update(error=str(exc))
   results.append({'name':name,'status':status,'evidence':{'observations':observations,'commands':logs[start:]}})
 results.sort(key=lambda o:NAMES.index(o['name']))
 return {'label':label,'outcomes':results,'own_test_result':results[-1]['evidence']['observations']}
if __name__=='__main__':
 parser=argparse.ArgumentParser(description='Replay all 40 independent planner outcomes without model calls.')
 parser.add_argument('--output',type=pathlib.Path)
 args=parser.parse_args()
 with concurrent.futures.ThreadPoolExecutor(4) as pool: products=list(pool.map(review,'ABCD'))
 data={'runtime':sys.version,'platform':platform.platform(),'products':products}
 if args.output: args.output.write_text(json.dumps(data,indent=2)+'\n')
 for p in products: print(p['label'],[(o['name'],o['status']) for o in p['outcomes']])
 raise SystemExit(any(o['status']!='pass' for p in products for o in p['outcomes']))
