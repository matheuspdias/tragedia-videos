"""Roda DENTRO da GitHub Action `tts`: gera os blocos de narração pela API do HeyGen (heygen-voice-1),
com velocidade e timestamps, e salva:
    media/<slug>/bN.mp3            (áudio do bloco)
    videos/<slug>/ts/blocoN.json   (resposta completa da API, com os tempos de cada palavra)
Pedido: tts_in/<slug>.json = {"slug": "...", "voice": "<voice_id>", "speed": 1.2, "blocos": ["texto 1", "texto 2", ...]}
Precisa do segredo HEYGEN_API_KEY. Erros vão para tts_out/<slug>_erros.txt (e a Action termina com falha)."""
import json, os, sys, time, urllib.error, urllib.request

KEY = os.environ.get('HEYGEN_API_KEY', '')
API = 'https://api.heygen.com/v3/models/audio/tts'


def speech(voice, text, speed):
    body = json.dumps({'text': text, 'voice_id': voice, 'model': 'heygen-voice-1', 'language': 'pt', 'speed': speed,
                       'with_timestamps': True,
                       'output_format': {'encoding': 'mp3', 'sample_rate_hertz': 44100, 'bitrate_bps': 192000}}).encode()
    for attempt in range(5):
        req = urllib.request.Request(API, data=body, method='POST',
                                     headers={'X-Api-Key': KEY, 'Content-Type': 'application/json', 'Accept': 'application/json'})
        try:
            with urllib.request.urlopen(req, timeout=300) as r:
                j = json.load(r)
                return j.get('data', j)
        except urllib.error.HTTPError as e:
            msg = e.read().decode(errors='replace')[:600]
            if e.code in (429, 500, 502, 503, 504) and attempt < 4:
                time.sleep(8 * (attempt + 1)); continue
            raise RuntimeError(f'HTTP {e.code}: {msg}')
        except urllib.error.URLError:
            if attempt < 4:
                time.sleep(8); continue
            raise


def main():
    if not KEY:
        os.makedirs('tts_out', exist_ok=True)
        open('tts_out/erros.txt', 'w').write('falta o segredo HEYGEN_API_KEY no repositório\n')
        return 1
    erros = []
    for f in sorted(os.listdir('tts_in')):
        if not f.endswith('.json'):
            continue
        spec = json.load(open(f'tts_in/{f}'))
        slug = spec['slug']
        os.makedirs(f'media/{slug}', exist_ok=True)
        os.makedirs(f'videos/{slug}/ts', exist_ok=True)
        falhou = False
        for i, texto in enumerate(spec['blocos'], 1):
            dest, ts = f'media/{slug}/b{i}.mp3', f'videos/{slug}/ts/bloco{i}.json'
            if os.path.exists(dest) and os.path.exists(ts):
                continue
            try:
                d = speech(spec['voice'], texto, spec.get('speed', 1.2))
                for attempt in range(4):
                    try:
                        urllib.request.urlretrieve(d['audio_url'], dest); break
                    except Exception:
                        time.sleep(4)
                json.dump(d, open(ts, 'w'), ensure_ascii=False)
                print('ok', slug, i, round(d.get('duration', 0), 2), 'chaves:', sorted(d.keys()), flush=True)
            except Exception as e:
                falhou = True
                erros.append(f'{slug} bloco {i}: {e}')
                print('ERRO', erros[-1], flush=True)
        if not falhou:
            os.remove(f'tts_in/{f}')
    if erros:
        os.makedirs('tts_out', exist_ok=True)
        open(f'tts_out/erros_{int(time.time())}.txt', 'w').write('\n'.join(erros) + '\n')
    return 1 if erros else 0


if __name__ == '__main__':
    sys.exit(main())
