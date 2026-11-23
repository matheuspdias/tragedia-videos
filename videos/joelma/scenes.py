"""TRAGÉDIA ANUNCIADA · Edifício Joelma, São Paulo (1974). Cenas ancoradas nas palavras da narração (palavras.json)."""
import json, os, re
from engine import *
from ilustrado import *
from tragedia import *
from tragedia import _t
from incendio import *

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


ANDRAUS_COL = (0.78, 0.80, 0.82)
JOELMA_Y = 1000


def joelma(c, t, x=1150, fogo=None, s=1.0, **kw):
    c.save(); c.translate(x, JOELMA_Y); c.scale(s, s)
    top = arranha_ceu(c, t, 0, 0, 380, 25, 30, fogo=fogo, garagem=10, **kw)
    c.restore()
    return top


def andraus(c, t, x=1150, fogo=None, s=1.0, **kw):
    c.save(); c.translate(x, JOELMA_Y); c.scale(s, s)
    top = arranha_ceu(c, t, 0, 0, 340, 32, 22, fogo=fogo, garagem=0, col=ANDRAUS_COL, heliponto=True, telhado="laje", **kw)
    c.restore()
    return top


def tudo(a0=11):
    return lambda a: 1.0 if a > a0 else 0.0


# ================================================================ ABERTURA: O AVISO DO ANDRAUS
@cena("Em fevereiro de mil novecentos e setenta e dois São Paulo")
def s_tv(c, t, s):
    cena_interior(c, t, "interior", "escritorio", seed=3)
    c.rectangle(0, 0, W, H); rgb(c, (0.10, 0.08, 0.06), 0.35); c.fill()

    def tela(cc, tt):
        luz("nublado"); cc.rectangle(0, 0, 520, 400); rgb(cc, (0.60, 0.62, 0.64)); cc.fill()
        cc.save(); cc.translate(260, 420); cc.scale(0.42, 0.42)
        arranha_ceu(cc, tt, 0, 0, 340, 32, 22, fogo=lambda a: 1.0 if 2 <= a <= 30 else 0, garagem=0, col=ANDRAUS_COL, heliponto=True, telhado="laje")
        cc.restore()
        ao_vivo(cc, tt, 30, 40)
    tv_antiga(c, t, 1180, 520, 1.05, tela)
    c.save(); c.translate(560, 170); date_stamp(c, "FEVEREIRO DE 1972", 44, ALERTA); c.restore()
    figurantes(c, t, 1060, n=3, s=0.5, seed=4, x0=200, x1=700, andando=False, figurinos=["moderno", "moderna"])


@cena("Era o Edifício Andraus")
def s_andraus(c, t, s):
    rua_centro(c, t, "nublado", seed=11)
    ceu_fumaca(c, 0.4)
    top = andraus(c, t, 1150, fogo=lambda a: 1.0 if a >= 2 else 0)
    rotulo(c, t, s.t0 + 0.3, "EDIFÍCIO ANDRAUS", "32 andares · centro de São Paulo", x=120, y=180)
    if t > s.w("dezesseis pessoas"):
        contador(c, t, s.w("dezesseis pessoas"), 16, 420, 520, 120, "mortes", col=ALERTA, dur=0.5)
    if t > s.w("um heliponto no topo"):
        hp = ease_out(prog(t, s.w("um heliponto no topo"), 0.6))
        helicoptero(c, t, 1150 + 260 * (1 - hp), top - 160 + 20 * math.sin(t * 2), 0.55)
        c.arc(1150, top - 82, 110, 0, 6.283); rgb(c, AMBER, 0.9 * hp); c.set_line_width(6); c.stroke()
        legenda(c, t, s.w("um heliponto no topo"), "O PRÉDIO TINHA HELIPONTO", 960 - 0 if False else 980, 40)


@cena("Depois daquele dia a cidade começou a discutir")
def s_discutir(c, t, s):
    cena_interior(c, t, "interior", "escritorio", seed=5)
    for k, (x, fig) in enumerate(((560, "moderno"), (960, "medico"), (1360, "moderno"))):
        f = dict(FIGURINO[fig]); f["pele"] = ["clara", "media", "morena"][k]
        boneco(c, t, x, 1020, 0.62, poses=((0, ["point_r", "think", "shrug"][k]), (s.t0 + 2 + k, ["think", "point_l", "hips"][k])),
               exprs=((0, "think"),), look=0.5 - k * 0.5, fid=70 + k, gravata=(0.2, 0.2, 0.25), **{kk: v for kk, v in f.items() if kk != "gravata"})
    c.save(); c.translate(960, 220); placa(c, "E SE UM ARRANHA-CÉU PEGAR FOGO?", "o debate de 1972", size=42); c.restore()
    if t > s.w("discutiu mas"):
        carimbo(c, t, s.w("quase nada mudou"), "NADA MUDOU", 1500, 520, 64)


@cena("Dois anos depois a pouco mais")
def s_joelma_intro(c, t, s):
    rua_centro(c, t, "nublado", seed=21)
    chuva(c, t, 0.25)
    t_f = s.w("pegou fogo numa")
    top = joelma(c, t, 1300, fogo=fogo_subindo(t, t_f, 12, 2.5))
    rotulo(c, t, s.t0 + 0.3, "1974", "25 andares · centro de São Paulo", x=120, y=180)
    itens = [(s.w("ele não tinha alarme"), "ALARME"), (s.w("não tinha sprinklers"), "SPRINKLERS"),
             (s.w("não tinha luz"), "LUZ DE EMERGÊNCIA"), (s.w("tinha uma escada"), "SÓ UMA ESCADA"), (s.w("e não tinha heliponto"), "HELIPONTO")]
    lista_nao_tinha(c, t, itens, x=110, y=400, size=40, dy=84)


@cena("Cento e oitenta e sete pessoas morreram")
def s_187(c, t, s):
    escuro(c)
    rglow(c, 960, 540, 700, FOGO2, 0.10)
    contador(c, t, s.t0 + 0.1, 187, 960, 560, 230, "pessoas morreram", col=ALERTA, dur=1.6, fundo=False)


@cena("Eu sou o Investigador Hoje")
def s_investigador(c, t, s):
    rua_centro(c, t, "nublado", seed=21)
    joelma(c, t, 1350, fogo=None)
    perito(c, t, 420, 1010, 1.05, poses=((0, "stand"), (s.t0 + 1.4, "point_r")), exprs=((0, "confident"), (s.t0 + 1.4, "think")))
    if t > s.w("cadeia de erros"):
        legenda(c, t, s.w("cadeia de erros"), "O INCÊNDIO DO EDIFÍCIO JOELMA", 150, 44)
    if t > s.w("e entender por"):
        _t(c, "por que o aviso de 1972 não salvou ninguém?", 1000, 270, 34, CREME, centro=False)


# ================================================================ CAP 1: O PRÉDIO NOVO
@cena("O Edifício Joelma ficava no centro")
def s_cap1(c, t, s):
    rua_centro(c, t, "dia", seed=31)
    joelma(c, t, 1200)
    figurantes(c, t, 1010, n=10, s=0.3, seed=5, x0=100, x1=1800, figurinos=["moderno", "moderna"])
    capitulo(c, t, s.t0 + 0.2, "1", "O PRÉDIO NOVO", 3.0)
    if t > s.t0 + 3.3:
        rotulo(c, t, s.t0 + 3.3, "AV. NOVE DE JULHO", "esq. com a R. Santo Antônio · Praça da Bandeira", x=120, y=180)
    if t > s.w("ficou pronto em"):
        c.save(); c.translate(1640, 260); date_stamp(c, "PRONTO EM 1971", 40, AMBER); c.restore()


@cena("Os andares de baixo eram garagem")
def s_usos(c, t, s):
    luz("dia"); escuro(c, LAUDO_BG)
    painel_laudo(c, 160, 80, 1600, 920, "EDIFÍCIO JOELMA · 25 ANDARES")
    y, ha, w = 960, 32, 520
    corte_predio(c, t, 760, y, w, 25, ha, elevadores=True)
    if t > s.w("garagem"):
        c.rectangle(500, y - 10 * ha, 520, 10 * ha); rgb(c, AMBER, 0.25); c.fill()
        marca_andar(c, 760, y, ha, 5, "garagem (até o 10º)", 1)
    if t > s.w("os de cima eram"):
        c.rectangle(500, y - 25 * ha, 520, 15 * ha); rgb(c, CREME, 0.12); c.fill()
        marca_andar(c, 760, y, ha, 18, "escritórios", 1)
    if t > s.w("o crefisul"):
        _t(c, "BANCO CREFISUL", 1080, 300, 44, AMBER, font=SERIF, bold=True)
        _t(c, "ainda terminando a mudança", 1080, 350, 28, CREME)


@cena("Por fora o prédio era moderno")
def s_concreto(c, t, s):
    rua_centro(c, t, "dia", seed=31)
    joelma(c, t, 1200)
    perito(c, t, 380, 1010, poses=((0, "point_r"),), exprs=((0, "confident"), (s.w("o problema"), "worried")))
    if t > s.w("concreto armado"):
        legenda(c, t, s.w("concreto armado"), "CONCRETO ARMADO: RESISTE AO FOGO", 140, 40)
    if t > s.w("o problema estava"):
        a = ease_out(prog(t, s.w("o problema estava"), 0.5))
        c.arc(1200, 600, 260, 0, 6.283); rgb(c, ALERTA, a); c.set_line_width(8); c.stroke()
        _t(c, "E DENTRO?", 1200, 260, 52, ALERTA, font=SERIF, bold=True, centro=True, a=a)


@cena("Os escritórios eram divididos por divisórias")
def s_dentro(c, t, s):
    escritorio_70(c, t)
    marcas = [("divisórias de madeira", "DIVISÓRIAS DE MADEIRA", 290, 300), ("o forro era feito", "FORRO DE CELULOSE", 960, 180),
              ("no chão carpete", "CARPETE", 960, 980), ("nas janelas cortinas", "CORTINAS", 1520, 170),
              ("as mesas e as cadeiras", "MESAS DE MADEIRA", 560, 700)]
    for frase, txt, x, y in marcas:
        tk = s.w(frase)
        if t > tk:
            a = ease_out(prog(t, tk, 0.3))
            c.save(); c.translate(x, y); c.scale(0.6 + 0.4 * a, 0.6 + 0.4 * a); hl(c, txt, 0, 0, 34); c.restore()


@cena("Ou seja um prédio de concreto recheado")
def s_recheado(c, t, s):
    escuro(c, LAUDO_BG)
    painel_laudo(c, 360, 120, 1200, 840, "CORTE DE UM ANDAR")
    c.rectangle(460, 260, 1000, 600); rgb(c, (0.55, 0.56, 0.58)); c.fill()
    c.rectangle(500, 300, 920, 520); rgb(c, FOGO2, 0.25 + 0.15 * math.sin(t * 3)); c.fill()
    _t(c, "concreto", 960, 290, 30, LAUDO_BG, font=SERIF, bold=True, centro=True)
    _t(c, "material que queima fácil", 960, 580, 46, CREME, font=SERIF, bold=True, centro=True)


@cena("E agora repara na lista")
def s_lista(c, t, s):
    luz("dia"); escuro(c, LAUDO_BG)
    painel_laudo(c, 100, 80, 760, 920, "CORTE DO PRÉDIO")
    corte_predio(c, t, 480, 960, 420, 25, 32, destaque_escada=t > s.w("a única saída"))
    itens = [(s.w("não tinha alarme de"), "ALARME DE INCÊNDIO"), (s.w("não tinha sprinklers aqueles"), "SPRINKLERS"),
             (s.w("não tinha luz de emergência não"), "LUZ DE EMERGÊNCIA"), (s.w("não tinha escada de emergência"), "ESCADA PROTEGIDA"),
             (s.w("e o telhado não"), "HELIPONTO")]
    lista_nao_tinha(c, t, itens, x=980, y=230, size=44, dy=100)
    if t > s.w("aqueles chuveiros"):
        a = ease_out(prog(t, s.w("aqueles chuveiros"), 0.3)) * (1 - ease_out(prog(t, s.w("não tinha luz de emergência não"), 0.3)))
        _t(c, "(chuveiros automáticos)", 1060, 410, 28, AMBER, a=a)
    if t > s.w("a única saída"):
        _t(c, "UMA ESCADA SÓ", 480, 1050, 40, AMBER, font=SERIF, bold=True, centro=True)


@cena("Nada disso era ilegal na época")
def s_legal(c, t, s):
    cena_interior(c, t, "interior", "escritorio", seed=9)
    documento(c, 1250, 520, "CÓDIGO DE OBRAS (1934)", ["regras de construção", "sem exigências para", "incêndio em", "arranha-céus"], 1.0)
    perito(c, t, 380, 1030, poses=((0, "shrug"),), exprs=((0, "think"),))
    if t > s.w("nada disso"):
        carimbo(c, t, s.w("ilegal"), "TUDO DENTRO DA LEI", 1250, 900, 48, AMBER)


@cena("Só que a cidade já tinha recebido")
def s_aviso(c, t, s):
    rua_centro(c, t, "nublado", seed=11)
    ceu_fumaca(c, 0.3)
    andraus(c, t, 1300, fogo=lambda a: 1.0 if a >= 2 else 0)
    perito(c, t, 420, 1010, poses=((0, "point_r"),), exprs=((0, "worried"),))
    legenda(c, t, s.t0 + 0.4, "O AVISO", 160, 56)


@cena("No dia vinte e quatro de fevereiro")
def s_andraus_fogo(c, t, s):
    rua_centro(c, t, "nublado", seed=11)
    t0 = s.w("o fogo começou no segundo")
    f = lambda a: 0.0 if t < t0 else (min(1.0, ((t - t0) * 4 - (a - 2)) / 3 + 0.3) if (t - t0) * 4 >= a - 2 and a >= 2 else 0.0)
    andraus(c, t, 1200, fogo=f)
    c.save(); c.translate(560, 170); date_stamp(c, "24 DE FEVEREIRO DE 1972", 42, ALERTA); c.restore()
    if t > s.w("muita gente fez"):
        legenda(c, t, s.w("muita gente fez"), "SEM ESCADA, AS PESSOAS SUBIRAM", 280, 40)


@cena("No topo esperava um heliponto")
def s_heliponto(c, t, s):
    luz("nublado"); ceu(c, t, passaros=False, seed=4)
    ceu_fumaca(c, 0.5)
    c.save(); c.translate(960, 1500); c.scale(1.6, 1.6)
    top = arranha_ceu(c, t, 0, 0, 340, 32, 22, fogo=lambda a: 1.0 if a < 22 else 0, garagem=0, col=ANDRAUS_COL, heliponto=True, telhado="laje", gente_telhado=18, fumaca_on=False)
    c.restore()
    p = ease_out(prog(t, s.w("helicópteros resgataram") if t > s.t0 else s.t0, 1.5))
    helicoptero(c, t, 1500 - 400 * p, 300 - 60 * p + 10 * math.sin(t * 2), 0.9)
    if t > s.w("preferência do arquiteto"):
        rotulo(c, t, s.w("preferência do arquiteto"), "O HELIPONTO", "estava lá por gosto do arquiteto", x=120, y=180)


@cena("Dezesseis pessoas morreram Trezentas")
def s_andraus_saldo(c, t, s):
    escuro(c)
    contador(c, t, s.t0 + 0.1, 16, 640, 520, 170, "mortes", col=ALERTA, dur=0.5)
    contador(c, t, s.w("trezentas e trinta"), 330, 1280, 520, 170, "feridos", dur=1.0)
    if t > s.w("a tragédia passou"):
        def tela(cc, tt):
            cc.rectangle(0, 0, 520, 400); rgb(cc, (0.55, 0.56, 0.58)); cc.fill()
            ao_vivo(cc, tt, 30, 40)
            _t(cc, "ANDRAUS", 260, 230, 50, (0.95, 0.95, 0.95), font=SERIF, bold=True, centro=True)
        tv_antiga(c, t, 960, 880, 0.45, tela)


@cena("Depois do Andraus especialistas começaram")
def s_nao_virou_lei(c, t, s):
    cena_interior(c, t, "interior", "escritorio", seed=9)
    documento(c, 1250, 520, "PROPOSTAS (1972)", ["escadas protegidas", "alarmes", "rotas de fuga"], 1.0, "ARQUIVADO" if t > s.w("não virou lei") else None)
    perito(c, t, 380, 1030, poses=((0, "point_r"), (s.w("não virou lei"), "hips")), exprs=((0, "think"), (s.w("não virou lei"), "angry")))
    if t > s.w("prédios como o joelma"):
        legenda(c, t, s.w("prédios como o joelma"), "E PRÉDIOS COMO O JOELMA CONTINUAVAM IGUAIS", 140, 36)


# ================================================================ CAP 2: O AR-CONDICIONADO
@cena("Na manhã de primeiro de fevereiro")
def s_cap2(c, t, s):
    rua_centro(c, t, "nublado", seed=21)
    chuva(c, t, 0.35)
    joelma(c, t, 1250)
    figurantes(c, t, 1010, n=12, s=0.3, seed=7, x0=100, x1=1800, figurinos=["moderno", "moderna"])
    capitulo(c, t, s.t0 + 0.2, "2", "O AR-CONDICIONADO", 3.0)
    if t > s.t0 + 3.3:
        c.save(); c.translate(560, 170); date_stamp(c, "SEXTA, 1º DE FEVEREIRO DE 1974", 40, ALERTA); c.restore()
    if t > s.w("mais de setecentas"):
        contador(c, t, s.w("mais de setecentas"), 756, 450, 520, 120, "pessoas no prédio", dur=1.0)


@cena("No décimo segundo andar num escritório")
def s_aparelho(c, t, s):
    escritorio_70(c, t)
    a = ease_out(prog(t, s.w("ar condicionado"), 0.6))
    c.arc(1330, 700, 220, 0, 6.283); rgb(c, AMBER, a); c.set_line_width(8); c.stroke()
    rotulo(c, t, s.t0 + 0.3, "12º ANDAR", "escritório do banco", x=120, y=180)


@cena("Segundo os relatos do caso")
def s_quadro(c, t, s):
    escuro(c, (0.06, 0.08, 0.11))
    c.save(); c.translate(960, 540); c.scale(1.5, 1.5); c.translate(-960, -560)
    quadro_eletrico(c, t, 960, 560, desvio=prog(t, s.w("então ele foi ligado"), 2.0)); c.restore()


@cena("Na prática isso quer dizer")
def s_sem_protecao(c, t, s):
    escuro(c, (0.06, 0.08, 0.11))
    c.save(); c.translate(960, 540); c.scale(1.5, 1.5); c.translate(-960, -560)
    quadro_eletrico(c, t, 960, 560, desvio=1.0); c.restore()
    if t > s.w("e alguma coisa deu"):
        carimbo(c, t, s.w("e alguma coisa deu"), "DEU ERRADO", 1300, 900, 56)


@cena("Por volta das oito e cinquenta")
def s_curto(c, t, s):
    tf = s.w("curto circuito")
    escritorio_70(c, t, fogo=0.0)
    ar_condicionado(c, t, 1330, 700, 1.0, faisca=prog(t, tf, 0.4) if t > tf else 0)
    c.save(); c.translate(560, 170); date_stamp(c, "8h50", 60, ALERTA); c.restore()


@cena("As faíscas atingiram as cortinas")
def s_espalha(c, t, s):
    p = prog(t, s.t0, 6.0)
    escritorio_70(c, t, fogo=0.15 + 0.85 * p, fumaca_a=0.75 * prog(t, s.w("uma fumaça preta"), 1.5))
    particulas(c, t, "brasas", 40, seed=3)


@cena("Aqui entra o elo mais cruel")
def s_escada(c, t, s):
    luz("dia"); escuro(c, LAUDO_BG)
    painel_laudo(c, 360, 60, 1200, 960, "A ESCADA ÚNICA")
    tf = s.w("o ar quente")
    corte_predio(c, t, 960, 990, 520, 25, 34, fogo=lambda a: 1.0 if a == 12 else 0, destaque_escada=True,
                 escada_fumaca=prog(t, tf, 4.0), ate_andar_fumaca=25)
    marca_andar(c, 960, 990, 34, 12, "12º: o fogo", -1, ALERTA)
    if t > s.w("funciona como uma chaminé"):
        _t(c, "CHAMINÉ", 1320, 300, 60, AMBER, font=SERIF, bold=True)


@cena("Cerca de quinze minutos depois")
def s_preso(c, t, s):
    luz("dia"); escuro(c, LAUDO_BG)
    painel_laudo(c, 360, 60, 1200, 960, "~15 MINUTOS DEPOIS")
    gente = [(a, dx) for a in range(14, 25, 2) for dx in (-200, -150, 150)]
    corte_predio(c, t, 960, 990, 520, 25, 34, fogo=lambda a: 1.0 if 12 <= a <= 13 else 0, destaque_escada=True,
                 escada_fumaca=1.0, gente=gente, seta_saida=prog(t, s.w("quem estava acima"), 0.6))
    if t > s.w("quem estava acima"):
        _t(c, "sem caminho para baixo", 1260, 180, 36, ALERTA, font=SERIF, bold=True)


@cena("Ao mesmo tempo o fogo saía pelas janelas")
def s_fachada(c, t, s):
    rua_centro(c, t, "nublado", seed=21)
    chuva(c, t, 0.2)
    ceu_fumaca(c, 0.4 * prog(t, s.t0, 4))
    joelma(c, t, 1150, fogo=fogo_subindo(t, s.t0 - 1, 12, 0.9))
    if t > s.w("em cerca de vinte"):
        legenda(c, t, s.w("em cerca de vinte"), "~20 MINUTOS: O PRÉDIO TOMADO", 140, 44)


@cena("Nos primeiros minutos cerca de trezentas")
def s_saem(c, t, s):
    rua_centro(c, t, "nublado", seed=21)
    joelma(c, t, 1300, fogo=tudo(11))
    for k in range(8):
        x = 1100 - ((t - s.t0) * 80 + k * 90) % 900
        f = dict(FIGURINO["moderno" if k % 2 else "moderna"]); f["pele"] = list(PELES)[k % 4]
        if f.get("mulher"):
            f["camisa"] = f["cor_roupa"]
        boneco(c, t, x, 1010, 0.42, poses=((0, "run"),), exprs=((0, "worried"),), look=-0.8, andar=True, fid=90 + k, **f)
    contador(c, t, s.t0 + 0.5, 300, 420, 260, 100, "saíram pela escada nos primeiros minutos", dur=1.0)


@cena("Outras trezentas foram retiradas pelos elevadores")
def s_elevadores(c, t, s):
    luz("dia"); escuro(c, LAUDO_BG)
    painel_laudo(c, 360, 60, 1200, 960, "OS ELEVADORES")
    corte_predio(c, t, 960, 990, 520, 25, 34, fogo=tudo(11), escada_fumaca=1.0)
    # cabines subindo e descendo
    for k in range(2):
        ph = (math.sin(t * 0.7 + k * 2) + 1) / 2
        cy = 990 - 34 - ph * 34 * 20
        c.rectangle(960 + 150 + k * 50 + 2, cy, 32, 34); rgb(c, AMBER); c.fill()
    contador(c, t, s.t0 + 0.3, 300, 1400, 300, 80, "pelos elevadores", dur=1.0)
    if t > s.w("os quatro ascensoristas"):
        _t(c, "4 ascensoristas", 1300, 420, 32, CREME)
    if t > s.w("nunca usar elevador"):
        legenda(c, t, s.w("nunca usar elevador"), "HOJE: NUNCA USE ELEVADOR NUM INCÊNDIO", 1000, 36)


@cena("Treze pessoas tentaram fugir")
def s_treze(c, t, s):
    luz("dia")
    c.rectangle(0, 0, W, H); rgb(c, P((0.70, 0.78, 0.84))); c.fill()
    chao(c, t, 860, "grama", seed=3)
    c.save(); c.translate(960, 900); c.scale(1.7, 1.7); c.translate(-960, -880); tumulos_sem_nome(c, t, 13, 880); c.restore()
    c.rectangle(0, 0, W, H); rgb(c, (0.15, 0.15, 0.18), 0.25); c.fill()
    if t > s.w("seus corpos"):
        rotulo(c, t, s.w("seus corpos"), "13 VÍTIMAS NUNCA IDENTIFICADAS", "Cemitério da Vila Alpina, São Paulo", x=120, y=180)


# ================================================================ CAP 3: OS BOMBEIROS
@cena("Os bombeiros foram chamados")
def s_cap3(c, t, s):
    rua_centro(c, t, "nublado", seed=21)
    ceu_fumaca(c, 0.6)
    joelma(c, t, 1250, fogo=tudo(11))
    x = 2200 - 1400 * ease_out(prog(t, s.w("as primeiras equipes"), 2.5))
    caminhao_escada(c, t, x, 1040, 0.7)
    capitulo(c, t, s.t0 + 0.2, "3", "OS BOMBEIROS", 3.0)
    if t > s.w("nove e dez"):
        c.save(); c.translate(500, 200); date_stamp(c, "9h10", 54, AMBER); c.restore()
    if t > s.w("às nove e meia"):
        c.save(); c.translate(600, 340); date_stamp(c, "9h30: CHAMAS NO TOPO", 40, ALERTA); c.restore()


@cena("E aí os bombeiros deram de cara")
def s_nao_sobem(c, t, s):
    luz("dia"); escuro(c, LAUDO_BG)
    painel_laudo(c, 360, 60, 1200, 960, "ATÉ ONDE OS BOMBEIROS CHEGARAM")
    corte_predio(c, t, 960, 990, 520, 25, 34, fogo=tudo(11), escada_fumaca=1.0,
                 bombeiro_ate=11 if t > s.w("décimo primeiro") else None)


@cena("Do lado de fora as escadas Magirus")
def s_magirus(c, t, s):
    rua_centro(c, t, "nublado", seed=21)
    ceu_fumaca(c, 0.6)
    top = joelma(c, t, 1250, fogo=tudo(11))
    ang = 1.05 * ease_out(prog(t, s.t0 + 0.3, 2.5))
    caminhao_escada(c, t, 620, 1040, 0.8, ang=ang, comp=0.6 + 0.4 * ease_out(prog(t, s.t0 + 1.5, 2.0)))
    if t > s.w("não alcançavam"):
        alc = 1040 - 0.8 * (180 + 560 * math.sin(1.05))
        c.rectangle(900, alc - 2, 640, 4); rgb(c, AMBER); c.fill()
        _t(c, "alcance da escada", 1560, alc + 10, 26, AMBER)
        _t(c, "gente presa aqui", 1560, top + 120, 26, ALERTA)


@cena("Dentro do prédio sem caminho")
def s_janelas(c, t, s):
    rua_centro(c, t, "nublado", seed=21)
    ceu_fumaca(c, 0.7)
    jg = [(a, k) for a in (16, 18, 19, 21, 23) for k in (1, 4, 7)]
    joelma(c, t, 1250, fogo=lambda a: 1.0 if 11 < a < 15 else (0.4 if a < 22 else 0.2), janelas_gente=jg)
    if t > s.w("lá embaixo"):
        multidao(c, t, 1060, n=18, s=0.36, seed=3, x0=0, x1=1000,
                 cartaz="CALMA!" if t > s.w("levantavam cartazes") else None)


@cena("Mesmo assim o desespero")
def s_desespero(c, t, s):
    rua_centro(c, t, "nublado", seed=21)
    ceu_fumaca(c, 0.7)
    joelma(c, t, 1250, fogo=tudo(11))
    c.rectangle(0, 0, W, H); rgb(c, (0.05, 0.05, 0.07), 0.55); c.fill()
    if t > s.w("nenhuma delas"):
        legenda(c, t, s.w("nenhuma delas"), "NENHUMA SOBREVIVEU", 540, 56)


# ================================================================ CAP 4: O TELHADO
@cena("Enquanto isso quem conseguiu fez")
def s_cap4(c, t, s):
    luz("dia"); escuro(c, LAUDO_BG)
    painel_laudo(c, 360, 60, 1200, 960, "PARA ONDE IR?")
    p = prog(t, s.w("subiu"), 3.0)
    gente = [(min(25, a + int(p * 12)), dx) for a in range(14, 25, 2) for dx in (-200, 150)]
    corte_predio(c, t, 960, 990, 520, 25, 34, fogo=tudo(11), escada_fumaca=1.0, gente=gente,
                 telhado_gente=int(30 * p))
    capitulo(c, t, s.t0 + 0.2, "4", "O TELHADO", 3.0)


@cena("Cento e setenta e uma pessoas chegaram")
def s_171(c, t, s):
    luz("nublado"); ceu(c, t, passaros=False, seed=4)
    ceu_fumaca(c, 0.6)
    c.save(); c.translate(960, 2300); c.scale(2.4, 2.4)
    arranha_ceu(c, t, 0, 0, 380, 25, 30, fogo=tudo(11), garagem=10, gente_telhado=40, fumaca_on=False)
    c.restore()
    contador(c, t, s.t0 + 0.2, 171, 960, 260, 120, "pessoas no telhado", dur=1.0)


@cena("Só que o telhado do Joelma")
def s_comparacao(c, t, s):
    luz("nublado"); escuro(c, (0.10, 0.12, 0.15))
    c.save(); c.translate(520, 1000); c.scale(0.95, 0.95)
    arranha_ceu(c, t, 0, 0, 340, 32, 22, garagem=0, col=ANDRAUS_COL, heliponto=True, telhado="laje")
    c.restore()
    c.save(); c.translate(1400, 1000); c.scale(0.95, 0.95)
    arranha_ceu(c, t, 0, 0, 380, 25, 30, garagem=10)
    c.restore()
    _t(c, "ANDRAUS · 1972", 520, 130, 40, CREME, font=SERIF, bold=True, centro=True)
    _t(c, "JOELMA · 1974", 1400, 130, 40, CREME, font=SERIF, bold=True, centro=True)
    _t(c, "heliponto", 520, 190, 30, AMBER, centro=True)
    _t(c, "telhas de amianto", 1400, 190, 30, ALERTA, centro=True)


@cena("Não havia heliponto A cobertura")
def s_helis(c, t, s):
    luz("nublado"); ceu(c, t, passaros=False, seed=4)
    ceu_fumaca(c, 0.8)
    c.save(); c.translate(960, 2450); c.scale(2.6, 2.6)
    arranha_ceu(c, t, 0, 0, 380, 25, 30, fogo=tudo(11), garagem=10, gente_telhado=30, fumaca_on=False)
    c.restore()
    fumaca(c, t, 700, 760, 260, 900, 0.9, seed=4, vento=80)
    fumaca(c, t, 1200, 760, 240, 900, 0.8, seed=8, vento=80)
    if t > s.w("helicópteros foram mandados"):
        helicoptero_fumaca(c, t, 1550, 260, 0.9, 2.0)
        helicoptero_fumaca(c, t + 3, 320, 330, 0.7, 2.0)
    if t > s.w("impediram o resgate"):
        legenda(c, t, s.w("impediram o resgate"), "SEM LUGAR PARA POUSAR", 960, 44)


@cena("Lá em cima o calor ficou insuportável")
def s_telhas(c, t, s):
    luz("nublado"); ceu(c, t, passaros=False, seed=4)
    ceu_fumaca(c, 0.9)
    # telhado de perto: telhas onduladas cinza
    c.rectangle(0, 620, W, H); rgb(c, P((0.58, 0.58, 0.56))); c.fill()
    for k in range(0, W, 60):
        c.rectangle(k, 620, 26, H); rgb(c, P((0.50, 0.50, 0.48))); c.fill()
    pg(c, [(0, 620), (W, 560), (W, 620)]); rgb(c, P((0.42, 0.40, 0.38))); c.fill()
    fumaca(c, t, 400, 700, 300, 800, 0.8, seed=2)
    fumaca(c, t, 1500, 700, 300, 800, 0.7, seed=5)
    particulas(c, t, "cinzas", 50, seed=4)
    if t > s.w("cerca de oitenta"):
        contador(c, t, s.w("cerca de oitenta"), 80, 960, 380, 140, "encontradas vivas sob as telhas", dur=0.8)


@cena("Por volta das dez e meia")
def s_apaga(c, t, s):
    rua_centro(c, t, "nublado", seed=21)
    p = prog(t, s.t0, 6.0)
    fade = 1 - p
    joelma(c, t, 1200, fogo=lambda a: (1.0 if a > 11 else 0) * fade)
    ceu_fumaca(c, 0.5 * fade + 0.2)
    if t > s.w("perto das três"):
        c.save(); c.translate(500, 200); date_stamp(c, "~15h: FOGO APAGADO", 44, AMBER); c.restore()
    if t > s.w("catorze andares"):
        legenda(c, t, s.w("catorze andares"), "14 ANDARES DESTRUÍDOS", 300, 44)


@cena("Só então bombeiros policiais e equipes")
def s_resgate(c, t, s):
    rua_centro(c, t, "nublado", seed=21)
    c.save(); c.translate(1300, JOELMA_Y)
    arranha_ceu(c, t, 0, 0, 380, 25, 30, fogo=lambda a: 0.05 if a > 11 else 0, garagem=10, col=(0.40, 0.36, 0.34), fumaca_on=False)
    c.restore()
    for k, fig in enumerate(("bombeiro", "policial", "medico", "bombeiro")):
        boneco(c, t, 300 + k * 170, 1010, 0.5, poses=((0, "stand"),), exprs=((0, "worried"),), look=0.8, fid=110 + k, **FIGURINO[fig])


@cena("O número exato de mortos nunca")
def s_saldo(c, t, s):
    escuro(c)
    if t > s.w("as estimativas vão"):
        _t(c, "179 a 189", 960, 300, 70, CREME, font=SERIF, bold=True, centro=True)
        _t(c, "estimativas", 960, 350, 30, AMBER, centro=True)
    if t > s.w("o número mais citado"):
        contador(c, t, s.w("o número mais citado"), 187, 640, 640, 170, "mortos", col=ALERTA, dur=0.8)
    if t > s.w("mais de trezentas"):
        contador(c, t, s.w("mais de trezentas"), 300, 1280, 640, 170, "+ feridos", dur=0.8)


@cena("Na época foi o incêndio em arranha céu")
def s_recorde(c, t, s):
    escuro(c, LAUDO_BG)
    painel_laudo(c, 260, 160, 1400, 760, "INCÊNDIOS EM PRÉDIOS ALTOS")
    _t(c, "1974 · Edifício Joelma", 380, 400, 54, CREME, font=SERIF, bold=True)
    _t(c, "o mais mortal do mundo, na época", 380, 460, 32, AMBER)
    if t > s.w("até hoje"):
        _t(c, "Só o 11 de setembro (2001) matou mais", 380, 640, 40, CREME, a=ease_out(prog(t, s.w("até hoje"), 0.4)))


# ================================================================ CAP 5: A CADEIA DE ERROS
ROTULOS = ["aviso|ignorado", "fiação|improvisada", "recheio|inflamável", "escada|única", "sem alarme,|sprinkler, luz", "telhado|sem saída"]


@cena("Agora vamos fazer o que")
def s_cap5(c, t, s):
    escuro(c, LAUDO_BG)
    corrente(c, t, s.t0 + 0.5, rotulos=ROTULOS, ativos=0)
    capitulo(c, t, s.t0 + 0.2, "5", "A CADEIA DE ERROS", 3.0)


def _elo(n, frase, fundo):
    @cena(frase)
    def s(c, t, s_):
        fundo(c, t, s_)
        c.rectangle(0, 760, W, H); rgb(c, (0.05, 0.06, 0.08), 0.86); c.fill()
        c.save(); c.translate(0, 300); c.scale(1, 1)
        corrente(c, t, s_.t0 - 5, rotulos=ROTULOS, ativos=n, y=560)
        c.restore()
        _t(c, f"ELO {n}", 120, 150, 70, ALERTA, font=SERIF, bold=True)
    return s


def _f1(c, t, s):
    rua_centro(c, t, "nublado", seed=11); andraus(c, t, 1300, fogo=lambda a: 1.0 if a > 1 else 0)


def _f2(c, t, s):
    escuro(c, (0.06, 0.08, 0.11)); quadro_eletrico(c, t, 960, 460, desvio=1.0)


def _f3(c, t, s):
    escritorio_70(c, t, fogo=0.4)


def _f4(c, t, s):
    luz("dia"); escuro(c, LAUDO_BG); corte_predio(c, t, 960, 760, 520, 25, 26, fogo=lambda a: 1.0 if a == 12 else 0, destaque_escada=True, escada_fumaca=1.0)


def _f5(c, t, s):
    escritorio_70(c, t, fogo=0.0, fumaca_a=0.9)
    lista_nao_tinha(c, t, [(s.t0 + 1, "ALARME"), (s.w("sem sprinklers"), "SPRINKLERS"), (s.w("sem luz"), "LUZ DE EMERGÊNCIA")], x=1060, y=260, size=40, dy=86)


def _f6(c, t, s):
    luz("nublado"); ceu(c, t, passaros=False, seed=4); ceu_fumaca(c, 0.8)
    c.save(); c.translate(960, 2450); c.scale(2.6, 2.6)
    arranha_ceu(c, t, 0, 0, 380, 25, 30, fogo=tudo(11), garagem=10, gente_telhado=30, fumaca_on=False); c.restore()
    helicoptero_fumaca(c, t, 1500, 240, 0.8, 2.0)


_elo(1, "Elo número um o aviso", _f1)
_elo(2, "Elo número dois a instalação", _f2)
_elo(3, "Elo número três o recheio", _f3)
_elo(4, "Elo número quatro uma escada", _f4)
_elo(5, "Elo número cinco nenhum sistema", _f5)
_elo(6, "Elo número seis o telhado", _f6)


@cena("Repara que nenhum desses elos")
def s_soma(c, t, s):
    escuro(c, LAUDO_BG)
    corrente(c, t, s.t0 - 5, rotulos=ROTULOS, ativos=6, y=480)
    if t > s.w("foi a soma"):
        _t(c, "= A SOMA", 960, 820, 80, AMBER, font=SERIF, bold=True, centro=True)
    if t > s.w("virou uma das maiores"):
        _t(c, "um curto-circuito virou uma das maiores tragédias do Brasil", 960, 920, 36, CREME, centro=True)


# ================================================================ CAP 6: O QUE FICOU
@cena("Depois do Andraus a cidade discutiu")
def s_cap6(c, t, s):
    escuro(c)
    capitulo(c, t, s.t0 + 0.2, "6", "O QUE FICOU", 3.0)
    if t > s.w("discutiu por dois anos"):
        _t(c, "ANDRAUS: 2 ANOS DE DEBATE", 960, 340, 56, CREME, font=SERIF, bold=True, centro=True)
    if t > s.w("agiu em seis dias"):
        _t(c, "JOELMA: 6 DIAS PARA AGIR", 960, 800, 56, AMBER, font=SERIF, bold=True, centro=True)


@cena("No dia sete de fevereiro de mil")
def s_decreto(c, t, s):
    cena_interior(c, t, "interior", "escritorio", seed=9)
    linhas = []
    for frase, ln in (("rotas de fuga definidas", "rotas de fuga"), ("a lotação máxima", "lotação máxima"),
                      ("escadas de segurança", "escadas resistentes ao fogo"), ("equipamentos de combate", "equipamentos de combate"),
                      ("exigiu sprinklers", "SPRINKLERS (1ª vez)")):
        if t > s.w(frase):
            linhas.append(ln)
    documento(c, 1150, 540, "DECRETO 10.878", ["7 de fevereiro de 1974", ""] + linhas, 1.05)
    perito(c, t, 380, 1030, poses=((0, "present"),), exprs=((0, "confident"),))


@cena("O decreto também deu à Prefeitura")
def s_existentes(c, t, s):
    rua_centro(c, t, "dia", seed=41)
    for k, x in enumerate((420, 960, 1500)):
        c.save(); c.translate(x, JOELMA_Y); c.scale(0.7, 0.7)
        arranha_ceu(c, t, 0, 0, 340, 22, 30, garagem=0, col=[(0.80, 0.76, 0.70), (0.70, 0.72, 0.76), (0.82, 0.74, 0.66)][k], telhado="laje")
        c.restore()
    if t > s.w("e até de fechar"):
        carimbo(c, t, s.w("e até de fechar"), "ADEQUE OU FECHE", 960, 300, 64)


@cena("Logo depois a Prefeitura criou")
def s_contru(c, t, s):
    cena_cidade(c, t, "dia", seed=70)
    predio_orgao(c, 560, 880, 820, 320, "CONTRU · SEGURANÇA DAS EDIFICAÇÕES")
    rotulo(c, t, s.t0 + 0.4, "1975", "nasce o Contru · novo Código de Obras", x=120, y=180)
    if t > s.w("pelo resto do país"):
        legenda(c, t, s.w("pelo resto do país"), "NORMAS CONTRA INCÊNDIO MUDAM NO PAÍS", 1000, 38)


@cena("O prédio ficou fechado por quatro anos")
def s_praca(c, t, s):
    rua_centro(c, t, "dia", seed=31)
    joelma(c, t, 1200, col=(0.80, 0.74, 0.66), nome="PRAÇA DA BANDEIRA" if t > s.w("ganhou um novo") else None)
    rotulo(c, t, s.t0 + 0.3, "4 ANOS FECHADO", "reconstruído e reaberto", x=120, y=180)


@cena("E tem um detalhe que fecha")
def s_folha(c, t, s):
    rua_centro(c, t, "dia", seed=41)
    c.save(); c.translate(560, JOELMA_Y); c.scale(0.9, 0.9)
    arranha_ceu(c, t, 0, 0, 340, 32, 22, garagem=0, col=ANDRAUS_COL, heliponto=True, telhado="laje"); c.restore()
    c.save(); c.translate(1360, JOELMA_Y); c.scale(0.9, 0.9)
    arranha_ceu(c, t, 0, 0, 380, 25, 30, garagem=10, col=(0.80, 0.74, 0.66)); c.restore()
    c.save(); c.translate(960, 150); date_stamp(c, "INSPEÇÃO DE 2013", 42, AMBER); c.restore()
    if t > s.w("passou com folga"):
        carimbo(c, t, s.w("passou com folga"), "APROVADO", 1360, 560, 60, (0.20, 0.62, 0.30))
    if t > s.w("foi reprovado"):
        carimbo(c, t, s.w("foi reprovado"), "REPROVADO", 560, 560, 60)


# ================================================================ FECHAMENTO
@cena("O incêndio do Joelma começou com um ar")
def s_anunciado(c, t, s):
    escuro(c)
    ar_condicionado(c, t, 960, 560, 1.4, faisca=0.4 + 0.3 * math.sin(t * 5))
    if t > s.w("foi anunciado bem antes"):
        _t(c, "anunciado bem antes", 960, 300, 52, AMBER, font=SERIF, bold=True, centro=True)


@cena("Foi anunciado quando o aparelho")
def s_recap(c, t, s):
    escuro(c)
    itens = [("foi anunciado quando o aparelho", "um ar-condicionado ligado por fora do quadro"),
             ("foi anunciado quando o prédio", "um prédio entregue com uma escada só"),
             ("e foi anunciado ao vivo", "um aviso ao vivo, dois anos antes: o Andraus")]
    for k, (frase, txt) in enumerate(itens):
        tk = s.w(frase)
        if t > tk:
            a = ease_out(prog(t, tk, 0.4))
            c.arc(300, 330 + k * 160, 16, 0, 6.283); rgb(c, ALERTA, a); c.fill()
            _t(c, txt, 350, 346 + k * 160, 48, CREME, font=SERIF, bold=True, a=a)


@cena("A lei veio em seis dias")
def s_frase(c, t, s):
    escuro(c, (0.05, 0.06, 0.08))
    _t(c, "A lei veio em seis dias.", 960, 460, 76, CREME, font=SERIF, bold=True, centro=True)
    if t > s.w("o aviso tinha"):
        _t(c, "O aviso tinha vindo dois anos antes.", 960, 600, 64, AMBER, font=SERIF, bold=True, centro=True,
           a=ease_out(prog(t, s.w("o aviso tinha"), 0.5)))


@cena("E a pergunta que fica")
def s_pergunta(c, t, s):
    rua_centro(c, t, "crepusculo", seed=55)
    perito(c, t, 360, 1010, poses=((0, "think"),), exprs=((0, "think"),))
    legenda(c, t, s.t0 + 0.6, "O SEU PRÉDIO TEM SAÍDA?", 160, 48)


@cena("Me conta nos comentários")
def s_comente(c, t, s):
    rua_centro(c, t, "tarde", seed=12)
    perito(c, t, 420, 1010, 1.05, poses=((0, "present"),), exprs=((0, "happy"),))
    c.save(); c.translate(1150, 420); placa(c, "VOCÊ CONHECIA ESSA HISTÓRIA?", "COMENTE", size=44); c.restore()


@cena("Eu sou o Investigador E aqui no Tragédia")
def s_final(c, t, s):
    escuro(c, (0.05, 0.06, 0.08))
    rglow(c, 960, 480, 600, FOGO2, 0.08)
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
