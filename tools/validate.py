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

def main():
    wf = plistlib.loads((ROOT / "src" / "ReShortcut-Unsign.plist").read_bytes())
    errors, seen, stack, script = [], set(), [], None
    for i, action in enumerate(wf["WFWorkflowActions"]):
        p = action["WFWorkflowActionParameters"]
        errors += [f"acción {i}: referencia a una salida inexistente {r}" for r in refs(p) if r not in seen]
        uid = p.get("UUID")
        if uid:
            if uid in seen:
                errors.append(f"acción {i}: UUID repetido")
            seen.add(uid)
        mode, group = p.get("WFControlFlowMode"), p.get("GroupingIdentifier")
        if mode == 0:
            stack.append(group)
        elif mode is not None:
            if not stack or stack[-1] != group:
                errors.append(f"acción {i}: bloque mal anidado")
            elif mode == 2:
                stack.pop()
        if p.get("CustomOutputName") == "Script base64":
            script = base64.b64decode(p["WFTextActionText"])
    if stack:
        errors.append("hay bloques sin cerrar")
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
    ids = [a["WFWorkflowActionParameters"].get("CustomOutputName") for a in acts]
    if "Versión remota" not in ids:
        errors.append("falta la acción 'Versión remota'")
    else:
        i = ids.index("Versión remota")
        c = acts[i + 1]["WFWorkflowActionParameters"] if i + 1 < len(acts) else {}
        s = c.get("WFConditionalActionString", {}).get("Value", {}).get("attachmentsByRange", {})
        if (c.get("WFCondition") != 5 or "WFNumberValue" in c
                or [v.get("VariableName") for v in s.values()] != ["Version"]):
            errors.append("la condición de actualización debe ser: Versión remota «no es» la variable Version")
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
