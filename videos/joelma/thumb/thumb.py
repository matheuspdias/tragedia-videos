"""Thumbnails do Edifício Joelma. Rodar da raiz: python videos/joelma/thumb/thumb.py"""
import sys, os, math
sys.path.insert(0, os.getcwd())
from engine import *
from ilustrado import *
from tragedia import *
from incendio import *

OUT = os.path.dirname(os.path.abspath(__file__))
PER = dict(PERITO); PER.pop("fid", None)
TUDO = lambda a: 1.0 if a > 11 else 0.0


def a(c, t):  # prédio em chamas, gente no telhado, sem heliponto
    luz("nublado"); ceu(c, t, passaros=False, seed=4); ceu_fumaca(c, 0.8)
    c.save(); c.translate(1320, 1900); c.scale(1.9, 1.9)
    arranha_ceu(c, t, 0, 0, 380, 25, 30, fogo=TUDO, garagem=10, gente_telhado=30, fumaca_on=False); c.restore()
    fumaca(c, t, 1500, 520, 220, 700, 0.8, seed=3)
    thumb_close(c, t, 400, 1560, 2.4, "shocked", "point_r", 0.8, quem=PER)
    thumb_texto(c, ["SEM SAÍDA", "NO TELHADO"], 1240, 110, 140, cores=[(0.98, 0.96, 0.90), (0.95, 0.30, 0.22)])
    thumb_selo(c, "SÃO PAULO, 1974", 1380, 1000, 56)


def b(c, t):  # os dois prédios: Andraus (heliponto) x Joelma (sem)
    luz("nublado"); c.rectangle(0, 0, 1920, 1080); rgb(c, (0.10, 0.12, 0.15)); c.fill()
    c.save(); c.translate(1080, 1060); c.scale(1.05, 1.05)
    arranha_ceu(c, t, 0, 0, 340, 32, 22, garagem=0, col=(0.78, 0.80, 0.82), heliponto=True, telhado="laje"); c.restore()
    c.save(); c.translate(1600, 1060); c.scale(1.05, 1.05)
    arranha_ceu(c, t, 0, 0, 380, 25, 30, fogo=TUDO, garagem=10, fumaca_on=False); c.restore()
    thumb_close(c, t, 400, 1560, 2.4, "worried", "point_r", 0.8, quem=PER)
    thumb_texto(c, ["O AVISO", "VEIO ANTES"], 1250, 110, 150, cores=[(0.98, 0.96, 0.90), (0.95, 0.30, 0.22)])


for nome, fn in (("A_telhado", a), ("B_dois_predios", b)):
    print(salvar_thumb(lambda c, t, fn=fn: fn(c, t), f"{OUT}/thumb_{nome}.png", tom="normal"))
