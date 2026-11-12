# Imágenes únicas con toque futurista (Stable Diffusion 1.5 Realistic Vision + LCM-LoRA, licencia OpenRAIL-M), en CPU.
# Uso: python futuro.py iconos <parte> <partes>   |   python futuro.py portadas <parte> <partes>
# Cada sonido, meditación, tipo de sesión, banda de frecuencia y chakra tiene SU imagen; ninguna se repite.
import os, sys
ICONOS = {
 # --- Sonidos de ambiente y naturaleza ---
 's-lluvia': 'rain streaking down a window pane with glowing city bokeh lights',
 's-tormenta': 'distant storm over a dark sea with violet lightning in the clouds',
 's-olas': 'luminous ocean wave breaking, foam glowing cyan',
 's-mar': 'calm sea horizon with a giant ringed planet in the sky',
 's-viento': 'tall grass swaying in wind with floating glowing seed particles',
 's-marron': 'slow deep brown and amber flowing liquid waves, smooth gradient',
 's-rosa': 'soft pink and violet flowing silk-like light waves',
 's-blanco': 'soft white luminous snow-like particle field, calm static glow',
 's-fuego': 'fireplace flames with floating glowing embers in a dark modern room',
 's-arroyo': 'small stream over smooth stones with bioluminescent moss',
 's-cascada': 'waterfall glowing with cyan light in a dark rainforest',
 's-bosque': 'dark forest with glowing fireflies and a small bird on a branch',
 's-grillos': 'summer night meadow with thousands of glowing fireflies and stars',
 's-ballenas': 'whale swimming through a glowing deep ocean, bioluminescent plankton',
 's-hojas': 'dry autumn leaves floating in the air lit by neon light',
 's-ventilador': 'sleek futuristic white fan with soft blue light ring',
 's-cafeteria': 'cup of coffee with steam on a glass table, neon cafe lights blurred',
 's-tecleo': 'hands on a glowing holographic keyboard, soft light',
 's-paginas': 'pages of an open book turning with glowing light particles',
 's-selva-lluviosa': 'tropical jungle in rain with giant glowing flowers',
 's-costa-tormentosa': 'rocky coast under a dramatic stormy sky with a distant lighthouse beam',
 's-cabana-invierno': 'snowy cabin with warm window light under an aurora',
 's-rio-bosque': 'river winding through a misty forest at dawn with soft cyan mist',
 's-noche-fogata': 'campfire at night with sparks rising toward a starry galaxy sky',
 's-valle-cascada': 'green valley with a tall waterfall and floating luminous islands',
 's-playa-brisa': 'tropical beach at dusk with palm trees and glowing turquoise water',
 's-tormenta-chimenea': 'view from a cozy window of a storm outside, glowing fireplace inside',
 's-amanecer-campo': 'countryside sunrise with golden mist and a huge pastel sun',
 's-lluvia-cabana': 'rain falling on a wooden cabin roof with warm lit windows',
 # --- Música ---
 's-musica-calma': 'floating glowing musical notes over a calm lavender horizon',
 's-musica-noche': 'crescent moon and drifting luminous notes over a night city skyline',
 's-musica-claridad': 'dawn light beams through crystal prisms, clear and bright',
 's-oriental-guzheng': 'chinese guzheng zither with neon blossom petals floating',
 's-zen-flauta': 'bamboo flute lying on a dark stone with glowing mist',
 's-cuencos-tibetanos': 'tibetan singing bowl with concentric glowing sound rings',
 's-kalimba': 'wooden kalimba with glowing keys and small sparks',
 's-arpa-celestial': 'golden harp with strings made of light in a starry sky',
 's-piano-suave': 'grand piano keys with soft reflections and a violet glow',
 's-canon-pachelbel': 'elegant string quartet silhouettes in an ornate hall with golden light',
 's-campanas-viento': 'wind chimes made of glass glowing in a night garden',
 's-tambor-chaman': 'hand drum with glowing geometric patterns and ember sparks',
 's-tanpura': 'indian tanpura with golden strings and warm glowing smoke',
 's-mantra-om': 'glowing om symbol shape made of light, incense smoke, dark background',
 's-canto-gregoriano': 'candlelit stone arches of an ancient chapel with floating light',
 's-cuencos-cuarzo': 'crystal quartz singing bowls glowing in rainbow light',
 's-flauta-nativa': 'wooden native flute with feathers on a desert dusk with glowing sky',
 's-guitarra-acustica': 'acoustic guitar with glowing strings against a night window',
 's-bach-preludio': 'baroque harpsichord with golden light and floating sheet music',
 's-chill-out': 'headphones on a neon lit table with soft lofi glow',
 's-ambient-espacial': 'astronaut view of nebula and stars from a quiet spaceship window',
 's-satie-gymnopedie': 'old grand piano in an empty minimal room with a single beam of light',
 's-debussy-claro-luna': 'full moon reflected on a still lake with glowing silver ripples',
 's-beethoven-luz-luna': 'moonlit piano by a window with silver mist',
 's-chopin-nocturno': 'night garden with a piano under glowing lanterns',
 's-schubert-ave-maria': 'stained glass window of light with a soft glowing dove',
 's-bach-aria-sol': 'violin with golden rays of sunlight and floating dust',
 's-faure-pavana': 'elegant ballroom with soft candle glow and drifting petals',
 's-romanza-guitarra': 'spanish guitar on a balcony at sunset with warm neon sky',
 's-arpa-celta': 'celtic harp on a green hill under aurora lights',
 's-koto-sakura': 'japanese koto and cherry blossom petals glowing at night',
 's-jardin-zen': 'zen sand garden with raked circles and a glowing lantern',
 's-raga-flauta': 'indian bamboo flute and a glowing lotus on a still lake',
 's-coro-celestial': 'choir of light beams rising in a vast cathedral of clouds',
 's-piano-noche-profunda': 'piano in a dark room with deep blue starlight window',
 's-kalimba-estrellas': 'kalimba surrounded by drifting stars and constellations',
 's-templo-campanas': 'temple bells hanging under red lanterns in glowing mist',
 's-cajita-musica-sueno': 'small music box open with glowing stars rising from it',
 's-piano-lluvioso': 'piano by a rainy window with neon reflections',
 # --- Meditaciones (una distinta cada una) ---
 'm-rain-8': 'a glowing heart-shaped orb held in open hands, soft rain of light',
 'm-montana-6': 'majestic mountain peak above clouds with a violet glowing sky',
 'm-lago-7': 'perfectly still lake mirror under an aurora sky',
 'm-miedo-6': 'small warm lantern in a vast dark forest, safe light',
 'm-noche-gratitud-6': 'night sky with a bright star over calm rooftops, grateful peaceful',
 'm-cansancio-7': 'soft pillow of clouds floating in a pastel sunset sky',
 'm-enfado-cuerpo-6': 'red and orange energy flowing and cooling into blue calm waves',
 'm-compasion-dificil-7': 'two hands reaching toward each other with a glowing bridge of light',
 'm-presente-3': 'single flower blooming with light petals, macro, dark background',
 'm-respiracion-5': 'gentle expanding rings of cyan light like breathing, minimal',
 'm-cuerpo-8': 'translucent human silhouette with a soft scanning ray of light',
 'm-compasion-5': 'hands holding a small glowing flame, tender',
 'm-pensamientos-6': 'clouds drifting across a sky as luminous thought bubbles',
 'm-dormir-10': 'bed under a moonlit window with floating dream particles',
 'm-gratitud-5': 'warm rising sun with golden rays through a window, thankful',
 'm-bondad-8': 'many tiny glowing hearts rising like lanterns into the night',
 'm-caminar-5': 'path of glowing stepping stones through a quiet forest',
 'm-comer-3': 'colorful fruits glowing on a table with soft studio light',
 'm-relajacion-10': 'floating on calm turquoise water under starlight, serene',
 'm-cuadrada-5': 'glowing square frame of light with a sand garden inside',
 'm-lugar-8': 'imagined tranquil island with glowing trees and calm water',
 'm-despertar-4': 'soft sunrise through curtains with golden dust in the air',
 'm-preocupacion-6': 'worries as small lights being placed gently on a wooden table',
 'm-ancla-2': 'ship anchor glowing softly in calm deep water, safe',
 'm-enfado-5': 'storm clouds opening to show a calm blue sky with light rays',
 # --- Tipos de sesión larga ---
 't-respiracion': 'luminous lungs-shaped tree of light breathing in a dark space',
 't-cuerpo': 'warm golden body scan light moving down a translucent silhouette',
 't-presencia': 'single drop falling into water with perfect concentric light rings',
 't-compasion': 'two hearts of light merging together, warm pink and gold',
 't-sueno': 'crescent moon cradle floating among soft clouds and stars',
 # --- Bandas de frecuencia ---
 'b-delta': 'deep dark blue ocean with very slow glowing waves, sleeping',
 'b-theta': 'twilight sky with slow violet waves and drifting dream lights',
 'b-alfa': 'calm lake at dawn with smooth teal waves, relaxed',
 'b-beta': 'bright focused golden light beams in clear blue sky',
 'b-gamma': 'fast shimmering electric blue and white light network, insight',
 # --- Chakras ---
 'ch-1': 'glowing red crystal at the base of a dark stone path, grounding',
 'ch-2': 'glowing orange liquid flowing in a calm bowl, creative',
 'ch-3': 'bright yellow sun orb with strong rays, power',
 'ch-4': 'glowing green heart-shaped crystal in a garden of light',
 'ch-5': 'glowing sky blue sound waves from a crystal throat orb',
 'ch-6': 'deep indigo third eye shaped nebula with stars',
 'ch-7': 'violet lotus of thousand light petals above the clouds',
}
PORTADAS = {
 'calma': 'calm lake at sunrise with soft mist and a pastel sky', 'respira': 'luminous clouds and gentle breathing rings of light',
 'meditaciones': 'meditation cushion in a minimal room with floating candles of light', 'sonidos': 'sound waves as glowing ribbons over singing bowls',
 'frecuencias': 'glowing sine waves over a calm night sea', 'conocerme': 'open notebook with holographic stars rising, warm tea',
 'animo': 'field of glowing wildflowers at golden hour', 'diario': 'notebook and pen with glowing handwriting light, cozy blanket',
 'suenos': 'starry night sky with giant moon over dreamy hills', 'chakras': 'seven glowing colored light orbs from red to violet in a vertical line',
 'cuestionarios': 'holographic checklist panel over a sunny desk', 'explorar': 'small explorer looking at a vast glowing valley map',
 'estados': 'aurora over a quiet snowy valley', 'aprende': 'floating glowing books above a quiet library',
 'frases': 'sunrise over the ocean with golden light', 'apoyo': 'two hands holding a warm glowing mug, comforting',
 'asistente': 'friendly glowing orb assistant in a cozy room with plants', 'plan': 'lighthouse beam crossing a calm night sea',
 'cerebro': 'glowing neurons and synapses network, violet and cyan', 'corazon': 'heart shaped glowing cloud at sunset',
 'ciclo': 'phases of the moon in a row over a night sea', 'grafica': 'rolling hills with a glowing line chart of light over them',
 'hablar': 'two cups of tea on a table with a glowing window', 'naturaleza': 'lush forest with ferns and glowing spores',
 'libro': 'old open book with glowing flowers rising from its pages', 'eneagrama': 'mandala of glowing geometric light, nine points',
 'yoga': 'yoga mat on a terrace over a futuristic city at sunrise', 'pensamientos': 'paper boats glowing on a calm pond',
 'mindfulness': 'zen stones balanced by a glowing stream', 'midia': 'sunrise through a window with plants and soft holographic clock',
 'programas': 'winding glowing path through a spring meadow', 'juegos': 'floating colorful puzzle pieces with glowing edges',
 'comida': 'top view of a healthy mediterranean meal, natural colors, appetizing', 'ejercicio': 'running shoes on a park path with glowing trail lines',
 'ajustes': 'minimal glowing sliders and dials on a dark glass panel',
 # nuevas (antes compartían imagen)
 'videos': 'cinematic wide screen with a person doing yoga in a bright studio, soft light',
 'cuerpomente': 'silhouette of a person balancing with glowing mind and body energy lines',
 'yoconocer': 'face-shaped constellation of stars with a gentle mirror reflection on water',
 'buzon': 'glowing letter in a mailbox at dusk, small floating ideas as lights',
}
ESTILO_ICONO = ', futuristic aesthetic, holographic neon glow, iridescent violet and cyan light, soft bloom, deep dark background, ultra detailed, centered composition, calm'
ESTILO_PORTADA = ', futuristic sci-fi ambience, soft holographic light trails, neon violet and teal glow, cinematic wide shot, ultra detailed, calm, no people'
NEG = 'text, letters, watermark, logo, frame, border, deformed, disfigured, blurry, lowres, nsfw, nude, child, face close-up, bad anatomy'
if __name__ == '__main__':
    import torch
    from diffusers import StableDiffusionPipeline, LCMScheduler, AutoencoderKL
    torch.set_num_threads(int(os.environ.get('OMP_NUM_THREADS', '4')))
    que, parte, partes = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    datos, estilo, (w, h) = (ICONOS, ESTILO_ICONO, (512, 512)) if que == 'iconos' else (PORTADAS, ESTILO_PORTADA, (768, 384))
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out', 'futuro-' + que); os.makedirs(out, exist_ok=True)
    vae = AutoencoderKL.from_pretrained('stabilityai/sd-vae-ft-mse', torch_dtype=torch.float32)
    pipe = StableDiffusionPipeline.from_pretrained('SG161222/Realistic_Vision_V5.1_noVAE', vae=vae, torch_dtype=torch.float32, safety_checker=None, requires_safety_checker=False)
    pipe.scheduler = LCMScheduler.from_config(pipe.scheduler.config)
    pipe.load_lora_weights('latent-consistency/lcm-lora-sdv1-5'); pipe.fuse_lora()
    for i, (k, v) in enumerate(datos.items()):
        if i % partes != parte: continue
        f = os.path.join(out, k + '.png')
        if os.path.exists(f): continue
        g = torch.Generator().manual_seed(2000 + i)
        pipe(v + estilo, negative_prompt=NEG, num_inference_steps=6, guidance_scale=1.5, width=w, height=h, generator=g).images[0].save(f)
        print('ok', k, flush=True)
    print('FIN', flush=True)
