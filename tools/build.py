#!/usr/bin/env python3
"""Incrusta src/unsign.py y shortcut/lang/es.json en src/ReShortcut-Unsign.plist y genera dist/ (plist binario sin firmar).

Uso: python3 tools/build.py
"""
import base64, plistlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src" / "ReShortcut-Unsign.plist"

def main():
    wf = plistlib.loads(SRC.read_bytes())
    targets = [a["WFWorkflowActionParameters"] for a in wf["WFWorkflowActions"]
               if a["WFWorkflowActionParameters"].get("CustomOutputName") == "Script base64"]
    if len(targets) != 1:
        raise SystemExit("No encontré una única acción 'Script base64'")
    targets[0]["WFTextActionText"] = base64.b64encode((ROOT / "src" / "unsign.py").read_bytes()).decode()
    base = [a["WFWorkflowActionParameters"] for a in wf["WFWorkflowActions"]
            if a["WFWorkflowActionParameters"].get("CustomOutputName") == "Idioma base"]
    if len(base) != 1:
        raise SystemExit("No encontré una única acción 'Idioma base'")
    base[0]["WFTextActionText"] = (ROOT / "shortcut" / "lang" / "es.json").read_text(encoding="utf-8").strip()
    SRC.write_bytes(plistlib.dumps(wf, fmt=plistlib.FMT_XML, sort_keys=False))
    out = ROOT / "dist" / "ReShortcut-Unsign.shortcut"
    out.parent.mkdir(exist_ok=True)
    out.write_bytes(plistlib.dumps(wf, fmt=plistlib.FMT_BINARY, sort_keys=False))
    print(f"Listo: {out.relative_to(ROOT)} ({len(wf['WFWorkflowActions'])} acciones)")

if __name__ == "__main__":
    main()
