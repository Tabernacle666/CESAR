# Outil facultatif : exécuter une fois dans le dossier du studio pour invalider les validations des clips modifiés.
import json,pathlib
p=pathlib.Path(__file__).with_name("studio_state.json")
if p.is_file():
 d=json.loads(p.read_text(encoding="utf-8"));d["project_pass2"]=False;d["scene_pass2"]={};d["clip_pass2"]={};d["ready"]={};d["scene_locked"]={};p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print("Ready réinitialisé; passe 2 désactivée")
else: print("Aucun état local: passe 2 désactivée par défaut")
