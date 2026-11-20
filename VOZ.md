# Voz oficial do canal Tragédia Anunciada: "O Perito"

| Item | Valor |
| --- | --- |
| Voz | **TA Perito B** (voz desenhada no HeyGen: ~55 anos, grave, levemente rouca, tom de documentário) |
| voice_id | `4d7b0dd73c9a4fa68f494a4cf0d31c10` |
| Motor | HeyGen Voice `create_speech` (modelo escolhido pelo plano) |
| Idioma | `language: "pt"` |
| Velocidade | **1.2** (escolhida pelo Matheus: na velocidade normal fica lenta e tediosa) |
| Timestamps | `withTimestamps: true` (resposta tem `original_words` com início/fim de cada palavra) |

- Tags que funcionam: `[serious]`, `[thoughtful]`, `[sad]`, `[mysterious]`, `[pause]`. Nunca `[whispers]`.
- Números por extenso.
- Blocos de até ~4.500 caracteres, cortando nas mudanças de capítulo.
- Junte sempre com `juntar_cortando.py` (corta silêncios longos e recalcula os tempos das palavras).
