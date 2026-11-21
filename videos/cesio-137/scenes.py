"""TRAGÉDIA ANUNCIADA · Césio-137, Goiânia (1987). Cenas ancoradas nas palavras da narração (palavras.json)."""
import json, os, re, unicodedata
from engine import *
from ilustrado import *
from tragedia import *
from tragedia import _t

STYLE = "ilustrado"
TOM = "normal"
THEME = "cidade"
SFX_OFF = True
AMBIENCE = None  # sem cama de vento/grave: o Matheus ouviu como ruído de fundo

_DIR = os.path.dirname(os.path.abspath(__file__))
PAL = json.load(open(os.path.join(_DIR, "palavras.json")))


def _n(s):
    s = s.lower().replace("-", " ")
    s = re.sub(r"[^\w\s]", " ", s)
    return s.split()


TOK = [(_n(p["w"]) or [""])[0] for p in PAL]


def _acha(frase, ini=0):
    alvo = _n(frase)
    for i in range(ini, len(TOK) - len(alvo) + 1):
        if TOK[i:i + len(alvo)] == alvo:
            return i
    raise ValueError(f"frase não encontrada: {frase!r} (a partir de {ini})")


class Cena:
    def __init__(self, i):
        self.i = i
        self.t0 = max(0.0, PAL[i]["t"] - 0.12)

    def w(self, frase):
        """tempo da frase dentro desta cena"""
        return PAL[_acha(frase, self.i)]["t"]


_REG = []


def cena(ancora):
    def deco(fn):
        _REG.append((ancora, fn))
        return fn
    return deco


# ---------------------------------------------------------------- personagens da história
ROBERTO = dict(FIGURINO["catador"], pele="morena", cor_roupa=(0.62, 0.52, 0.36))
WAGNER = dict(FIGURINO["catador"], pele="media", chapeu=None, cor_roupa=(0.42, 0.50, 0.58), cabelo="cacheado")
DEVAIR = dict(FIGURINO["moderno"], pele="media", bigode=True, cor_roupa=(0.70, 0.62, 0.42))
GABRIELA = dict(roupa="vestido", cor_roupa=(0.62, 0.32, 0.36), avental=False, cinto=(0.35, 0.22, 0.22), cabelo="longo", mulher=True, pele="media")
FISICO = dict(roupa="camisa", cor_roupa=(0.86, 0.86, 0.80), cor_calca=(0.30, 0.30, 0.34), oculos=True, cabelo="calvo", idade=0.4)


def perito(c, t, x=330, y=1010, s=1.0, poses=((0, "stand"),), exprs=((0, "neutral"),), look=0.5, **kw):
    perito_i(c, t, x, y, s, poses=poses, exprs=exprs, look=look, **kw)


def escuro(c, col=(0.07, 0.09, 0.12)):
    luz("interior")
    c.rectangle(0, 0, 1920, 1080); rgb(c, col); c.fill()


def legenda(c, t, t0, texto, y=150, size=46):
    if t < t0:
        return
    a = ease_out(prog(t, t0, 0.4))
    c.save(); c.translate(960, y - 20 * (1 - a)); caption_box(c, texto, size); c.restore()


# ================================================================ ABERTURA
@cena("Em setembro de mil novecentos e oitenta e seis alguém avisou")
def s_aviso(c, t, s):
    cena_interior(c, t, "interior", "escritorio", seed=3)
    mesa_i(c, 1250, 880, 640)
    documento(c, 1250, 520, "OFÍCIO AO TRIBUNAL", ["Assunto: material", "radioativo", "abandonado no", "imóvel da Av.", "Paranaíba"], 0.95,
              "RECEBIDO" if t > s.w("o aviso foi") else None)
    perito(c, t, 360, 1030, poses=((0, "stand"), (s.t0 + 2, "point_r")), exprs=((0, "neutral"), (s.t0 + 2, "think")), look=0.6)
    if t > s.t0 + 0.4:
        c.save(); c.translate(560, 170); date_stamp(c, "SETEMBRO DE 1986", 44, ALERTA); c.restore()


@cena("Num prédio abandonado no centro de Goiânia")
def s_predio(c, t, s):
    cena_cidade(c, t, "tarde", seed=31)
    predio_ruina(c, t, 760, 880)
    if t > s.w("e dentro dela"):
        a = ease_out(prog(t, s.w("e dentro dela"), 1.0))
        rglow(c, 1040, 800, 220, AZUL_CESIO, 0.35 * a)
        trevo(c, 1040, 790, 22 * a)
    perito(c, t, 330, 1010, poses=((0, "point_r"),), exprs=((0, "worried"),), look=0.6)
    rotulo(c, t, s.t0 + 0.5, "AV. PARANAÍBA", "centro de Goiânia", x=760, y=190)


@cena("O aviso foi registrado")
def s_registrado(c, t, s):
    cena_cidade(c, t, "crepusculo", seed=31)
    predio_ruina(c, t, 760, 880)
    rglow(c, 1040, 800, 200, AZUL_CESIO, 0.30)
    documento(c, 1500, 470, "OFÍCIO AO TRIBUNAL", ["Assunto: material", "radioativo"], 0.7, "REGISTRADO")
    for k, (frase, txt) in enumerate((("o aviso foi", "O AVISO: REGISTRADO"), ("o prédio continuou", "O PRÉDIO: DE PÉ"), ("a máquina continuou", "A MÁQUINA: LÁ DENTRO"))):
        tk = s.w(frase)
        if t > tk:
            a = ease_out(prog(t, tk, 0.3))
            c.save(); c.translate(560, 150 + k * 80); hl(c, txt, 0, 0, 40); c.restore()
    perito(c, t, 330, 1010, poses=((0, "hips"),), exprs=((0, "think"),), look=0.6)


@cena("Um ano depois dois homens")
def s_dois_homens(c, t, s):
    cena_cidade(c, t, "noite", seed=31)
    predio_ruina(c, t, 760, 880)
    x = 1700 - (t - s.t0) * 70
    boneco(c, t, x, 980, 0.75, look=-0.8, andar=True, fid=3, **ROBERTO)
    boneco(c, t, x + 140, 985, 0.72, look=-0.8, andar=True, fid=4, **WAGNER)
    carrinho_mao(c, x + 300, 990, 0.7)
    if t > s.w("chumbo para vender"):
        legenda(c, t, s.w("chumbo para vender"), "ELES PROCURAVAM CHUMBO PARA VENDER")


@cena("O que eles levaram embora")
def s_numeros(c, t, s):
    escuro(c)
    rglow(c, 960, 540, 700, AZUL_CESIO, 0.10)
    itens = [("duzentas e quarenta e nove", 249, "pessoas contaminadas", 330),
             ("mais de cem mil", 112000, "pessoas examinadas num estádio", 960),
             ("milhares de metros", 3500, "m³ de lixo radioativo", 1590)]
    for frase, v, rot, x in itens:
        contador(c, t, s.w(frase), v, x, 470, 110, rot)
    if t > s.w("matar quatro pessoas"):
        contador(c, t, s.w("matar quatro pessoas"), 4, 960, 800, 150, "mortes", col=ALERTA, dur=0.4)
    if t > s.w("uma menina de seis"):
        _t(c, "uma delas, uma menina de 6 anos", 960, 930, 34, CREME, centro=True)


@cena("Esse é o maior acidente radiológico")
def s_maior(c, t, s):
    escuro(c)
    p = ease_out(prog(t, s.t0, 0.8))
    trevo(c, 1300, 480, 170 * p)
    perito(c, t, 420, 1010, poses=((0, "present"),), exprs=((0, "worried"), (s.w("ele foi anunciado"), "think")), look=0.5)
    legenda(c, t, s.t0 + 0.4, "O MAIOR ACIDENTE RADIOLÓGICO FORA DE UMA USINA", 140, 40)
    carimbo(c, t, s.w("ele foi anunciado"), "ANUNCIADO", 1300, 840, 70)


@cena("Eu sou o Perito Hoje")
def s_titulo(c, t, s):
    cena_cidade(c, t, "crepusculo", seed=12)
    predio_ruina(c, t, 980, 880, 560, 380)
    rglow(c, 1240, 800, 260, AZUL_CESIO, 0.35)
    perito(c, t, 360, 1010, 1.05, poses=((0, "wave"), (s.t0 + 1.5, "present")), exprs=((0, "confident"),), look=0.5)
    if t > s.t0 + 1.2:
        p = ease_out(prog(t, s.t0 + 1.2, 0.8))
        c.save(); c.translate(0, 30 * (1 - p))
        _t(c, "TRAGÉDIA ANUNCIADA", 1180, 150, 34, AMBER, font=SERIF, bold=True, centro=True, a=p)
        titulo_i(c, "CÉSIO-137", 1180, 270, 120)
        _t(c, "O BRILHO AZUL DE GOIÂNIA", 1180, 340, 44, CREME, font=SERIF, bold=True, centro=True, a=p)
        c.restore()


# ================================================================ CAP. 1 · A MÁQUINA ESQUECIDA
@cena("Para entender Goiânia")
def s_cap1(c, t, s):
    cena_cidade(c, t, "dia", seed=7)
    predio_orgao(c, 700, 880, 640, 320, "INSTITUTO GOIANO DE RADIOTERAPIA")
    figurantes(c, t, 930, n=6, s=0.34, seed=4, x0=300, x1=1800, figurinos=["moderno", "moderna", "medico"])
    perito(c, t, 330, 1010, poses=((0, "point_r"),), exprs=((0, "neutral"),))
    capitulo(c, t, s.t0 + 0.2, "1", "A MÁQUINA ESQUECIDA", 3.2)


@cena("Nos anos setenta uma clínica")
def s_clinica(c, t, s):
    luz("interior")
    interior(c, t, "reboco", "pedra", "reta", jx=1500, cor=(0.88, 0.90, 0.88))
    maquina_teleterapia(c, t, 1150, 900, 1.0)
    boneco(c, t, 1520, 1010, 0.9, poses=((0, "present_l"),), exprs=((0, "neutral"),), look=-0.6, **FIGURINO["medico"])
    if t > s.w("ela aponta um feixe"):
        a = 0.3 + 0.1 * math.sin(t * 6)
        pg(c, [(1350, 640), (1380, 640), (1300, 760), (1240, 760)]); rgb(c, AZUL_CESIO, a); c.fill()
    perito(c, t, 330, 1010, poses=((0, "present"),), exprs=((0, "neutral"),))
    rotulo(c, t, s.t0 + 0.5, "ANOS 70 · TELETERAPIA", "tratamento de câncer", x=700, y=180)


@cena("O coração dessa máquina")
def s_capsula(c, t, s):
    escuro(c)
    painel_laudo(c, 760, 200, 900, 640, "A FONTE")
    capsula(c, t, 1210, 480, 2.4, brilho=0.0)
    if t > s.w("noventa e três gramas"):
        _t(c, "≈ 93 g de cloreto de césio-137".replace("≈", "~"), 1210, 720, 38, AMBER, centro=True)
    if t > s.w("um pó parecido"):
        _t(c, "um pó parecido com sal", 1210, 780, 30, CREME, centro=True)
    if t > s.w("altamente radioativo"):
        trevo(c, 1520, 300, 40)
    perito(c, t, 360, 1010, poses=((0, "point_r"),), exprs=((0, "think"),), look=0.6)


@cena("Para proteger quem trabalhava")
def s_corte(c, t, s):
    escuro(c)
    painel_laudo(c, 560, 120, 1240, 860, "CORTE DA CABEÇA GIRATÓRIA")
    tl = s.w("quando ligava")
    gir = ease_out(prog(t, tl, 1.2))
    diagrama_cabeca(c, t, s.t0 + 0.3, 960, 500, 0.95, girada=gir)
    _t(c, "DESLIGADA" if gir < 0.5 else "LIGADA", 960, 940, 40, ALERTA if gir > 0.5 else CREME, font=SERIF, bold=True, centro=True)
    perito(c, t, 300, 1030, 0.95, poses=((0, "present"),), exprs=((0, "neutral"),), look=0.7)


@cena("Ou seja toda a segurança")
def s_seguranca(c, t, s):
    escuro(c)
    capsula(c, t, 1250, 520, 2.0)
    c.arc(1250, 520, 210, 0, 6.283); c.set_line_width(10); rgb(c, AMBER); c.stroke()
    perito(c, t, 420, 1010, poses=((0, "finger_up"),), exprs=((0, "confident"),))
    legenda(c, t, s.t0 + 0.3, "TODA A SEGURANÇA = A CÁPSULA NUNCA SAIR DALI", 150, 42)


@cena("Em mil novecentos e oitenta e cinco a clínica")
def s_mudanca(c, t, s):
    cena_cidade(c, t, "dia", seed=9)
    predio_orgao(c, 300, 880, 560, 300, "IGR · PRÉDIO ANTIGO")
    x = 1100 + (t - s.t0) * 80
    for k in range(3):
        boneco(c, t, x + k * 150, 990, 0.62, look=0.8, andar=True, fid=10 + k, **FIGURINO["operario"])
    if t > s.w("ficou para trás"):
        a = ease_out(prog(t, s.w("ficou para trás"), 0.6))
        painel_laudo(c, 1280, 300, 460, 340, None, a)
        c.save(); c.translate(1470, 600); c.scale(0.5, 0.5); maquina_teleterapia(c, t, 0, 0, 1.0); c.restore()
        _t(c, "FICOU PARA TRÁS", 1510, 360, 34, ALERTA, font=SERIF, bold=True, centro=True, a=a)
    if t > s.t0 + 0.3:
        c.save(); c.translate(1000, 180); date_stamp(c, "1985", 60, ALERTA); c.restore()


@cena("E aqui começa o primeiro aviso ignorado")
def s_cnen(c, t, s):
    cena_interior(c, t, "interior", "escritorio", seed=5)
    documento(c, 1200, 520, "COMUNICAÇÃO À CNEN", ["mudança de endereço", "desativação de", "fonte radioativa"], 1.0)
    if t > s.w("isso não foi feito"):
        p = ease_out(prog(t, s.w("isso não foi feito"), 0.3))
        c.save(); c.translate(1200, 520); c.set_line_width(26); rgb(c, ALERTA, 0.9)
        c.move_to(-180 * p, -220 * p); c.line_to(180 * p, 220 * p); c.move_to(180 * p, -220 * p); c.line_to(-180 * p, 220 * p); c.stroke(); c.restore()
        _t(c, "segundo o MPF: não foi feito", 1200, 900, 34, CREME, centro=True)
    perito(c, t, 360, 1030, poses=((0, "point_r"),), exprs=((0, "worried"),))
    legenda(c, t, s.t0 + 0.2, "AVISO IGNORADO Nº 1", 120, 44)


@cena("Ao mesmo tempo o prédio entrou")
def s_briga(c, t, s):
    cena_cidade(c, t, "nublado", seed=31)
    predio_ruina(c, t, 760, 880)
    boneco(c, t, 640, 1010, 0.85, poses=((0, "point_r"),), exprs=((0, "angry"),), look=0.7, **FIGURINO["cavalheiro"])
    boneco(c, t, 1420, 1010, 0.85, poses=((0, "point_l"),), exprs=((0, "angry"),), look=-0.7, roupa="casaco", cor_roupa=(0.30, 0.32, 0.40), gravata=(0.5, 0.1, 0.1), idade=0.5)
    if t > s.w("demolido aos poucos"):
        particulas(c, t, "poeira", 50)
    legenda(c, t, s.t0 + 0.4, "UMA BRIGA NA JUSTIÇA PELO PRÉDIO", 130, 42)


@cena("Em setembro de mil novecentos e oitenta e seis a Justiça")
def s_linha86(c, t, s):
    escuro(c)
    ev = [(0, "Justiça avisada", "SET/86"), (6, "polícia chamada", "MAI/87"), (8, "vigia no prédio", "VIGIA"), (10, "carta à CNEN", "CARTA")]
    marcos = ["a justiça foi informada", "a polícia chegou", "o tribunal colocou", "a clínica escreveu"]
    ativo = 0
    for k, m in enumerate(marcos):
        if t > s.w(m):
            ativo = k
    linha_tempo(c, t, s.t0, ev, ativo=ativo, y=600, titulo="SETEMBRO DE 1986 A MAIO DE 1987")


@cena("Repara no que aconteceu todo mundo sabia")
def s_todos_sabiam(c, t, s):
    cena_cidade(c, t, "crepusculo", seed=31)
    predio_ruina(c, t, 900, 880, 560, 400)
    rglow(c, 1150, 800, 200, AZUL_CESIO, 0.3)
    for k, (frase, txt) in enumerate((("a clínica sabia", "A CLÍNICA SABIA"), ("a justiça sabia", "A JUSTIÇA SABIA"), ("a cnen foi avisada", "A CNEN FOI AVISADA"))):
        tk = s.w(frase)
        if t > tk:
            c.save(); c.translate(1500, 200 + k * 90); hl(c, txt, 0, 0, 40); c.restore()
    if t > s.w("protegida por um vigia"):
        boneco(c, t, 1600, 1000, 0.6, poses=((0, "stand"),), exprs=((0, "neutral"),), look=-0.5, **FIGURINO["policial"])
    perito(c, t, 330, 1010, poses=((0, "shrug"),), exprs=((0, "worried"),))


@cena("No dia treze de setembro")
def s_domingo(c, t, s):
    cena_cidade(c, t, "noite", seed=31)
    predio_ruina(c, t, 760, 880)
    # cadeira vazia do vigia
    c.rectangle(1500, 920, 90, 12); c.rectangle(1500, 830, 12, 100); c.rectangle(1500, 932, 10, 60); c.rectangle(1580, 932, 10, 60)
    rgb(c, P((0.45, 0.32, 0.22))); c.fill()
    if t > s.t0 + 0.4:
        c.save(); c.translate(960, 170); date_stamp(c, "13 DE SETEMBRO DE 1987 · DOMINGO", 46, ALERTA); c.restore()
    if t > s.w("o vigia não apareceu"):
        legenda(c, t, s.w("o vigia não apareceu"), "O VIGIA NÃO APARECEU", 300, 52)


# ================================================================ CAP. 2 · O BRILHO AZUL
@cena("Naquele domingo dois catadores")
def s_cap2(c, t, s):
    cena_cidade(c, t, "dia", seed=31)
    predio_ruina(c, t, 760, 880)
    x = 1500 - (t - s.t0) * 60
    boneco(c, t, x, 990, 0.8, look=-0.8, andar=True, fid=3, **ROBERTO)
    boneco(c, t, x + 150, 995, 0.78, look=-0.8, andar=True, fid=4, **WAGNER)
    capitulo(c, t, s.t0 + 0.2, "2", "O BRILHO AZUL", 3.0)
    if t > s.t0 + 3.3:
        rotulo(c, t, s.t0 + 3.3, "ROBERTO E WAGNER", "catadores", x=150, y=180)


@cena("Eles tinham ouvido falar")
def s_dentro(c, t, s):
    luz("interior")
    interior(c, t, "reboco", "pedra", None, piso_y=860, cor=(0.56, 0.54, 0.50))
    particulas(c, t, "poeira", 40)
    maquina_teleterapia(c, t, 1050, 900, 1.0)
    boneco(c, t, 1500, 1010, 0.9, poses=((0, "point_l"),), exprs=((0, "happy"),), look=-0.6, **ROBERTO)
    boneco(c, t, 1700, 1015, 0.86, poses=((0, "stand"),), exprs=((0, "neutral"),), look=-0.6, **WAGNER)
    if t > s.w("chumbo vale dinheiro"):
        legenda(c, t, s.w("chumbo vale dinheiro"), "CHUMBO VALE DINHEIRO NO FERRO-VELHO", 150, 40)


@cena("Com ferramentas simples eles desmontaram")
def s_desmonta(c, t, s):
    luz("interior")
    interior(c, t, "reboco", "pedra", None, piso_y=860, cor=(0.56, 0.54, 0.50))
    d = ease_out(prog(t, s.w("separaram a cabeça"), 1.5))
    maquina_teleterapia(c, t, 900, 900, 1.0, desmontada=d)
    boneco(c, t, 1500, 1010, 0.9, poses=((0, "hold"),), exprs=((0, "think"),), look=-0.6, **ROBERTO)
    if t > s.w("colocaram tudo"):
        carrinho_mao(c, 1700, 1000, 0.8)
    if t > s.w("quase duzentos quilos"):
        _t(c, "~200 kg de peças", 1450, 300, 50, CREME, font=SERIF, bold=True, centro=True)


@cena("Naquela mesma noite os dois")
def s_noite_mal(c, t, s):
    interior_casa(c, t, "vela")
    boneco(c, t, 800, 1010, 0.95, poses=((0, "head"),), exprs=((0, "sad"),), look=0.4, **ROBERTO)
    boneco(c, t, 1150, 1015, 0.9, poses=((0, "stand"),), exprs=((0, "worried"),), look=-0.4, **WAGNER)
    for k, (frase, txt) in enumerate((("tontura", "TONTURA"), ("enjoo", "ENJOO"), ("vômito", "VÔMITO"))):
        if t > s.w(frase):
            c.save(); c.translate(1550, 250 + k * 90); hl(c, txt, 0, 0, 40); c.restore()
    if t > s.w("eles acharam"):
        legenda(c, t, s.w("eles acharam"), "\"FOI ALGO QUE A GENTE COMEU\"", 900, 40)


@cena("No dia seguinte Wagner piorou")
def s_hospital1(c, t, s):
    cena_cidade(c, t, "dia", seed=21, predios=False)
    predio_orgao(c, 700, 880, 640, 300, "PRONTO-SOCORRO", cruz=True)
    boneco(c, t, 1500, 1010, 0.9, poses=((0, "stand"),), exprs=((0, "worried"),), look=-0.5, **WAGNER)
    boneco(c, t, 1250, 1010, 0.9, poses=((0, "present_l"),), exprs=((0, "neutral"),), look=0.5, **FIGURINO["medico"])
    if t > s.w("reação alimentar"):
        c.save(); c.translate(960, 180); hl(c, "DIAGNÓSTICO: REAÇÃO ALIMENTAR", 0, 0, 40); c.restore()
    perito(c, t, 330, 1010, poses=((0, "stand"),), exprs=((0, "worried"),))


@cena("Esse é um ponto que vai se repetir")
def s_invisivel(c, t, s):
    escuro(c)
    painel_laudo(c, 760, 220, 960, 600, "POR QUE NINGUÉM DESCONFIOU")
    for k, (frase, txt) in enumerate((("não tem cheiro", "SEM CHEIRO"), ("não tem cor", "SEM COR"), ("não arde na hora", "NÃO ARDE NA HORA"))):
        if t > s.w(frase):
            _t(c, txt, 900, 380 + k * 90, 52, CREME, font=SERIF, bold=True)
    if t > s.w("parecem os de uma intoxicação"):
        _t(c, "sintomas = intoxicação comum", 900, 700, 36, AMBER)
    perito(c, t, 360, 1010, poses=((0, "finger_up"),), exprs=((0, "think"),))


@cena("Enquanto isso Roberto continuou")
def s_chave(c, t, s):
    interior_casa(c, t, "vela")
    mesa_cozinha(c, 1050, 860, 600)
    furo = t > s.w("furou a janelinha")
    capsula(c, t, 1050, 800, 1.0, furada=furo)
    boneco(c, t, 1450, 1010, 0.95, poses=((0, "hold"),), exprs=((0, "think"),), look=-0.6, **ROBERTO)
    rotulo(c, t, s.w("segundo o relatório"), "RELATÓRIO DA AIEA", "Agência Internacional de Energia Atômica", x=150, y=180, size=44)


@cena("Do furo saiu um brilho azul")
def s_brilho(c, t, s):
    escuro(c, (0.03, 0.04, 0.06))
    b = ease_out(prog(t, s.t0 + 0.3, 1.6))
    capsula(c, t, 960, 560, 3.0, brilho=b, furada=True)


@cena("Um azul intenso que aparecia")
def s_azul(c, t, s):
    interior_casa(c, t, "vela")
    escurecer(c, 0.25)
    mesa_cozinha(c, 960, 860, 600)
    capsula(c, t, 960, 800, 1.1, brilho=1.0, furada=True)
    boneco(c, t, 1330, 1010, 0.95, poses=((0, "point_l"),), exprs=((0, "happy"),), look=-0.6, **ROBERTO)
    if t > s.w("parecia valioso"):
        legenda(c, t, s.w("parecia valioso"), "PARECIA VALIOSO", 160, 50)


@cena("No dia dezoito de setembro Roberto vendeu")
def s_venda(c, t, s):
    cena_ferro_velho(c, t, "tarde")
    boneco(c, t, 760, 1010, 0.9, poses=((0, "present"),), exprs=((0, "happy"),), look=0.6, **ROBERTO)
    boneco(c, t, 1100, 1010, 0.92, poses=((0, "hips"),), exprs=((0, "neutral"),), look=-0.6, **DEVAIR)
    carrinho_mao(c, 940, 1020, 0.65)
    rotulo(c, t, s.t0 + 0.4, "18 DE SETEMBRO", "ferro-velho de Devair, Rua 26-A", x=150, y=180)


@cena("E naquela noite Devair viu o brilho")
def s_devair_ve(c, t, s):
    cena_ferro_velho(c, t, "noite")
    capsula(c, t, 960, 900, 1.0, brilho=1.0, furada=True)
    boneco(c, t, 1200, 1010, 0.95, poses=((0, "point_l"),), exprs=((0, "shocked"),), look=-0.7, **DEVAIR)


@cena("Devair ficou encantado")
def s_encantado(c, t, s):
    interior_casa(c, t, "vela")
    escurecer(c, 0.2)
    mesa_cozinha(c, 960, 860, 600)
    capsula(c, t, 960, 800, 1.0, brilho=1.0, furada=True)
    boneco(c, t, 1300, 1010, 0.95, poses=((0, "present_l"),), exprs=((0, "happy"),), look=-0.6, **DEVAIR)
    if t > s.w("talvez até sobrenatural"):
        legenda(c, t, s.w("talvez até sobrenatural"), "PRECIOSA? SOBRENATURAL?", 150, 44)


@cena("Nos dias seguintes a casa virou")
def s_visitas(c, t, s):
    interior_casa(c, t, "vela")
    escurecer(c, 0.18)
    mesa_cozinha(c, 960, 860, 600)
    capsula(c, t, 960, 800, 1.0, brilho=1.0, furada=True)
    rnd = random.Random(3)
    for k, x in enumerate((420, 600, 1320, 1500, 1680)):
        if t > s.t0 + k * 0.7:
            f = dict(FIGURINO[rnd.choice(["moderno", "moderna"])]); f["pele"] = rnd.choice(list(PELES))
            boneco(c, t, x, 1010, 0.85, poses=((0, "point_r" if x < 960 else "point_l"),), exprs=((0, "happy"),),
                   look=0.6 if x < 960 else -0.6, fid=50 + k, appear=s.t0 + k * 0.7, **f)
    legenda(c, t, s.w("uma pessoa levava"), "UMA PESSOA LEVAVA A OUTRA", 150, 42)


@cena("No dia vinte e um um conhecido")
def s_po(c, t, s):
    interior_casa(c, t, "vela")
    escurecer(c, 0.2)
    mesa_cozinha(c, 960, 860, 600)
    po_brilhante(c, t, 960, 840, 180, 60)
    if t > s.w("o material começou"):
        po_brilhante(c, t, 600, 1000, 120, 30, seed=5)
        po_brilhante(c, t, 1350, 1010, 120, 30, seed=6)
    boneco(c, t, 1400, 1010, 0.9, poses=((0, "hold"),), exprs=((0, "happy"),), look=-0.6, fid=7, **FIGURINO["moderno"])
    if t > s.w("como se fosse purpurina"):
        legenda(c, t, s.w("como se fosse purpurina"), "COMO SE FOSSE PURPURINA", 150, 44)
    rotulo(c, t, s.t0 + 0.3, "21 DE SETEMBRO", "o pó é dividido", x=150, y=180)


@cena("Devair ainda mostrou o achado")
def s_gabriela(c, t, s):
    interior_casa(c, t, "vela")
    escurecer(c, 0.15)
    po_brilhante(c, t, 960, 840, 140, 40)
    boneco(c, t, 700, 1010, 0.95, poses=((0, "present"),), exprs=((0, "happy"),), look=0.6, **DEVAIR)
    boneco(c, t, 1250, 1010, 0.92, poses=((0, "stand"), (s.w("ela começou"), "head")), exprs=((0, "neutral"), (s.w("ela começou"), "worried")), look=-0.6, **GABRIELA)
    rotulo(c, t, s.t0 + 0.4, "MARIA GABRIELA FERREIRA", "esposa de Devair", x=150, y=180)


@cena("No dia vinte e quatro o irmão")
def s_ivo(c, t, s):
    interior_casa(c, t, "dia")
    mesa_cozinha(c, 960, 860, 700)
    po_brilhante(c, t, 960, 840, 160, 40, a=0.8)
    po_brilhante(c, t, 760, 1010, 140, 40, seed=9, a=0.8)
    boneco(c, t, 1400, 1010, 0.92, poses=((0, "present_l"),), exprs=((0, "neutral"),), look=-0.6, fid=12, pele="media", roupa="camisa", cor_roupa=(0.40, 0.48, 0.36), bigode=True)
    rotulo(c, t, s.t0 + 0.4, "24 DE SETEMBRO · CASA DE IVO", "o pó chega à mesa da família", x=150, y=180)


@cena("A filha mais nova de Ivo")
def s_leide(c, t, s):
    luz("crepusculo")
    c.rectangle(0, 0, 1920, 1080); rgb(c, (0.12, 0.13, 0.16)); c.fill()
    rglow(c, 960, 520, 520, (1.0, 0.86, 0.6), 0.18)
    vela_i(c, t, 960, 760, 1.4)
    if t > s.t0 + 0.4:
        a = ease_out(prog(t, s.t0 + 0.4, 1.0))
        _t(c, "LEIDE DAS NEVES FERREIRA", 960, 380, 64, CREME, font=SERIF, bold=True, centro=True, a=a)
        _t(c, "6 anos", 960, 450, 40, AMBER, centro=True, a=a)
    if t > s.w("ela engoliu"):
        a = ease_out(prog(t, s.w("ela engoliu"), 0.8))
        _t(c, "ela ingeriu partículas de césio-137", 960, 940, 36, CREME, centro=True, a=a)


@cena("Nesse ponto o problema já não estava")
def s_mapa1(c, t, s):
    escuro(c)
    mapa_goiania(c, t, s.t0, pontos=["igr", "roberto", "devair", "ivo"], rota=["igr", "roberto", "devair", "ivo"],
                 p_rota=prog(t, s.t0 + 0.5, 4.0), contaminado=["roberto", "devair", "ivo"])
    if t > s.w("e continuava se movendo"):
        legenda(c, t, s.w("e continuava se movendo"), "E CONTINUAVA SE MOVENDO", 1010, 40)


@cena("Funcionários de Devair mexeram")
def s_funcionarios(c, t, s):
    cena_ferro_velho(c, t, "dia")
    boneco(c, t, 800, 1010, 0.88, poses=((0, "hold"),), exprs=((0, "think"),), look=0.6, fid=21, **FIGURINO["operario"])
    boneco(c, t, 1050, 1010, 0.86, poses=((0, "hold"),), exprs=((0, "neutral"),), look=0.6, fid=22, pele="escura", roupa="camisa", cor_roupa=(0.6, 0.6, 0.62))
    po_brilhante(c, t, 920, 1000, 160, 30, a=0.7)
    if t > s.w("com um maçarico"):
        legenda(c, t, s.w("com um maçarico"), "ALGUÉM SE OFERECEU PARA CORTAR A PEÇA COM MAÇARICO", 150, 34)


@cena("No dia vinte e cinco Devair vendeu")
def s_mapa2(c, t, s):
    escuro(c)
    mapa_goiania(c, t, s.t0 - 5, pontos=["igr", "roberto", "devair", "ivo", "j"], rota=["devair", "j"],
                 p_rota=prog(t, s.t0 + 0.5, 1.5), contaminado=["roberto", "devair", "ivo"] + (["j"] if t > s.t0 + 2 else []))
    rotulo(c, t, s.t0 + 0.3, "25 DE SETEMBRO", "a cápsula vai junto com o chumbo", x=300, y=1030, size=40)


# ================================================================ CAP. 3 · A MULHER QUE DESCONFIOU
@cena("No fim daquela semana")
def s_cap3(c, t, s):
    cena_cidade(c, t, "nublado", seed=21, predios=False)
    predio_orgao(c, 700, 880, 640, 300, "HOSPITAL", cruz=True)
    fila_gente(c, t, 520, 1500, 1010, n=8, s=0.62, seed=4)
    capitulo(c, t, s.t0 + 0.2, "3", "A MULHER QUE DESCONFIOU", 3.2)


@cena("Os médicos que atendiam")
def s_medicos(c, t, s):
    luz("interior")
    interior(c, t, "reboco", "pedra", "reta", jx=1500, cor=(0.88, 0.90, 0.88))
    boneco(c, t, 1100, 1010, 0.95, poses=((0, "think"),), exprs=((0, "think"),), look=0.4, **FIGURINO["medico"])
    for k, (frase, txt) in enumerate((("alergia", "ALERGIA?"), ("doença tropical", "DOENÇA TROPICAL?"))):
        if t > s.w(frase):
            c.save(); c.translate(1500, 300 + k * 100); hl(c, txt, 0, 0, 44); c.restore()
    perito(c, t, 330, 1010, poses=((0, "stand"),), exprs=((0, "worried"),))


@cena("Quem ligou os pontos foi")
def s_ela(c, t, s):
    interior_casa(c, t, "dia")
    boneco(c, t, 1100, 1010, 1.05, poses=((0, "think"), (s.w("ela percebeu"), "point_r")), exprs=((0, "think"), (s.w("ela percebeu"), "confident")), look=0.5, **GABRIELA)
    if t > s.w("chegado perto daquele"):
        po_brilhante(c, t, 1550, 900, 120, 30)
        legenda(c, t, s.w("chegado perto daquele"), "TODOS TINHAM CHEGADO PERTO DO PÓ", 150, 40)
    if t > s.w("pegou um ônibus"):
        c.save(); c.translate(560, 200); date_stamp(c, "28 DE SETEMBRO", 44, ALERTA); c.restore()


@cena("Um ônibus comum de linha")
def s_onibus(c, t, s):
    cena_cidade(c, t, "dia", seed=5)
    x = -300 + (t - s.t0) * 260
    onibus(c, t, x, 980, 1.0)
    rglow(c, x - 60, 800, 120, AZUL_CESIO, 0.45)
    figurantes(c, t, 930, n=5, s=0.32, seed=2, x0=0, x1=1920, figurinos=["moderno", "moderna"])
    legenda(c, t, s.w("com uma fonte"), "UMA FONTE RADIOATIVA DENTRO DE UM SACO", 150, 40)


@cena("O destino era a Vigilância")
def s_visa(c, t, s):
    cena_cidade(c, t, "dia", seed=14, predios=False)
    predio_orgao(c, 640, 880, 700, 320, "VIGILÂNCIA SANITÁRIA")
    boneco(c, t, 1500, 1010, 0.9, poses=((0, "hold"),), exprs=((0, "worried"),), look=-0.6, **GABRIELA)
    boneco(c, t, 1680, 1010, 0.88, poses=((0, "hold"),), exprs=((0, "neutral"),), look=-0.6, fid=31, **FIGURINO["moderno"])
    rglow(c, 1440, 900, 90, AZUL_CESIO, 0.35)


@cena("Lá a peça foi entregue")
def s_cadeira(c, t, s):
    cena_cidade(c, t, "tarde", seed=14, predios=False)
    predio_orgao(c, 200, 880, 600, 300, "VIGILÂNCIA SANITÁRIA")
    # cadeira no pátio com o saco
    c.rectangle(1200, 900, 110, 14); c.rectangle(1200, 800, 14, 114); c.rectangle(1200, 914, 12, 80); c.rectangle(1298, 914, 12, 80)
    rgb(c, P((0.50, 0.38, 0.26))); c.fill()
    ellipse(c, 1258, 870, 50, 36); rgb(c, P((0.70, 0.62, 0.46))); c.fill()
    rglow(c, 1258, 870, 160, AZUL_CESIO, 0.35)
    boneco(c, t, 1560, 1010, 0.9, poses=((0, "think"),), exprs=((0, "worried"),), look=-0.6, **FIGURINO["medico"])
    if t > s.w("por cerca de um dia"):
        legenda(c, t, s.w("por cerca de um dia"), "CERCA DE UM DIA NUMA CADEIRA NO PÁTIO", 150, 40)


@cena("Enquanto isso Maria Gabriela e outros")
def s_hdt(c, t, s):
    cena_cidade(c, t, "tarde", seed=17, predios=False)
    predio_orgao(c, 600, 880, 760, 320, "HOSPITAL DE DOENÇAS TROPICAIS", cruz=True)
    boneco(c, t, 1550, 1010, 0.9, poses=((0, "think"),), exprs=((0, "think"),), look=-0.5, **FIGURINO["medico"])
    if t > s.w("lesões de radiação"):
        trevo(c, 1550, 340, 50)
        legenda(c, t, s.w("lesões de radiação"), "SUSPEITA: LESÕES DE RADIAÇÃO", 150, 44)


@cena("A suspeita chegou a um físico")
def s_fisico(c, t, s):
    cena_cidade(c, t, "dia", seed=19)
    boneco(c, t, 1150, 1010, 1.0, poses=((0, "hold"),), exprs=((0, "think"),), look=0.5, **FISICO)
    if t > s.w("pegou emprestado"):
        medidor(c, t, 1350, 760, 0.7, nivel=0.0)
    rotulo(c, t, s.w("na manhã de"), "29 DE SETEMBRO", "um físico de férias", x=150, y=180)
    perito(c, t, 330, 1010, poses=((0, "point_r"),), exprs=((0, "neutral"),))


@cena("O ponteiro disparou")
def s_ponteiro(c, t, s):
    escuro(c)
    nv = ease_out(prog(t, s.t0 + 0.2, 0.5))
    medidor(c, t, 960, 520, 3.2, nivel=nv)
    if t > s.t0 + 0.4:
        rglow(c, 960, 520, 700, ALERTA, 0.08 + 0.05 * math.sin(t * 9))


@cena("O medidor mostrava radiação alta")
def s_troca(c, t, s):
    cena_cidade(c, t, "dia", seed=14, predios=False)
    predio_orgao(c, 300, 880, 600, 300, "VIGILÂNCIA SANITÁRIA")
    boneco(c, t, 1250, 1010, 1.0, poses=((0, "hold"),), exprs=((0, "shocked"),), look=-0.4, **FISICO)
    medidor(c, t, 1450, 760, 0.7, nivel=1.0)
    if t > s.w("estava com defeito"):
        c.save(); c.translate(1500, 300); hl(c, "DEFEITO?", 0, 0, 48); c.restore()
    if t > s.w("o segundo medidor"):
        medidor(c, t, 1650, 760, 0.7, nivel=1.0)
        carimbo(c, t, s.w("o segundo medidor"), "A MESMA COISA", 1400, 500, 56)


@cena("Os bombeiros foram chamados")
def s_bombeiros(c, t, s):
    cena_cidade(c, t, "dia", seed=14, predios=False)
    predio_orgao(c, 300, 880, 600, 300, "VIGILÂNCIA SANITÁRIA")
    for k, x in enumerate((1000, 1180)):
        boneco(c, t, x, 1010, 0.88, poses=((0, "stand"),), exprs=((0, "worried"),), look=0.4, fid=60 + k, **FIGURINO["bombeiro"])
    boneco(c, t, 1500, 1010, 0.92, poses=((0, "point_l"),), exprs=((0, "worried"),), look=-0.6, **FISICO)
    if t > s.w("o prédio foi isolado"):
        for x in range(0, 1920, 80):  # faixa de isolamento
            c.rectangle(x, 905, 40, 14); rgb(c, (0.95, 0.80, 0.10)); c.fill()
            c.rectangle(x + 40, 905, 40, 14); rgb(c, (0.12, 0.12, 0.12)); c.fill()
        boneco(c, t, 1720, 1010, 0.88, poses=((0, "stand"),), exprs=((0, "neutral"),), look=-0.6, fid=63, **FIGURINO["policial"])
    if t > s.w("jogar a peça num rio"):
        legenda(c, t, s.w("jogar a peça num rio"), "CHEGARAM A PENSAR EM JOGAR A PEÇA NUM RIO", 150, 38)


@cena("Perto do meio dia ele foi")
def s_acima(c, t, s):
    cena_ferro_velho(c, t, "dia")
    boneco(c, t, 1300, 1010, 0.95, poses=((0, "hold"),), exprs=((0, "shocked"),), look=-0.5, **FISICO)
    medidor(c, t, 1500, 760, 0.7, nivel=1.0)
    po_brilhante(c, t, 900, 1000, 220, 40, a=0.6)
    carimbo(c, t, s.w("passava do limite"), "ACIMA DA ESCALA", 760, 300, 64)


@cena("Dezesseis dias depois do domingo")
def s_dezesseis(c, t, s):
    escuro(c)
    ev = [(13, "roubo"), (18, "ferro-velho"), (21, "o pó se espalha"), (24, "casa de Ivo"), (28, "o ônibus"), (29, "o medidor")]
    linha_tempo(c, t, s.t0, ev, ativo=5, y=560)
    if t > s.t0 + 2.5:
        _t(c, "16 DIAS", 960, 900, 90, ALERTA, font=SERIF, bold=True, centro=True)


# ================================================================ CAP. 4 · O ESTÁDIO
@cena("A partir daquela tarde")
def s_cap4(c, t, s):
    luz("crepusculo"); ceu(c, t, seed=8); chao(c, t, 880, "grama")
    estadio(c, t, 300, 880)
    capitulo(c, t, s.t0 + 0.2, "4", "O ESTÁDIO", 3.0)
    if t > s.w("a cnen foi avisada"):
        for k, txt in enumerate(("CNEN AVISADA", "PACIENTES ISOLADOS", "DEFESA CIVIL")):
            tk = s.w(["a cnen foi avisada", "os dez pacientes", "a defesa civil"][k])
            if t > tk:
                c.save(); c.translate(1550, 200 + k * 80); hl(c, txt, 0, 0, 36); c.restore()
    if t > s.w("estádio olímpico"):
        rotulo(c, t, s.w("estádio olímpico"), "ESTÁDIO OLÍMPICO", "centro de triagem", x=150, y=180)


@cena("Na madrugada seguinte")
def s_lavagem(c, t, s):
    luz("noite"); ceu(c, t, seed=8); chao(c, t, 880, "grama")
    estadio(c, t, 200, 880, 900, depth=0.4)
    for k, x in enumerate((1100, 1300)):
        boneco(c, t, x, 1010, 0.85, poses=((0, "hold"),), exprs=((0, "neutral"),), look=0.6, fid=70 + k, **FIGURINO["tecnico"])
    fila_gente(c, t, 1450, 1850, 1010, n=4, s=0.8, seed=6)
    contador(c, t, s.w("duzentas e quarenta e nove"), 249, 560, 300, 110, "pessoas registradas e descontaminadas")
    if t > s.w("água sabão e vinagre"):
        legenda(c, t, s.w("água sabão e vinagre"), "ÁGUA, SABÃO E VINAGRE", 520, 40)


@cena("E então veio o medo")
def s_medo(c, t, s):
    luz("dia"); ceu(c, t, seed=9); chao(c, t, 880, "grama")
    estadio(c, t, 200, 880, 1500, depth=0.3)
    fila_gente(c, t, 120, 1800, 1010, n=18, s=0.55, seed=12)
    contador(c, t, s.w("mais de cento e doze mil"), 112000, 960, 230, 120, "pessoas examinadas no estádio")
    perito(c, t, 1750, 1010, 0.8, look=-0.6, exprs=((0, "worried"),))


@cena("Do lado de fora outro problema")
def s_preconceito(c, t, s):
    cena_cidade(c, t, "nublado", seed=44)
    boneco(c, t, 700, 1010, 0.92, poses=((0, "stand"),), exprs=((0, "sad"),), look=0.6, fid=80, **FIGURINO["moderno"])
    for k, x in enumerate((1150, 1330, 1500)):
        boneco(c, t, x, 1010, 0.86, poses=((0, "hips" if k else "point_l"),), exprs=((0, "angry"),), look=-0.6, fid=81 + k, **FIGURINO["moderna" if k == 1 else "moderno"])
    legenda(c, t, s.t0 + 0.3, "O PRECONCEITO", 150, 56)
    if t > s.w("tratado como ameaça"):
        _t(c, "quem foi contaminado virou \"ameaça\"", 960, 260, 34, CREME, centro=True)


@cena("Os casos mais graves foram transferidos")
def s_rio(c, t, s):
    cena_cidade(c, t, "crepusculo", seed=50, predios=True)
    predio_orgao(c, 560, 880, 820, 320, "HOSPITAL NAVAL MARCÍLIO DIAS", cruz=True)
    rotulo(c, t, s.t0 + 0.4, "RIO DE JANEIRO", "os casos mais graves", x=150, y=180)


@cena("No dia vinte e três de outubro morreram")
def s_mortes(c, t, s):
    luz("crepusculo")
    c.rectangle(0, 0, 1920, 1080); rgb(c, (0.10, 0.11, 0.14)); c.fill()
    rglow(c, 960, 560, 640, (1.0, 0.86, 0.6), 0.15)
    nomes = [("leide das neves ferreira", "LEIDE DAS NEVES FERREIRA", "23/10/1987"),
             ("maria gabriela ferreira a mulher", "MARIA GABRIELA FERREIRA", "23/10/1987"),
             ("israel batista", "ISRAEL BATISTA DOS SANTOS", "27/10/1987"),
             ("admilson alves", "ADMILSON ALVES DE SOUZA", "28/10/1987")]
    for k, (frase, nome, data) in enumerate(nomes):
        tk = s.w(frase)
        if t > tk:
            a = ease_out(prog(t, tk, 0.8))
            _t(c, nome, 960, 330 + k * 120, 52, CREME, font=SERIF, bold=True, centro=True, a=a)
            _t(c, data, 960, 372 + k * 120, 28, AMBER, centro=True, a=a)
    vela_i(c, t, 360, 940, 1.1); vela_i(c, t, 1560, 940, 1.1)


@cena("O enterro de Leide em Goiânia")
def s_enterro(c, t, s):
    luz("nublado"); ceu(c, t, nuvens=True, astro=False, seed=3); chao(c, t, 880, "grama")
    for k in range(9):
        lapide(c, 300 + k * 170, 900 - (k % 2) * 10, 0.5, tipo=["arco", "cruz"][k % 2])
    if t > s.w("mais de duas mil pessoas"):
        fila_gente(c, t, 200, 1750, 1020, n=20, s=0.5, seed=21)
        contador(c, t, s.w("mais de duas mil pessoas"), 2000, 960, 230, 100, "pessoas protestaram no cemitério", fmt="+{:,}")
    if t > s.w("caixão de chumbo"):
        legenda(c, t, s.w("caixão de chumbo"), "ENTERRADA NUM CAIXÃO DE CHUMBO", 360, 40)


@cena("Devair que ficou dias ao lado")
def s_sobreviventes(c, t, s):
    escuro(c)
    painel_laudo(c, 760, 260, 960, 560, "QUEM SOBREVIVEU")
    for k, (frase, txt) in enumerate((("devair que ficou", "DEVAIR: SOBREVIVEU"), ("roberto um dos", "ROBERTO: PARTE DO BRAÇO AMPUTADA"), ("dezenas de outras", "DEZENAS: SEQUELAS PARA A VIDA"))):
        if t > s.w(frase):
            _t(c, txt, 820, 400 + k * 110, 40, CREME, font=SERIF, bold=True)
    perito(c, t, 360, 1010, poses=((0, "stand"),), exprs=((0, "sad"),))


# ================================================================ CAP. 5 · LIMPAR UMA CIDADE
@cena("Encontrar e retirar o césio")
def s_cap5(c, t, s):
    cena_cidade(c, t, "dia", seed=60)
    helicoptero(c, t, 300 + (t - s.t0) * 90, 230, 0.9)
    for k, x in enumerate((900, 1150, 1400)):
        boneco(c, t, x, 1010, 0.82, poses=((0, "hold"),), exprs=((0, "neutral"),), look=0.5, fid=90 + k, **FIGURINO["tecnico"],
               prop=("r", lambda c, tt: medidor(c, tt, 0, 20, 0.35, nivel=0.6)))
    capitulo(c, t, s.t0 + 0.2, "5", "LIMPAR UMA CIDADE", 3.0)
    if t > s.w("houve casas demolidas"):
        legenda(c, t, s.w("houve casas demolidas"), "CASAS DEMOLIDAS · SOLO RASPADO", 150, 40)
    if t > s.w("cinquenta mil rolos"):
        legenda(c, t, s.w("cinquenta mil rolos"), "ATÉ 50 MIL ROLOS DE PAPEL HIGIÊNICO", 250, 36)


@cena("No fim o acidente gerou cerca")
def s_lixo(c, t, s):
    luz("dia"); ceu(c, t, seed=61); chao(c, t, 880, "terra")
    for r in range(2):
        for k in range(7):
            conteiner(c, 260 + k * 210 + r * 60, 960 - r * 180, 190, 150, depth=0.15 * r)
    contador(c, t, s.w("três mil e quinhentos"), 3500, 960, 230, 120, "m³ de lixo radioativo")


@cena("Todo esse material foi colocado")
def s_abadia(c, t, s):
    luz("tarde"); ceu(c, t, seed=62); colinas(c, 700, 120, seed=4, col=(0.44, 0.56, 0.36), depth=0.4); chao(c, t, 880, "grama")
    c.rectangle(500, 760, 920, 140); rgb(c, P((0.70, 0.70, 0.68))); c.fill()
    for k in range(5):
        trevo(c, 600 + k * 180, 830, 26)
    rotulo(c, t, s.t0 + 0.4, "ABADIA DE GOIÁS", "depósito definitivo · 23 km de Goiânia", x=150, y=180)
    if t > s.w("trinta anos"):
        legenda(c, t, s.w("trinta anos"), "~30 ANOS PARA PERDER METADE DA RADIOATIVIDADE", 300, 36)
    if t > s.w("são precisos séculos"):
        carimbo(c, t, s.w("são precisos séculos"), "SÉCULOS", 1500, 560, 64, AMBER)


@cena("Mesmo com todo esse esforço")
def s_fracao(c, t, s):
    escuro(c)
    mapa_goiania(c, t, s.t0 - 9, pontos=[], contaminado=["devair", "ivo", "roberto", "j"])
    legenda(c, t, s.t0 + 0.4, "PARTE DO CÉSIO NUNCA FOI RECUPERADA", 1010, 40)


# ================================================================ CAP. 6 · A CADEIA DE ERROS
ROT_ELOS = ["fonte|abandonada", "problema|de papel", "só um|vigia", "aviso que|ninguém leu", "sintomas|confundidos", "o brilho"]


@cena("Agora vamos fazer o que a gente faz")
def s_cap6(c, t, s):
    escuro(c)
    corrente(c, t, s.t0 + 3.2, ativos=0, y=600)
    capitulo(c, t, s.t0 + 0.2, "6", "A CADEIA DE ERROS", 3.0)
    if t > s.w("ele tem uma sequência"):
        legenda(c, t, s.w("ele tem uma sequência"), "NÃO TEM UMA CAUSA SÓ. TEM UMA SEQUÊNCIA.", 180, 40)


def _elo(c, t, s, n, extra=None):
    escuro(c)
    corrente(c, t, s.t0 - 9, ativos=n, rotulos=ROT_ELOS, y=430)
    _t(c, f"ELO {n}", 960, 170, 60, ALERTA, font=SERIF, bold=True, centro=True)
    if extra:
        extra(c, t)


@cena("Elo número um a fonte")
def s_elo1(c, t, s):
    _elo(c, t, s, 1, lambda c, t: (c.save(), c.translate(960, 980), c.scale(0.5, 0.5), maquina_teleterapia(c, t, 0, 0, 1.0), c.restore()))


@cena("Elo número dois o abandono")
def s_elo2(c, t, s):
    _elo(c, t, s, 2, lambda c, t: documento(c, 960, 830, "PROCESSO", ["disputa pelo imóvel"], 0.45, "ARQUIVO"))


@cena("Elo número três a proteção")
def s_elo3(c, t, s):
    _elo(c, t, s, 3, lambda c, t: boneco(c, t, 960, 1060, 0.55, poses=((0, "stand"),), exprs=((0, "neutral"),), alpha=0.5, **FIGURINO["policial"]))


@cena("Elo número quatro ninguém entendeu")
def s_elo4(c, t, s):
    escuro(c)
    tn = s.w("anos depois")
    if t < tn:
        trevo(c, 960, 500, 190 * ease_out(prog(t, s.t0, 0.6)))
        for k, (frase, txt) in enumerate((("não dizia perigo", "\"PERIGO\"?"), ("não dizia fique longe", "\"FIQUE LONGE\"?"), ("isso pode te matar", "\"ISSO PODE TE MATAR\"?"))):
            if t > s.w(frase):
                _t(c, txt, [380, 1540, 960][k], [400, 400, 880][k], 44, CREME, font=SERIF, bold=True, centro=True)
        _t(c, "ELO 4 · O AVISO QUE NINGUÉM LEU", 960, 120, 46, ALERTA, font=SERIF, bold=True, centro=True)
    else:
        trevo(c, 560, 520, 150)
        simbolo_iso(c, 1360, 540, 1.3 * ease_out_back(prog(t, tn, 0.6)))
        _t(c, "1946 (trevo)", 560, 780, 34, CREME, centro=True)
        _t(c, "2007 · ISO 21482", 1360, 820, 34, AMBER, centro=True)
        legenda(c, t, tn + 0.3, "UM AVISO PARA QUALQUER PESSOA ENTENDER", 140, 40)


@cena("Elo número cinco os sintomas")
def s_elo5(c, t, s):
    _elo(c, t, s, 5, lambda c, t: [_t(c, x, 960, 860 + k * 54, 36, CREME, centro=True) for k, x in enumerate(("alergia · intoxicação · doença tropical",))])


@cena("Elo número seis o brilho")
def s_elo6(c, t, s):
    _elo(c, t, s, 6, lambda c, t: capsula(c, t, 960, 880, 0.9, brilho=1.0, furada=True))


@cena("Repara que nenhum desses elos")
def s_alinhados(c, t, s):
    escuro(c)
    corrente(c, t, s.t0 - 9, ativos=6, rotulos=ROT_ELOS, y=430)
    if t > s.w("dezesseis dias"):
        _t(c, "TODOS SE ALINHARAM EM 16 DIAS", 960, 900, 60, ALERTA, font=SERIF, bold=True, centro=True)
    elif t > s.w("quando todos se alinham"):
        _t(c, "a tragédia acontece quando todos se alinham", 960, 900, 40, CREME, centro=True)


# ================================================================ CAP. 7 · O QUE FICOU
@cena("Depois do acidente o governo de Goiás")
def s_cap7(c, t, s):
    cena_cidade(c, t, "dia", seed=70)
    predio_orgao(c, 640, 880, 760, 320, "FUNDAÇÃO LEIDE DAS NEVES FERREIRA")
    capitulo(c, t, s.t0 + 0.2, "7", "O QUE FICOU", 3.0)
    if t > s.t0 + 3.3:
        rotulo(c, t, s.t0 + 3.3, "FEVEREIRO DE 1988", "acompanhamento das vítimas", x=150, y=180)


@cena("Na Justiça a responsabilização")
def s_justica(c, t, s):
    cena_interior(c, t, "interior", "escritorio", seed=9)
    documento(c, 1250, 520, "SENTENÇA (2000)", ["Justiça Federal", "indenizações", "atendimento médico", "e psicológico às", "vítimas e descendentes"], 1.0)
    perito(c, t, 360, 1030, poses=((0, "point_r"),), exprs=((0, "think"),))
    if t > s.w("até hoje sobreviventes"):
        legenda(c, t, s.w("até hoje sobreviventes"), "ATÉ HOJE: FALTA DE ASSISTÊNCIA E PRECONCEITO", 120, 36)


@cena("O acidente também mudou a forma")
def s_licao(c, t, s):
    escuro(c)
    c.save(); c.translate(1200, 940); c.scale(0.8, 0.8); maquina_teleterapia(c, t, 0, 0, 1.0); c.restore()
    if t > s.w("não está só no reator"):
        _t(c, "não é só o reator gigante...", 1200, 220, 40, CREME, centro=True)
    if t > s.w("está também na máquina"):
        _t(c, "é também a máquina pequena e esquecida", 1200, 290, 44, AMBER, font=SERIF, bold=True, centro=True)
    perito(c, t, 380, 1010, poses=((0, "present"),), exprs=((0, "confident"),))


@cena("O terreno onde ficava a clínica")
def s_hoje(c, t, s):
    cena_cidade(c, t, "dia", seed=80)
    predio_orgao(c, 560, 880, 820, 300, "CENTRO DE CONVENÇÕES DE GOIÂNIA")
    figurantes(c, t, 930, n=9, s=0.34, seed=8, x0=200, x1=1800, figurinos=["moderno", "moderna"])
    rotulo(c, t, s.t0 + 0.4, "HOJE", "onde ficava o IGR", x=150, y=180)


# ================================================================ FECHAMENTO
@cena("O césio 137 de Goiânia costuma ser lembrado")
def s_acaso(c, t, s):
    cena_cidade(c, t, "crepusculo", seed=31)
    predio_ruina(c, t, 760, 880)
    perito(c, t, 330, 1010, poses=((0, "think"),), exprs=((0, "think"),))
    if t > s.w("difícil chamar de acaso"):
        carimbo(c, t, s.w("difícil chamar de acaso"), "ACASO?", 1500, 300, 70)


@cena("Houve um prédio em ruínas")
def s_recap(c, t, s):
    escuro(c)
    itens = [("houve um prédio", "um prédio em ruínas"), ("houve um aviso", "um aviso à Justiça"), ("houve uma carta", "uma carta à CNEN"),
             ("houve um vigia", "um vigia que faltou"), ("e houve uma cidade", "uma cidade que não sabia ler o perigo")]
    for k, (frase, txt) in enumerate(itens):
        tk = s.w(frase)
        if t > tk:
            a = ease_out(prog(t, tk, 0.4))
            c.arc(640, 250 + k * 130, 14, 0, 6.283); rgb(c, ALERTA, a); c.fill()
            _t(c, txt, 680, 266 + k * 130, 48, CREME, font=SERIF, bold=True, a=a)


@cena("A pergunta que fica")
def s_pergunta(c, t, s):
    cena_cidade(c, t, "noite", seed=31)
    predio_ruina(c, t, 760, 880)
    c.rectangle(1500, 920, 90, 12); c.rectangle(1500, 830, 12, 100); c.rectangle(1500, 932, 10, 60); c.rectangle(1580, 932, 10, 60)
    rgb(c, P((0.45, 0.32, 0.22))); c.fill()
    rglow(c, 1040, 800, 180, AZUL_CESIO, 0.25 + 0.08 * math.sin(t * 2))
    perito(c, t, 330, 1010, poses=((0, "think"),), exprs=((0, "think"),))
    legenda(c, t, s.t0 + 0.6, "QUANTAS MÁQUINAS ESQUECIDAS EXISTEM HOJE?", 150, 42)


@cena("Me conta nos comentários")
def s_comente(c, t, s):
    cena_cidade(c, t, "tarde", seed=12)
    perito(c, t, 420, 1010, 1.05, poses=((0, "present"),), exprs=((0, "happy"),))
    c.save(); c.translate(1150, 420); placa(c, "VOCÊ CONHECIA ESSA HISTÓRIA?", "COMENTE", size=44); c.restore()


@cena("Eu sou o Perito E aqui no Tragédia")
def s_final(c, t, s):
    escuro(c, (0.05, 0.06, 0.08))
    rglow(c, 960, 480, 600, AZUL_CESIO, 0.10)
    perito(c, t, 420, 1010, 1.05, poses=((0, "stand"),), exprs=((0, "confident"),))
    if t > s.w("tragédia anunciada"):
        p = ease_out(prog(t, s.w("tragédia anunciada"), 0.8))
        _t(c, "TRAGÉDIA", 1200, 430, 120, CREME, font=SERIF, bold=True, centro=True, a=p)
        _t(c, "ANUNCIADA", 1200, 560, 120, ALERTA, font=SERIF, bold=True, centro=True, a=p)
    if t > s.w("a gente mostra"):
        _t(c, "toda tragédia deu sinais antes", 1200, 660, 40, AMBER, centro=True)
        c.save(); c.translate(1200, 800); placa(c, "INSCREVA-SE", None, size=40); c.restore()


# ---------------------------------------------------------------- monta a lista de cenas
_scs = []
_cur = 0
for _anc, _fn in _REG:
    _i = _acha(_anc, _cur)
    _cur = _i + 1
    _scs.append((Cena(_i), _fn))
SCENES = []
for _k, (_s, _fn) in enumerate(_scs):
    _ini = 0.0 if _k == 0 else _s.t0
    _fim = _scs[_k + 1][0].t0 if _k + 1 < len(_scs) else 999.0
    SCENES.append((_ini, _fim, (lambda f, s: (lambda c, t: f(c, t, s)))(_fn, _s)))

# sons nos momentos-chave (tons, sem ruído)
def _tt(frase):
    return PAL[_acha(frase)]["t"]


SFX = [(_tt("ele foi anunciado"), "boom"), (_tt("eu sou o perito hoje"), "tum"), (_tt("o vigia não apareceu para"), "boom"),
       (_tt("do furo saiu"), "boom"), (_tt("ela engoliu"), "heartbeat"), (_tt("o ponteiro disparou"), "boom"),
       (_tt("e então veio o medo"), "heartbeat"), (_tt("no dia vinte e três de outubro"), "bell"),
       (_tt("elo número um"), "tum"), (_tt("elo número quatro"), "tum"), (_tt("dezesseis dias e"), "boom") if False else (_tt("todos se alinharam"), "boom"),
       (_tt("é difícil chamar de acaso"), "tum"), (_tt("eu sou o perito e"), "boom")]
