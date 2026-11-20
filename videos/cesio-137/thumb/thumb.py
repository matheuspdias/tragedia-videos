"""Thumbnails do piloto Césio-137. Rodar da raiz: python videos/cesio-137/thumb/thumb.py"""
import sys, os
sys.path.insert(0, os.getcwd())
from engine import *
from ilustrado import *
from tragedia import *

OUT = os.path.dirname(os.path.abspath(__file__))
PER = dict(PERITO); PER.pop("fid", None)


def a(c, t):  # cápsula brilhando no escuro + Perito chocado
    luz("noite"); c.rectangle(0, 0, 1920, 1080); rgb(c, (0.03, 0.05, 0.08)); c.fill()
    capsula(c, t, 1380, 640, 3.0, brilho=1.0, furada=True)
    thumb_close(c, t, 400, 1560, 2.4, "shocked", "point_r", 0.8, quem=PER)
    thumb_texto(c, ["ELES LEVARAM", "PARA CASA"], 1230, 120, 140)
    thumb_selo(c, "GOIÂNIA, 1987", 1380, 960, 60)


def b(c, t):  # prédio em ruínas com brilho azul + aviso
    cena_cidade(c, t, "noite", seed=31)
    predio_ruina(c, t, 800, 880, 700, 460)
    rglow(c, 1120, 800, 300, AZUL_CESIO, 0.6)
    capsula(c, t, 1120, 820, 0.9, brilho=1.0, furada=True)
    thumb_close(c, t, 400, 1560, 2.4, "worried", "point_r", 0.8, quem=PER)
    thumb_texto(c, ["AVISARAM", "UM ANO ANTES"], 1250, 110, 150, cores=[(0.98, 0.96, 0.90), (0.95, 0.30, 0.22)])
    trevo(c, 1700, 880, 70)


for nome, fn in (("A_capsula", a), ("B_predio", b)):
    print(salvar_thumb(lambda c, t, fn=fn: fn(c, t), f"{OUT}/thumb_{nome}.png", tom="normal"))
