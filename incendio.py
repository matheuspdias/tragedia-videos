"""
Kit de INCÊNDIO URBANO do Tragédia Anunciada (arranha-céus, fumaça, chamas, bombeiros, cortes técnicos).
Usado no episódio do Edifício Joelma; serve também para Andraus, Gran Circo etc.
Tudo chapado, cores por P(cor, depth). Nada de corpos ou sangue: o peso vem do fogo, da fumaça e da escala.
"""
import math, random
import ilustrado
from engine import ease_out, ease_out_back, prog, rgb, ellipse, SERIF, TYPE, AMBER
from ilustrado import *
from ilustrado import _bold
from tragedia import _t, CREME, ALERTA, LAUDO_BG, painel_laudo, ACO, CHUMBO

FOGO1 = (1.00, 0.78, 0.22)
FOGO2 = (0.98, 0.42, 0.10)
FOGO3 = (0.80, 0.16, 0.06)
FUMACA = (0.16, 0.15, 0.15)
FUMACA_CLARA = (0.42, 0.40, 0.40)
FACHADA_JOELMA = (0.74, 0.64, 0.52)


# ---------------------------------------------------------------- fogo e fumaça
def chama(c, t, x, y, w=60, h=110, seed=0, a=1.0):
    """língua de fogo com base em (x, y), tremendo"""
    if h <= 1 or w <= 1 or a <= 0.01:
        return
    k = 1 + 0.18 * math.sin(t * 9 + seed * 1.7) * math.sin(t * 5.3 + seed)
    hh = h * k
    sway = 0.25 * w * math.sin(t * 4 + seed)
    for col, s in ((FOGO3, 1.0), (FOGO2, 0.78), (FOGO1, 0.5)):
        ww, hs = w * s, hh * s
        c.move_to(x - ww / 2, y)
        c.curve_to(x - ww / 2, y - hs * 0.5, x + sway - ww * 0.2, y - hs * 0.7, x + sway, y - hs)
        c.curve_to(x + sway + ww * 0.1, y - hs * 0.6, x + ww / 2, y - hs * 0.45, x + ww / 2, y)
        c.close_path(); rgb(c, col, a); c.fill()


def fumaca(c, t, x, y, w=160, h=600, a=0.85, seed=1, vento=60, col=FUMACA):
    """coluna de fumaça subindo de (x, y), alargando e indo com o vento"""
    if a <= 0.01 or h <= 1:
        return
    rnd = random.Random(seed)
    n = 16
    for i in range(n):
        ph = rnd.uniform(0, 1)
        f = ((t * 0.18 + ph + i / n) % 1.0)
        yy = y - f * h
        xx = x + f * f * vento * 3 + math.sin(t * 0.8 + i) * 18
        r = w * (0.35 + 0.9 * f)
        ellipse(c, xx, yy, r, r * 0.8)
        rgb(c, mix(col, (0.30, 0.29, 0.29), f * 0.6), a * (0.75 - 0.55 * f)); c.fill()


def ceu_fumaca(c, a=0.5):
    lgrad(c, 0, 0, 0, 700, [(0, (0.20, 0.18, 0.18), a), (1, (0.20, 0.18, 0.18), 0)])
    c.rectangle(0, 0, W, 700); c.fill()


def _brilho_fogo(c, x, y, r, a):
    rglow(c, x, y, r, FOGO2, a)


# ---------------------------------------------------------------- o arranha-céu
def arranha_ceu(c, t, x, y, w=380, andares=25, ha=26, fogo=None, col=FACHADA_JOELMA, depth=0.0,
                heliponto=False, telhado="telhas", gente_telhado=0, garagem=10, nome=None, seed=3, fumaca_on=True,
                janelas_gente=()):
    """
    prédio alto de frente, pés em (x, y) no centro da base.
    fogo(andar) -> 0..1 (intensidade das chamas naquele andar; andar 1 = térreo).
    garagem: andares baixos com faixas abertas (Joelma: garagem até o 10º).
    telhado: "telhas" (cobertura de madeira e amianto) ou "laje"; heliponto=True desenha o H.
    """
    x0 = x - w / 2
    top = y - andares * ha
    base = P(col, depth)
    c.rectangle(x0, top, w, andares * ha); rgb(c, base); c.fill()
    # sombra lateral
    c.rectangle(x0 + w - 26, top, 26, andares * ha); rgb(c, dk(base, 0.18)); c.fill()
    nj = 9
    for a_ in range(1, andares + 1):
        fy = y - a_ * ha
        if a_ <= garagem:
            c.rectangle(x0 + 14, fy + 7, w - 40, ha - 14); rgb(c, P((0.20, 0.20, 0.22), depth)); c.fill()
            continue
        # faixa do peitoril
        c.rectangle(x0, fy + ha - 6, w, 6); rgb(c, dk(base, 0.10)); c.fill()
        f = fogo(a_) if fogo else 0.0
        for k in range(nj):
            wx = x0 + 16 + k * (w - 42) / nj
            ww = (w - 42) / nj - 6
            fw = f * (0.35 + 0.65 * (((a_ * 7919 + k * 104729) % 97) / 96.0)) if f > 0.02 else 0.0
            if fw > 0.02:
                vid = mix((0.22, 0.20, 0.20), FOGO2, min(1, fw * 1.2))
                if fw > 0.75:
                    vid = mix(FOGO2, FOGO1, 0.5 + 0.5 * math.sin(t * 7 + k + a_))
            else:
                vid = P(mix(ilustrado._L["fora"], (0.2, 0.24, 0.3), 0.55), depth)
            c.rectangle(wx, fy + 5, ww, ha - 13); rgb(c, vid); c.fill()
        if f > 0.02:
            _brilho_fogo(c, x, fy + ha / 2, w * 0.7, 0.10 * f)
    # chamas saindo das janelas (por cima da fachada)
    if fogo:
        for a_ in range(garagem + 1, andares + 1):
            f = fogo(a_)
            if f > 0.35:
                fy = y - a_ * ha
                for k in range((a_ % 3), nj, 3):
                    wx = x0 + 16 + k * (w - 42) / nj + 8
                    chama(c, t, wx, fy + ha - 6, 26 * f, ha * 1.15 * f, seed=a_ * 7 + k, a=0.92)
    # cobertura
    if telhado == "telhas":
        pg(c, [(x0 - 8, top), (x0 + 30, top - 34), (x0 + w - 30, top - 34), (x0 + w + 8, top)])
        rgb(c, P((0.62, 0.60, 0.56), depth)); c.fill()
        for k in range(12):
            c.rectangle(x0 + 30 + k * (w - 60) / 12, top - 32, 3, 30); rgb(c, P((0.48, 0.46, 0.44), depth)); c.fill()
        c.rectangle(x - 50, top - 70, 100, 38); rgb(c, P(dk(col, 0.2), depth)); c.fill()  # casa de máquinas
    else:
        c.rectangle(x0 - 8, top - 12, w + 16, 14); rgb(c, dk(base, 0.25)); c.fill()
        c.rectangle(x - 50, top - 60, 100, 48); rgb(c, dk(base, 0.18)); c.fill()
    if heliponto:
        ellipse(c, x, top - 64, w * 0.42, 20); rgb(c, P((0.35, 0.36, 0.38), depth)); c.fill()
        c.rectangle(x - 20, top - 70, 40, 12); rgb(c, P((0.30, 0.30, 0.32), depth)); c.fill()
        _bold(c, SERIF); c.set_font_size(30); c.move_to(x - 11, top - 70); rgb(c, P((0.95, 0.85, 0.20), depth)); c.show_text("H")
    if gente_telhado:
        rnd = random.Random(seed + 9)
        for i in range(gente_telhado):
            gx = x0 + 30 + rnd.uniform(0, w - 60)
            ellipse(c, gx, top - 44 - rnd.uniform(0, 6), 5, 5); rgb(c, P((0.18, 0.16, 0.16), depth)); c.fill()
            c.rectangle(gx - 4, top - 40, 8, 10); c.fill()
    for (a_, k) in janelas_gente:
        fy = y - a_ * ha
        wx = x0 + 16 + k * (w - 42) / nj
        ellipse(c, wx + 12, fy + 10, 5, 5); rgb(c, P((0.12, 0.10, 0.10), depth)); c.fill()
    if nome:
        _t(c, nome, x, top - 110 if not heliponto else top - 120, 28, P((0.98, 0.95, 0.88)), font=SERIF, bold=True, centro=True)
    # fumaça das janelas em chamas
    if fogo and fumaca_on:
        quentes = [a_ for a_ in range(garagem + 1, andares + 1) if fogo(a_) > 0.25]
        if quentes:
            alto = max(quentes)
            inten = min(1.0, len(quentes) / 6)
            fumaca(c, t, x + w * 0.1, y - alto * ha, w * 0.35 * (0.6 + inten), 700, 0.85 * inten + 0.15, seed=seed, vento=50)
    return top


def fogo_subindo(t, t_ini, andar0=12, vel=1.2, max_andar=25, garagem=10):
    """função fogo(andar) para arranha_ceu: começa no andar0 em t_ini e sobe vel andares por segundo"""
    dt = t - t_ini

    def f(a):
        if dt <= 0 or a < andar0:
            return 0.0
        alcance = dt * vel
        d = a - andar0
        if d > alcance:
            return 0.0
        return min(1.0, (alcance - d) / 3 + 0.3)
    return f


# ---------------------------------------------------------------- corte técnico do prédio (paleta laudo)
def corte_predio(c, t, x=960, y=960, w=520, andares=25, ha=30, fogo=None, escada_fumaca=0.0, ate_andar_fumaca=25,
                 elevadores=True, destaque_escada=False, gente=(), seta_saida=0.0, bombeiro_ate=None, telhado_gente=0):
    """
    corte do prédio (andares como faixas), escada única no meio (poço creme), elevadores à direita.
    escada_fumaca 0..1 = quanto a fumaça tomou o poço da escada (sobe a partir do andar 12).
    gente = [(andar, dx), ...] pontos de pessoas.
    """
    x0 = x - w / 2
    top = y - andares * ha
    c.rectangle(x0, top, w, andares * ha); rgb(c, (0.16, 0.20, 0.26)); c.fill()
    for a_ in range(andares + 1):
        c.rectangle(x0, y - a_ * ha - 2, w, 4); rgb(c, (0.40, 0.46, 0.52)); c.fill()
    # fogo nos andares
    if fogo:
        for a_ in range(1, andares + 1):
            f = fogo(a_)
            if f > 0.02:
                c.rectangle(x0 + 4, y - a_ * ha + 2, w - 8, ha - 4); rgb(c, FOGO2, 0.25 + 0.5 * f); c.fill()
    # poço da escada no meio
    ex = x - 40
    c.rectangle(ex, top, 80, andares * ha); rgb(c, CREME if not destaque_escada else AMBER, 0.20 if not destaque_escada else 0.35); c.fill()
    for a_ in range(andares):
        yy = y - a_ * ha
        c.move_to(ex + 6, yy - 4); c.line_to(ex + 74, yy - ha + 6)
        rgb(c, CREME, 0.7); c.set_line_width(3); c.stroke()
    if escada_fumaca > 0:
        h_f = (ate_andar_fumaca - 12 + 1) * ha * min(1, escada_fumaca)
        yb = y - 11 * ha
        c.rectangle(ex, yb - h_f, 80, h_f); rgb(c, (0.08, 0.08, 0.08), 0.85); c.fill()
        for k in range(8):
            ph = (t * 0.6 + k / 8) % 1
            ellipse(c, ex + 40 + math.sin(t * 2 + k) * 14, yb - ph * h_f, 30, 22); rgb(c, (0.25, 0.24, 0.24), 0.6 * (1 - ph)); c.fill()
    # elevadores
    if elevadores:
        for k in range(2):
            c.rectangle(x0 + w - 110 + k * 50, top, 36, andares * ha); rgb(c, (0.30, 0.36, 0.44)); c.fill()
    # gente
    for (a_, dx) in gente:
        gx = x + dx; gy = y - (a_ - 1) * ha - 6
        ellipse(c, gx, gy - 16, 5, 5); rgb(c, CREME); c.fill()
        c.rectangle(gx - 4, gy - 11, 8, 11); c.fill()
    if telhado_gente:
        rnd = random.Random(5)
        for i in range(telhado_gente):
            gx = x0 + 20 + rnd.uniform(0, w - 40)
            ellipse(c, gx, top - 18, 5, 5); rgb(c, CREME); c.fill()
            c.rectangle(gx - 4, top - 13, 8, 11); c.fill()
    pg(c, [(x0 - 10, top), (x0 + 20, top - 26), (x0 + w - 20, top - 26), (x0 + w + 10, top)])
    rgb(c, (0.55, 0.57, 0.60)); c.fill()
    if seta_saida > 0:
        # setas vermelhas: caminho para baixo bloqueado
        p = ease_out(seta_saida)
        c.move_to(ex + 40, y - 13 * ha); c.line_to(ex + 40, y - 13 * ha + 60 * p)
        rgb(c, ALERTA); c.set_line_width(8); c.stroke()
        c.save(); c.translate(ex + 40, y - 11.5 * ha); c.set_line_width(10)
        c.move_to(-26 * p, -26 * p); c.line_to(26 * p, 26 * p); c.move_to(26 * p, -26 * p); c.line_to(-26 * p, 26 * p); c.stroke(); c.restore()
    if bombeiro_ate:
        c.rectangle(x0 - 60, y - bombeiro_ate * ha - 3, w + 120, 6); rgb(c, AMBER, 0.9); c.fill()
        _t(c, f"bombeiros: até o {bombeiro_ate}º", x0 + w + 70, y - bombeiro_ate * ha + 10, 26, AMBER)
    return top


def marca_andar(c, x, y, ha, andar, texto, lado=1, col=AMBER, w=520):
    yy = y - (andar - 0.5) * ha
    xa = x + lado * (w / 2 + 20)
    c.move_to(x + lado * w / 2, yy); c.line_to(xa + lado * 40, yy); rgb(c, col); c.set_line_width(3); c.stroke()
    if lado > 0:
        _t(c, texto, xa + 50, yy + 9, 26, col)
    else:
        c.select_font_face(TYPE); c.set_font_size(26); tw = c.text_extents(texto).x_advance
        _t(c, texto, xa - 50 - tw, yy + 9, 26, col)


# ---------------------------------------------------------------- escritório anos 70
def escritorio_70(c, t, fogo=0.0, fumaca_a=0.0, seed=4, divisorias=True, cortina=True, ar=True):
    """escritório de banco nos anos 70: divisórias de madeira, forro de placas, carpete, cortinas, mesas"""
    luz("interior")
    parede = P((0.86, 0.82, 0.72))
    c.rectangle(0, 0, W, H); rgb(c, parede); c.fill()
    # forro de placas
    c.rectangle(0, 0, W, 130); rgb(c, P((0.92, 0.90, 0.84))); c.fill()
    for gx in range(0, W, 120):
        c.rectangle(gx, 0, 3, 130); rgb(c, P((0.55, 0.42, 0.28))); c.fill()
    for gy in (40, 85, 128):
        c.rectangle(0, gy, W, 3); rgb(c, P((0.55, 0.42, 0.28))); c.fill()
    # janelas com cortina
    for jx in (1180, 1560):
        c.rectangle(jx, 200, 300, 420); rgb(c, P((0.62, 0.70, 0.76))); c.fill()
        for k in range(1, 3):
            c.rectangle(jx + k * 100, 200, 4, 420); rgb(c, P((0.40, 0.40, 0.42))); c.fill()
        if cortina:
            for side in (0, 1):
                cx = jx - 30 + side * 260
                for k in range(5):
                    c.rectangle(cx + k * 14, 180, 14, 470); rgb(c, P((0.80, 0.62, 0.36) if k % 2 else (0.74, 0.56, 0.30))); c.fill()
    # divisórias de madeira
    if divisorias:
        for dx in (80, 560):
            c.rectangle(dx, 330, 420, 520); rgb(c, P((0.58, 0.40, 0.24))); c.fill()
            for k in range(1, 4):
                c.rectangle(dx + k * 105, 330, 4, 520); rgb(c, P((0.46, 0.31, 0.18))); c.fill()
            c.rectangle(dx, 330, 420, 150); rgb(c, P((0.70, 0.80, 0.84)), 0.6); c.fill()
    # carpete
    c.rectangle(0, 850, W, H - 850); rgb(c, P((0.48, 0.30, 0.26))); c.fill()
    for k in range(0, W, 30):
        c.rectangle(k, 850, 2, H - 850); rgb(c, P((0.42, 0.26, 0.22))); c.fill()
    # mesas de madeira
    for mx in (300, 820):
        c.rectangle(mx - 160, 760, 320, 26); rgb(c, P((0.50, 0.34, 0.20))); c.fill()
        c.rectangle(mx - 150, 786, 20, 100); c.rectangle(mx + 130, 786, 20, 100); c.fill()
        c.rectangle(mx - 60, 720, 90, 40); rgb(c, P((0.86, 0.86, 0.82))); c.fill()  # máquina de escrever
    # ar-condicionado de janela
    if ar:
        ar_condicionado(c, t, 1330, 700, 1.0)
    if fogo > 0:
        rglow(c, 1330, 640, 700 * fogo, FOGO2, 0.45 * fogo)
        for k in range(int(8 * fogo) + 1):
            chama(c, t, 1100 + k * 90, 650 + (k % 2) * 30, 70 * fogo + 20, 260 * fogo, seed=k)
        if fogo > 0.5:
            for k in range(6):
                chama(c, t, 100 + k * 170, 480, 60, 180 * (fogo - 0.4), seed=20 + k)
    if fumaca_a > 0:
        lgrad(c, 0, 0, 0, 600, [(0, (0.10, 0.09, 0.09), fumaca_a), (1, (0.10, 0.09, 0.09), fumaca_a * 0.2)])
        c.rectangle(0, 0, W, 600); c.fill()


def ar_condicionado(c, t, x, y, s=1.0, faisca=0.0):
    """aparelho de ar-condicionado de janela, anos 70 (centro em x, y)"""
    c.save(); c.translate(x, y); c.scale(s, s)
    rr(c, -150, -90, 300, 180, 10); rgb(c, P((0.82, 0.80, 0.74))); c.fill()
    rr(c, -130, -70, 170, 140, 6); rgb(c, P((0.62, 0.60, 0.56))); c.fill()
    for k in range(9):
        c.rectangle(-122, -62 + k * 15, 154, 5); rgb(c, P((0.48, 0.46, 0.43))); c.fill()
    for k in range(2):
        ellipse(c, 95, -30 + k * 55, 16, 16); rgb(c, P((0.30, 0.30, 0.32))); c.fill()
    if faisca > 0:
        rnd = random.Random(int(t * 20))
        for i in range(int(10 * faisca)):
            ang = rnd.uniform(0, 6.28); r = rnd.uniform(20, 110) * faisca
            c.move_to(130, 70); c.line_to(130 + math.cos(ang) * r, 70 + math.sin(ang) * r)
            rgb(c, FOGO1); c.set_line_width(3); c.stroke()
        rglow(c, 130, 70, 120, FOGO1, 0.6 * faisca)
    c.restore()


def quadro_eletrico(c, t, x, y, desvio=0.0, faisca=0.0):
    """diagrama: quadro do andar com disjuntores; o fio do ar-condicionado passando POR FORA (desvio 0..1)"""
    painel_laudo(c, x - 520, y - 300, 1040, 560, "LIGAÇÃO DO AR-CONDICIONADO")
    # quadro
    rr(c, x - 420, y - 200, 260, 360, 10); rgb(c, (0.55, 0.58, 0.62)); c.fill()
    for k in range(6):
        rr(c, x - 390, y - 170 + k * 52, 200, 38, 4); rgb(c, (0.20, 0.22, 0.26)); c.fill()
        c.rectangle(x - 300, y - 164 + k * 52, 22, 26); rgb(c, CREME); c.fill()
    _t(c, "QUADRO DO 12º", x - 290, y + 200, 24, CREME, centro=True)
    # vaga do disjuntor que faltou
    rr(c, x - 390, y + 142 - 52, 200, 38, 4); rgb(c, ALERTA, 0.5); c.fill()
    _t(c, "?", x - 290, y + 120, 30, CREME, font=SERIF, bold=True, centro=True)
    # rede
    c.move_to(x - 520, y - 250); c.line_to(x - 290, y - 250); c.line_to(x - 290, y - 200)
    rgb(c, AMBER); c.set_line_width(6); c.stroke()
    # ar-condicionado
    c.save(); c.translate(x + 300, y); ar_condicionado(c, t, 0, 0, 0.9, faisca); c.restore()
    if desvio > 0:
        p = ease_out(desvio)
        pts = [(x - 290, y - 250), (x - 80, y - 250), (x - 80, y + 60), (x + 150, y + 60)]
        tot = sum(math.dist(pts[i], pts[i + 1]) for i in range(3))
        L = tot * p
        c.move_to(*pts[0])
        for i in range(3):
            d = math.dist(pts[i], pts[i + 1])
            if L >= d:
                c.line_to(*pts[i + 1]); L -= d
            else:
                fx = pts[i][0] + (pts[i + 1][0] - pts[i][0]) * L / d
                fy = pts[i][1] + (pts[i + 1][1] - pts[i][1]) * L / d
                c.line_to(fx, fy); break
        rgb(c, ALERTA); c.set_line_width(7); c.set_dash([18, 10]); c.stroke(); c.set_dash([])
        if p > 0.95:
            _t(c, "por fora do quadro", x - 60, y - 150, 30, ALERTA)
            _t(c, "sem proteção", x - 60, y + 110, 30, ALERTA)


# ---------------------------------------------------------------- bombeiros e rua
def caminhao_escada(c, t, x, y, s=1.0, ang=0.0, comp=1.0, depth=0.0):
    """caminhão de bombeiro com escada Magirus; ang em radianos (0 = deitada), comp = extensão (1 = ~560 px)"""
    c.save(); c.translate(x, y); c.scale(s, s)
    red = P((0.78, 0.14, 0.10), depth)
    rr(c, -300, -170, 600, 130, 14); rgb(c, red); c.fill()
    rr(c, 160, -230, 150, 110, 14); c.fill()
    rr(c, 190, -215, 90, 50, 6); rgb(c, P((0.55, 0.70, 0.80), depth)); c.fill()
    c.rectangle(-300, -60, 600, 16); rgb(c, P((0.86, 0.86, 0.84), depth)); c.fill()
    for wx in (-200, 200):
        ellipse(c, wx, -30, 46, 46); rgb(c, P((0.12, 0.12, 0.13), depth)); c.fill()
        ellipse(c, wx, -30, 18, 18); rgb(c, P((0.6, 0.6, 0.62), depth)); c.fill()
    # escada
    c.save(); c.translate(-180, -180); c.rotate(-ang)
    L = 560 * comp
    c.rectangle(0, -14, L, 6); c.rectangle(0, 8, L, 6); rgb(c, P((0.80, 0.80, 0.82), depth)); c.fill()
    k = 0
    while k * 30 < L:
        c.rectangle(k * 30, -10, 4, 22); c.fill(); k += 1
    c.restore()
    ellipse(c, -180, -180, 24, 24); rgb(c, P((0.3, 0.3, 0.32), depth)); c.fill()
    c.restore()


def multidao(c, t, y=1000, n=24, s=0.36, seed=3, x0=0, x1=1920, olhando_cima=True, cartaz=None):
    rnd = random.Random(seed)
    figs = ["moderno", "moderna", "policial", "moderno"]
    for i in range(n):
        f = dict(FIGURINO[rnd.choice(figs)])
        f["pele"] = rnd.choice(list(PELES))
        f["cor_roupa"] = rnd.choice([(0.55, 0.30, 0.26), (0.30, 0.42, 0.58), (0.40, 0.52, 0.40), (0.70, 0.62, 0.40), (0.50, 0.40, 0.56), (0.86, 0.84, 0.78)])
        if f.get("mulher"):
            f["camisa"] = f["cor_roupa"]
        pose = rnd.choice(["stand", "head", "point_ru", "think"]) if olhando_cima else "stand"
        boneco(c, t, x0 + (x1 - x0) * (i + 0.5) / n + rnd.uniform(-20, 20), y + rnd.uniform(-14, 14), s * rnd.uniform(0.9, 1.1),
               poses=((0, pose),), exprs=((0, rnd.choice(["worried", "shocked"])),), look=rnd.uniform(-0.3, 0.3), fid=60 + i, **f)
    if cartaz:
        cx = x0 + (x1 - x0) * 0.62
        c.rectangle(cx - 4, y - 330, 8, 160); rgb(c, P((0.45, 0.32, 0.20))); c.fill()
        rr(c, cx - 140, y - 420, 280, 110, 6); rgb(c, P((0.96, 0.94, 0.88))); c.fill()
        _t(c, cartaz, cx, y - 350, 52, P((0.70, 0.12, 0.10)), font=SERIF, bold=True, centro=True)


def rua_centro(c, t, hora="nublado", seed=7, chao_y=980):
    """centro de São Paulo, anos 70: prédios altos ao fundo, avenida na frente"""
    luz(hora)
    ceu(c, t, passaros=False, seed=seed)
    rnd = random.Random(seed)
    x = -60
    while x < 1980:
        w = rnd.uniform(180, 280); h = rnd.uniform(380, 720)
        predio(c, x, chao_y - 60, w, h, "moderno", seed=rnd.randint(1, 999), depth=0.6, telhado=False, porta=False)
        x += w + rnd.uniform(0, 30)
    c.rectangle(0, chao_y - 60, W, H); rgb(c, P((0.36, 0.36, 0.38))); c.fill()
    c.rectangle(0, chao_y - 60, W, 26); rgb(c, P((0.62, 0.60, 0.56))); c.fill()
    for k in range(0, W, 160):
        c.rectangle(k, chao_y + 40, 80, 8); rgb(c, P((0.90, 0.86, 0.60))); c.fill()


def chuva(c, t, a=0.35, n=120, seed=2):
    rnd = random.Random(seed)
    for i in range(n):
        x0, y0, sp = rnd.uniform(0, W + 200), rnd.uniform(0, H), rnd.uniform(900, 1300)
        y = (y0 + t * sp) % H; x = (x0 - (t * sp) * 0.15) % (W + 200)
        c.move_to(x, y); c.line_to(x - 6, y + 30); rgb(c, (0.80, 0.85, 0.92), a); c.set_line_width(2); c.stroke()


def tv_antiga(c, t, x, y, s=1.0, conteudo=None):
    """televisor dos anos 70 (centro da tela em x, y); conteudo(c, t) desenha na tela (área 520x380, origem no canto)"""
    c.save(); c.translate(x, y); c.scale(s, s)
    rr(c, -330, -260, 660, 520, 30); rgb(c, P((0.42, 0.28, 0.18))); c.fill()
    rr(c, -290, -220, 520, 400, 40); rgb(c, (0.06, 0.07, 0.08)); c.fill()
    if conteudo:
        c.save(); rr(c, -290, -220, 520, 400, 40); c.clip(); c.translate(-290, -220); conteudo(c, t); c.restore()
        rr(c, -290, -220, 520, 400, 40); rgb(c, (0.6, 0.7, 0.8), 0.08); c.fill()
        for k in range(0, 400, 6):
            c.rectangle(-290, -220 + k, 520, 2); rgb(c, (0, 0, 0), 0.12); c.fill()
    for k in range(2):
        ellipse(c, 285, -120 + k * 90, 20, 20); rgb(c, P((0.80, 0.74, 0.60))); c.fill()
    c.rectangle(-240, 260, 30, 60); c.rectangle(210, 260, 30, 60); rgb(c, P((0.30, 0.20, 0.14))); c.fill()
    c.move_to(-40, -260); c.line_to(-140, -400); c.move_to(40, -260); c.line_to(140, -400)
    rgb(c, P((0.6, 0.6, 0.62))); c.set_line_width(5); c.stroke()
    c.restore()


def ao_vivo(c, t, x, y):
    if int(t * 2) % 2 == 0:
        ellipse(c, x, y, 10, 10); rgb(c, ALERTA); c.fill()
    _t(c, "AO VIVO", x + 20, y + 9, 26, CREME, font=SERIF, bold=True)


def lista_nao_tinha(c, t, itens, x=1060, y=230, size=46, dy=96):
    """itens = [(t0, texto)]: cada item entra com um X vermelho"""
    for k, (tk, txt) in enumerate(itens):
        if t < tk:
            continue
        a = ease_out(prog(t, tk, 0.35))
        yy = y + k * dy
        rr(c, x - 20, yy - size, 760, size * 1.5, 10); rgb(c, (0.05, 0.06, 0.08), 0.7 * a); c.fill()
        c.save(); c.translate(x + 20, yy - size * 0.3); c.set_line_width(9); sc = ease_out_back(prog(t, tk + 0.1, 0.3))
        c.move_to(-18 * sc, -18 * sc); c.line_to(18 * sc, 18 * sc); c.move_to(18 * sc, -18 * sc); c.line_to(-18 * sc, 18 * sc)
        rgb(c, ALERTA); c.stroke(); c.restore()
        _t(c, txt, x + 70, yy, size, CREME, font=SERIF, bold=True, a=a)


def helicoptero_fumaca(c, t, x, y, s=1.0, tremor=1.0):
    hx = x + math.sin(t * 0.9) * 30 * tremor
    hy = y + math.sin(t * 1.7) * 12 * tremor
    from tragedia import helicoptero
    helicoptero(c, t, hx, hy, s)


def tumulos_sem_nome(c, t, n=13, y=900, seed=6):
    """fileira de covas simples sem nome (cemitério de dia, sem nada sombrio)"""
    rnd = random.Random(seed)
    for i in range(n):
        x = 160 + i * (1600 / (n - 1))
        yy = y + (i % 2) * 40
        c.rectangle(x - 46, yy - 20, 92, 30); rgb(c, P((0.58, 0.56, 0.52))); c.fill()
        c.rectangle(x - 6, yy - 120, 12, 100); c.rectangle(x - 34, yy - 96, 68, 12); rgb(c, P((0.72, 0.72, 0.70))); c.fill()
