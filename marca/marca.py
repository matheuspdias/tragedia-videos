"""Foto de perfil (800x800) e banner (2560x1440) do Tragédia Anunciada. Rodar da raiz: python marca/marca.py"""
import sys, os
sys.path.insert(0, os.getcwd())
import cairo
import engine
from engine import *
from ilustrado import *
import ilustrado
from tragedia import *
from tragedia import _t

OUT = os.path.dirname(os.path.abspath(__file__))
PER = dict(PERITO); PER.pop("fid", None)
engine.STYLE, engine.TOM = "ilustrado", "normal"


def _salvar(surf, fn, w, h):
    tmp = fn + ".big.png"
    surf.write_to_png(tmp)
    os.system(f'ffmpeg -loglevel error -y -i "{tmp}" -vf scale={w}:{h}:flags=lanczos "{fn}" && rm "{tmp}"')


# ---------------------------------------------------------------- foto de perfil
def avatar(variante):
    S = 1080
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, S, S); c = cairo.Context(surf)
    luz("interior")
    g = cairo.RadialGradient(S / 2, S * 0.45, 0, S / 2, S / 2, S * 0.75)
    g.add_color_stop_rgb(0, 0.14, 0.19, 0.25); g.add_color_stop_rgb(1, 0.04, 0.05, 0.07)
    c.set_source(g); c.paint()
    if variante == "C":  # o Investigador + selo "TA" no canto
        rglow(c, S * 0.42, S * 0.42, S * 0.55, AZUL_CESIO, 0.22)
        c.save(); c.translate(-520, -20)
        thumb_close(c, 1.0, 960, 1720, 3.1, "confident", "stand", 0.0, quem=PER)
        c.restore()
        bx, by, r = S * 0.70, S * 0.62, 200  # triângulo dentro do círculo do YouTube
        tri = [(bx, by - r), (bx + r * 0.95, by + r * 0.70), (bx - r * 0.95, by + r * 0.70)]
        c.save(); c.translate(10, 14); pg(c, tri); rgb(c, (0, 0, 0), 0.45); c.fill(); c.restore()
        pg(c, tri); rgb(c, CREME); c.fill()
        pg(c, tri); c.set_line_width(30); c.set_line_join(1); rgb(c, ALERTA); c.stroke()
        _t(c, "TA", bx, by + r * 0.52, 132, (0.10, 0.12, 0.15), font=SERIF, bold=True, centro=True)
    elif variante == "A":  # o Investigador em close, com o brilho azul atrás
        rglow(c, S * 0.5, S * 0.42, S * 0.55, AZUL_CESIO, 0.22)
        c.save(); c.translate(-420, -20)
        thumb_close(c, 1.0, 960, 1720, 3.1, "confident", "stand", 0.0, quem=PER)
        c.restore()
    else:  # monograma: triângulo de alerta com "TA"
        pg(c, [(S / 2, 170), (S - 150, S - 230), (150, S - 230)]); rgb(c, CREME); c.fill()
        pg(c, [(S / 2, 170), (S - 150, S - 230), (150, S - 230)]); c.set_line_width(46); c.set_line_join(1); rgb(c, ALERTA); c.stroke()
        _t(c, "TA", S / 2, S - 330, 300, (0.10, 0.12, 0.15), font=SERIF, bold=True, centro=True)
    v = cairo.RadialGradient(S / 2, S / 2, S * 0.36, S / 2, S / 2, S * 0.72)
    v.add_color_stop_rgba(0, 0, 0, 0, 0); v.add_color_stop_rgba(1, 0, 0, 0, 0.7)
    c.set_source(v); c.paint()
    fn = f"{OUT}/avatar_{variante}.png"
    _salvar(surf, fn, 800, 800)
    # prévia no círculo
    os.system(f'ffmpeg -loglevel error -y -i "{fn}" -vf "format=rgba,geq=r=\'r(X,Y)\':g=\'g(X,Y)\':b=\'b(X,Y)\':a=\'if(lte(hypot(X-400,Y-400),400),255,0)\'" "{OUT}/preview_circulo_{variante}.png"')
    return fn


# ---------------------------------------------------------------- banner
def banner():
    """desenhado em 1920x1080 e ampliado para 2560x1440; área segura (todos os aparelhos): x 380-1540, y 381-698"""
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, 1920, 1080); c = cairo.Context(surf)
    t = 1.0
    cena_cidade(c, t, "crepusculo", seed=31)
    predio_ruina(c, t, 1180, 880, 560, 380)
    rglow(c, 1440, 800, 260, AZUL_CESIO, 0.40)
    capsula(c, t, 1440, 820, 0.7, brilho=1.0, furada=True)
    # faixa escura atrás do texto (dentro da área segura)
    c.rectangle(0, 381, 1920, 317); rgb(c, (0.05, 0.06, 0.08), 0.62); c.fill()
    perito_i(c, t, 560, 885, 0.92, poses=((0, "present"),), exprs=((0, "confident"),), look=0.5)
    _t(c, "TRAGÉDIA", 1080, 520, 96, CREME, font=SERIF, bold=True, centro=True)
    _t(c, "ANUNCIADA", 1080, 612, 96, ALERTA, font=SERIF, bold=True, centro=True)
    _t(c, "toda tragédia deu sinais antes", 1080, 668, 34, AMBER, centro=True)
    trevo(c, 1440, 470, 38)
    fn = f"{OUT}/banner_tragedia.png"
    _salvar(surf, fn, 2560, 1440)
    # prévia com as áreas marcadas
    c.rectangle(380, 381, 1160, 317); c.set_line_width(3); rgb(c, (0, 1, 0), 0.8); c.stroke()
    surf.write_to_png(f"{OUT}/preview_banner_area_segura.png")
    return fn


if __name__ == "__main__":
    for v in ("A", "B", "C"):
        print(avatar(v))
    print(banner())
