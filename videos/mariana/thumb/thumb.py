"""Thumbnails de Mariana. Rodar da raiz: python videos/mariana/thumb/thumb.py"""
import sys, os, math
sys.path.insert(0, os.getcwd())
from engine import *
from ilustrado import *
from tragedia import *
from barragem import *

OUT = os.path.dirname(os.path.abspath(__file__))
PER = dict(PERITO); PER.pop("fid", None)


def a(c, t):  # barragem rompendo, lama descendo no vilarejo
    vale(c, t, "tarde", seed=5)
    barragem_paisagem(c, t, 1250, 520, 1000, 0.85, 6, rompida=0.8, depth=0.15)
    vilarejo(c, t, 1300, 980, 0.9, 7, seed=4)
    onda_lama(c, t, 1100, 1040, 380)
    thumb_close(c, t, 400, 1560, 2.4, "shocked", "point_r", 0.8, quem=PER)
    thumb_texto(c, ["SEM SIRENE"], 1240, 110, 150, cores=[(0.95, 0.30, 0.22)])
    thumb_selo(c, "MARIANA, 2015", 1380, 300, 56)


def b(c, t):  # sirene riscada + barragem
    vale(c, t, "tarde", seed=8)
    barragem_paisagem(c, t, 1300, 560, 900, 0.85, 6, vazamento=0.8, trinca=1.0, depth=0.15)
    sirene(c, t, 1600, 700, 0.9, riscada=True)
    thumb_close(c, t, 400, 1560, 2.4, "worried", "point_r", 0.8, quem=PER)
    thumb_texto(c, ["6 ANOS", "DE AVISOS"], 1250, 110, 140, cores=[(0.98, 0.96, 0.90), (0.95, 0.30, 0.22)])


for nome, fn in (("A_sem_sirene", a), ("B_6_anos", b)):
    print(salvar_thumb(lambda c, t, fn=fn: fn(c, t), f"{OUT}/thumb_{nome}.png", tom="normal"))
