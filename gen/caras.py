# Mejora las caras de las fotos de cuerpo entero: se localiza la cabeza con el propio esqueleto de la postura,
# se amplía el recorte, se repinta solo la cara (img2img, poca fuerza para no cambiar a la persona) y se pega con borde suave.
import json, os, sys
import numpy as np
import torch
from PIL import Image, ImageFilter, ImageDraw
from poses import puntos, prompt_yoga, YOGA_PROF, GYM_PROF
from diffusers import StableDiffusionImg2ImgPipeline, LCMScheduler, AutoencoderKL
torch.set_num_threads(int(os.environ.get('OMP_NUM_THREADS', '4')))
D = os.path.dirname(os.path.abspath(__file__))
FUERZA = float(os.environ.get('FUERZA_CARA', '0.5'))
TAM = int(os.environ.get('TAM_FOTO', '384'))      # tamaño de las fotos de entrada (el esqueleto está a 512)
CARA = 120                                        # lado del recorte a 512 px
_pipe = None
def pipe():
    global _pipe
    if _pipe is None:
        vae = AutoencoderKL.from_pretrained('stabilityai/sd-vae-ft-mse', torch_dtype=torch.float32)
        p = StableDiffusionImg2ImgPipeline.from_pretrained('SG161222/Realistic_Vision_V5.1_noVAE', vae=vae, torch_dtype=torch.float32, safety_checker=None, requires_safety_checker=False)
        p.scheduler = LCMScheduler.from_config(p.scheduler.config)
        p.load_lora_weights('latent-consistency/lcm-lora-sdv1-5'); p.fuse_lora()
        _pipe = p
    return _pipe
NEG = 'cartoon, drawing, 3d render, deformed face, disfigured, asymmetrical eyes, bad eyes, blurry, lowres, text, watermark, nsfw, child, extra eyes, mask'
def mejorar_cara(img, p, quien, semilla):
    """img: foto completa (cualquier tamaño, cuadrada). p: postura (diccionario de posturas.json)."""
    k = puntos(p)
    n = k[0] or k[1]
    if not n: return img
    s = img.width / 512.0
    cx, cy = n[0] * s, (n[1] - 6) * s            # centro de la cabeza (la nariz queda algo por debajo)
    lado = CARA * s
    x0, y0 = int(cx - lado / 2), int(cy - lado / 2)
    x0 = max(0, min(img.width - int(lado), x0)); y0 = max(0, min(img.height - int(lado), y0))
    caja = (x0, y0, x0 + int(lado), y0 + int(lado))
    rec = img.crop(caja).resize((512, 512), Image.LANCZOS)
    prompt = f'close-up portrait photo of the face of a {quien}, natural detailed face, symmetrical eyes, sharp focus, soft light, photorealistic'
    g = torch.Generator().manual_seed(semilla)
    nuevo = pipe()(prompt, image=rec, strength=FUERZA, negative_prompt=NEG, num_inference_steps=8, guidance_scale=1.5, generator=g).images[0]
    nuevo = nuevo.resize((caja[2] - caja[0], caja[3] - caja[1]), Image.LANCZOS)
    m = Image.new('L', nuevo.size, 0); w = nuevo.width
    ImageDraw.Draw(m).ellipse([w * 0.18, w * 0.08, w * 0.82, w * 0.92], fill=255)
    m = m.filter(ImageFilter.GaussianBlur(w * 0.07))
    out = img.copy(); out.paste(nuevo, caja[:2], m)
    return out
def quien_de(qué, prof, nombre, patrones):
    if qué == 'yoga': return YOGA_PROF[prof], {'ana': 4242, 'awa': 777, 'kenji': 1313}[prof]
    i = patrones.index(nombre.rsplit('-', 1)[0]); return GYM_PROF[i % len(GYM_PROF)], 9000 + i
def mezcla(a, b, t):
    if isinstance(a, list): return [mezcla(x, y, t) for x, y in zip(a, b)]
    if isinstance(a, (int, float)) and not isinstance(a, bool): return a + (b - a) * t
    return a
def postura_trans(datos, a, b, k, N=3):
    t = k / (N + 1); pa, pb = datos[a], datos[b]
    p = {**pa, **{key: mezcla(pa[key], pb[key], t) for key in ('cabeza', 'cuello', 'cadera', 'brazos', 'piernas')}}
    if len(pa['brazos']) != len(pb['brazos']) or len(pa['piernas']) != len(pb['piernas']): p = pa if t < 0.5 else pb
    return p
if __name__ == '__main__':
    qué, prof, carpeta = sys.argv[1], sys.argv[2], sys.argv[3]       # carpeta con coh-*/ y trans-*/ (webp)
    datos = json.load(open(os.path.join(D, 'posturas.json')))[qué]
    patrones = sorted({n.rsplit('-', 1)[0] for n in datos})
    sub = ('yoga-' + prof) if qué == 'yoga' else 'gym'
    solo = set(sys.argv[4:])
    for pref in ('coh-', 'trans-'):
        d = os.path.join(carpeta, pref + sub)
        if not os.path.isdir(d): continue
        for f in sorted(os.listdir(d)):
            nombre = os.path.splitext(f)[0]
            if solo and nombre not in solo: continue
            ruta = os.path.join(d, f)
            if pref == 'coh-':
                if nombre not in datos: continue
                p, base = datos[nombre], nombre
            else:
                a, b, k = nombre.split('__')
                if a not in datos or b not in datos: continue
                p, base = postura_trans(datos, a, b, int(k)), a
            quien, semilla = quien_de(qué, prof, base, patrones)
            img = Image.open(ruta).convert('RGB')
            mejorar_cara(img, p, quien, semilla).save(ruta, 'WEBP', quality=80, method=6)
            print('cara', pref, nombre, flush=True)
