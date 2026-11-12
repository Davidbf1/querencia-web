# Vídeo real entre dos posturas: fotogramas intermedios con la misma persona y el mismo fondo.
# Para cada paso se interpola el esqueleto (OpenPose) y se repinta la foto anterior (img2img + ControlNet),
# así se conserva la identidad y la ropa y solo cambia la postura.
import json, os, sys
import torch
from PIL import Image
sys.argv, _args = [sys.argv[0]], sys.argv[1:]
from poses import esqueleto, prompt_yoga, prompt_gym, PESO
from diffusers import StableDiffusionControlNetImg2ImgPipeline, ControlNetModel, LCMScheduler, AutoencoderKL
torch.set_num_threads(4)
D = os.path.dirname(os.path.abspath(__file__))
qué, prof, pares = _args[0], _args[1], _args[2:]
datos = json.load(open(os.path.join(D, 'posturas.json')))[qué]
src = os.path.join(D, 'out', os.environ.get('ORIGEN', 'coh') + '-' + qué + ('-' + prof if qué == 'yoga' else ''))
out = os.path.join(D, 'out', 'trans-' + qué + ('-' + prof if qué == 'yoga' else '')); os.makedirs(out, exist_ok=True)
cn = ControlNetModel.from_pretrained('lllyasviel/control_v11p_sd15_openpose', torch_dtype=torch.float32)
vae = AutoencoderKL.from_pretrained('stabilityai/sd-vae-ft-mse', torch_dtype=torch.float32)
pipe = StableDiffusionControlNetImg2ImgPipeline.from_pretrained('SG161222/Realistic_Vision_V5.1_noVAE', controlnet=cn, vae=vae, torch_dtype=torch.float32, safety_checker=None, requires_safety_checker=False)
pipe.scheduler = LCMScheduler.from_config(pipe.scheduler.config)
pipe.load_lora_weights('latent-consistency/lcm-lora-sdv1-5'); pipe.fuse_lora()
NEG = 'cartoon, drawing, 3d render, deformed, disfigured, extra limbs, extra fingers, bad anatomy, blurry, lowres, text, watermark, nsfw, nude, child'
def mezcla(a, b, t):
    if isinstance(a, list): return [mezcla(x, y, t) for x, y in zip(a, b)]
    if isinstance(a, (int, float)) and not isinstance(a, bool): return a + (b - a) * t
    return a
N = int(os.environ.get('PASOS', '3'))
semilla = {'ana': 4242, 'awa': 777, 'kenji': 1313}.get(prof, 9000)
patrones = sorted({n.rsplit('-', 1)[0] for n in datos})
for par in pares:
    a, b = par.split('>')
    fa = os.path.join(src, a + '.png')
    if not (os.path.exists(fa) and os.path.exists(os.path.join(src, b + '.png'))): print('falta foto', par, flush=True); continue
    if qué == 'yoga': prompt = prompt_yoga(prof)
    else:
        i = patrones.index(a.rsplit('-', 1)[0]); prompt = prompt_gym(i) + PESO.get(datos[a].get('peso') or '', ''); semilla = 9000 + i
    prev = Image.open(fa).convert('RGB')
    for k in range(1, N + 1):
        f = os.path.join(out, f'{a}__{b}__{k}.png')
        if os.path.exists(f): prev = Image.open(f).convert('RGB'); continue
        t = k / (N + 1)
        pa, pb = datos[a], datos[b]
        p = {**pa, **{key: mezcla(pa[key], pb[key], t) for key in ('cabeza', 'cuello', 'cadera', 'brazos', 'piernas')}}
        if len(pa['brazos']) != len(pb['brazos']) or len(pa['piernas']) != len(pb['piernas']): p = pa if t < 0.5 else pb
        g = torch.Generator().manual_seed(semilla)
        img = pipe(prompt, image=prev, control_image=esqueleto(p), strength=min(0.8, 0.62 + 0.06 * k), negative_prompt=NEG, num_inference_steps=10, guidance_scale=1.5, controlnet_conditioning_scale=1.8, generator=g).images[0]
        img.save(f); prev = img
        print('ok', par, k, flush=True)
print('TRANS_FIN', flush=True)
