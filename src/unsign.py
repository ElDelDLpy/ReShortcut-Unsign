#!/usr/bin/env python3
# unsign.py — Quita la firma a un .shortcut firmado (AEA1) y deja el plist sin firmar.
# 100% Python puro (incluye descompresor LZFSE/LZVN), funciona en a-Shell.
#
# Acepta también un JSON o plist de atajo (WFWorkflowActions) y lo convierte a .shortcut (plist binario, sin firmar).
# --salida shortcut|json|plist|todos  (solo en el modo de Atajos: limita lo que se devuelve)
# Uso:  python3 unsign.py entrada.shortcut [salida.shortcut] [--json salida.json] [--plist salida.plist]
#       python3 unsign.py --shortcuts <enlace iCloud | base64 del .shortcut>   (modo Atajos)
import sys, struct, plistlib, json, base64, datetime, os, re

# ---------------------------------------------------------------- LZFSE
def _bases(extra):
    b, v = [], 0
    for e in extra:
        b.append(v); v += 1 << e
    return b

L_EXTRA = [0]*16 + [2, 3, 5, 8]
M_EXTRA = [0]*16 + [3, 5, 8, 11]
D_EXTRA = [0,0,0,0] + [e for e in range(1, 16) for _ in range(4)]
L_BASE, M_BASE, D_BASE = _bases(L_EXTRA), _bases(M_EXTRA), _bases(D_EXTRA)
M64 = (1 << 64) - 1

_NB = [2,3,2,5,2,3,2,8,2,3,2,5,2,3,2,14]*2
_VT = [0,2,1,4,0,3,1,-1,0,2,1,5,0,3,1,-1,0,2,1,6,0,3,1,-1,0,2,1,7,0,3,1,-1]

def _freq_value(bits):
    b = bits & 31
    n = _NB[b]
    if n == 8:  return 8 + ((bits >> 4) & 0xF), n
    if n == 14: return 24 + ((bits >> 4) & 0x3FF), n
    return _VT[b], n

def _ktab(nstates, freq):
    """Devuelve lista de (k, delta, idx_simbolo) por estado."""
    t = []
    for i, f in enumerate(freq):
        if not f: continue
        k = nstates.bit_length() - f.bit_length()
        j0 = ((2 * nstates) >> k) - f
        for j in range(f):
            if j < j0: t.append((k, ((f + j) << k) - nstates, i))
            else:      t.append((k - 1, (j - j0) << (k - 1), i))
    if len(t) != nstates:
        raise ValueError("Tabla FSE inválida")
    return t

class _In:
    def __init__(self, buf, start, end, n):
        self.b, self.start, self.pos = buf, start, end
        if n:
            self.pos -= 8
            self.acc = int.from_bytes(buf[self.pos:self.pos+8], "little"); self.nb = n + 64
        else:
            self.pos -= 7
            self.acc = int.from_bytes(buf[self.pos:self.pos+7], "little"); self.nb = 56
        if self.pos < start or not (56 <= self.nb < 64) or (self.acc >> self.nb):
            raise ValueError("Flujo FSE inválido")
    def flush(self):
        nbits = (63 - self.nb) & ~7
        if not nbits: return
        self.pos -= nbits >> 3
        if self.pos < 0: raise ValueError("Flujo FSE agotado")
        inc = int.from_bytes(self.b[self.pos:self.pos + (nbits >> 3)], "little")
        self.acc = ((self.acc << nbits) | inc) & M64
        self.nb += nbits
    def pull(self, n):
        self.nb -= n
        r = self.acc >> self.nb
        self.acc &= (1 << self.nb) - 1
        return r

def _vdec(state, tab, extra, base, ins):
    k, delta, s = tab[state]
    vb = extra[s]
    x = ins.pull(k + vb)
    return delta + (x >> vb), base[s] + (x & ((1 << vb) - 1))

def _bvx2(d, p, out):
    n_raw = struct.unpack_from("<I", d, p + 4)[0]
    v0, v1, v2 = struct.unpack_from("<QQQ", d, p + 8)
    g = lambda v, o, n: (v >> o) & ((1 << n) - 1)
    n_lit, n_litpay, n_match = g(v0,0,20), g(v0,20,20), g(v0,40,20)
    lit_bits = g(v0,60,3) - 7
    lit_state = [g(v1,0,10), g(v1,10,10), g(v1,20,10), g(v1,30,10)]
    n_lmdpay, lmd_bits = g(v1,40,20), g(v1,60,3) - 7
    hsize = g(v2,0,32)
    ls, ms, ds = g(v2,32,10), g(v2,42,10), g(v2,52,10)
    freqs = [0] * 360
    q, end, acc, nb = p + 32, p + hsize, 0, 0
    for i in range(360):
        while nb < 14 and q < end:
            acc |= d[q] << nb; nb += 8; q += 1
        f, n = _freq_value(acc)
        acc >>= n; nb -= n
        freqs[i] = f
    lf, mf, df, litf = freqs[:20], freqs[20:40], freqs[40:104], freqs[104:]
    lt, mt, dt, littab = _ktab(64, lf), _ktab(64, mf), _ktab(256, df), _ktab(1024, litf)

    s0 = p + hsize
    ins = _In(d, s0, s0 + n_litpay, lit_bits)
    lits = bytearray(n_lit)
    st = lit_state[:]
    for i in range(0, n_lit, 4):
        ins.flush()
        for j in range(4):
            k, delta, sym = littab[st[j]]
            st[j] = delta + ins.pull(k)
            lits[i + j] = sym

    s1 = s0 + n_litpay
    ins = _In(d, s1, s1 + n_lmdpay, lmd_bits)
    lp, D, start = 0, -1, len(out)
    for _ in range(n_match):
        ins.flush()
        ls, L = _vdec(ls, lt, L_EXTRA, L_BASE, ins)
        ms, M = _vdec(ms, mt, M_EXTRA, M_BASE, ins)
        ds, nd = _vdec(ds, dt, D_EXTRA, D_BASE, ins)
        if nd: D = nd
        out += lits[lp:lp + L]; lp += L
        if M:
            if D <= 0 or D > len(out): raise ValueError("Distancia inválida")
            src = len(out) - D
            if D >= M: out += out[src:src + M]
            else:
                for i in range(M): out.append(out[src + i])
    if len(out) - start != n_raw:
        raise ValueError(f"Tamaño inesperado ({len(out)-start} != {n_raw})")
    return s1 + n_lmdpay

def _bvxn(d, p, out):
    n_raw, n_pay = struct.unpack_from("<II", d, p + 4)
    s, e, start, D = p + 12, p + 12 + n_pay, len(out), 0
    while s < e:
        o = d[s]
        if 0xE0 <= o <= 0xEF:
            if o == 0xE0: L = d[s+1] + 16; s += 2
            else: L = o & 0xF; s += 1
            out += d[s:s+L]; s += L; continue
        if o >= 0xF0:
            if o == 0xF0: M = d[s+1] + 16; s += 2
            else: M = o & 0xF; s += 1
            L = 0
        elif 0xA0 <= o <= 0xBF:
            b1, b2 = d[s+1], d[s+2]
            L = (o >> 3) & 3; M = (((o & 7) << 2) | (b1 & 3)) + 3; D = (b2 << 6) | (b1 >> 2); s += 3
        elif 0x70 <= o <= 0x7F or 0xD0 <= o <= 0xDF:
            raise ValueError("Opcode LZVN inválido")
        elif (o & 7) == 7:
            L = o >> 6; M = ((o >> 3) & 7) + 3; D = d[s+1] | (d[s+2] << 8); s += 3
        elif (o & 7) == 6:
            if o < 0x40:
                if o == 0x06: break
                if o in (0x0E, 0x16): s += 1; continue
                raise ValueError("Opcode LZVN inválido")
            L = o >> 6; M = ((o >> 3) & 7) + 3; s += 1
        else:
            L = o >> 6; M = ((o >> 3) & 7) + 3; D = ((o & 7) << 8) | d[s+1]; s += 2
        out += d[s:s+L]; s += L
        src = len(out) - D
        if D <= 0 or src < start: raise ValueError("Distancia LZVN inválida")
        for i in range(M): out.append(out[src + i])
    if len(out) - start != n_raw:
        raise ValueError("Tamaño LZVN inesperado")
    return e

def lzfse_decompress(d, p=0):
    out = bytearray()
    while True:
        m = d[p:p+4]
        if m == b"bvx$": return bytes(out), p + 4
        if m == b"bvx2": p = _bvx2(d, p, out)
        elif m == b"bvxn": p = _bvxn(d, p, out)
        elif m == b"bvx-":
            n = struct.unpack_from("<I", d, p + 4)[0]
            out += d[p+8:p+8+n]; p += 8 + n
        else:
            raise ValueError(f"Bloque LZFSE desconocido: {m!r}")

# ---------------------------------------------------------- Apple Archive
def apple_archive_files(a):
    """Itera (ruta, datos) de un Apple Archive (AA01/YAA1)."""
    p = 0
    while p + 6 <= len(a):
        if a[p:p+4] not in (b"AA01", b"YAA1"): break
        hs = struct.unpack_from("<H", a, p + 4)[0]
        q, end, path, blobs = p + 6, p + hs, "", []
        while q < end:
            key, t = a[q:q+3].decode("latin1"), chr(a[q+3]); q += 4
            if t == "*": continue
            if t in "1248": q += int(t)
            elif t == "P":
                n = struct.unpack_from("<H", a, q)[0]
                v = a[q+2:q+2+n].decode("utf-8", "replace"); q += 2 + n
                if key == "PAT": path = v
            elif t in "ABC":
                sz = {"A": 2, "B": 4, "C": 8}[t]
                n = int.from_bytes(a[q:q+sz], "little"); q += sz
                blobs.append((key, n))
            elif t == "T": q += 12
            elif t == "S": q += 8
            elif t == "F": q += struct.unpack_from("<H", a, q)[0] + 2
            else: raise ValueError(f"Campo AA desconocido {key}{t}")
        p = end
        data = None
        for key, n in blobs:
            if key == "DAT": data = a[p:p+n]
            p += n
        if data is not None:
            yield path, data

# ------------------------------------------------------------------- AEA
def _from_json(o):
    """Revierte _json_default (bytes/UID) al volver de JSON a plist."""
    if isinstance(o, dict):
        if set(o) == {"__data_base64__"}: return base64.b64decode(o["__data_base64__"])
        if set(o) == {"__uid__"}: return plistlib.UID(o["__uid__"])
        return {k: _from_json(v) for k, v in o.items()}
    if isinstance(o, list): return [_from_json(v) for v in o]
    return o

def unsign(raw):
    if raw.lstrip(b"\xef\xbb\xbf \t\r\n")[:1] == b"{":       # JSON -> .shortcut
        try: wf = _from_json(json.loads(raw.decode("utf-8-sig")))
        except ValueError as e: raise ValueError(f"JSON inválido: {e}")
        if not isinstance(wf, dict) or "WFWorkflowActions" not in wf:
            raise ValueError("El JSON no parece un atajo (falta WFWorkflowActions)")
        return plistlib.dumps(wf, fmt=plistlib.FMT_BINARY, sort_keys=False)
    if raw[:4] != b"AEA1":
        wf = plistlib.loads(raw)     # ya está sin firmar (plist XML o binario)
        if not isinstance(wf, dict) or "WFWorkflowActions" not in wf:
            raise ValueError("El plist no parece un atajo (falta WFWorkflowActions)")
        return raw
    if raw[4:7] != b"\0\0\0":
        raise ValueError("Perfil AEA cifrado: no se puede extraer sin clave")
    p = raw.find(b"bvx")
    while p != -1:
        try:
            archive, _ = lzfse_decompress(raw, p)
            break
        except ValueError:
            p = raw.find(b"bvx", p + 1)
    else:
        raise ValueError("No encontré datos comprimidos LZFSE")
    for path, data in apple_archive_files(archive):
        if path.endswith(".wflow") or data[:6] == b"bplist":
            return data
    raise ValueError("No encontré Shortcut.wflow dentro del archivo")

def _json_default(o):
    if isinstance(o, (bytes, bytearray)): return {"__data_base64__": base64.b64encode(o).decode()}
    if isinstance(o, (datetime.datetime, datetime.date)): return o.isoformat()
    if isinstance(o, plistlib.UID): return {"__uid__": o.data}
    raise TypeError(type(o))

def _fetch(url):
    import urllib.request
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as r:
        return r.read()

def from_icloud(link):
    import re
    m = re.search(r"[0-9a-fA-F]{32}", link)
    if not m: raise ValueError("No encontré un ID de iCloud en el enlace")
    rec = json.loads(_fetch(f"https://www.icloud.com/shortcuts/api/records/{m.group(0)}"))
    f = rec["fields"]
    name = f.get("name", {}).get("value", m.group(0))
    url = f["shortcut"]["value"]["downloadURL"].replace("${f}", "atajo.shortcut")
    return name, _fetch(url)

# plist XML: XML 1.0 no admite caracteres de control ni UID (el binario sí). Se adaptan.
_CTRL = re.compile("[\x00-\x08\x0b\x0c\x0e-\x1f\ufffe\uffff]")
def _xml_safe(o, st):
    if isinstance(o, str):
        o, n = _CTRL.subn("\ufffd", o); st[0] += n; return o
    if isinstance(o, plistlib.UID): return {"CF$UID": o.data}
    if isinstance(o, dict): return {_xml_safe(k, st): _xml_safe(v, st) for k, v in o.items()}
    if isinstance(o, (list, tuple)): return [_xml_safe(v, st) for v in o]
    return o

def to_xml(wf):
    """Devuelve (texto plist XML, nº de caracteres de control reemplazados)."""
    st = [0]
    return plistlib.dumps(_xml_safe(wf, st), fmt=plistlib.FMT_XML, sort_keys=False).decode("utf-8"), st[0]

def shortcuts_mode(arg, from_file=False, want="todos"):
    """Entrada: enlace de iCloud o base64 de un .shortcut. Salida (stdout): JSON para Atajos."""
    arg = arg.strip()
    try:
        if from_file:
            with open(arg, "rb") as fh: raw = fh.read()
            name = os.path.splitext(os.path.basename(arg))[0]
            try: os.remove(arg)
            except OSError: pass
        elif "icloud.com" in arg:
            name, raw = from_icloud(arg)
        else:
            name, raw = "Atajo", base64.b64decode(arg + "=" * (-len(arg) % 4))
        wf = plistlib.loads(unsign(raw))
        bin_ = plistlib.dumps(wf, fmt=plistlib.FMT_BINARY, sort_keys=False)
        res = {"ok": True, "name": name, "acciones": len(wf.get("WFWorkflowActions", [])),
               "shortcut": base64.b64encode(bin_).decode()}
        if want in ("json", "todos", "ambos"):
            res["json"] = json.dumps(wf, ensure_ascii=False, indent=2, default=_json_default)
        if want in ("plist", "todos", "ambos"):   # solo se genera si se pide: respuesta más corta
            try:
                res["plist"], n = to_xml(wf)
                if n: res["plist_aviso"] = f"{n} carácter(es) de control no válidos en XML se reemplazaron por U+FFFD."
            except Exception as e:
                res["plist"] = ""; res["plist_error"] = f"{type(e).__name__}: {e}"
    except Exception as e:
        res = {"ok": False, "error": f"{type(e).__name__}: {e}"}
    print(json.dumps(res, ensure_ascii=False))

if __name__ == "__main__":
    args = sys.argv[1:]
    want = "todos"
    if "--salida" in args:
        i = args.index("--salida"); want = (args[i+1] if i+1 < len(args) else "todos").strip().lower(); del args[i:i+2]
    if args[:1] == ["--shortcuts-file"]:
        shortcuts_mode(" ".join(args[1:]), True, want); sys.exit(0)
    if args[:1] == ["--shortcuts"]:
        shortcuts_mode(" ".join(args[1:]), False, want); sys.exit(0)
    js = pl = None
    if "--plist" in args:
        i = args.index("--plist"); pl = args[i+1]; del args[i:i+2]
    if "--json" in args:
        i = args.index("--json"); js = args[i+1]; del args[i:i+2]
    if not args: sys.exit("Uso: python3 unsign.py entrada.shortcut [salida.shortcut] [--json salida.json] [--plist salida.plist]")
    src = args[0]
    dst = args[1] if len(args) > 1 else os.path.splitext(src)[0] + "_sinfirma.shortcut"
    data = unsign(open(src, "rb").read())
    wf = plistlib.loads(data)
    with open(dst, "wb") as f:
        plistlib.dump(wf, f, fmt=plistlib.FMT_BINARY, sort_keys=False)
    if pl:
        with open(pl, "w", encoding="utf-8") as f:
            f.write(to_xml(wf)[0])
    if js:
        with open(js, "w", encoding="utf-8") as f:
            json.dump(wf, f, ensure_ascii=False, indent=2, default=_json_default)
    print(f"Listo: {dst} ({len(wf.get('WFWorkflowActions', []))} acciones)" + (f" + {js}" if js else ""))