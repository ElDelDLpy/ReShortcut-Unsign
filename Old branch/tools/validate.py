#!/usr/bin/env python3
"""Revisa la estructura del atajo: bloques, referencias, UUID y script incrustado.

Uso: python3 tools/validate.py
"""
import base64, json, plistlib, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def refs(o):
    if isinstance(o, dict):
        if o.get("Type") == "ActionOutput":
            yield o["OutputUUID"]
        for v in o.values():
            yield from refs(v)
    elif isinstance(o, list):
        for v in o:
            yield from refs(v)

def var_refs(o):
    if isinstance(o, dict):
        if o.get("Type") == "Variable" and "VariableName" in o:
            yield o["VariableName"]
        for v in o.values():
            yield from var_refs(v)
    elif isinstance(o, list):
        for v in o:
            yield from var_refs(v)

def main():
    wf = plistlib.loads((ROOT / "src" / "ReShortcut-Unsign.plist").read_bytes())
    errors, seen, stack, script = [], set(), [], None
    setvars = {"Repeat Item"}          # variables ya definidas (Repeat Item la crea el bucle)
    menus, cond_input, check_menu_seen = {}, {}, False
    for i, action in enumerate(wf["WFWorkflowActions"]):
        p = action["WFWorkflowActionParameters"]
        ident = action["WFWorkflowActionIdentifier"].rsplit(".", 1)[-1]
        errors += [f"acción {i}: referencia a una salida inexistente {r}" for r in refs(p) if r not in seen]
        errors += [f"acción {i}: usa la variable «{v}» antes de definirla" for v in sorted(set(var_refs(p))) if v not in setvars]
        if ident == "setvariable":
            setvars.add(p["WFVariableName"])
        uid = p.get("UUID")
        if uid:
            if uid in seen:
                errors.append(f"acción {i}: UUID repetido")
            seen.add(uid)
        mode, group = p.get("WFControlFlowMode"), p.get("GroupingIdentifier")
        if mode == 0:
            stack.append(group)
            if ident == "conditional":
                cond_input[group] = p.get("WFInput", {}).get("Variable", {}).get("Value", {}).get("VariableName")
        elif mode is not None:
            if not stack or stack[-1] != group:
                errors.append(f"acción {i}: bloque mal anidado")
            elif mode == 2:
                stack.pop()
        if ident == "choosefrommenu":
            if mode == 0:
                menus[group] = [len(p["WFMenuItems"]), 0]
                prompt = p.get("WFMenuPrompt")
                atts = prompt["Value"]["attachmentsByRange"].values() if isinstance(prompt, dict) else []
                names = {a.get("OutputName") for a in atts}
                check_menu_seen = check_menu_seen or "menu_check_title" in names
            elif mode == 1 and group in menus:
                menus[group][1] += 1
        if p.get("CustomOutputName") == "URL de versión":
            # el aviso previo (Revisar ahora / Omitir) va antes de consultar version.json
            if not check_menu_seen:
                errors.append("falta el aviso previo (menu_check_title) antes de consultar version.json")
            if "Buscar" not in [cond_input.get(g) for g in stack]:
                errors.append("la consulta de version.json debe ir dentro de «Si Buscar es si» (así Omitir no busca)")
        if p.get("CustomOutputName") == "Script base64":
            script = base64.b64decode(p["WFTextActionText"])
    if stack:
        errors.append("hay bloques sin cerrar")
    errors += [f"menú {g[:8]}: {n} opciones y {c} casos" for g, (n, c) in menus.items() if n != c]
    main_menu = [a["WFWorkflowActionParameters"] for a in wf["WFWorkflowActions"]
                 if a["WFWorkflowActionIdentifier"].endswith("choosefrommenu")
                 and a["WFWorkflowActionParameters"].get("WFControlFlowMode") == 0
                 and any(isinstance(it, dict) and "Idioma / Language" in it["WFValue"]["Value"]["string"]
                         for it in a["WFWorkflowActionParameters"]["WFMenuItems"])]
    if len(main_menu) != 1:
        errors.append("no encontré el menú principal (el que tiene «Idioma / Language»)")
    else:
        prompt = main_menu[0]["WFMenuPrompt"]["Value"]
        if "RSU v" not in prompt["string"] or "Version" not in [a.get("VariableName") for a in prompt["attachmentsByRange"].values()]:
            errors.append("el menú principal debe decir «RSU v» y la variable Version")
    aviso = [a["WFWorkflowActionParameters"].get("WFTextActionText") for a in wf["WFWorkflowActions"]
             if a["WFWorkflowActionParameters"].get("CustomOutputName") == "Aviso por defecto"]
    if aviso != ["si"]:
        errors.append("el aviso previo debe estar activado por defecto («Aviso por defecto» = si)")
    if script != (ROOT / "src" / "unsign.py").read_bytes():
        errors.append("el script incrustado no coincide con src/unsign.py (ejecuta build.py)")
    es = json.loads((ROOT / "lang" / "es.json").read_text(encoding="utf-8"))
    embedded = [a["WFWorkflowActionParameters"]["WFTextActionText"] for a in wf["WFWorkflowActions"]
                if a["WFWorkflowActionParameters"].get("CustomOutputName") == "Idioma base"]
    if [json.loads(t) for t in embedded] != [es]:
        errors.append("el español incrustado no coincide con lang/es.json (ejecuta build.py)")
    for path in sorted((ROOT / "lang").glob("*.json")):
        pack = json.loads(path.read_text(encoding="utf-8"))
        if set(pack) != set(es):
            errors.append(f"{path.name}: claves distintas a es.json")
        errors += [f"{path.name}: la clave {k} lleva punto" for k in pack if "." in k]
    ver = json.loads((ROOT / "version.json").read_text(encoding="utf-8"))["version"]
    readme = re.search(r"\*\*Versión:\*\* (\S+)", (ROOT / "Readme.md").read_text(encoding="utf-8"))
    change = re.search(r"^## (\S+)", (ROOT / "CHANGELOG.md").read_text(encoding="utf-8"), re.M)
    shortcut = [a["WFWorkflowActionParameters"]["WFTextActionText"] for a in wf["WFWorkflowActions"]
                if a["WFWorkflowActionParameters"].get("CustomOutputName") == "Versión valor"]
    for name, v in (("Readme.md", readme and readme.group(1)),
                    ("CHANGELOG.md", change and change.group(1)),
                    ("atajo", shortcut[0] if len(shortcut) == 1 else None)):
        if v != ver:
            errors.append(f"versión de {name} ({v}) distinta a version.json ({ver})")
    url = json.loads((ROOT / "version.json").read_text(encoding="utf-8")).get("url", "")
    pattern = [a["WFWorkflowActionParameters"]["WFMatchTextPattern"] for a in wf["WFWorkflowActions"]
               if a["WFWorkflowActionParameters"].get("CustomOutputName") == "Enlace válido"]
    if url and (len(pattern) != 1 or not re.search(pattern[0], url, re.I)):
        errors.append("version.json: url no es un enlace que el atajo acepte")
    comment = next((a["WFWorkflowActionParameters"].get("WFCommentActionText", "") for a in wf["WFWorkflowActions"]
                    if a["WFWorkflowActionIdentifier"].endswith(".comment")), "")
    cv = re.search(r"\bv(\d+\.\d+\.\d+)", comment)
    if not cv or cv.group(1) != ver:
        errors.append(f"versión del comentario inicial ({cv and cv.group(1)}) distinta a version.json ({ver})")
    acts = wf["WFWorkflowActions"]
    names = [x["WFWorkflowActionParameters"].get("CustomOutputName") for x in acts]
    try:
        i = names.index("Misma versión")
        m = acts[i]["WFWorkflowActionParameters"]
        c = acts[i + 1]["WFWorkflowActionParameters"]
        used_in = [v.get("OutputName") for v in m["text"]["Value"]["attachmentsByRange"].values()]
        ok = (acts[i]["WFWorkflowActionIdentifier"].endswith("text.match")
              and used_in == ["Versión remota texto", "Versión valor"]
              and "Versión remota texto" in names[:i]
              and c.get("WFCondition") == 101
              and c["WFInput"]["Variable"]["Value"]["OutputUUID"] == m["UUID"])
    except (ValueError, KeyError, IndexError):
        ok = False
    if not ok:
        errors.append("la comparación de versión debe ser: Texto(remota) | Versión valor -> coincidencia -> Si «no tiene ningún valor»")
    used = {a["WFWorkflowActionParameters"]["WFDictionaryKey"] for a in wf["WFWorkflowActions"]
            if a["WFWorkflowActionIdentifier"].endswith(".getvalueforkey")
            and a["WFWorkflowActionParameters"].get("WFInput", {}).get("Value", {}).get("VariableName") == "Textos"
            and isinstance(a["WFWorkflowActionParameters"].get("WFDictionaryKey"), str)}
    errors += [f"el atajo usa la clave {k} y no está en es.json" for k in sorted(used - set(es))]
    if errors:
        raise SystemExit("\n".join(errors))
    print("OK")

if __name__ == "__main__":
    main()
