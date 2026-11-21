"""
Kit visual do canal TRAGÉDIA ANUNCIADA (por cima do estilo ilustrado).
Tudo chapado, sem contorno, com cores passadas por P(cor, depth) para seguir a luz da cena.
Peças técnicas (diagramas, mapa, linha do tempo, corrente de erros) usam a paleta "laudo":
fundo azul-ardósia, traço creme, destaque âmbar e vermelho de alerta.
"""
import math, random
import engine
from engine import ease_out, ease_out_back, prog, rgb, ellipse, SERIF, TYPE, HAND, AMBER
from ilustrado import *
from ilustrado import _bold

# ---------------------------------------------------------------- paleta do canal
LAUDO_BG = (0.10, 0.14, 0.19)
LAUDO_GRADE = (0.20, 0.27, 0.34)
CREME = (0.95, 0.92, 0.84)
ALERTA = (0.86, 0.20, 0.16)
AZUL_CESIO = (0.35, 0.75, 1.00)
CHUMBO = (0.40, 0.42, 0.46)
ACO = (0.66, 0.68, 0.72)


def _t(c, s, x, y, size, col=CREME, font=None, bold=False, a=1.0, centro=False):
    if bold:
        _bold(c, font or SERIF)
    else:
        c.select_font_face(font or TYPE)
    c.set_font_size(size)
    w = c.text_extents(s).x_advance
    c.move_to(x - (w / 2 if centro else 0), y); rgb(c, col, a); c.show_text(s)
    return w


# ---------------------------------------------------------------- cenário urbano anos 80
def cena_cidade(c, t, hora="dia", seed=31, chao_y=880, predios=True):
    """rua de cidade brasileira dos anos 80: prédios baixos modernos ao fundo, casas na frente"""
    luz(hora)
    ceu(c, t, passaros=hora in ("dia", "tarde"), seed=seed)
    if predios:
        rnd = random.Random(seed)
        x = -40
        while x < 1960:
            w = rnd.uniform(160, 260); h = rnd.uniform(260, 520)
            predio(c, x, chao_y - 40, w, h, "moderno", seed=rnd.randint(1, 999), depth=0.55, telhado=False, porta=False)
            x += w + rnd.uniform(10, 40)
    casario(c, t, chao_y, "colonial", seed=seed + 3, h=(220, 320), w=(220, 320), depth=0.15)
    chao(c, t, chao_y, "pedra", seed=seed)


def predio_ruina(c, t, x, y, w=620, h=420, depth=0.0, seed=4):
    """o prédio abandonado do IGR: concreto manchado, janelas sem vidro, parede meio demolida, mato"""
    rnd = random.Random(seed)
    base = P((0.70, 0.68, 0.64), depth)
    top = y - h
    # silhueta com o canto direito demolido
    pg(c, [(x, y), (x, top), (x + w * 0.62, top), (x + w * 0.70, top + 60), (x + w * 0.78, top + 40),
           (x + w * 0.86, top + 140), (x + w, top + 170), (x + w, y)])
    rgb(c, base); c.fill()
    # manchas
    for _ in range(18):
        ellipse(c, x + rnd.uniform(0, w), top + rnd.uniform(20, h), rnd.uniform(10, 50), rnd.uniform(20, 70))
        rgb(c, dk(base, rnd.uniform(0.06, 0.16)), 0.6); c.fill()
    # laje
    c.rectangle(x - 10, top - 12, w * 0.62 + 10, 16); rgb(c, dk(base, 0.18)); c.fill()
    # janelas vazias (buracos escuros)
    for r in range(2):
        for k in range(4):
            wx = x + 50 + k * (w - 100) / 4
            wy = top + 70 + r * 160
            if wx > x + w * 0.80 and r == 0:
                continue
            c.rectangle(wx, wy, 80, 90); rgb(c, P((0.12, 0.11, 0.11), depth)); c.fill()
            if rnd.random() < 0.5:  # tábua pregada
                c.save(); c.translate(wx + 40, wy + 45); c.rotate(rnd.uniform(-0.4, 0.4))
                c.rectangle(-50, -8, 100, 16); rgb(c, P((0.48, 0.36, 0.24), depth)); c.fill(); c.restore()
    # porta escura
    c.rectangle(x + w * 0.42, y - 150, 110, 150); rgb(c, P((0.08, 0.08, 0.08), depth)); c.fill()
    # entulho e mato
    for _ in range(14):
        ex = x + rnd.uniform(-40, w + 40)
        pg(c, [(ex - 30, y), (ex - 8, y - rnd.uniform(14, 40)), (ex + 26, y)])
        rgb(c, P(rnd.choice([(0.58, 0.56, 0.52), (0.50, 0.40, 0.34)]), depth)); c.fill()
    for _ in range(30):
        mx = x + rnd.uniform(-60, w + 60)
        c.move_to(mx, y + 2); c.line_to(mx + rnd.uniform(-10, 10), y - rnd.uniform(14, 46))
        rgb(c, P((0.36, 0.48, 0.26), depth)); c.set_line_width(4); c.stroke()


def placa_texto(c, x, y, linhas, w=300, col=(0.92, 0.90, 0.84), tinta=(0.15, 0.15, 0.17), size=26, rot=-0.02):
    c.save(); c.translate(x, y); c.rotate(rot)
    h = 30 + len(linhas) * size * 1.25
    rr(c, -w / 2 + 5, 7, w, h, 4); rgb(c, (0, 0, 0), 0.3); c.fill()
    rr(c, -w / 2, 0, w, h, 4); rgb(c, P(col)); c.fill()
    for i, s in enumerate(linhas):
        _t(c, s, 0, 24 + size + i * size * 1.25 - 6, size, P(tinta), font=SERIF, bold=True, centro=True)
    c.restore()


# ---------------------------------------------------------------- a máquina e a cápsula
def capsula(c, t, x, y, s=1.0, brilho=0.0, furada=False):
    """cápsula de aço (cilindro curto) com janela; brilho>0 acende o azul do césio"""
    if s <= 0.01:
        return
    c.save(); c.translate(x, y); c.scale(s, s)
    if brilho > 0:
        pulso = 1 + 0.08 * math.sin(t * 3.1)
        rglow(c, 0, 0, 260 * brilho * pulso, AZUL_CESIO, 0.55 * brilho)
        rglow(c, 0, 0, 110 * brilho, (0.75, 0.92, 1.0), 0.6 * brilho)
    rr(c, -46, -40, 92, 80, 14); rgb(c, P(ACO)); c.fill()
    rr(c, -46, -40, 92, 18, 9); rgb(c, P(lt(ACO, 0.2))); c.fill()
    c.rectangle(-46, 22, 92, 6); rgb(c, P(dk(ACO, 0.25))); c.fill()
    ellipse(c, 0, 0, 18, 18); rgb(c, P((0.30, 0.32, 0.36))); c.fill()
    if furada or brilho > 0:
        ellipse(c, 0, 0, 12, 12); rgb(c, (0.55, 0.85, 1.0) if brilho > 0 else P((0.1, 0.1, 0.1))); c.fill()
    c.restore()


def maquina_teleterapia(c, t, x, y, s=1.0, depth=0.0, desmontada=0.0):
    """aparelho de teleterapia: base, coluna, braço e a cabeça giratória blindada (com trevo)"""
    c.save(); c.translate(x, y); c.scale(s, s)
    corpo = P((0.82, 0.82, 0.78), depth)
    rr(c, -170, -60, 340, 60, 10); rgb(c, dk(corpo, 0.1)); c.fill()
    rr(c, -60, -360, 120, 310, 12); rgb(c, corpo); c.fill()
    rr(c, -60, -380, 300, 70, 14); rgb(c, corpo); c.fill()
    if True:
        c.save(); c.translate(200 + desmontada * 160, -300 + desmontada * 190); c.rotate(desmontada * 0.6)
        ellipse(c, 0, 0, 110, 110); rgb(c, P(CHUMBO, depth)); c.fill()
        ellipse(c, 0, 0, 82, 82); rgb(c, P(lt(CHUMBO, 0.15), depth)); c.fill()
        trevo(c, 0, 0, 34, P((0.95, 0.80, 0.10), depth), P((0.12, 0.12, 0.12), depth))
        c.restore()
    # mesa do paciente
    rr(c, -320, -180, 200, 24, 8); rgb(c, dk(corpo, 0.05)); c.fill()
    c.rectangle(-240, -156, 20, 100); rgb(c, dk(corpo, 0.2)); c.fill()
    c.restore()


def trevo(c, x, y, r, amarelo=(0.98, 0.82, 0.10), preto=(0.10, 0.10, 0.10), fundo=True):
    """símbolo internacional de radiação (trevo de três pás)"""
    if r <= 0.5:
        return
    c.save(); c.translate(x, y)
    if fundo:
        c.arc(0, 0, r * 1.15, 0, 6.283); rgb(c, amarelo); c.fill()
    for k in range(3):
        a0 = -math.pi / 2 + k * 2 * math.pi / 3 - math.pi / 6
        c.move_to(0, 0); c.arc(0, 0, r, a0, a0 + math.pi / 3); c.close_path()
        c.new_sub_path(); c.arc(0, 0, r * 0.28, 0, 6.283)
        rgb(c, preto); c.fill()
    c.arc(0, 0, r * 0.18, 0, 6.283); rgb(c, preto); c.fill()
    c.arc(0, 0, r * 0.28, 0, 6.283); c.set_line_width(r * 0.07); rgb(c, amarelo); c.stroke()
    c.restore()


def simbolo_iso(c, x, y, s=1.0, a=1.0):
    """símbolo complementar (ISO 21482, 2007): triângulo vermelho com ondas, caveira e pessoa correndo"""
    if s <= 0.01:
        return
    c.save(); c.translate(x, y); c.scale(s, s)
    pg(c, [(0, -170), (190, 150), (-190, 150)]); rgb(c, (0.98, 0.96, 0.92), a); c.fill()
    pg(c, [(0, -170), (190, 150), (-190, 150)]); c.set_line_width(22); rgb(c, ALERTA, a); c.set_line_join(1); c.stroke()
    # trevo pequeno com ondas
    trevo(c, 0, -60, 26, (0.98, 0.96, 0.92), (0.1, 0.1, 0.1), fundo=False)
    for k in range(3):
        c.arc(0, -60, 40 + k * 14, math.pi * 0.2, math.pi * 0.8); c.set_line_width(5); rgb(c, (0.1, 0.1, 0.1), a); c.stroke()
    # caveira
    ellipse(c, -50, 60, 30, 30); rgb(c, (0.1, 0.1, 0.1), a); c.fill()
    c.rectangle(-64, 82, 28, 16); c.fill()
    ellipse(c, -60, 56, 7, 8); ellipse(c, -40, 56, 7, 8); rgb(c, (0.98, 0.96, 0.92), a); c.fill()
    # pessoa correndo
    c.arc(70, 20, 12, 0, 6.283); rgb(c, (0.1, 0.1, 0.1), a); c.fill()
    c.set_line_width(10); c.set_line_cap(1)
    c.move_to(66, 36); c.line_to(54, 80); c.move_to(54, 80); c.line_to(78, 116); c.move_to(54, 80); c.line_to(30, 104)
    c.move_to(62, 50); c.line_to(90, 64); c.move_to(62, 50); c.line_to(40, 50); c.stroke()
    c.restore()


def carrinho_mao(c, x, y, s=1.0, carga=True, depth=0.0):
    c.save(); c.translate(x, y); c.scale(s, s)
    ellipse(c, 70, -30, 32, 32); rgb(c, P((0.14, 0.14, 0.15), depth)); c.fill()
    ellipse(c, 70, -30, 12, 12); rgb(c, P((0.5, 0.5, 0.52), depth)); c.fill()
    pg(c, [(-120, -110), (90, -110), (60, -50), (-90, -50)]); rgb(c, P((0.36, 0.48, 0.30), depth)); c.fill()
    c.move_to(-90, -60); c.line_to(-190, -30); c.move_to(-90, -100); c.line_to(-200, -70)
    rgb(c, P((0.46, 0.34, 0.22), depth)); c.set_line_width(8); c.stroke()
    c.move_to(-80, -50); c.line_to(-90, 0); rgb(c, P((0.3, 0.3, 0.32), depth)); c.set_line_width(7); c.stroke()
    if carga:
        ellipse(c, -10, -126, 70, 40); rgb(c, P(CHUMBO, depth)); c.fill()
        ellipse(c, -10, -126, 40, 24); rgb(c, P(lt(CHUMBO, 0.15), depth)); c.fill()
    c.restore()


def sucata(c, x, y, w=600, seed=5, depth=0.0):
    """monte de sucata de ferro-velho"""
    rnd = random.Random(seed)
    cores = [(0.52, 0.36, 0.26), (0.46, 0.46, 0.48), (0.60, 0.50, 0.38), (0.38, 0.34, 0.32), (0.66, 0.60, 0.52)]
    for i in range(46):
        px = x + rnd.uniform(0, w); hh = (1 - abs(px - x - w / 2) / (w / 2)) * 200 + 20
        py = y - rnd.uniform(0, hh)
        c.save(); c.translate(px, py); c.rotate(rnd.uniform(-1, 1))
        kind = rnd.random()
        col = P(rnd.choice(cores), depth)
        if kind < 0.4:
            c.rectangle(-rnd.uniform(20, 60), -10, rnd.uniform(40, 120), rnd.uniform(14, 30))
        elif kind < 0.7:
            ellipse(c, 0, 0, rnd.uniform(16, 40), rnd.uniform(16, 40))
        else:
            c.rectangle(-70, -4, 140, 8)
        rgb(c, col); c.fill(); c.restore()


def cena_ferro_velho(c, t, hora="tarde", seed=41, portao=True):
    luz(hora)
    ceu(c, t, seed=seed, passaros=False)
    casario(c, t, 860, "colonial", seed=seed, h=(200, 280), w=(220, 300), depth=0.45)
    chao(c, t, 880, "terra", seed=seed)
    sucata(c, 1250, 900, 380, seed=seed)
    sucata(c, 60, 900, 380, seed=seed + 1, depth=0.1)
    if portao:
        c.rectangle(1640, 620, 12, 280); c.rectangle(1840, 620, 12, 280); rgb(c, P((0.3, 0.3, 0.32))); c.fill()
        placa_texto(c, 1746, 540, ["FERRO-VELHO", "COMPRA-SE SUCATA"], w=320, size=24)


def casa_simples(c, x, y, w=420, h=260, col=(0.86, 0.80, 0.64), depth=0.0, porta=True, acesa=False):
    base = P(col, depth)
    pg(c, [(x - 20, y - h), (x + w / 2, y - h - 110), (x + w + 20, y - h)]); rgb(c, P(TELHA, depth)); c.fill()
    c.rectangle(x, y - h, w, h); rgb(c, base); c.fill()
    c.rectangle(x, y - 40, w, 40); rgb(c, dk(base, 0.12)); c.fill()
    janela_i(c, x + 50, y - h + 70, 100, 90, acesa=acesa, depth=depth)
    if porta:
        c.rectangle(x + w - 150, y - 170, 90, 170); rgb(c, P((0.42, 0.28, 0.18), depth)); c.fill()


def interior_casa(c, t, hora="noite"):
    """sala/cozinha simples (luz de lâmpada)"""
    luz(hora)
    c.rectangle(0, 0, 1920, 1080); rgb(c, P((0.78, 0.70, 0.56))); c.fill()
    c.rectangle(0, 0, 1920, 120); rgb(c, P((0.70, 0.62, 0.50))); c.fill()
    c.rectangle(0, 820, 1920, 260); rgb(c, P((0.62, 0.50, 0.40))); c.fill()
    for k in range(0, 1920, 120):
        c.rectangle(k, 820, 3, 260); rgb(c, P((0.52, 0.42, 0.34))); c.fill()
    # lâmpada pendurada
    c.move_to(1300, 0); c.line_to(1300, 200); rgb(c, P((0.2, 0.2, 0.2))); c.set_line_width(3); c.stroke()
    ellipse(c, 1300, 214, 22, 26); rgb(c, (1.0, 0.92, 0.70)); c.fill()
    rglow(c, 1300, 230, 520, (1.0, 0.86, 0.55), 0.25)


def mesa_cozinha(c, x, y, w=520):
    c.rectangle(x - w / 2, y - 20, w, 24); rgb(c, P((0.58, 0.40, 0.26))); c.fill()
    for dx in (-w / 2 + 20, w / 2 - 40):
        c.rectangle(x + dx, y + 4, 20, 150); rgb(c, P((0.48, 0.32, 0.20))); c.fill()


def po_brilhante(c, t, x, y, w=160, n=40, seed=3, a=1.0):
    """pozinho azul espalhado (chão, mesa, mãos)"""
    rnd = random.Random(seed)
    rglow(c, x, y, w * 1.2, AZUL_CESIO, 0.25 * a)
    for i in range(n):
        px = x + rnd.gauss(0, w / 3); py = y + rnd.gauss(0, w / 10)
        tw = 0.6 + 0.4 * math.sin(t * 4 + i)
        c.arc(px, py, rnd.uniform(2, 5), 0, 6.283); rgb(c, (0.6, 0.88, 1.0), a * tw); c.fill()


# ---------------------------------------------------------------- cidade, transporte, instituições
def onibus(c, t, x, y, s=1.0, depth=0.0, col=(0.86, 0.66, 0.16)):
    """ônibus urbano dos anos 80, de perfil (frente para a direita)"""
    c.save(); c.translate(x, y); c.scale(s, s)
    base = P(col, depth)
    rr(c, -380, -250, 760, 210, 22); rgb(c, base); c.fill()
    c.rectangle(-380, -120, 760, 26); rgb(c, P((0.92, 0.92, 0.90), depth)); c.fill()
    for k in range(7):
        rr(c, -350 + k * 96, -232, 80, 80, 6); rgb(c, P((0.30, 0.42, 0.50), depth)); c.fill()
    rr(c, 300, -232, 60, 120, 6); rgb(c, P((0.30, 0.42, 0.50), depth)); c.fill()
    for wx in (-250, 230):
        ellipse(c, wx, -40, 52, 52); rgb(c, P((0.12, 0.12, 0.13), depth)); c.fill()
        ellipse(c, wx, -40, 22, 22); rgb(c, P((0.6, 0.6, 0.62), depth)); c.fill()
    c.restore()


def medidor(c, t, x, y, s=1.0, nivel=0.0, depth=0.0):
    """medidor de radiação portátil com ponteiro; nivel 0..1 (1 = fundo de escala, tremendo)"""
    c.save(); c.translate(x, y); c.scale(s, s)
    rr(c, -110, -80, 220, 160, 16); rgb(c, P((0.86, 0.72, 0.20), depth)); c.fill()
    rr(c, -90, -64, 180, 96, 8); rgb(c, P((0.96, 0.94, 0.86), depth)); c.fill()
    c.arc(0, 26, 72, math.pi * 1.15, math.pi * 1.85); c.set_line_width(4); rgb(c, P((0.2, 0.2, 0.2), depth)); c.stroke()
    c.arc(0, 26, 72, math.pi * 1.65, math.pi * 1.85); c.set_line_width(8); rgb(c, ALERTA); c.stroke()
    jit = 0.05 * math.sin(t * 37) * nivel if nivel > 0.9 else 0
    ang = math.pi * (1.15 + 0.70 * min(1.0, nivel)) + jit
    c.move_to(0, 26); c.line_to(70 * math.cos(ang), 26 + 70 * math.sin(ang)); c.set_line_width(4); rgb(c, (0.1, 0.1, 0.1)); c.stroke()
    c.rectangle(-40, 80, 80, 40); rgb(c, P((0.2, 0.2, 0.22), depth)); c.fill()
    c.restore()


def predio_orgao(c, x, y, w=560, h=300, nome="VIGILÂNCIA SANITÁRIA", depth=0.0, cruz=False):
    base = P((0.88, 0.86, 0.80), depth)
    c.rectangle(x, y - h, w, h); rgb(c, base); c.fill()
    c.rectangle(x - 10, y - h - 14, w + 20, 18); rgb(c, dk(base, 0.15)); c.fill()
    for k in range(5):
        janela_i(c, x + 30 + k * (w - 60) / 5, y - h + 60, 70, 80, depth=depth)
    c.rectangle(x + w / 2 - 50, y - 130, 100, 130); rgb(c, P((0.3, 0.36, 0.42), depth)); c.fill()
    if nome:
        _t(c, nome, x + w / 2, y - h - 30, 26, P((0.15, 0.17, 0.2), depth), font=SERIF, bold=True, centro=True)
    if cruz:
        c.rectangle(x + w - 90, y - h + 20, 60, 20); c.rectangle(x + w - 70, y - h, 20, 60); rgb(c, ALERTA); c.fill()


def estadio(c, t, x, y, w=1300, depth=0.2, gente=0):
    """arquibancada vista de longe, com refletores"""
    base = P((0.66, 0.66, 0.68), depth)
    pg(c, [(x, y), (x + 80, y - 260), (x + w - 80, y - 260), (x + w, y)]); rgb(c, base); c.fill()
    for k in range(8):
        yy = y - 30 - k * 28
        c.rectangle(x + 30 + k * 7, yy, w - 60 - k * 14, 6); rgb(c, dk(base, 0.18)); c.fill()
    for px in (x + 60, x + w - 60):
        c.rectangle(px - 6, y - 480, 12, 230); rgb(c, P((0.4, 0.4, 0.42), depth)); c.fill()
        rr(c, px - 46, y - 520, 92, 50, 6); rgb(c, P((0.3, 0.3, 0.32), depth)); c.fill()
        rglow(c, px, y - 495, 160, (1, 0.96, 0.8), 0.35 if __import__("ilustrado")._L.get("noite") else 0.1)


def fila_gente(c, t, x0, x1, y, n=14, s=0.42, seed=8, figs=("moderno", "moderna")):
    rnd = random.Random(seed)
    for i in range(n):
        f = dict(FIGURINO[rnd.choice(figs)])
        f["pele"] = rnd.choice(list(PELES)); f["cor_roupa"] = rnd.choice([(0.55, 0.30, 0.26), (0.30, 0.42, 0.58), (0.40, 0.52, 0.40), (0.70, 0.62, 0.40), (0.50, 0.40, 0.56)])
        if f.get("mulher"):
            f["camisa"] = f["cor_roupa"]
        boneco(c, t, x0 + (x1 - x0) * i / max(1, n - 1) + rnd.uniform(-10, 10), y + rnd.uniform(-6, 6), s * rnd.uniform(0.92, 1.08),
               look=rnd.uniform(-0.6, 0.6), fid=40 + i, **f)


def helicoptero(c, t, x, y, s=1.0, depth=0.3):
    c.save(); c.translate(x, y); c.scale(s, s)
    col = P((0.30, 0.38, 0.30), depth)
    ellipse(c, 0, 0, 120, 60); rgb(c, col); c.fill()
    c.rectangle(100, -14, 200, 22); c.fill()
    ellipse(c, 40, -6, 50, 34); rgb(c, P((0.6, 0.78, 0.86), depth)); c.fill()
    k = abs(math.sin(t * 30))
    c.rectangle(-220 * k, -78, 440 * k, 8); rgb(c, P((0.2, 0.2, 0.2), depth), 0.8); c.fill()
    c.rectangle(-6, -78, 12, 20); c.fill()
    c.move_to(-60, 64); c.line_to(60, 64); c.set_line_width(6); c.stroke()
    c.restore()


def conteiner(c, x, y, w=220, h=170, depth=0.0, trevo_on=True):
    base = P((0.70, 0.70, 0.68), depth)
    c.rectangle(x, y - h, w, h); rgb(c, base); c.fill()
    for k in range(1, 4):
        c.rectangle(x + k * w / 4 - 3, y - h, 6, h); rgb(c, dk(base, 0.12)); c.fill()
    if trevo_on:
        trevo(c, x + w / 2, y - h / 2, 32)


# ---------------------------------------------------------------- peças de laudo (diagramas)
def painel_laudo(c, x, y, w, h, titulo=None, a=1.0):
    """quadro técnico: fundo ardósia com grade fina, borda creme e etiqueta"""
    c.save()
    rr(c, x + 8, y + 10, w, h, 14); rgb(c, (0, 0, 0), 0.35 * a); c.fill()
    rr(c, x, y, w, h, 14); rgb(c, LAUDO_BG, 0.96 * a); c.fill()
    c.save(); rr(c, x, y, w, h, 14); c.clip()
    for gx in range(int(x), int(x + w), 40):
        c.rectangle(gx, y, 1, h)
    for gy in range(int(y), int(y + h), 40):
        c.rectangle(x, gy, w, 1)
    rgb(c, LAUDO_GRADE, 0.6 * a); c.fill(); c.restore()
    rr(c, x, y, w, h, 14); c.set_line_width(3); rgb(c, CREME, 0.8 * a); c.stroke()
    if titulo:
        _bold(c, SERIF); c.set_font_size(30)
        tw = c.text_extents(titulo).x_advance
        rr(c, x + 30, y - 22, tw + 40, 44, 6); rgb(c, AMBER, a); c.fill()
        c.move_to(x + 50, y + 11); rgb(c, (0.1, 0.1, 0.12), a); c.show_text(titulo)
    c.restore()


def seta(c, x0, y0, x1, y1, p=1.0, col=CREME, w=5):
    xe, ye = x0 + (x1 - x0) * p, y0 + (y1 - y0) * p
    c.move_to(x0, y0); c.line_to(xe, ye); c.set_line_width(w); rgb(c, col); c.stroke()
    if p > 0.95:
        a = math.atan2(y1 - y0, x1 - x0)
        pg(c, [(x1, y1), (x1 - 22 * math.cos(a - 0.4), y1 - 22 * math.sin(a - 0.4)),
               (x1 - 22 * math.cos(a + 0.4), y1 - 22 * math.sin(a + 0.4))]); rgb(c, col); c.fill()


def diagrama_cabeca(c, t, t0, x=960, y=540, s=1.0, girada=0.0, mostrar_furo=False):
    """corte da cabeça giratória: blindagem de chumbo, tambor que gira, cápsula, janela de saída do feixe"""
    c.save(); c.translate(x, y); c.scale(s, s)
    p = max(0.02, ease_out(prog(t, t0, 0.8)))
    ellipse(c, 0, 0, 260 * p, 260 * p); rgb(c, CHUMBO); c.fill()
    ellipse(c, 0, 0, 252 * p, 252 * p); rgb(c, (0.48, 0.50, 0.55)); c.fill()
    # janela (abertura para baixo)
    c.rectangle(-30, 120, 60, 150); rgb(c, LAUDO_BG); c.fill()
    # tambor girando
    c.save(); c.rotate(girada * math.pi)
    ellipse(c, 0, 0, 120, 120); rgb(c, (0.62, 0.64, 0.68)); c.fill()
    c.rectangle(-26, -10, 52, 140); rgb(c, (0.38, 0.40, 0.44)); c.fill()
    capsula(c, t, 0, -40, 0.55, brilho=0.0, furada=mostrar_furo)
    c.restore()
    if girada > 0.95:  # feixe saindo
        pg(c, [(-26, 120), (26, 120), (90, 420), (-90, 420)]); rgb(c, AZUL_CESIO, 0.25 + 0.1 * math.sin(t * 6)); c.fill()
    c.restore()
    if t > t0 + 0.8:
        a = ease_out(prog(t, t0 + 0.8, 0.5))
        _t(c, "BLINDAGEM DE CHUMBO", x + 290 * s, y - 180 * s, 30, CREME, a=a)
        seta(c, x + 280 * s, y - 190 * s, x + 200 * s, y - 150 * s, a)
        _t(c, "CÁPSULA DE CÉSIO-137", x + 290 * s, y - 20 * s, 30, AMBER, a=a)
        seta(c, x + 280 * s, y - 30 * s, x + 50 * s, y - 40 * s, a, AMBER)
        _t(c, "JANELA DO FEIXE", x + 290 * s, y + 200 * s, 30, CREME, a=a)
        seta(c, x + 280 * s, y + 190 * s, x + 40 * s, y + 180 * s, a)


# mapa esquemático de Goiânia (não é em escala: só as posições relativas da história)
LOCAIS = {
    "igr": (560, 430, "IGR (abandonado)"),
    "roberto": (700, 560, "casa de Roberto"),
    "devair": (900, 640, "ferro-velho de Devair"),
    "ivo": (1080, 560, "casa de Ivo"),
    "j": (1260, 720, "3º ferro-velho"),
    "visa": (1380, 420, "Vigilância Sanitária"),
    "estadio": (820, 300, "Estádio Olímpico"),
}


def mapa_goiania(c, t, t0, pontos=(), rota=(), p_rota=1.0, a=1.0, contaminado=()):
    """mapa ilustrativo: quadras, avenidas e os pontos da história; rota = lista de chaves em ordem"""
    painel_laudo(c, 260, 140, 1400, 800, "GOIÂNIA, 1987 · MAPA ILUSTRATIVO", a)
    c.save(); rr(c, 260, 140, 1400, 800, 14); c.clip()
    rnd = random.Random(7)
    for gx in range(300, 1660, 130):
        for gy in range(190, 940, 110):
            rr(c, gx + 8, gy + 8, 112, 92, 6); rgb(c, (0.16, 0.21, 0.27), a); c.fill()
    c.move_to(260, 520); c.line_to(1660, 470); c.set_line_width(14); rgb(c, (0.30, 0.36, 0.42), a); c.stroke()
    c.move_to(640, 140); c.line_to(700, 940); c.stroke()
    _t(c, "AV. PARANAÍBA", 300, 505, 20, (0.70, 0.74, 0.78), a=0.8 * a)
    c.restore()
    for k in contaminado:
        px, py, _ = LOCAIS[k]
        rglow(c, px, py, 120 + 10 * math.sin(t * 3), AZUL_CESIO, 0.35 * a)
    if len(rota) > 1:
        pts = [LOCAIS[k][:2] for k in rota]
        seg = (len(pts) - 1) * min(1.0, p_rota)
        for i in range(len(pts) - 1):
            f = max(0.0, min(1.0, seg - i))
            if f <= 0:
                break
            (x0, y0), (x1, y1) = pts[i], pts[i + 1]
            c.set_dash([16, 12]); seta(c, x0, y0, x1, y1, f, AMBER, 6); c.set_dash([])
    for i, k in enumerate(pontos):
        px, py, nome = LOCAIS[k]
        pp = ease_out_back(prog(t, t0 + i * 0.5, 0.4))
        if pp <= 0:
            continue
        c.arc(px, py, 16 * pp, 0, 6.283); rgb(c, ALERTA if k != "estadio" else AMBER, a); c.fill()
        c.arc(px, py, 7 * pp, 0, 6.283); rgb(c, CREME, a); c.fill()
        _t(c, nome, px + 26, py + 9, 26, CREME, a=a * min(1, pp))


def linha_tempo(c, t, t0, eventos, ativo=None, y=540, x0=220, x1=1700, titulo="SETEMBRO DE 1987"):
    """eventos = [(dia, rótulo), ...]; ativo = índice destacado"""
    painel_laudo(c, x0 - 60, y - 230, x1 - x0 + 120, 400, titulo)
    p = ease_out(prog(t, t0, 0.9))
    c.move_to(x0, y); c.line_to(x0 + (x1 - x0) * p, y); c.set_line_width(6); rgb(c, CREME); c.stroke()
    eventos = [e if len(e) == 3 else (e[0], e[1], str(e[0])) for e in eventos]
    d0, d1 = eventos[0][0], eventos[-1][0]
    for i, (dia, rot, topo) in enumerate(eventos):
        fx = x0 + (x1 - x0) * (dia - d0) / max(1, d1 - d0)
        pp = ease_out_back(prog(t, t0 + 0.3 + i * 0.35, 0.4))
        if pp <= 0:
            continue
        on = ativo is not None and i == ativo
        c.arc(fx, y, (22 if on else 14) * pp, 0, 6.283); rgb(c, ALERTA if on else AMBER); c.fill()
        _t(c, topo, fx, y - 40, 40 if on else 32, CREME, font=SERIF, bold=True, centro=True, a=min(1, pp))
        yy = y + 60 + (i % 2) * 44
        _t(c, rot, fx, yy, 22 if not on else 26, AMBER if on else CREME, centro=True, a=min(1, pp))


def corrente(c, t, t0, n_quebrado=None, rotulos=(), x=960, y=560, ativos=6):
    """corrente de 6 elos; os elos já explicados ficam vermelhos com rótulo"""
    n = 6
    gap = 250
    xs = [x + (i - (n - 1) / 2) * gap for i in range(n)]
    for i, xx in enumerate(xs):
        pp = ease_out_back(prog(t, t0 + i * 0.15, 0.45))
        if pp <= 0.01:
            continue
        on = i < ativos
        c.save(); c.translate(xx, y); c.scale(pp, pp)
        rr(c, -130, -70, 260, 140, 70); c.set_line_width(30)
        rgb(c, ALERTA if on else (0.55, 0.57, 0.6)); c.stroke()
        c.restore()
        _t(c, f"{i + 1}", xx, y + 14, 46, CREME if on else (0.75, 0.75, 0.78), font=SERIF, bold=True, centro=True, a=min(1, pp))
        if on and i < len(rotulos):
            for k, linha in enumerate(rotulos[i].split("|")):
                _t(c, linha, xx, y + 130 + k * 32, 26, CREME, centro=True, a=min(1, pp))


def contador(c, t, t0, valor, x, y, size=120, rot="", col=CREME, dur=1.4, fmt="{:,}", fundo=True):
    """número que sobe até o valor (com separador de milhar em ponto)"""
    if t < t0:
        return
    p = ease_out(prog(t, t0, dur))
    v = valor if valor < 10 else int(valor * p)
    s = fmt.format(v).replace(",", ".")
    if fundo:
        _bold(c, SERIF); c.set_font_size(size); w = c.text_extents(s).x_advance
        c.select_font_face(TYPE); c.set_font_size(size * 0.28); w = max(w, c.text_extents(rot).x_advance) if rot else w
        rr(c, x - w / 2 - 40, y - size * 0.95, w + 80, size * (1.25 + (0.45 if rot else 0)), 16)
        rgb(c, (0.06, 0.07, 0.09), 0.72 * min(1, p * 3)); c.fill()
    _t(c, s, x, y, size, col, font=SERIF, bold=True, centro=True)
    if rot:
        _t(c, rot, x, y + size * 0.55, size * 0.28, AMBER, centro=True)


def carimbo(c, t, t0, texto, x, y, size=70, col=ALERTA, rot=-0.12):
    if t < t0:
        return
    p = prog(t, t0, 0.25)
    sc = 1.6 - 0.6 * ease_out(p)
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(sc, sc)
    _bold(c, SERIF); c.set_font_size(size)
    w = c.text_extents(texto).x_advance
    rr(c, -w / 2 - 24, -size * 0.95, w + 48, size * 1.35, 8); c.set_line_width(7); rgb(c, col, 0.9 * min(1, p * 3)); c.stroke()
    c.move_to(-w / 2, size * 0.2); rgb(c, col, 0.9 * min(1, p * 3)); c.show_text(texto)
    c.restore()


def documento(c, x, y, titulo, linhas, s=1.0, carimbo_txt=None, rot=-0.03):
    """ofício/carta datilografada"""
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s)
    rr(c, -200 + 8, -260 + 10, 400, 520, 4); rgb(c, (0, 0, 0), 0.35); c.fill()
    rr(c, -200, -260, 400, 520, 4); rgb(c, P((0.96, 0.94, 0.88))); c.fill()
    _t(c, titulo, 0, -200, 26, P((0.15, 0.15, 0.18)), font=SERIF, bold=True, centro=True)
    for i, ln in enumerate(linhas):
        _t(c, ln, -170, -140 + i * 34, 21, P((0.25, 0.25, 0.28)))
    for i in range(len(linhas), 11):
        c.rectangle(-170, -150 + i * 34, 300 - (i % 3) * 40, 4); rgb(c, P((0.6, 0.6, 0.62))); c.fill()
    if carimbo_txt:
        c.save(); c.translate(60, 190); c.rotate(-0.2)
        _bold(c, SERIF); c.set_font_size(30); w = c.text_extents(carimbo_txt).x_advance
        rr(c, -w / 2 - 14, -34, w + 28, 46, 4); c.set_line_width(4); rgb(c, ALERTA, 0.85); c.stroke()
        c.move_to(-w / 2, 0); c.show_text(carimbo_txt); c.restore()
    c.restore()


def capitulo(c, t, t0, num, nome, d=3.0):
    """cartão de capítulo do canal: faixa escura, número âmbar, nome creme"""
    if t < t0 or t > t0 + d:
        return
    p = ease_out(prog(t, t0, 0.5)) * (1 - ease_out(prog(t, t0 + d - 0.5, 0.5)))
    c.rectangle(0, 400, 1920, 260); rgb(c, (0.05, 0.06, 0.08), 0.82 * p); c.fill()
    _t(c, f"CAPÍTULO {num}", 960, 485, 34, AMBER, font=SERIF, bold=True, centro=True, a=p)
    _t(c, nome, 960, 590, 86, CREME, font=SERIF, bold=True, centro=True, a=p)
