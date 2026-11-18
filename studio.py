"""Cesar Workflow Studio: ComfyUI API JSON is the canonical production document.
Python standard library only. HTTP listener binds to 127.0.0.1.
"""
import json
import io
import zipfile
import os
import re
import threading
import time
import uuid
import webbrowser
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, quote, unquote, urlparse
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent
WF_DIR = ROOT / 'data' / 'workflows'
STATE_FILE = ROOT / 'studio_state.json'
INPUT_FALLBACK = ROOT / 'input'
PORT = int(os.environ.get('CESAR_STUDIO_PORT', '8765'))
LOCK = threading.RLock()
WFPAT = re.compile(r'(?i)(S\d{2,3})[_-](C\d{3,4})')
IMGPAT = re.compile(r'(?i)\.(?:png|jpe?g|webp)$')
SOURCE_IMAGE_NODES = {'first': ('7','87'), 'middle': ('127','130'), 'last': ('109','112')}
SCENE_NAMES = {'S01':'Ouverture','S02':'Observation','S03':'Réhabilitation','S04':'Promenade','S05':'Démonstration','S06':'Final'}
DEFAULTS = {'project_name':'César — The Teen Whisperer','project_pass2':False,
            'scene_pass2':{}, 'clip_pass2':{}, 'ready':{}, 'scene_locked':{},
            'input_dir':str(INPUT_FALLBACK), 'comfy_url':'http://127.0.0.1:8188',
            'queue':{'pending':[],'active':None,'state':'idle','last_error':'','completed':[]}}

def now(): return datetime.now(timezone.utc).isoformat(timespec='seconds')
def atomic_json(path, data):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_name(path.name+'.tmp')
    temp.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    os.replace(temp,path)

def load_state():
    if STATE_FILE.is_file():
        try:
            result=json.loads(STATE_FILE.read_text(encoding='utf-8'))
            s={**DEFAULTS,**result}
            for k in ('scene_pass2','clip_pass2','ready','scene_locked'):
                if not isinstance(s.get(k),dict):s[k]={}
            q=s['queue']
            if q.get('active'):
                active=q['active']
                q['pending']=[active.get('key')]+q.get('pending',[])
                q['pending']=[k for k in q['pending'] if k]
                q['active']=None
                q['state']='paused'
                q['last_error']='Exécution précédente non confirmée : file en pause. Vérifier l’historique ComfyUI avant reprise.'
            return s
        except Exception as e: print('Warning state not loaded:',e)
    s=json.loads(json.dumps(DEFAULTS))
    if not STATE_FILE.exists():
        booleans=[]
        for p in sorted(WF_DIR.glob('*.json')):
            try:booleans.append(bool(json.loads(p.read_text(encoding='utf-8'))['104']['inputs']['value']))
            except Exception: pass
        if booleans:s['project_pass2']=sum(booleans)>=len(booleans)/2
    return s

STATE=load_state()
REVISION_TAG = 'CESAR_TRIPLE_GUIDE_NO_UPSCALE_R3'
if STATE.get('applied_revision') != REVISION_TAG:
    STATE['project_pass2'] = False
    STATE['scene_pass2'] = {}
    STATE['clip_pass2'] = {}
    STATE['ready'] = {}
    STATE['scene_locked'] = {}
    STATE['queue'] = {'pending': [], 'active': None, 'state': 'idle', 'last_error': '', 'completed': []}
    STATE['applied_revision'] = REVISION_TAG
    atomic_json(STATE_FILE, STATE)

def save_state():atomic_json(STATE_FILE,STATE)
def find_workflows():
    found={}
    for p in WF_DIR.rglob('*.json'):
        m=WFPAT.search(p.stem)
        if m: found[m.group(1).upper()+'_'+m.group(2).upper()]=p
    return dict(sorted(found.items()))

def workflow(key):
    path=find_workflows().get(key)
    if not path:raise ValueError('Workflow introuvable : '+key)
    try:return path,json.loads(path.read_text(encoding='utf-8'))
    except Exception as e:raise ValueError('Impossible de lire '+str(path)+': '+str(e))

def nvalue(w,nid,field='value',default=None):return w.get(nid,{}).get('inputs',{}).get(field,default)
def key_for(scene,clip):return scene+'_'+clip

def effective_pass2(key):
    scene=key.split('_')[0]
    val=STATE['project_pass2']
    if scene in STATE['scene_pass2']:val=STATE['scene_pass2'][scene]
    if key in STATE['clip_pass2']:val=STATE['clip_pass2'][key]
    return bool(val)

def patch_pass2(keys):
    for key in keys:
        path,w=workflow(key)
        if nvalue(w,'104') != effective_pass2(key):
            w['104']['inputs']['value']=effective_pass2(key)
            atomic_json(path,w)

def scan():
    out={}
    for key,path in find_workflows().items():
        try:
            w=json.loads(path.read_text(encoding='utf-8'))
            scene,clip=key.split('_')
            # If user edited this JSON outside the app, honor its saved pass-2 value.
            if key not in STATE['clip_pass2'] and bool(nvalue(w,'104')) != effective_pass2(key):
                STATE['clip_pass2'][key] = bool(nvalue(w,'104'))
                save_state()
            prompt=str(nvalue(w,'5','text',''))
            desc_match=re.search(r'location and visual direction:\s*(.*)',prompt,re.I)
            description=desc_match.group(1).split('\n')[0].strip() if desc_match else ''
            title=description.split(';')[0].strip() if description else clip
            if len(title)>70:title=title[:67]+'…'
            active={f:bool(nvalue(w,nid,'value',False)) for f,(_,nid) in SOURCE_IMAGE_NODES.items()}
            images={f: str(nvalue(w,nid,'image','')) for f,(nid,_) in SOURCE_IMAGE_NODES.items()}
            input_dir=Path(STATE['input_dir'])
            missing=[images[f] for f in ('first','middle','last') if active[f] and not (input_dir/images[f]).is_file()]
            out[key]={'key':key,'scene':scene,'clip':clip,'title':title,'filename':path.name,
                'frames':int(nvalue(w,'10') or 289),'fps':int(nvalue(w,'11') or 24),
                'pass2':bool(nvalue(w,'104')),'missing':missing,'ready':bool(STATE['ready'].get(key,False))}
        except Exception as e:print('Workflow scan error',path,e)
    return out

def clip_detail(key):
    path,w=workflow(key)
    base=scan().get(key)
    if not base:raise ValueError('Clip invalide : '+key)
    frames=base['frames'];fps=base['fps']; middle_idx=int(nvalue(w,'131') or 0)
    guides={}
    for name,(iid,sid) in SOURCE_IMAGE_NODES.items():
        filename=str(nvalue(w,iid,'image',''))
        enabled=bool(nvalue(w,sid,'value',False))
        index={'first':0,'middle':middle_idx,'last':frames-1}[name]
        guides[name]={'enabled':enabled,'filename':filename,'frame':index,
                      'time':round(index/fps,3),'present':bool((Path(STATE['input_dir'])/filename).is_file())}
    return {**base,'prompt':nvalue(w,'5','text',''),'negative_prompt':nvalue(w,'6','text',''),
      'guides':guides,'duration':round((frames-1)/fps,3),'output_prefix':nvalue(w,'108','filename_prefix',''),
      'pass2_setting':'on' if key in STATE['clip_pass2'] and STATE['clip_pass2'][key] else 'off' if key in STATE['clip_pass2'] else 'inherit',
      'pass2_effective':bool(nvalue(w,'104')),'node_count':len(w)}

def choose_path_safe(directory, filename):
    p=Path(filename)
    if p.name!=filename or not IMGPAT.search(filename) or '/' in filename or '\\' in filename or '..' in filename:
        raise ValueError('Nom de fichier image non valide')
    return Path(directory)/filename

def update_clip(key,values):
    path,w=workflow(key)
    fps=int(nvalue(w,'11') or 24)
    oldframes=int(nvalue(w,'10') or 289)
    duration=float(values.get('duration',(oldframes-1)/fps))
    if not 5<=duration<=20:raise ValueError('Durée admise : 5 à 20 secondes')
    frames=round(duration*fps/8)*8+1
    frames=max(121,min(481,frames))
    middle=values.get('middle',{})
    last=values.get('last',{})
    first=values.get('first',{})
    middle_on=bool(middle.get('enabled',False));last_on=bool(last.get('enabled',False))
    midtime=float(middle.get('time',float(nvalue(w,'131') or 144)/fps))
    if middle_on and not 0<midtime<((frames-1)/fps):raise ValueError('Le guide MIDDLE doit être entre le début et la fin.')
    middle_idx=max(8,min(frames-9,round(midtime*fps/8)*8))
    vals={'first':(first,True,0),'middle':(middle,middle_on,middle_idx),'last':(last,last_on,frames-1)}
    for part,(field,enable,frame_idx) in vals.items():
        nid,sid=SOURCE_IMAGE_NODES[part]
        chosen=(field.get('filename') or '').strip()
        auto=f'CESAR_{key}_F{frame_idx:04d}.png'
        if enable:
            # A disabled guide often contains the FIRST filename as a placeholder.
            # When enabling it, propose the actual timestamped guide name instead.
            was_enabled=bool(nvalue(w,sid,'value',False))
            old_name=str(nvalue(w,nid,'image',''))
            first_name=str(nvalue(w,'7','image',''))
            if (not chosen or (not was_enabled and chosen==first_name) or
                (chosen==old_name and int(field.get('old_frame',frame_idx))!=frame_idx)):
                chosen=auto
            choose_path_safe(STATE['input_dir'],chosen)
            w[nid]['inputs']['image']=chosen
        w[sid]['inputs']['value']=enable
    w['10']['inputs']['value']=frames
    w['131']['inputs']['value']=middle_idx
    if 'prompt' in values:
        if not isinstance(values['prompt'],str):raise ValueError('Prompt non valide')
        prompt=values['prompt']
        # Keep the structured clip timing in sync with the node 10 duration.
        # Explicit dialogue timestamps are NOT rewritten or reordered.
        seconds=(frames-1)/fps
        fmtsec=f'{seconds:.3f}'.rstrip('0').rstrip('.')
        prompt=re.sub(r'(exactly )\d+(?:\.\d+)?( seconds)',lambda m:m.group(1)+fmtsec+m.group(2),prompt,count=1)
        guides=['FIRST guide at 0.0s']
        if middle_on:guides.append(f'MIDDLE guide at {middle_idx/fps:.3f}s')
        if last_on:guides.append(f'LAST guide at {seconds:.3f}s')
        guidance='This clip has '+', '.join(guides)+'. These are successive narrative moments, not transitions by morphing.'
        prompt=re.sub(r'^This clip has FIRST guide.*$',lambda m:guidance,prompt,count=1,flags=re.M)
        if 'This clip has FIRST guide' not in prompt:
            prompt=re.sub(r'^FIRST guide at 0\.0s only\..*$',lambda m:guidance,prompt,count=1,flags=re.M)
        w['5']['inputs']['text']=prompt
    if 'negative_prompt' in values:w['6']['inputs']['text']=values['negative_prompt']
    if 'output_prefix' in values:
        prefix=values['output_prefix'].strip()
        if not prefix or '..' in prefix:raise ValueError('Préfixe de sortie non valide')
        w['108']['inputs']['filename_prefix']=prefix
    if 'pass2' in values:
        setting=values['pass2']
        if setting not in ('inherit','on','off'):raise ValueError('Mode de deuxième passe non valide')
        if setting=='inherit':STATE['clip_pass2'].pop(key,None)
        else:STATE['clip_pass2'][key]=(setting=='on')
    w['104']['inputs']['value']=effective_pass2(key)
    # Keep output keyframes indexes valid on short clips (diagnostic node).
    if '102' in w:
        idxs=[]
        for i in [0,middle_idx,frames-1]:
            if 0<=i<frames and i not in idxs:idxs.append(i)
        w['102']['inputs']['indexes']=','.join(map(str,idxs[:-1]))+',-1' if len(idxs)>1 else '0,-1'
    atomic_json(path,w)
    save_state()
    return clip_detail(key)

def update_scope(level,ident,values):
    # Reconcile edits made directly to JSON before applying inherited options.
    scan()
    allkeys=find_workflows()
    if level=='project':
        if 'pass2' in values:
            STATE['project_pass2']=bool(values['pass2'])
        if 'input_dir' in values:
            p=Path(str(values['input_dir'])).expanduser()
            if not p.is_dir():raise ValueError('Le dossier input doit exister sur cet ordinateur')
            STATE['input_dir']=str(p.resolve())
        if 'comfy_url' in values:
            u=str(values['comfy_url']).rstrip('/')
            parsed=urlparse(u)
            if parsed.scheme not in ('http','https') or not parsed.netloc or parsed.path not in ('','/'):
                raise ValueError('URL ComfyUI invalide (exemple http://127.0.0.1:8188)')
            STATE['comfy_url']=u
        if 'project_name' in values:STATE['project_name']=str(values['project_name']).strip() or 'Projet'
        patch_pass2(allkeys)
    elif level=='scene':
        if ident not in [k.split('_')[0] for k in allkeys]:raise ValueError('Scène inconnue')
        if 'pass2' in values:
            v=values['pass2']
            if v=='inherit':STATE['scene_pass2'].pop(ident,None)
            elif v in ('on','off'):STATE['scene_pass2'][ident]=v=='on'
            else:raise ValueError('Mode invalide')
            patch_pass2(k for k in allkeys if k.startswith(ident+'_'))
        if 'locked' in values:STATE['scene_locked'][ident]=bool(values['locked'])
    else:raise ValueError('Niveau inconnu')
    save_state();return tree_data()

def tree_data():
    clips=scan();groups={}
    for key,c in clips.items():
        s=c['scene'];groups.setdefault(s,[]).append(c)
    scenes=[]
    for s,cs in sorted(groups.items()):
        cs=sorted(cs,key=lambda x:x['clip'])
        auto_ready=bool(cs) and all(c['ready'] for c in cs)
        locked=bool(STATE['scene_locked'].get(s))
        scenes.append({'id':s,'title':SCENE_NAMES.get(s,s),'clips':cs,'ready':auto_ready or locked,
                       'auto_ready':auto_ready,'locked':locked,
                       'pass2_setting':'inherit' if s not in STATE['scene_pass2'] else ('on' if STATE['scene_pass2'][s] else 'off')})
    q=STATE['queue']
    return {'project':STATE['project_name'],'project_pass2':STATE['project_pass2'],
            'input_dir':STATE['input_dir'],'comfy_url':STATE['comfy_url'],
            'scenes':scenes,'queue':q,'count':len(clips)}

def api_comfy(path, payload=None,timeout=20):
    url=STATE['comfy_url']+path
    req=Request(url,data=json.dumps(payload).encode('utf-8') if payload is not None else None,
               headers={'Content-Type':'application/json'} if payload is not None else {},
               method='POST' if payload is not None else 'GET')
    try:
        with urlopen(req,timeout=timeout) as res:
            raw=res.read().decode('utf-8');return json.loads(raw) if raw else {}
    except HTTPError as e:
        try: detail=e.read().decode('utf-8')[:1000]
        except Exception:detail=str(e)
        raise ValueError(f'ComfyUI HTTP {e.code}: {detail}')
    except (URLError,TimeoutError) as e:raise ValueError(f'Impossible de joindre ComfyUI: {e}')

def preflight(key):
    item=clip_detail(key)
    if item['missing']:raise ValueError('Guides absents de input/ : '+', '.join(item['missing']))
    return item

WORKER=None

def worker_loop():
    while True:
        with LOCK:
            q=STATE['queue']
            if q['state'] in ('paused','stopping','idle'):
                if q['state']=='stopping':q.update({'state':'idle','pending':[]})
                save_state();return
            if not q['pending']:
                q['state']='idle';save_state();return
            key=q['pending'][0]
        try:
            preflight(key)
            # Use on-disk JSON as the exact API payload.
            _,w=workflow(key)
            response=api_comfy('/prompt',{'prompt':w,'client_id':str(uuid.uuid4())})
            pid=response.get('prompt_id')
            if not pid:raise ValueError('ComfyUI ne retourne pas prompt_id: '+str(response))
            with LOCK:
                q=STATE['queue'];q['active']={'key':key,'prompt_id':pid,'started':now(),'status':'running'}
                save_state()
            connection_failures=0
            while True:
                time.sleep(1.5)
                with LOCK:
                    active=STATE['queue'].get('active')
                    if active is None or active.get('prompt_id')!=pid:
                        return  # Targeted interrupt / external local cancellation.
                try:
                    history=api_comfy('/history/'+quote(pid),timeout=15)
                    connection_failures=0
                except ValueError as e:
                    connection_failures+=1
                    if connection_failures>=12:raise ValueError('API ComfyUI inaccessible pendant le suivi : '+str(e))
                    continue
                data=history.get(pid)
                if not data:continue
                status=data.get('status',{})
                if status.get('completed') or status.get('status_str') in ('success','error'):
                    if status.get('status_str') == 'error':
                        raise ValueError('Exécution ComfyUI en erreur pour '+key+' : '+str(status.get('messages',[]))[-800:])
                    with LOCK:
                        q=STATE['queue']
                        q['completed'].insert(0,{'key':key,'prompt_id':pid,'finished':now(),'outputs':data.get('outputs',{})})
                        q['completed']=q['completed'][:80]
                        if q['pending'] and q['pending'][0]==key:q['pending'].pop(0)
                        q['active']=None
                        save_state()
                    break
        except Exception as e:
            with LOCK:
                q=STATE['queue'];q['last_error']=f'{key}: {e}'
                q['state']='paused';q['active']=None
                save_state()
            return

def start_worker():
    global WORKER
    if WORKER and WORKER.is_alive():return
    WORKER=threading.Thread(target=worker_loop,name='comfy-queue',daemon=True)
    WORKER.start()

def generate(level,ident,force=False):
    allc=scan()
    if level=='project':keys=list(allc)
    elif level=='scene':keys=[k for k in allc if k.startswith(ident+'_')]
    elif level=='clip':keys=[ident] if ident in allc else []
    else:raise ValueError('Niveau inconnu')
    if not keys:raise ValueError('Aucun clip disponible')
    eligible=[]
    for key in keys:
        if not force and (STATE['ready'].get(key) or STATE['scene_locked'].get(key.split('_')[0])):continue
        eligible.append(key)
    with LOCK:
        if STATE['queue']['state'] in ('running','paused') and STATE['queue']['pending']:
            raise ValueError('Une file existe déjà : reprendre ou arrêter avant une nouvelle génération')
        for key in eligible:preflight(key)
        STATE['queue'].update({'pending':eligible,'active':None,'state':'running' if eligible else 'idle','last_error':''})
        save_state()
        if eligible:start_worker()
    return {'queued':eligible,'skipped':[k for k in keys if k not in eligible]}

def queue_control(action):
    with LOCK:
        q=STATE['queue']
        if action=='pause':
            if q['state']=='running':q['state']='paused'
        elif action=='resume':
            if q['state']=='paused':
                q['state']='running';q['last_error']=''
                if not q['active']:start_worker()
        elif action=='stop':
            if q['active']:q['state']='stopping'
            else:q.update({'pending':[],'state':'idle','active':None})
        elif action=='interrupt':
            if not q['active']:raise ValueError('Aucun calcul actif à interrompre')
            pid=q['active']['prompt_id']
            # Target only this prompt, not another ComfyUI user task.
            api_comfy('/interrupt',{'prompt_id':pid})
            # Also cancel if ComfyUI had accepted the prompt but not begun executing it.
            api_comfy('/queue',{'delete':[pid]})
            q['state']='paused'
            q['active']=None
            q['last_error']='Interruption ciblée demandée pour '+pid+'. Vérifier ComfyUI avant de reprendre.'
        else:raise ValueError('Commande inconnue')
        save_state()
        return q

class Handler(BaseHTTPRequestHandler):
    def log_message(self,format,*args):pass
    def send_json(self,obj,status=200):
        raw=json.dumps(obj,ensure_ascii=False,default=str).encode('utf-8')
        self.send_response(status);self.send_header('Content-Type','application/json; charset=utf-8');self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw)
    def serve_file(self,path,content_type,download=None):
        data=Path(path).read_bytes()
        self.send_response(200);self.send_header('Content-Type',content_type);self.send_header('Content-Length',str(len(data)))
        if download:self.send_header('Content-Disposition',f'attachment; filename="{download}"')
        self.end_headers();self.wfile.write(data)
    def do_GET(self):
        try:
            u=urlparse(self.path);qs=parse_qs(u.query);pick=lambda k,default='':qs.get(k,[default])[0]
            if u.path=='/':return self.serve_file(ROOT/'web'/'index.html','text/html; charset=utf-8')
            if u.path=='/api/tree':return self.send_json(tree_data())
            if u.path=='/api/clip':return self.send_json(clip_detail(pick('key')))
            if u.path=='/api/images':
                d=Path(STATE['input_dir']);items=sorted(x.name for x in d.iterdir() if x.is_file() and IMGPAT.search(x.name)) if d.is_dir() else []
                return self.send_json({'images':items,'directory':str(d)})
            if u.path=='/api/image':
                file=choose_path_safe(STATE['input_dir'],pick('name'))
                if not file.is_file():raise ValueError('Image absente')
                ext=file.suffix.lower();mime={'png':'image/png','jpg':'image/jpeg','jpeg':'image/jpeg','webp':'image/webp'}[ext.lstrip('.')]
                return self.serve_file(file,mime)
            if u.path=='/api/workflow':
                path,_=workflow(pick('key'));return self.serve_file(path,'application/json',path.name)
            if u.path=='/api/export':
                scene=pick('scene')
                paths=[(k,p) for k,p in find_workflows().items() if not scene or k.startswith(scene+'_')]
                if not paths:raise ValueError('Aucun workflow à exporter')
                buf=io.BytesIO()
                with zipfile.ZipFile(buf,'w',compression=zipfile.ZIP_DEFLATED) as z:
                    for k,p in paths:z.write(p,arcname=p.name)
                data=buf.getvalue();self.send_response(200)
                self.send_header('Content-Type','application/zip')
                self.send_header('Content-Disposition',f'attachment; filename="CESAR_{scene or "TOUS"}_WORKFLOWS.zip"')
                self.send_header('Content-Length',str(len(data)))
                self.end_headers();self.wfile.write(data);return
            if u.path=='/api/queue':return self.send_json(STATE['queue'])
            if u.path=='/api/status':
                try:
                    info=api_comfy('/system_stats',timeout=2)
                    return self.send_json({'connected':True,'stats':info})
                except Exception as e:return self.send_json({'connected':False,'error':str(e)})
            return self.send_json({'error':'Route inconnue'},404)
        except Exception as e:self.send_json({'error':str(e)},400)
    def do_POST(self):
        try:
            if int(self.headers.get('Content-Length','0'))>2_000_000:raise ValueError('Requête trop volumineuse')
            raw=self.rfile.read(int(self.headers.get('Content-Length','0')))
            d=json.loads(raw.decode('utf-8') or '{}');u=urlparse(self.path)
            if u.path=='/api/clip':return self.send_json(update_clip(d['key'],d['values']))
            if u.path=='/api/ready':
                key=d['key'];workflow(key)
                STATE['ready'][key]=bool(d['ready']);save_state();return self.send_json(tree_data())
            if u.path=='/api/scope':return self.send_json(update_scope(d['level'],d.get('id',''),d['values']))
            if u.path=='/api/generate':return self.send_json(generate(d['level'],d.get('id',''),bool(d.get('force',False))))
            if u.path=='/api/queue':return self.send_json(queue_control(d['action']))
            return self.send_json({'error':'Route inconnue'},404)
        except Exception as e:self.send_json({'error':str(e)},400)

if __name__=='__main__':
    WF_DIR.mkdir(parents=True,exist_ok=True);INPUT_FALLBACK.mkdir(exist_ok=True)
    if not STATE_FILE.exists():save_state()
    srv=ThreadingHTTPServer(('127.0.0.1',PORT),Handler)
    print(f'César Workflow Studio: http://127.0.0.1:{PORT}/')
    print(f'Workflows: {WF_DIR} ({len(find_workflows())} JSON)')
    print('Input:', STATE['input_dir'])
    try:
        webbrowser.open(f'http://127.0.0.1:{PORT}/')
        srv.serve_forever()
    except KeyboardInterrupt:pass
    finally:srv.server_close()
