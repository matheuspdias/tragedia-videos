"""
Junta os blocos da narração cortando silêncios longos (ritmo de "corte seco") e recalcula o tempo de cada palavra.

Uso:
  python juntar_cortando.py videos/<slug> out/<slug>_narracao.wav b1.wav b2.wav ...

Lê videos/<slug>/ts/blocoN.json (resposta do HeyGen com original_words) e grava:
  - o WAV final (float 32, mono)
  - videos/<slug>/palavras.json  -> [{"w": palavra, "t": início, "e": fim, "b": bloco, "i": índice}]
  - videos/<slug>/transcricao.txt -> "(m:ss) frase" por frase

Regras (variáveis de ambiente para ajustar):
  GAP_MAX=0.32   silêncio máximo entre palavras dentro de um bloco (segundos)
  GAP_PAUSA=0.85 silêncio mantido onde o roteiro tem [pause]
  GAP_BLOCO=0.45 silêncio entre blocos
  Silêncios menores que GAP_MAX ficam como estão (respiração natural).
"""
import json, os, re, sys
import numpy as np
import subprocess

TAGS = {"serious", "thoughtful", "sad", "mysterious", "pause", "calm", "curious", "short", "long"}
GAP_MAX = float(os.environ.get("GAP_MAX", 99))  # padrão: NÃO corta silêncios (o 1.2x já basta); GAP_MAX=0.32 liga o corte
GAP_PAUSA = float(os.environ.get("GAP_PAUSA", 99))
GAP_BLOCO = float(os.environ.get("GAP_BLOCO", 0.45))
FADE = 0.012


def ler_wav(fn):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", fn, "-f", "f32le", "-ac", "1", "-ar", "44100", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).copy()


def palavras_do_bloco(js):
    """palavras sem as tags; marca as que vêm logo depois de [pause]"""
    chars = "".join(ch["text"] for ch in js["original_characters"])
    out = []
    pos = 0
    for w in js["original_words"]:
        txt = w["text"]
        k = chars.find(txt, pos)
        antes = chars[max(0, k - 2):k] if k >= 0 else ""
        if k >= 0:
            pos = k + len(txt)
        if txt.lower() in TAGS and antes.endswith("["):
            if txt.lower() == "pause":
                out.append({"pausa": True})
            continue
        out.append({"w": txt, "t": w["start_time"], "e": w["end_time"]})
    # junta a marca de pausa na palavra seguinte
    res, pausa = [], False
    for o in out:
        if o.get("pausa"):
            pausa = True
            continue
        o["pausa"] = pausa
        pausa = False
        res.append(o)
    return res


def main():
    pasta, saida, blocos = sys.argv[1], sys.argv[2], sys.argv[3:]
    sr = 44100
    final = []
    palavras = []
    cursor = 0.0  # tempo atual no áudio final
    MARGEM = 0.12   # nunca corta a menos disso de uma palavra (os tempos do HeyGen não são exatos)
    FADE_C = 0.008  # transição suave em cada corte (evita estalo)
    LIMIAR = 10 ** (-42 / 20)  # só corta trecho realmente silencioso
    for bi, fn in enumerate(blocos, 1):
        js = json.load(open(os.path.join(pasta, "ts", f"bloco{bi}.json")))
        audio = ler_wav(fn)
        ws = palavras_do_bloco(js)
        dur_b = len(audio) / sr
        # regiões a remover (em segundos do bloco), só no meio de silêncios longos
        rem = []
        for i in range(len(ws) - 1):
            a, b = ws[i]["e"] + MARGEM, ws[i + 1]["t"] - MARGEM
            limite = (GAP_PAUSA if ws[i + 1]["pausa"] else GAP_MAX) - 2 * MARGEM
            excesso = (b - a) - max(0.0, limite)
            if excesso <= 0.02:
                continue
            ca = a + (b - a - excesso) / 2; cb = ca + excesso
            trecho = audio[int(ca * sr):int(cb * sr)]
            if len(trecho) and np.sqrt(np.mean(trecho ** 2)) < LIMIAR and np.max(np.abs(trecho)) < 0.05:
                rem.append((ca, cb))
        # monta o bloco sem as regiões removidas, com fade nas emendas
        pedaços, mapa, pos, saida_t = [], [], 0.0, 0.0
        for ca, cb in rem + [(dur_b, dur_b)]:
            seg = audio[int(pos * sr):int(ca * sr)].copy()
            n = min(int(FADE_C * sr), len(seg) // 2)
            if n > 0:
                if pos > 0:
                    seg[:n] *= np.linspace(0, 1, n)
                if ca < dur_b:
                    seg[-n:] *= np.linspace(1, 0, n)
            mapa.append((pos, ca, saida_t))
            pedaços.append(seg); saida_t += len(seg) / sr
            pos = cb
        bloco_out = np.concatenate(pedaços)

        def conv(tb):
            for p0, p1, o in mapa:
                if tb <= p1:
                    return o + max(0.0, tb - p0)
            return saida_t
        for w in ws:
            palavras.append({"w": w["w"], "t": round(cursor + conv(w["t"]), 3), "e": round(cursor + conv(w["e"]), 3), "b": bi})
        final.append(bloco_out); cursor += len(bloco_out) / sr
        if bi < len(blocos):
            final.append(np.zeros(int(GAP_BLOCO * sr), dtype=np.float32)); cursor += GAP_BLOCO
    out = np.concatenate(final).astype(np.float32)
    os.makedirs(os.path.dirname(saida) or ".", exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "f32le", "-ar", str(sr), "-ac", "1", "-i", "-",
                    "-c:a", "pcm_f32le", saida], input=out.tobytes(), check=True)
    for i, p in enumerate(palavras):
        p["i"] = i
    json.dump(palavras, open(os.path.join(pasta, "palavras.json"), "w"), ensure_ascii=False, indent=0)
    # transcrição por frase
    linhas, frase, t0 = [], [], None
    for p in palavras:
        if t0 is None:
            t0 = p["t"]
        frase.append(p["w"])
        if re.search(r"[.!?:]$", p["w"]):
            linhas.append(f"({int(t0 // 60)}:{t0 % 60:05.2f}) " + " ".join(frase)); frase, t0 = [], None
    if frase:
        linhas.append(f"({int(t0 // 60)}:{t0 % 60:05.2f}) " + " ".join(frase))
    open(os.path.join(pasta, "transcricao.txt"), "w").write("\n".join(linhas) + "\n")
    orig = sum(len(ler_wav(f)) for f in blocos) / sr
    print(f"original {orig:.1f}s -> final {len(out) / sr:.1f}s ({len(palavras)} palavras, "
          f"{len(palavras) / (len(out) / sr) * 60:.0f} palavras/min)")


if __name__ == "__main__":
    main()
