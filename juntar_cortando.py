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
GAP_MAX = float(os.environ.get("GAP_MAX", 0.32))
GAP_PAUSA = float(os.environ.get("GAP_PAUSA", 0.85))
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
    for bi, fn in enumerate(blocos, 1):
        js = json.load(open(os.path.join(pasta, "ts", f"bloco{bi}.json")))
        audio = ler_wav(fn)
        ws = palavras_do_bloco(js)
        # trechos de fala: do início da palavra i ao fim; entre palavras, o silêncio é limitado
        segs = []  # (ini, fim) no bloco, já com o silêncio que vem antes
        prev_end = 0.0
        for i, w in enumerate(ws):
            gap = w["t"] - prev_end
            limite = GAP_PAUSA if w["pausa"] else GAP_MAX
            if i == 0:
                gap_keep = min(gap, 0.05)
            else:
                gap_keep = min(gap, limite)
            segs.append((w["t"] - gap_keep, w["e"], w))
            prev_end = w["e"]
        # monta: cada segmento vai de (t - gap_keep) até o fim da palavra
        for ini, fim, w in segs:
            a, b = int(max(0, ini) * sr), int(min(len(audio) / sr, fim) * sr)
            pedaço = audio[a:b].copy()
            n = min(int(FADE * sr), len(pedaço) // 4)
            if n > 0:
                pedaço[:n] *= np.linspace(0, 1, n)
            start_out = cursor + (w["t"] - max(0, ini))
            palavras.append({"w": w["w"], "t": round(start_out, 3), "e": round(start_out + (w["e"] - w["t"]), 3),
                             "b": bi})
            final.append(pedaço)
            cursor += len(pedaço) / sr
        # cauda do bloco (respiro final) + silêncio entre blocos
        cauda = audio[int(ws[-1]["e"] * sr): int(min(len(audio) / sr, ws[-1]["e"] + 0.15) * sr)].copy()
        if len(cauda):
            cauda *= np.linspace(1, 0, len(cauda))
        final.append(cauda); cursor += len(cauda) / sr
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
