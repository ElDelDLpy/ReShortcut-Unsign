#!/usr/bin/env python3
"""Revisa la estructura del atajo: bloques, referencias, UUID y script incrustado.

Uso: python3 tools/validate.py
"""
import base64, json
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
    wf = json.loads((ROOT / "src" / "ReShortcut Unsign.json").read_text(encoding="utf-8"))
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
    if errors:
        raise SystemExit("\n".join(errors))
    print("OK")

if __name__ == "__main__":
    main()
