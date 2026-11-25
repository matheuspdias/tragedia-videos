"""TRAGÉDIA ANUNCIADA · Barragem de Fundão, Mariana (2015). Cenas ancoradas nas palavras da narração (palavras.json)."""
import json, os, re
from engine import *
from ilustrado import *
from tragedia import *
from tragedia import _t
from incendio import *
from barragem import *

STYLE = "ilustrado"
TOM = "normal"
THEME = "cidade"
SFX_OFF = True
AMBIENCE = None

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
        return PAL[_acha(frase, self.i)]["t"]


_REG = []


def cena(ancora):
    def deco(fn):
        _REG.append((ancora, fn))
        return fn
    return deco


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


BARR_Y = 600


def cena_barragem(c, t, hora="dia", nivel=0.85, **kw):
    vale(c, t, hora, seed=5)
    return barragem_paisagem(c, t, 960, BARR_Y, 1100, nivel, 6, depth=0.15, **kw)


def cena_bento(c, t, hora="dia", soterrado=0.0, gente=False, lama_x=None):
    vale(c, t, hora, seed=8)
    rio(c, t, [(-50, 1000), (600, 960), (1200, 1010), (1980, 970)], 50)
    vilarejo(c, t, 960, 880, 1.0, 8, seed=4, soterrado=soterrado, gente=gente)
    if lama_x is not None:
        onda_lama(c, t, lama_x, 960, 320)


# ================================================================ ABERTURA
@cena("Em novembro de dois mil e vinte e cinco um tribunal")
def s_londres(c, t, s):
    luz("dia"); ceu(c, t, passaros=False, seed=9)
    c.rectangle(0, 760, W, H); rgb(c, P((0.62, 0.60, 0.58))); c.fill()
    tribunal(c, t, 960, 660, 1.0, "HIGH COURT · LONDRES")
    c.save(); c.translate(500, 170); date_stamp(c, "NOVEMBRO DE 2025", 44, ALERTA); c.restore()
    if t > s.w("no interior de minas"):
        _t(c, "Minas Gerais, 10 anos antes", 960, 1010, 40, CREME, font=SERIF, bold=True, centro=True)


@cena("Na decisão o tribunal escreveu")
def s_previsivel(c, t, s):
    escuro(c, LAUDO_BG)
    painel_laudo(c, 260, 120, 1400, 840, "A DECISÃO")
    itens = [("previsível", "risco PREVISÍVEL"), ("estava encharcada", "barragem encharcada"),
             ("vazamentos e rachaduras", "vazamentos e rachaduras"), ("várias vezes", "várias vezes, ANTES")]
    for k, (fr, txt) in enumerate(itens):
        tk = s.w(fr)
        if t > tk:
            a = ease_out(prog(t, tk, 0.4))
            ellipse(c, 400, 320 + k * 150, 14, 14); rgb(c, ALERTA, a); c.fill()
            _t(c, txt, 450, 338 + k * 150, 54, CREME, font=SERIF, bold=True, a=a)


@cena("Ou seja a barragem avisou")
def s_avisou(c, t, s):
    cena_barragem(c, t, "dia", vazamento=0.6, trinca=0.6)
    legenda(c, t, s.t0 + 0.2, "A BARRAGEM AVISOU", 160, 56)
    eventos = [(s.w("ela avisou em dois mil e nove"), "2009"), (s.w("avisou de novo"), "2010–2012"), (s.w("e em dois mil e treze"), "2013")]
    for k, (tk, txt) in enumerate(eventos):
        if t > tk:
            c.save(); c.translate(500 + k * 460, 940); date_stamp(c, txt, 44, ALERTA if k == 2 else AMBER); c.restore()


@cena("No dia cinco de novembro de dois mil e quinze ela rompeu")
def s_rompeu(c, t, s):
    tr = s.t0 + 1.0
    if t < s.w("a lama apagou"):
        cena_barragem(c, t, "dia", rompida=prog(t, tr, 1.5), trinca=1.0)
        c.save(); c.translate(560, 170); date_stamp(c, "5 DE NOVEMBRO DE 2015", 42, ALERTA); c.restore()
    else:
        cena_bento(c, t, "nublado", soterrado=ease_out(prog(t, s.w("a lama apagou"), 3.0)))
        if t > s.w("matou dezenove"):
            contador(c, t, s.w("matou dezenove"), 19, 480, 300, 130, "mortos", col=ALERTA, dur=0.5)
        if t > s.w("seiscentos quilômetros"):
            contador(c, t, s.w("seiscentos quilômetros"), 600, 1440, 300, 130, "km até o mar", dur=0.8)


@cena("Eu sou o Investigador Hoje a gente")
def s_investigador(c, t, s):
    cena_barragem(c, t, "tarde")
    perito(c, t, 400, 1010, 1.05, poses=((0, "stand"), (s.t0 + 1.4, "point_r")), exprs=((0, "confident"), (s.t0 + 1.4, "think")))
    if t > s.w("cadeia de erros"):
        legenda(c, t, s.w("cadeia de erros"), "O ROMPIMENTO DA BARRAGEM DE FUNDÃO", 150, 42)
    if t > s.w("e entender por que"):
        _t(c, "por que tantos avisos não bastaram?", 1000, 270, 34, CREME)


# ================================================================ CAP 1: A BARRAGEM
@cena("Para entender essa história primeiro")
def s_cap1(c, t, s):
    cena_barragem(c, t, "dia")
    capitulo(c, t, s.t0 + 0.2, "1", "A BARRAGEM", 3.0)


@cena("Quando uma mineradora tira minério")
def s_rejeito(c, t, s):
    escuro(c, LAUDO_BG)
    painel_laudo(c, 200, 100, 1520, 880, "O QUE É REJEITO")
    # minério -> separação -> rejeito
    for k, (x, rot, col) in enumerate(((480, "minério de ferro", (0.45, 0.30, 0.26)), (960, "separação", (0.55, 0.56, 0.58)), (1440, "rejeito", REJEITO))):
        a = ease_out(prog(t, s.t0 + 0.5 + k * 1.6, 0.5))
        if a <= 0:
            continue
        ellipse(c, x, 520, 150 * a, 120 * a); rgb(c, col); c.fill()
        _t(c, rot, x, 720, 38, CREME, font=SERIF, bold=True, centro=True, a=a)
        if k < 2:
            seta(c, x + 180, 520, x + 300, 520, a, AMBER)
    if t > s.w("areia pó de minério"):
        _t(c, "areia + pó de minério + água", 1440, 790, 30, AMBER, centro=True)


@cena("Esse lugar é a barragem")
def s_paredao(c, t, s):
    cena_barragem(c, t, "dia")
    if t > s.w("um grande paredão"):
        _t(c, "paredão de terra", 960, 720, 40, CREME, font=SERIF, bold=True, centro=True)
        _t(c, "lago de lama", 960, 380, 40, CREME, font=SERIF, bold=True, centro=True)


@cena("A barragem de Fundão ficava em Mariana")
def s_samarco(c, t, s):
    cena_barragem(c, t, "dia")
    rotulo(c, t, s.t0 + 0.3, "BARRAGEM DE FUNDÃO", "Mariana (MG) · Samarco", x=120, y=180)
    if t > s.w("controlada por duas"):
        a = ease_out(prog(t, s.w("controlada por duas"), 0.5))
        rr(c, 1180, 820, 620, 190, 14); rgb(c, (0.06, 0.07, 0.09), 0.8 * a); c.fill()
        _t(c, "SAMARCO", 1490, 880, 44, CREME, font=SERIF, bold=True, centro=True, a=a)
        _t(c, "Vale (Brasil)  +  BHP (Inglaterra/Austrália)", 1490, 940, 26, AMBER, centro=True, a=a)
    if t > s.w("começou a funcionar"):
        c.save(); c.translate(1500, 200); date_stamp(c, "DESDE 2008", 40, AMBER); c.restore()


@cena("E ela foi construída de um jeito específico")
def s_montante(c, t, s):
    luz("dia"); escuro(c, LAUDO_BG)
    painel_laudo(c, 60, 60, 1800, 960, "ALTEAMENTO A MONTANTE")
    dg = 0.0
    if t > s.w("funciona assim"):
        dg = 6 * prog(t, s.w("o próximo degrau"), 6.0)
    corte_barragem(c, t, 1050, 860, 0.95, degraus=dg, rotulos=True)
    if t > s.w("por cima do próprio rejeito"):
        _t(c, "cada degrau novo em cima do rejeito", 1050, 180, 40, AMBER, font=SERIF, bold=True, centro=True)


@cena("É o método mais barato")
def s_sensivel(c, t, s):
    luz("dia"); escuro(c, LAUDO_BG)
    painel_laudo(c, 60, 60, 1800, 960, "O PONTO FRACO")
    sat = prog(t, s.w("se ele ficar encharcado"), 2.0)
    corte_barragem(c, t, 1050, 860, 0.95, degraus=6, saturacao=0.7 * sat, rotulos=True)
    if t > s.w("mais barato"):
        _t(c, "+ barato", 260, 200, 44, (0.40, 0.80, 0.45), font=SERIF, bold=True)
    if t > s.w("o mais sensível"):
        _t(c, "+ sensível", 260, 260, 44, ALERTA, font=SERIF, bold=True)
    if t > s.w("seco e firme"):
        _t(c, "o rejeito precisa ficar SECO", 1050, 180, 40, AMBER, font=SERIF, bold=True, centro=True)


@cena("Alguns quilômetros abaixo da barragem")
def s_bento(c, t, s):
    cena_bento(c, t, "dia", gente=True)
    rotulo(c, t, s.t0 + 0.4, "BENTO RODRIGUES", "distrito de Mariana · vale abaixo da barragem", x=120, y=180)
    if t > s.w("cerca de seiscentas"):
        contador(c, t, s.w("cerca de seiscentas"), 600, 1500, 300, 110, "moradores", dur=1.0)


# ================================================================ CAP 2: OS SINAIS
@cena("O primeiro aviso veio cedo")
def s_cap2(c, t, s):
    luz("dia"); escuro(c, LAUDO_BG)
    corte_barragem(c, t, 1050, 860, 0.95, degraus=1, dreno_ok=t < s.t0 + 2.5)
    capitulo(c, t, s.t0 + 0.2, "2", "OS SINAIS", 3.0)
    if t > s.t0 + 3:
        c.save(); c.translate(400, 220); date_stamp(c, "2009", 60, ALERTA); c.restore()


@cena("O sistema de drenagem no fundo")
def s_dreno(c, t, s):
    luz("dia"); escuro(c, LAUDO_BG)
    painel_laudo(c, 60, 60, 1800, 960, "O DRENO DE FUNDO")
    corte_barragem(c, t, 1050, 820, 0.95, degraus=1, dreno_ok=t < s.w("construído com defeitos"))
    marca = ease_out(prog(t, s.w("construído com defeitos"), 0.5))
    if marca > 0:
        _t(c, "DEFEITOS NO DRENO", 960, 960, 46, ALERTA, font=SERIF, bold=True, centro=True, a=marca)
    if t > s.w("já não podia mais"):
        carimbo(c, t, s.w("já não podia mais"), "PROJETO ORIGINAL INVIÁVEL", 1250, 300, 44)


@cena("Lembra da regra do método a montante")
def s_encharcado(c, t, s):
    luz("dia"); escuro(c, LAUDO_BG)
    painel_laudo(c, 60, 60, 1800, 960, "ÁGUA PRESA")
    corte_barragem(c, t, 1050, 860, 0.95, degraus=3, dreno_ok=False, saturacao=0.3 + 0.6 * prog(t, s.w("mais água ficou presa"), 4.0))
    if t > s.w("liquefação"):
        _t(c, "RISCO: LIQUEFAÇÃO", 1050, 190, 56, ALERTA, font=SERIF, bold=True, centro=True)


@cena("Liquefação é quando um material")
def s_liquefacao(c, t, s):
    escuro(c, LAUDO_BG)
    painel_laudo(c, 260, 100, 1400, 880, "LIQUEFAÇÃO")
    tl = s.w("perde a firmeza")
    p = ease_out(prog(t, tl, 1.2))
    # bloco de areia que vira líquido
    c.save(); c.translate(960, 720)
    h = 260 * (1 - 0.8 * p); w_ = 420 * (1 + 0.9 * p)
    rr(c, -w_ / 2, -h, w_, h, 20 + 60 * p); rgb(c, mix((0.70, 0.58, 0.42), LAMA, p)); c.fill()
    # casinha em cima
    yy = -h - 120 + 200 * ease_out(prog(t, s.w("desaba"), 0.8))
    c.save(); c.rotate(0.4 * ease_out(prog(t, s.w("desaba"), 0.8)))
    c.rectangle(-90, yy, 180, 120); rgb(c, (0.92, 0.88, 0.78)); c.fill()
    pg(c, [(-110, yy), (0, yy - 80), (110, yy)]); rgb(c, (0.70, 0.36, 0.24)); c.fill()
    c.restore(); c.restore()
    _t(c, "sólido" if p < 0.5 else "líquido", 960, 860, 46, CREME, font=SERIF, bold=True, centro=True)
    if t > s.w("um pequeno empurrão"):
        seta(c, 520, 600, 700, 600, 1, AMBER)


@cena("Nos anos seguintes a barragem continuou")
def s_recuo(c, t, s):
    luz("dia"); escuro(c, LAUDO_BG)
    painel_laudo(c, 60, 60, 1800, 960, "O RECUO DO EIXO")
    rec = ease_out(prog(t, s.w("foi recuado"), 1.5))
    corte_barragem(c, t, 1050, 860, 0.95, degraus=6, dreno_ok=False, saturacao=0.6, recuo=rec)
    if t > s.w("em dois mil e treze"):
        c.save(); c.translate(400, 220); date_stamp(c, "2013", 60, ALERTA); c.restore()


@cena("Segundo o relatório do Ministério Público")
def s_recuo2(c, t, s):
    luz("dia"); escuro(c, LAUDO_BG)
    painel_laudo(c, 60, 60, 1800, 960, "RELATÓRIO DO MP-MG")
    corte_barragem(c, t, 1050, 860, 0.95, degraus=6, dreno_ok=False, saturacao=0.65, recuo=1.0)
    if t > s.w("rejeitos mais fracos"):
        _t(c, "apoiado em rejeito fraco e encharcado", 1050, 190, 38, AMBER, font=SERIF, bold=True, centro=True)
    if t > s.w("foi exatamente ali"):
        a = ease_out(prog(t, s.w("foi exatamente ali"), 0.5))
        c.new_sub_path(); c.arc(1050 - 0.95 * 560, 860 - 0.95 * 400, 160, 0, 6.283); rgb(c, ALERTA, a); c.set_line_width(8); c.stroke()
        _t(c, "AQUI COMEÇOU", 1050 - 0.95 * 560, 860 - 0.95 * 400 - 190, 40, ALERTA, font=SERIF, bold=True, centro=True, a=a)


@cena("E também em dois mil e treze veio")
def s_pristino(c, t, s):
    cena_interior(c, t, "interior", "escritorio", seed=9)
    documento(c, 1180, 520, "ESTUDO · INSTITUTO PRÍSTINO (2013)",
              ["a pedido do Ministério Público", "", "risco de rompimento"] +
              (["mais monitoramento"] if t > s.w("recomendou mais") else []) +
              (["plano de emergência"] if t > s.w("um plano de emergência") else []), 1.05)
    perito(c, t, 380, 1030, poses=((0, "point_r"),), exprs=((0, "think"), (s.w("foi entregue"), "worried")))
    if t > s.w("foi entregue"):
        _t(c, "entregue à empresa e ao governo do estado", 1180, 990, 30, AMBER, centro=True)


@cena("A barragem continuou recebendo rejeito")
def s_continua(c, t, s):
    cena_barragem(c, t, "tarde", vazamento=0.5)
    legenda(c, t, s.t0 + 0.3, "E A BARRAGEM CONTINUOU CRESCENDO", 160, 44)


@cena("Agora pensa em quem morava lá embaixo")
def s_embaixo(c, t, s):
    cena_bento(c, t, "dia", gente=True)
    a = ease_out(prog(t, s.w("no caminho"), 0.8))
    if a > 0:
        seta(c, 150, 300, 700, 700, a, ALERTA)
        _t(c, "da barragem", 150, 270, 32, ALERTA, a=a)
    if t > s.w("poucos minutos"):
        legenda(c, t, s.w("poucos minutos"), "POUCOS MINUTOS PARA FUGIR", 150, 44)


@cena("Para isso existe uma coisa básica")
def s_sirene(c, t, s):
    vale(c, t, "dia", seed=8)
    sirene(c, t, 960, 600, 1.4, tocando=True)
    if t > s.w("rotas de fuga"):
        _t(c, "rota de fuga", 1400, 900, 38, CREME, font=SERIF, bold=True)


@cena("Bento Rodrigues não tinha sirene")
def s_sem_sirene(c, t, s):
    vale(c, t, "dia", seed=8)
    sirene(c, t, 960, 600, 1.4, riscada=True)
    if t > s.w("baixo risco"):
        carimbo(c, t, s.w("baixo risco"), "BAIXO RISCO", 1450, 320, 64, AMBER)


# ================================================================ CAP 3: A TARDE
@cena("Cinco de novembro de dois mil e quinze Uma quinta")
def s_cap3(c, t, s):
    cena_barragem(c, t, "tarde")
    capitulo(c, t, s.t0 + 0.2, "3", "A TARDE DE 5 DE NOVEMBRO", 3.0)


@cena("Naquela tarde a região registrou")
def s_tremores(c, t, s):
    sh = 6 * math.sin(t * 50) * (1 if int(t * 2) % 3 == 0 else 0)
    c.save(); c.translate(sh, 0)
    cena_barragem(c, t, "tarde", trinca=0.5)
    c.restore()
    # sismógrafo
    rr(c, 1260, 820, 560, 200, 12); rgb(c, (0.96, 0.95, 0.90)); c.fill()
    c.move_to(1280, 920)
    for k in range(80):
        amp = 40 if (k // 12) % 3 == 1 else 6
        c.line_to(1280 + k * 6.5, 920 + amp * math.sin(k * 2.3 + t * 8))
    rgb(c, ALERTA); c.set_line_width(3); c.stroke()
    _t(c, "pequenos tremores", 1540, 860, 26, (0.3, 0.3, 0.3), centro=True)


@cena("Mas a barragem já estava no limite")
def s_limite(c, t, s):
    luz("dia"); escuro(c, LAUDO_BG)
    painel_laudo(c, 60, 60, 1800, 960, "PAINEL INTERNACIONAL")
    corte_barragem(c, t, 1050, 860, 0.95, degraus=6, dreno_ok=False, saturacao=0.85, recuo=1.0)
    if t > s.w("só aceleraram"):
        _t(c, "os tremores só deram o último empurrão", 1050, 190, 38, AMBER, font=SERIF, bold=True, centro=True)


@cena("Por volta das três e meia da tarde")
def s_ruptura(c, t, s):
    tl = s.w("liquefação")
    if t < s.w("a barragem de fundão se desfez"):
        luz("dia"); escuro(c, LAUDO_BG)
        corte_barragem(c, t, 1050, 860, 0.95, degraus=6, dreno_ok=False, saturacao=0.85, recuo=1.0, liquefeita=prog(t, tl, 2.0))
        c.save(); c.translate(400, 200); date_stamp(c, "~15h30", 64, ALERTA); c.restore()
    else:
        t2 = s.w("a barragem de fundão se desfez")
        cena_barragem(c, t, "tarde", rompida=prog(t, t2, 1.5))
        onda_lama(c, t, -60 + 2100 * ease_out(prog(t, t2 + 0.5, 4.0)), 980, 300)
        if t > s.w("quarenta milhões"):
            contador(c, t, s.w("quarenta milhões"), 40, 960, 260, 130, "milhões de m³ de lama", dur=0.8)


@cena("Para ter uma ideia é lama")
def s_piscinas(c, t, s):
    escuro(c, LAUDO_BG)
    piscinas(c, t, s.t0 + 0.3, 960, 500)


@cena("A onda passou por cima de outra barragem")
def s_santarem(c, t, s):
    vale(c, t, "tarde", seed=12)
    barragem_paisagem(c, t, 1300, 720, 600, 0.6, 3, rompida=prog(t, s.w("também foi danificada"), 1.0), depth=0.2)
    _t(c, "SANTARÉM", 1300, 520, 40, CREME, font=SERIF, bold=True, centro=True)
    onda_lama(c, t, -60 + 1300 * ease_out(prog(t, s.t0, 3.0)) + 700 * ease_out(prog(t, s.w("e ganhou ainda"), 3.0)), 980, 320)


@cena("E seguiu na direção de Bento Rodrigues")
def s_direcao(c, t, s):
    cena_bento(c, t, "tarde", lama_x=-60 + 300 * ease_out(prog(t, s.t0, 3.0)))


@cena("Sem sirene o aviso foi dado por telefone")
def s_telefone(c, t, s):
    cena_interior(c, t, "interior", "casa", seed=4)
    telefone_antigo(c, t, 640, 590, 1.3, tocando=True)
    if t > s.w("ligou para a prefeitura"):
        lista = [(s.w("ligou para a prefeitura"), "prefeitura"), (s.w("para a defesa civil"), "Defesa Civil"), (s.w("alguns moradores"), "alguns moradores")]
        for k, (tk, txt) in enumerate(lista):
            if t > tk:
                _t(c, txt, 1000, 360 + k * 80, 48, (0.25, 0.2, 0.16), font=SERIF, bold=True)


@cena("No vilarejo muita gente só percebeu")
def s_fuga(c, t, s):
    vale(c, t, "tarde", seed=8)
    vilarejo(c, t, 960, 880, 1.0, 8, seed=4)
    for k in range(9):
        x = 1500 - ((t - s.t0) * 120 + k * 120) % 1300
        f = dict(FIGURINO[["moderno", "moderna", "catador"][k % 3]]); f["pele"] = list(PELES)[k % 4]
        if f.get("mulher"):
            f["camisa"] = f["cor_roupa"]
        boneco(c, t, 1900 - x, 1010 - (k % 3) * 20, 0.4, poses=((0, "run"),), exprs=((0, "shocked"),), look=0.8, andar=True, fid=120 + k, **f)
    c.rectangle(0, 0, W, H); rgb(c, LAMA_CLARA, 0.12 + 0.06 * math.sin(t * 2)); c.fill()


@cena("A lama chegou e engoliu Bento Rodrigues")
def s_engoliu(c, t, s):
    cena_bento(c, t, "nublado", soterrado=ease_out(prog(t, s.t0 + 0.3, 5.0)))
    if t > s.w("deixou de existir"):
        legenda(c, t, s.w("deixou de existir"), "BENTO RODRIGUES DEIXOU DE EXISTIR", 160, 44)


@cena("Dezenove pessoas morreram Catorze")
def s_19(c, t, s):
    escuro(c)
    contador(c, t, s.t0 + 0.1, 19, 960, 440, 220, "pessoas morreram", col=ALERTA, dur=0.6, fundo=False)
    if t > s.w("catorze eram"):
        _t(c, "14 trabalhadores", 640, 780, 54, CREME, font=SERIF, bold=True, centro=True)
    if t > s.w("cinco eram moradores"):
        _t(c, "5 moradores", 1280, 780, 54, CREME, font=SERIF, bold=True, centro=True)


@cena("Muita gente em Bento Rodrigues sobreviveu")
def s_vizinho(c, t, s):
    vale(c, t, "nublado", seed=8)
    casa_simples(c, 700, 900, 420, 260, col=(0.92, 0.88, 0.78))
    boneco(c, t, 1250, 1010, 0.62, poses=((0, "point_l"),), exprs=((0, "shocked"),), look=-0.8, fid=140, **FIGURINO["moderno"])
    if t > s.w("não porque um alarme"):
        sirene(c, t, 1620, 560, 0.7, riscada=True)


# ================================================================ CAP 4: O RIO
@cena("E a lama não parou ali")
def s_cap4(c, t, s):
    mapa_rio_doce(c, t, 0.1)
    capitulo(c, t, s.t0 + 0.2, "4", "O RIO", 3.0)


@cena("Ela desceu pelos rios da região")
def s_rio(c, t, s):
    mapa_rio_doce(c, t, 0.1 + 0.6 * prog(t, s.t0, 10.0))
    if t > s.w("água cortada"):
        _t(c, "água cortada nas cidades", 300, 300, 34, ALERTA, font=SERIF, bold=True)
    if t > s.w("peixes morreram"):
        _t(c, "peixes mortos", 300, 360, 34, ALERTA, font=SERIF, bold=True)
    if t > s.w("perdeu o sustento"):
        _t(c, "pesca e lavoura perdidas", 300, 420, 34, ALERTA, font=SERIF, bold=True)


@cena("No dia vinte e um de novembro")
def s_mar(c, t, s):
    mapa_rio_doce(c, t, 0.7 + 0.3 * prog(t, s.t0, 3.0))
    c.save(); c.translate(500, 200); date_stamp(c, "21/11: 16 DIAS DEPOIS", 42, ALERTA); c.restore()
    if t > s.w("mais de seiscentos"):
        contador(c, t, s.w("mais de seiscentos"), 600, 900, 900, 90, "km de rio atingidos", dur=0.8)


@cena("É considerado o maior desastre ambiental")
def s_maior(c, t, s):
    mapa_rio_doce(c, t, 1.0)
    c.rectangle(0, 0, W, H); rgb(c, (0.05, 0.05, 0.06), 0.55); c.fill()
    _t(c, "o maior desastre ambiental", 960, 500, 70, CREME, font=SERIF, bold=True, centro=True)
    _t(c, "da história do Brasil", 960, 590, 56, AMBER, font=SERIF, bold=True, centro=True)


# ================================================================ CAP 5: A CADEIA DE ERROS
ROTULOS = ["método|a montante", "dreno|com defeito", "recuo|de 2013", "avisos|ignorados", "baixo|risco", "nenhuma|sirene"]


@cena("Agora vamos fazer o que a gente")
def s_cap5(c, t, s):
    escuro(c, LAUDO_BG)
    corrente(c, t, s.t0 + 0.5, rotulos=ROTULOS, ativos=0)
    capitulo(c, t, s.t0 + 0.2, "5", "A CADEIA DE ERROS", 3.0)


def _elo(n, frase, fundo):
    @cena(frase)
    def s(c, t, s_):
        fundo(c, t, s_)
        c.rectangle(0, 760, W, H); rgb(c, (0.05, 0.06, 0.08), 0.86); c.fill()
        c.save(); c.translate(0, 300)
        corrente(c, t, s_.t0 - 5, rotulos=ROTULOS, ativos=n, y=560)
        c.restore()
        _t(c, f"ELO {n}", 120, 150, 70, ALERTA, font=SERIF, bold=True)
    return s


def _f1(c, t, s):
    luz("dia"); escuro(c, LAUDO_BG); corte_barragem(c, t, 1050, 700, 0.8, degraus=6)


def _f2(c, t, s):
    luz("dia"); escuro(c, LAUDO_BG); corte_barragem(c, t, 1050, 700, 0.8, degraus=2, dreno_ok=False, saturacao=0.5)


def _f3(c, t, s):
    luz("dia"); escuro(c, LAUDO_BG); corte_barragem(c, t, 1050, 700, 0.8, degraus=6, dreno_ok=False, saturacao=0.6, recuo=1.0)


def _f4(c, t, s):
    cena_barragem(c, t, "tarde", vazamento=0.8, trinca=0.8)


def _f5(c, t, s):
    cena_interior(c, t, "interior", "escritorio", seed=9)
    carimbo(c, t, s.t0 + 0.5, "BAIXO RISCO", 1200, 380, 70, AMBER)


def _f6(c, t, s):
    vale(c, t, "dia", seed=8); sirene(c, t, 960, 450, 1.1, riscada=True)


_elo(1, "Elo número um o método", _f1)
_elo(2, "Elo número dois a drenagem", _f2)
_elo(3, "Elo número três o recuo", _f3)
_elo(4, "Elo número quatro os avisos", _f4)
_elo(5, "Elo número cinco a classificação", _f5)
_elo(6, "Elo número seis nenhuma sirene", _f6)


@cena("Repara que os tremores daquela tarde")
def s_soma(c, t, s):
    escuro(c, LAUDO_BG)
    corrente(c, t, s.t0 - 5, rotulos=ROTULOS, ativos=6, y=480)
    if t > s.w("o último empurrão"):
        _t(c, "tremores = só o último empurrão", 960, 820, 52, AMBER, font=SERIF, bold=True, centro=True)
    if t > s.w("seis anos"):
        _t(c, "6 anos de avisos (2009–2015)", 960, 920, 38, CREME, centro=True)


# ================================================================ CAP 6: O QUE FICOU
@cena("E aqui vem a parte mais dura")
def s_cap6(c, t, s):
    cena_barragem(c, t, "crepusculo")
    c.rectangle(0, 0, W, H); rgb(c, (0.04, 0.04, 0.06), 0.55); c.fill()
    capitulo(c, t, s.t0 + 0.2, "6", "O QUE FICOU", 3.0)


@cena("Três anos depois em janeiro")
def s_brumadinho(c, t, s):
    vale(c, t, "nublado", seed=21)
    barragem_paisagem(c, t, 960, 600, 1000, 0.8, 6, rompida=prog(t, s.w("se rompeu em brumadinho"), 1.5), depth=0.2)
    if t > s.w("se rompeu em brumadinho"):
        onda_lama(c, t, -60 + 2100 * ease_out(prog(t, s.w("se rompeu em brumadinho") + 0.5, 4.0)), 980, 280)
    c.save(); c.translate(500, 170); date_stamp(c, "BRUMADINHO · JANEIRO DE 2019", 40, ALERTA); c.restore()
    if t > s.w("mesmo método"):
        _t(c, "mesmo método: a montante", 1180, 250, 34, AMBER, font=SERIF, bold=True)
    if t > s.w("duzentas e setenta"):
        contador(c, t, s.w("duzentas e setenta"), 270, 960, 420, 150, "mortos", col=ALERTA, dur=1.0)


@cena("Só depois disso em dois mil e vinte")
def s_lei(c, t, s):
    cena_interior(c, t, "interior", "escritorio", seed=9)
    documento(c, 1180, 520, "LEI 14.066/2020", ["Política de Segurança de Barragens", "", "PROIBIDO: método a montante",
                                                "barragens existentes: desativar"], 1.05)
    perito(c, t, 380, 1030, poses=((0, "present"),), exprs=((0, "think"),))
    if t > s.t0 + 0.5:
        _t(c, "só depois de Mariana e Brumadinho", 1180, 990, 30, AMBER, centro=True)


@cena("Na Justiça o caso de Mariana")
def s_justica(c, t, s):
    escuro(c, LAUDO_BG)
    eventos = [(s.w("em outubro de dois mil e vinte e quatro"), "OUT 2024", "acordo de R$ 170 bilhões", CREME),
               (s.w("no mês seguinte"), "NOV 2024", "absolvição criminal (falta de provas)", AMBER),
               (s.w("o ministério público federal recorreu"), "", "MPF recorre", CREME)]
    painel_laudo(c, 200, 120, 1520, 840, "NA JUSTIÇA")
    for k, (tk, d, txt, col) in enumerate(eventos):
        if t > tk:
            a = ease_out(prog(t, tk, 0.4))
            _t(c, d, 330, 340 + k * 180, 44, ALERTA, font=SERIF, bold=True, a=a)
            _t(c, txt, 640, 340 + k * 180, 48, col, font=SERIF, bold=True, a=a)


@cena("E em novembro de dois mil e vinte e cinco veio")
def s_londres2(c, t, s):
    luz("dia"); ceu(c, t, passaros=False, seed=9)
    c.rectangle(0, 760, W, H); rgb(c, P((0.62, 0.60, 0.58))); c.fill()
    tribunal(c, t, 960, 660, 1.0, "HIGH COURT · LONDRES")
    if t > s.w("considerou a bhp"):
        carimbo(c, t, s.w("considerou a bhp"), "BHP RESPONSÁVEL", 960, 900, 60)
    if t > s.w("vai recorrer"):
        _t(c, "a empresa vai recorrer", 960, 1040, 32, CREME, centro=True)


@cena("Bento Rodrigues nunca voltou a existir")
def s_novo_bento(c, t, s):
    cena_bento(c, t, "tarde", soterrado=1.0)
    c.rectangle(0, 0, W, H); rgb(c, (0.1, 0.08, 0.06), 0.3); c.fill()
    if t > s.w("um vilarejo novo"):
        rotulo(c, t, s.w("um vilarejo novo"), "NOVO BENTO", "reassentamento, construído anos depois", x=120, y=180)


# ================================================================ FECHAMENTO
@cena("A barragem de Fundão rompeu numa quinta")
def s_anunciada(c, t, s):
    cena_barragem(c, t, "crepusculo", vazamento=0.5, trinca=0.5)
    c.rectangle(0, 0, W, H); rgb(c, (0.05, 0.05, 0.08), 0.35); c.fill()
    if t > s.w("muito antes"):
        _t(c, "anunciada muito antes", 960, 200, 56, AMBER, font=SERIF, bold=True, centro=True)


@cena("Foi anunciada quando a drenagem falhou")
def s_recap(c, t, s):
    escuro(c)
    itens = [("foi anunciada quando a drenagem", "2009: o dreno falhou"), ("foi anunciada quando o eixo", "2013: o recuo sobre rejeito fraco"),
             ("foi anunciada por escrito", "2013: o estudo que alertou"), ("e foi anunciada toda vez", "um vilarejo avisado por telefone")]
    for k, (frase, txt) in enumerate(itens):
        tk = s.w(frase)
        if t > tk:
            a = ease_out(prog(t, tk, 0.4))
            ellipse(c, 300, 300 + k * 150, 16, 16); rgb(c, ALERTA, a); c.fill()
            _t(c, txt, 350, 316 + k * 150, 48, CREME, font=SERIF, bold=True, a=a)


@cena("A barragem deu seis anos de sinais")
def s_frase(c, t, s):
    escuro(c, (0.05, 0.06, 0.08))
    _t(c, "A barragem deu seis anos de sinais.", 960, 460, 70, CREME, font=SERIF, bold=True, centro=True)
    if t > s.w("a sirene"):
        _t(c, "A sirene, ninguém instalou.", 960, 600, 64, AMBER, font=SERIF, bold=True, centro=True,
           a=ease_out(prog(t, s.w("a sirene"), 0.5)))


@cena("E a pergunta que fica")
def s_pergunta(c, t, s):
    vale(c, t, "crepusculo", seed=5)
    barragem_paisagem(c, t, 1250, 620, 800, 0.8, 5, depth=0.3)
    perito(c, t, 360, 1010, poses=((0, "think"),), exprs=((0, "think"),))
    legenda(c, t, s.t0 + 0.6, "TEM BARRAGEM PERTO DA SUA CIDADE?", 160, 44)


@cena("Me conta nos comentários")
def s_comente(c, t, s):
    vale(c, t, "tarde", seed=5)
    perito(c, t, 420, 1010, 1.05, poses=((0, "present"),), exprs=((0, "happy"),))
    c.save(); c.translate(1150, 420); placa(c, "ONDE VOCÊ ESTAVA EM 2015?", "COMENTE", size=44); c.restore()


@cena("Eu sou o Investigador E aqui no Tragédia")
def s_final(c, t, s):
    escuro(c, (0.05, 0.06, 0.08))
    rglow(c, 960, 480, 600, LAMA, 0.12)
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

SFX = []
