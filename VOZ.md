# Voz oficial do canal Tragédia Anunciada: "O Investigador"

| Item | Valor |
| --- | --- |
| Voz | **TA Perito B** (nome interno da voz no HeyGen; voz desenhada no HeyGen: ~55 anos, grave, levemente rouca, tom de documentário) |
| voice_id | `4d7b0dd73c9a4fa68f494a4cf0d31c10` |
| Motor | HeyGen Voice `create_speech` (modelo escolhido pelo plano) |
| Idioma | `language: "pt"` |
| Velocidade | **1.2** (escolhida pelo Matheus: na velocidade normal fica lenta e tediosa) |
| Timestamps | `withTimestamps: true` (resposta tem `original_words` com início/fim de cada palavra) |

- Tags que funcionam: `[serious]`, `[thoughtful]`, `[sad]`, `[mysterious]`, `[pause]`. Nunca `[whispers]`.
- Números por extenso.
- Blocos de até ~4.500 caracteres, cortando nas mudanças de capítulo.
- Junte sempre com `juntar_cortando.py` (corta silêncios longos e recalcula os tempos das palavras).

- O nome do narrador é **"o Investigador"** (o Matheus trocou de "Perito" porque soava como "Peto"). Frase de apresentação gerada à parte em `out/audio/investigador.wav` e encaixada com emenda no silêncio.

- **Sem corte de silêncios** (decisão de nov/2026): a voz em 1.2x já sai com ~180 palavras/min; o corte só tirava ~2 s por vídeo e foi a origem dos estalos. `juntar_cortando.py` por padrão só junta os blocos (0,45 s entre eles) e gera `palavras.json`. Edição de áudio só quando necessária (troca de frase), sempre cortando onde a energia mostra silêncio real — os tempos do HeyGen vêm ~0,3 s adiantados.
