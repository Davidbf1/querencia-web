# Fotos realistas de cada postura: se dibuja el esqueleto OpenPose a partir de las posturas de la app
# y ControlNet (lllyasviel/control_v11p_sd15_openpose, OpenRAIL) genera a la persona en esa postura.
import json, math, os, sys
from PIL import Image, ImageDraw
D = os.path.dirname(os.path.abspath(__file__))
COL = [(255,0,0),(255,85,0),(255,170,0),(255,255,0),(170,255,0),(85,255,0),(0,255,0),(0,255,85),(0,255,170),(0,255,255),(0,170,255),(0,85,255),(0,0,255),(85,0,255),(170,0,255),(255,0,255),(255,0,170),(255,0,85)]
LIMBS = [(1,2),(1,5),(2,3),(3,4),(5,6),(6,7),(1,8),(8,9),(9,10),(1,11),(11,12),(12,13),(1,0),(0,14),(14,16),(0,15),(15,17)]
def puntos(p):
    E = 2.3; O = (512 - 200 * E) / 2
    T = lambda xy: (O + xy[0] * E, O + xy[1] * E)
    cab, cue, cad = p['cabeza'], p['cuello'], p['cadera']
    br, pi = p['brazos'], p['piernas']
    if len(br) == 1: br = [br[0], br[0]]
    if len(pi) == 1: pi = [pi[0], pi[0]]
    k = [None] * 18
    if p.get('frente'):
        k[0] = (cab[0], cab[1] + 3); k[14] = (cab[0] - 4, cab[1] - 2); k[15] = (cab[0] + 4, cab[1] - 2); k[16] = (cab[0] - 9, cab[1]); k[17] = (cab[0] + 9, cab[1])
        k[2] = (cue[0] - 12, cue[1] + 4); k[5] = (cue[0] + 12, cue[1] + 4); k[8] = (cad[0] - 8, cad[1]); k[11] = (cad[0] + 8, cad[1])
    else:
        dx = 1 if (br[0][1][0] >= cue[0] or cab[0] >= cue[0]) else -1
        k[0] = (cab[0] + 7 * dx, cab[1] + 2); k[14] = (cab[0] + 4 * dx, cab[1] - 2); k[16] = (cab[0] - 4 * dx, cab[1])
        k[2] = (cue[0] - 2, cue[1] + 4); k[5] = (cue[0] + 2, cue[1] + 4); k[8] = (cad[0] - 2, cad[1]); k[11] = (cad[0] + 2, cad[1])
    k[1] = (cue[0], cue[1])
    k[3], k[4] = br[0][0], br[0][1]; k[6], k[7] = br[1][0], br[1][1]
    k[9], k[10] = pi[0][0], pi[0][1]; k[12], k[13] = pi[1][0], pi[1][1]
    return [T(x) if x else None for x in k]
def esqueleto(p):
    im = Image.new('RGB', (512, 512), 'black'); d = ImageDraw.Draw(im)
    k = puntos(p)
    for i, (a, b) in enumerate(LIMBS):
        if k[a] and k[b]: d.line([k[a], k[b]], fill=COL[i], width=8)
    for i, x in enumerate(k):
        if x: d.ellipse([x[0] - 5, x[1] - 5, x[0] + 5, x[1] + 5], fill=COL[i])
    return im
PESO = {'barra': ', holding a barbell', 'mancuernas': ', holding dumbbells', 'barra-alta': ', hanging from a pull-up bar', 'pecho': ', using a gym machine'}
YOGA_PROF = {
  'ana': 'fit adult woman aged 35 with light skin and long brown hair in a ponytail',
  'awa': 'fit adult woman aged 35 with dark brown skin and curly black hair tied up',
  'kenji': 'fit adult East Asian man aged 35 with short black hair',
}
GYM_PROF = [
  'fit adult man aged 35 with light skin and short blond hair',
  'fit adult man aged 35 with dark skin and a shaved head',
  'fit adult woman aged 35 with fair skin and red hair in a ponytail',
  'fit adult South Asian woman aged 35 with long black hair in a ponytail',
]
def prompt_yoga(prof): return f'full body photo of a {YOGA_PROF[prof]}, wearing a black sports top and black leggings, barefoot, doing yoga on a mat, bright minimalist yoga studio with plants, soft natural light, photorealistic, high detail'
def prompt_gym(i): return f'full body photo of a {GYM_PROF[i % len(GYM_PROF)]}, wearing a lavender t-shirt, black shorts and sneakers, exercising in a bright modern gym, soft light, photorealistic, high detail'
if __name__ == '__main__':
    import torch
    from diffusers import StableDiffusionControlNetPipeline, ControlNetModel, LCMScheduler, AutoencoderKL
    torch.set_num_threads(4)
    qué = sys.argv[1]; prof = sys.argv[2] if len(sys.argv) > 2 else 'ana'; solo = sys.argv[3:]
    datos = json.load(open(os.path.join(D, 'posturas.json')))[qué]
    out = os.path.join(D, 'out', 'poses-' + qué + ('-' + prof if qué == 'yoga' else '')); os.makedirs(out, exist_ok=True); os.makedirs(os.path.join(D, 'esq'), exist_ok=True)
    patrones = sorted({n.rsplit('-', 1)[0] for n in datos})
    cn = ControlNetModel.from_pretrained('lllyasviel/control_v11p_sd15_openpose', torch_dtype=torch.float32)
    vae = AutoencoderKL.from_pretrained('stabilityai/sd-vae-ft-mse', torch_dtype=torch.float32)
    pipe = StableDiffusionControlNetPipeline.from_pretrained('SG161222/Realistic_Vision_V5.1_noVAE', controlnet=cn, vae=vae, torch_dtype=torch.float32, safety_checker=None, requires_safety_checker=False)
    pipe.scheduler = LCMScheduler.from_config(pipe.scheduler.config)
    pipe.load_lora_weights('latent-consistency/lcm-lora-sdv1-5'); pipe.fuse_lora()
    NEG = 'cartoon, drawing, 3d render, deformed, disfigured, extra limbs, extra fingers, bad anatomy, blurry, lowres, text, watermark, nsfw, nude, child'
    for nombre, p in datos.items():
        if solo and nombre not in solo: continue
        f = os.path.join(out, nombre + '.png')
        if os.path.exists(f): continue
        e = esqueleto(p); e.save(os.path.join(D, 'esq', f'{qué}-{nombre}.png'))
        if qué == 'yoga': prompt, semilla = prompt_yoga(prof), {'ana': 4242, 'awa': 777, 'kenji': 1313}[prof] + int(os.environ.get('OFFSET', '0'))
        else:
            i = patrones.index(nombre.rsplit('-', 1)[0]); prompt, semilla = prompt_gym(i) + PESO.get(p.get('peso') or '', ''), 9000 + i + int(os.environ.get('OFFSET', '0'))
            if os.environ.get('OFFSET'): prompt = 'wide shot, camera far away, the whole body visible from head to feet, ' + prompt
        if qué == 'yoga' and os.environ.get('OFFSET'): prompt = 'wide shot, camera far away, the whole body visible from head to feet, ' + prompt
        g = torch.Generator().manual_seed(semilla)
        img = pipe(prompt, image=e, negative_prompt=NEG, num_inference_steps=8, guidance_scale=1.5, controlnet_conditioning_scale=1.6, width=512, height=512, generator=g).images[0]
        img.save(f); print('ok', nombre, flush=True)
    print('fin')
