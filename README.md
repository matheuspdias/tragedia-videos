# tragedia-videos

Motor de vídeos do canal **Tragédia Anunciada** (@tragedia.anunciada): documentários ilustrados de desastres reais, contados pela cadeia de erros que levou a cada um. Narrador fixo: **O Investigador** (função `perito_i`).

Base: motor do Ponto Cego (`engine.py`, `ilustrado.py`, `render.py`, `cortes.py`, `capas.py`). O README do Ponto Cego (repo `pontocego-videos`) documenta todas as peças herdadas. Aqui fica o que é próprio do canal.

## Identidade fixa
- **Narrador**: `perito_i(c, t, x, y, s, poses, exprs, look)` — capacete branco, jaqueta azul-marinho, óculos, barba curta, prancheta na mão esquerda. Em geral à esquerda (x≈330, pés em y≈1010).
- **Voz**: ver `VOZ.md` (TA Perito B, HeyGen Voice, velocidade 1.2).
- **Ritmo**: ~180 palavras/min, sem pausas longas (as referências do nicho no Brasil ficam entre 180 e 240). Só 2 ou 3 `[pause]` por vídeo, nos momentos de impacto.
- **Estrutura do roteiro**: abertura com o aviso ignorado → capítulos → "A CADEIA DE ERROS" (elos numerados) → o que ficou → pergunta ao espectador → encerramento: "Eu sou o Investigador. E aqui no Tragédia Anunciada, toda tragédia deu sinais antes. A gente mostra quais ninguém ouviu."
- **Paleta "laudo"** (peças técnicas): fundo ardósia `LAUDO_BG`, traço `CREME`, destaque `AMBER`, alerta `ALERTA`.
- **Cuidado com vítimas**: nada gráfico; mortes viram memorial (nomes, datas, vela). Fatos conferidos em fonte oficial; o que é ilustrativo é dito na tela (ex.: "MAPA ILUSTRATIVO").

## Kit do canal (`tragedia.py`)
- Cenários: `cena_cidade(hora)` (cidade brasileira anos 80), `predio_ruina`, `cena_ferro_velho`, `interior_casa`, `casa_simples`, `predio_orgao(nome, cruz=)`, `estadio`, `helicoptero`, `onibus`.
- Objetos: `capsula(brilho, furada)`, `maquina_teleterapia(desmontada)`, `carrinho_mao`, `sucata`, `po_brilhante`, `medidor(nivel)`, `conteiner`, `mesa_cozinha`, `documento(titulo, linhas, carimbo_txt)`, `placa_texto`.
- Símbolos: `trevo` (radiação) e `simbolo_iso` (ISO 21482).
- Peças de laudo: `painel_laudo`, `diagrama_cabeca`, `mapa_goiania` (troque `LOCAIS` por vídeo), `linha_tempo(eventos=[(pos, rótulo, topo)])`, `corrente(ativos, rotulos)` (cadeia de erros), `contador` (número que sobe, com fundo), `carimbo`, `capitulo(num, nome)`, `seta`.
- Figurinos novos em `ilustrado.py`: `bombeiro operario catador tecnico policial moderno moderna`; chapéu `capacete`; `avental=False` tira o avental dos vestidos.

## Fluxo de um vídeo
1. Roteiro em `videos/<slug>/roteiro.txt` (fatos conferidos, fontes no topo).
2. Narração no HeyGen (`create_speech`, `withTimestamps: true`), um bloco por parte; salve cada resposta em `videos/<slug>/ts/blocoN.json`. O Matheus baixa os `.wav` e anexa.
3. `python juntar_cortando.py videos/<slug> out/<slug>_narracao.wav b1.wav b2.wav ...` — junta, corta silêncios longos e gera `palavras.json` e `transcricao.txt`.
4. `scenes.py` com cenas **ancoradas em frases** (`@cena("frase da narração")` e `s.w("frase")` para eventos dentro da cena): os tempos saem do `palavras.json`, sem conta de m:ss. Modelo: `videos/cesio-137/scenes.py`.
5. Prévias: `python render.py sheet videos/<slug>/scenes.py out/sheet.png t1 t2 ...`; render: `python render.py build videos/<slug>/scenes.py out/<slug>_narracao.wav out/<slug>.mp4`.
6. Thumbnails: `videos/<slug>/thumb/thumb.py` (Perito em close via `thumb_close(..., quem=PER)`).

Fila de temas: `automacao/temas.md`.
