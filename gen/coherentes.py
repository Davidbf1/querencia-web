# Rehace las fotos de cada postura partiendo de UNA foto base (misma persona, ropa y sala): img2img + ControlNet.
import json, os, sys
import torch
from PIL import Image
sys.argv, _args = [sys.argv[0]], sys.argv[1:]
from poses import esqueleto, prompt_yoga, prompt_gym, PESO
from diffusers import StableDiffusionControlNetImg2ImgPipeline, ControlNetModel, LCMScheduler, AutoencoderKL
torch.set_num_threads(4)
D = os.path.dirname(os.path.abspath(__file__))
qué, prof = _args[0], _args[1]; solo = _args[2:]
FUERZA = float(os.environ.get('FUERZA', '0.8'))
datos = json.load(open(os.path.join(D, 'posturas.json')))[qué]
src = os.path.join(D, 'out', 'poses-' + qué + ('-' + prof if qué == 'yoga' else ''))
out = os.path.join(D, 'out', 'coh-' + qué + ('-' + prof if qué == 'yoga' else '')); os.makedirs(out, exist_ok=True)
cn = ControlNetModel.from_pretrained('lllyasviel/control_v11p_sd15_openpose', torch_dtype=torch.float32)
vae = AutoencoderKL.from_pretrained('stabilityai/sd-vae-ft-mse', torch_dtype=torch.float32)
pipe = StableDiffusionControlNetImg2ImgPipeline.from_pretrained('SG161222/Realistic_Vision_V5.1_noVAE', controlnet=cn, vae=vae, torch_dtype=torch.float32, safety_checker=None, requires_safety_checker=False)
pipe.scheduler = LCMScheduler.from_config(pipe.scheduler.config)
pipe.load_lora_weights('latent-consistency/lcm-lora-sdv1-5'); pipe.fuse_lora()
NEG = 'cartoon, drawing, 3d render, deformed, disfigured, extra limbs, extra fingers, bad anatomy, blurry, lowres, text, watermark, nsfw, nude, child'
patrones = sorted({n.rsplit('-', 1)[0] for n in datos})
for nombre, p in datos.items():
    if solo and nombre not in solo: continue
    f = os.path.join(out, nombre + '.png')
    if os.path.exists(f): continue
    if qué == 'yoga': prompt, semilla, base = prompt_yoga(prof), {'ana': 4242, 'awa': 777, 'kenji': 1313}[prof], os.path.join(src, 'montana.png')
    else:
        pat = nombre.rsplit('-', 1)[0]; i = patrones.index(pat)
        prompt, semilla, base = prompt_gym(i) + PESO.get(p.get('peso') or '', ''), 9000 + i, os.path.join(src, pat + '-0.png')
    if not os.path.exists(base): print('sin base', nombre, flush=True); continue
    g = torch.Generator().manual_seed(semilla)
    img = pipe(prompt, image=Image.open(base).convert('RGB'), control_image=esqueleto(p), strength=FUERZA, negative_prompt=NEG, num_inference_steps=10, guidance_scale=1.5, controlnet_conditioning_scale=1.6, generator=g).images[0]
    img.save(f); print('ok', nombre, flush=True)
print('COH_FIN', flush=True)
