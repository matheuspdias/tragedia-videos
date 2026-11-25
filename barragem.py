"""
Kit de BARRAGEM / MINERAÇÃO do Tragédia Anunciada (Mariana; serve para Brumadinho e outras barragens).
Chapado, cores por P(cor, depth). A lama é a "personagem": nada de corpos.
"""
import math, random
import ilustrado
from engine import ease_out, ease_out_back, prog, rgb, ellipse, SERIF, TYPE, AMBER
from ilustrado import *
from tragedia import _t, CREME, ALERTA, LAUDO_BG, painel_laudo, casa_simples

LAMA = (0.55, 0.30, 0.16)
LAMA_ESC = (0.40, 0.21, 0.11)
LAMA_CLARA = (0.70, 0.44, 0.26)
REJEITO = (0.62, 0.50, 0.38)
TERRA = (0.50, 0.40, 0.28)
VERDE = (0.36, 0.52, 0.30)
VERDE_ESC = (0.26, 0.40, 0.24)
AGUA = (0.36, 0.56, 0.70)


# ---------------------------------------------------------------- paisagem: vale de Minas
def morros(c, t, y=700, seed=3, depth=0.5, col=VERDE, n=6, amp=160):
    rnd = random.Random(seed)
    pts = [(-100, y)]
    for i in range(n + 1):
        x = -100 + i * (W + 200) / n
        pts.append((x, y - rnd.uniform(0.3, 1.0) * amp))
    pts.append((W + 100, y))
    c.move_to(-100, H)
    c.line_to(*pts[0])
    for i in range(1, len(pts)):
        x0, y0 = pts[i - 1]; x1, y1 = pts[i]
        c.curve_to((x0 + x1) / 2, y0, (x0 + x1) / 2, y1, x1, y1)
    c.line_to(W + 100, H); c.close_path()
    rgb(c, P(col, depth)); c.fill()


def vale(c, t, hora="dia", seed=5):
    luz(hora)
    ceu(c, t, passaros=hora == "dia", seed=seed)
    morros(c, t, 560, seed, 0.7, (0.46, 0.58, 0.44), 5, 200)
    morros(c, t, 700, seed + 1, 0.4, VERDE, 7, 150)


def rio(c, t, pts, w=40, col=AGUA, a=1.0):
    """rio como curva grossa passando pelos pontos"""
    if len(pts) < 2:
        return
    c.move_to(*pts[0])
    for i in range(1, len(pts)):
        x0, y0 = pts[i - 1]; x1, y1 = pts[i]
        c.curve_to((x0 + x1) / 2, y0, (x0 + x1) / 2, y1, x1, y1)
    rgb(c, P(col), a); c.set_line_width(w); c.stroke()


def vilarejo(c, t, x, y, s=1.0, n=7, seed=4, igreja=True, depth=0.0, soterrado=0.0, gente=False):
    """Bento Rodrigues: casas simples espalhadas, igreja branca. soterrado 0..1 cobre de lama de baixo pra cima"""
    c.save(); c.translate(x, y); c.scale(s, s)
    rnd = random.Random(seed)
    cores = [(0.92, 0.88, 0.78), (0.86, 0.72, 0.56), (0.80, 0.84, 0.88), (0.94, 0.82, 0.62), (0.88, 0.66, 0.58)]
    for i in range(n):
        hx = -520 + i * 1040 / max(1, n - 1) + rnd.uniform(-30, 30)
        hy = rnd.uniform(-30, 30)
        sc = 0.42 + rnd.uniform(-0.04, 0.06)
        c.save(); c.translate(hx, hy); c.scale(sc, sc)
        casa_simples(c, -210, 0, 420, 260, col=cores[i % len(cores)], depth=depth, porta=True)
        c.restore()
    if igreja:
        ix, iy = 40, -40
        c.rectangle(ix - 70, iy - 150, 140, 150); rgb(c, P((0.96, 0.95, 0.92), depth)); c.fill()
        pg(c, [(ix - 80, iy - 150), (ix, iy - 220), (ix + 80, iy - 150)]); rgb(c, P((0.70, 0.36, 0.24), depth)); c.fill()
        c.rectangle(ix - 20, iy - 280, 40, 70); rgb(c, P((0.96, 0.95, 0.92), depth)); c.fill()
        c.rectangle(ix - 3, iy - 320, 6, 40); c.rectangle(ix - 16, iy - 306, 32, 6); rgb(c, P((0.35, 0.30, 0.26), depth)); c.fill()
        rr(c, ix - 24, iy - 70, 48, 70, 20); rgb(c, P((0.45, 0.30, 0.20), depth)); c.fill()
    if gente:
        figurantes(c, t, 40, n=6, s=0.32, seed=seed, x0=-500, x1=500, andando=False, figurinos=["catador", "moderna", "moderno"])
    if soterrado > 0:
        h = 230 * soterrado
        c.move_to(-1000, 60)
        for k in range(0, 21):
            xx = -1000 + k * 100
            c.line_to(xx, 60 - h - 30 * math.sin(k * 1.9) * soterrado + 6 * math.sin(k * 1.3 + t * 2))
        c.line_to(1000, 60); c.line_to(1000, 300); c.line_to(-1000, 300); c.close_path()
        rgb(c, P(LAMA, depth)); c.fill()
    c.restore()


# ---------------------------------------------------------------- a barragem
def barragem_paisagem(c, t, x=960, y=640, w=1100, nivel=0.85, degraus=6, rompida=0.0, depth=0.2, vazamento=0.0, trinca=0.0):
    """barragem de rejeitos vista de frente/de cima: paredão em degraus + lago de lama atrás"""
    x0 = x - w / 2
    # lago de rejeito atrás
    c.save()
    ellipse(c, x, y - 120, w * 0.55, 120); rgb(c, P(REJEITO, depth)); c.fill()
    ellipse(c, x + 60, y - 140, w * 0.30, 60); rgb(c, P((0.56, 0.62, 0.64), depth), 0.6); c.fill()
    c.restore()
    # paredão em degraus
    alt = 36
    for k in range(degraus):
        yy = y - k * alt
        ins = k * 28
        if rompida > 0 and k >= 0:
            pass
        pg(c, [(x0 + ins, yy), (x0 + w - ins, yy), (x0 + w - ins - 16, yy - alt), (x0 + ins + 16, yy - alt)])
        rgb(c, P(mix(TERRA, (0.62, 0.55, 0.42), k / degraus), depth)); c.fill()
        c.rectangle(x0 + ins + 16, yy - alt, w - 2 * ins - 32, 5); rgb(c, P((0.40, 0.48, 0.30), depth)); c.fill()
    if vazamento > 0:
        for k in range(3):
            vx = x0 + w * (0.25 + 0.2 * k)
            c.move_to(vx, y - 60); c.curve_to(vx + 6, y - 30, vx - 6, y - 10, vx + 4, y + 30 * vazamento)
            rgb(c, P((0.48, 0.34, 0.22), depth), 0.9); c.set_line_width(8); c.stroke()
    if trinca > 0:
        c.move_to(x0 + w * 0.62, y - degraus * alt + 6)
        for k in range(6):
            c.line_to(x0 + w * 0.62 + (k % 2) * 22 - 10, y - degraus * alt + 6 + (k + 1) * 30 * trinca)
        rgb(c, P((0.12, 0.08, 0.06), depth)); c.set_line_width(5); c.stroke()
    if rompida > 0:
        # brecha em V no paredão + rio de lama descendo
        bx = x0 + w * 0.22
        p = min(1.0, rompida * 1.4)
        top = y - degraus * alt
        bt, bb = 200 * p, 70 * p
        pg(c, [(bx - bt / 2, top - 4), (bx + bt / 2, top - 4), (bx + bb / 2, y + 4), (bx - bb / 2, y + 4)])
        rgb(c, P(LAMA_ESC, depth)); c.fill()
        c.move_to(bx - bb / 2, y)
        c.curve_to(bx - 60 * p, y + 80, bx - 160 * p, y + 140, bx - 260 * p, y + 260 * p)
        c.line_to(bx + 220 * p, y + 260 * p)
        c.curve_to(bx + 120 * p, y + 140, bx + 50 * p, y + 80, bx + bb / 2, y)
        c.close_path(); rgb(c, P(LAMA, depth)); c.fill()
        for k in range(4):
            ph = (t * 0.8 + k / 4) % 1
            ellipse(c, bx + math.sin(k * 2.1) * 20 * p, top + (y + 200 - top) * ph, 16 * p + 4, 8); rgb(c, P(LAMA_CLARA, depth), 0.8); c.fill()
    return y - degraus * alt


def corte_barragem(c, t, x=960, y=880, s=1.0, degraus=0, dreno_ok=True, saturacao=0.0, recuo=0.0, liquefeita=0.0,
                   rotulos=False):
    """corte técnico (paleta laudo): dique de partida + degraus a montante apoiados no rejeito.
    degraus: quantos degraus já foram construídos (0..6, aceita fração). saturacao 0..1 pinta a água presa.
    recuo 0..1 desloca os degraus de cima para trás (sobre rejeito). liquefeita 0..1 derrete a estrutura."""
    c.save(); c.translate(x, y); c.scale(s, s)
    # chão
    c.rectangle(-900, 0, 1800, 120); rgb(c, (0.30, 0.26, 0.22)); c.fill()
    # rejeito (montante = esquerda)
    topo = 60 + 70 * max(1.0, degraus)
    pg(c, [(-880, 0), (200, 0), (60 - 0 * 1, -topo + 30), (-880, -topo + 30)])
    rgb(c, (0.58, 0.48, 0.36)); c.fill()
    # pontinhos de areia
    rnd = random.Random(3)
    for i in range(140):
        px, py = rnd.uniform(-860, 120), -rnd.uniform(4, topo - 34)
        ellipse(c, px, py, 3, 3); rgb(c, (0.68, 0.58, 0.44)); c.fill()
    # água presa (saturação)
    if saturacao > 0:
        hs = (topo - 40) * saturacao
        c.rectangle(-880, -hs, 1060, hs); rgb(c, (0.30, 0.50, 0.70), 0.45); c.fill()
        for k in range(10):
            ph = (t * 0.5 + k / 10) % 1
            ellipse(c, -800 + k * 95, -hs * ph, 6, 9); rgb(c, (0.55, 0.75, 0.95), 0.7); c.fill()
    # dique de partida (jusante, à direita)
    pg(c, [(60, 0), (520, 0), (330, -150), (220, -150)])
    rgb(c, (0.44, 0.40, 0.34)); c.fill()
    # dreno de fundo
    c.rectangle(-700, -10, 900, 10); rgb(c, (0.75, 0.75, 0.70) if dreno_ok else ALERTA); c.fill()
    if not dreno_ok:
        for k in range(5):
            c.move_to(-600 + k * 180, -12); c.line_to(-560 + k * 180, 4); c.move_to(-560 + k * 180, -12); c.line_to(-600 + k * 180, 4)
            rgb(c, (0.1, 0.1, 0.1)); c.set_line_width(4); c.stroke()
    # degraus a montante (cada um um pouco mais para a esquerda, em cima do rejeito)
    nfull = int(degraus); frac = degraus - nfull
    for k in range(nfull + (1 if frac > 0.02 else 0)):
        a = 1.0 if k < nfull else frac
        base = -150 - k * 70
        dx = -110 * (k + 1)
        if k >= 3:
            dx -= 160 * recuo
        p = ease_out(a)
        cx = 280 + dx
        derrete = liquefeita * (0.5 + 0.5 * (k / 6))
        yy = base + 120 * derrete
        pg(c, [(cx - 120, yy + 70 * p), (cx + 120, yy + 70 * p), (cx + 60, yy), (cx - 60, yy)])
        rgb(c, (0.50, 0.44, 0.36) if k < 3 else ((0.62, 0.40, 0.26) if recuo > 0.5 else (0.50, 0.44, 0.36)), 1 - 0.6 * liquefeita); c.fill()
    if liquefeita > 0:
        lx = 520 + 900 * ease_out(liquefeita)
        pg(c, [(-200, -120 * (1 - liquefeita)), (lx, 0), (lx, 0), (-200, 0)])
        rgb(c, LAMA, 0.95); c.fill()
    if rotulos:
        _t(c, "rejeito", -560, -topo + 80, 30, CREME, centro=True)
        _t(c, "dique de partida", 380, 40, 26, CREME, centro=True)
    c.restore()


def onda_lama(c, t, x_frente, y=900, h=260, depth=0.0, seed=2):
    """frente de lama avançando para a direita até x_frente"""
    if x_frente <= -50:
        return
    rnd = random.Random(seed)
    c.move_to(-60, y + 200)
    c.line_to(-60, y - h * 0.8)
    n = 14
    for k in range(n + 1):
        xx = -60 + (x_frente + 60) * k / n
        bump = math.sin(k * 1.7 + t * 3) * 16 + rnd.uniform(-8, 8)
        frente = (k / n) ** 3
        c.line_to(xx, y - h * (0.8 - 0.5 * frente) + bump)
    c.curve_to(x_frente + 60, y - h * 0.2, x_frente + 40, y + 40, x_frente - 40, y + 200)
    c.close_path(); rgb(c, P(LAMA, depth)); c.fill()
    for k in range(10):
        bx = x_frente - rnd.uniform(0, max(10, x_frente))
        ellipse(c, bx, y - h * 0.4 + rnd.uniform(-40, 60), rnd.uniform(18, 40), 10)
        rgb(c, P(LAMA_ESC, depth)); c.fill()
    # espuma/respingos na frente
    for k in range(6):
        ellipse(c, x_frente - 20 + math.sin(t * 6 + k) * 14, y - h * 0.25 - k * 18, 22, 14); rgb(c, P(LAMA_CLARA, depth)); c.fill()


def sirene(c, t, x, y, s=1.0, tocando=False, riscada=False):
    c.save(); c.translate(x, y); c.scale(s, s)
    c.rectangle(-8, -10, 16, 260); rgb(c, P((0.55, 0.56, 0.58))); c.fill()
    rr(c, -60, -90, 120, 80, 18); rgb(c, P((0.80, 0.80, 0.78))); c.fill()
    for k in (-1, 1):
        pg(c, [(k * 50, -80), (k * 110, -110), (k * 110, 10), (k * 50, -20)]); rgb(c, P((0.68, 0.68, 0.66))); c.fill()
    if tocando:
        for r in (140, 190, 240):
            c.arc(0, -50, r + 20 * math.sin(t * 6), -0.6, 0.6); rgb(c, AMBER, 0.6); c.set_line_width(6); c.stroke()
    if riscada:
        c.set_line_width(16)
        c.move_to(-170, -230); c.line_to(170, 200); rgb(c, ALERTA); c.stroke()
        c.arc(0, -20, 230, 0, 6.283); c.stroke()
    c.restore()


def telefone_antigo(c, t, x, y, s=1.0, tocando=False):
    c.save(); c.translate(x, y); c.scale(s, s)
    if tocando:
        c.translate(math.sin(t * 40) * 4, 0)
    rr(c, -110, -60, 220, 120, 26); rgb(c, P((0.22, 0.22, 0.24))); c.fill()
    rr(c, -140, -110, 280, 56, 28); c.fill()
    ellipse(c, 0, 0, 40, 40); rgb(c, P((0.85, 0.84, 0.80))); c.fill()
    c.restore()


def piscinas(c, t, t0, x=960, y=600, n_col=20, n_lin=8, total="15.000+"):
    """grade de mini piscinas olímpicas que vai se enchendo"""
    k_max = int(n_col * n_lin * ease_out(prog(t, t0, 2.5)))
    for k in range(k_max):
        i, j = k % n_col, k // n_col
        px = x - n_col * 42 / 2 + i * 42; py = y - n_lin * 26 / 2 + j * 26
        c.rectangle(px, py, 36, 20); rgb(c, (0.45, 0.70, 0.85)); c.fill()
        c.rectangle(px, py, 36, 20); rgb(c, CREME, 0.4); c.set_line_width(1.5); c.stroke()
    if k_max > 10:
        _t(c, f"{total} piscinas olímpicas", x, y + n_lin * 13 + 70, 46, CREME, font=SERIF, bold=True, centro=True)


def mapa_rio_doce(c, t, p=1.0, x=0, y=0):
    """mapa esquemático MG -> ES: Mariana, rio do Carmo/Gualaxo, Rio Doce, Regência (ES). p = avanço da lama 0..1"""
    c.save(); c.translate(x, y)
    c.rectangle(0, 0, W, H); rgb(c, (0.86, 0.84, 0.76)); c.fill()
    # mar
    pg(c, [(1640, 0), (W, 0), (W, H), (1560, H), (1600, 700), (1580, 400)]); rgb(c, (0.40, 0.62, 0.78)); c.fill()
    _t(c, "OCEANO ATLÂNTICO", 1760, 160, 26, (0.95, 0.98, 1.0), centro=True)
    # divisa MG/ES
    c.move_to(1180, 0); c.curve_to(1220, 300, 1150, 600, 1250, H); rgb(c, (0.55, 0.50, 0.42)); c.set_dash([14, 10]); c.set_line_width(3); c.stroke(); c.set_dash([])
    _t(c, "MINAS GERAIS", 560, 120, 44, (0.45, 0.40, 0.32), font=SERIF, bold=True, centro=True)
    _t(c, "ESPÍRITO SANTO", 1400, 120, 32, (0.45, 0.40, 0.32), font=SERIF, bold=True, centro=True)
    pts = [(260, 760), (420, 700), (560, 720), (720, 600), (900, 560), (1080, 480), (1260, 520), (1420, 460), (1590, 470)]
    rio(c, t, pts, 18, (0.42, 0.60, 0.74))
    # lama avançando
    if p > 0:
        L = int(1 + (len(pts) - 1) * min(1, p))
        sub = pts[:L]
        if L < len(pts):
            fr = (len(pts) - 1) * p - (L - 1)
            a, b = pts[L - 1], pts[L]
            sub = sub + [(a[0] + (b[0] - a[0]) * fr, a[1] + (b[1] - a[1]) * fr)]
        rio(c, t, sub, 24, LAMA)
        if p >= 1:
            ellipse(c, 1650, 470, 120 + 10 * math.sin(t * 2), 90); rgb(c, LAMA, 0.55); c.fill()
    for (px, py, nome) in ((260, 760, "Mariana · Bento Rodrigues"), (1590, 470, "Regência (ES)")):
        ellipse(c, px, py, 12, 12); rgb(c, ALERTA); c.fill()
        _t(c, nome, px + (20 if px < 1000 else -20), py + 50, 28, (0.25, 0.22, 0.18), centro=px > 1000)
    _t(c, "Rio Doce", 980, 620, 30, (0.25, 0.40, 0.55), font=SERIF, bold=True)
    c.restore()


def tribunal(c, t, x=960, y=600, s=1.0, texto=None):
    """fachada de tribunal clássico (colunas) com placa"""
    c.save(); c.translate(x, y); c.scale(s, s)
    pg(c, [(-420, -300), (0, -440), (420, -300)]); rgb(c, P((0.86, 0.84, 0.80))); c.fill()
    c.rectangle(-440, -300, 880, 40); c.fill()
    for k in range(6):
        c.rectangle(-380 + k * 150, -260, 60, 360); rgb(c, P((0.92, 0.90, 0.86))); c.fill()
    c.rectangle(-460, 100, 920, 40); rgb(c, P((0.80, 0.78, 0.74))); c.fill()
    if texto:
        _t(c, texto, 0, -320, 34, P((0.30, 0.28, 0.26)), font=SERIF, bold=True, centro=True)
    c.restore()
