# Conectar un dominio .com propio a la web de Querencia

> Sustituye `TUDOMINIO.com` por el dominio real cuando lo compres.

## Antes de empezar: lo que conviene saber

1. **La web solo funciona bien en la raíz de un dominio.** El build de Expo usa rutas absolutas
   (`/_expo/...`, `/sw.js`, `/manifest.webmanifest`, `scope: "/"`). En `davidbf1.github.io/querencia-web/`
   esas rutas apuntan a `davidbf1.github.io/_expo/...`, que no existe. Con un dominio propio la web
   se sirve en `/` y el problema desaparece sin recompilar.
2. **Los datos guardados en el navegador no se mudan de dominio.** La app guarda los datos en
   `localStorage`, que va ligado al origen. Quien la haya usado en otra dirección empezará de cero en
   `TUDOMINIO.com`. Si hay usuarios reales, avísalos u ofrece exportar/importar antes del cambio.
3. **El enlace al aviso legal está fijado en el código fuente** (`https://davidbf1.github.io/querencia/aviso-legal.html`,
   dentro de la pantalla de Ajustes). Sigue funcionando, pero si quieres que apunte a `TUDOMINIO.com`
   hay que cambiarlo en el repositorio privado y recompilar.

## Hosting actual

- **Plataforma:** GitHub Pages, publicado con GitHub Actions (`.github/workflows/pages.yml`) en cada push a `main`.
- **Qué se publica:** el repositorio entero tal cual (`path: .`), ya compilado.
- **Archivo `CNAME`:** no hace falta. Con despliegue por Actions, GitHub **ignora** el archivo `CNAME`;
  el dominio se guarda en *Settings → Pages*.
- **HTTPS:** GitHub emite gratis un certificado de Let's Encrypt para el dominio propio.

## Paso 1. Comprar el dominio

Cualquier registrador vale (Cloudflare Registrar, Porkbun, Namecheap, etc.). Recomendable:
- Que permita editar registros A, AAAA, CNAME y TXT (casi todos).
- **No** activar el "parking", el "redireccionamiento web" ni el "forwarding" del registrador:
  añaden sus propios registros A que chocan con los de GitHub.
- Activar la protección de privacidad WHOIS.

## Paso 2. Verificar el dominio en GitHub (evita que otro lo secuestre)

1. GitHub → foto de perfil → **Settings → Pages → Add a domain** → escribe `TUDOMINIO.com`.
2. GitHub muestra un registro TXT. Créalo en el registrador:

| Tipo | Nombre / Host | Valor |
|------|---------------|-------|
| TXT  | `_github-pages-challenge-Davidbf1` | *(el código que te da GitHub)* |

3. Espera unos minutos y pulsa **Verify**.

## Paso 3. Registros DNS exactos

Borra antes cualquier registro A, AAAA o CNAME que el registrador haya creado por defecto en `@` y `www`.

| Tipo  | Nombre / Host | Valor | TTL |
|-------|---------------|-------|-----|
| A     | `@` | `185.199.108.153` | 3600 (o automático) |
| A     | `@` | `185.199.109.153` | 3600 |
| A     | `@` | `185.199.110.153` | 3600 |
| A     | `@` | `185.199.111.153` | 3600 |
| AAAA  | `@` | `2606:50c0:8000::153` | 3600 |
| AAAA  | `@` | `2606:50c0:8001::153` | 3600 |
| AAAA  | `@` | `2606:50c0:8002::153` | 3600 |
| AAAA  | `@` | `2606:50c0:8003::153` | 3600 |
| CNAME | `www` | `davidbf1.github.io` | 3600 |

Notas:
- El CNAME de `www` apunta a `davidbf1.github.io` **sin** `/querencia-web`. GitHub sabe qué repositorio servir por el dominio configurado en el Paso 4.
- **No** crees un registro comodín (`*`): permite que otros cuelguen webs en tus subdominios.
- Si usas Cloudflare como DNS, deja las nubes en **gris (DNS only)** al menos hasta que GitHub emita el certificado.
- Si el registrador tiene registros **CAA**, añade uno que permita `letsencrypt.org`
  (`CAA @ 0 issue "letsencrypt.org"`). Si no hay ningún CAA, no hace falta crear ninguno.

## Paso 4. Configurar el dominio en el repositorio

1. `github.com/Davidbf1/querencia-web` → **Settings → Pages**.
2. *Build and deployment → Source*: debe estar en **GitHub Actions** (ya lo está por el workflow).
3. *Custom domain*: escribe `TUDOMINIO.com` (sin `www`) → **Save**.
4. Espera a que el *DNS check* salga en verde.
5. Cuando GitHub termine de emitir el certificado (de minutos a 24 h), marca **Enforce HTTPS**.

GitHub redirige solo `www.TUDOMINIO.com` → `TUDOMINIO.com` (o al revés si guardas el dominio con `www`).

## Paso 5. Comprobar

```bash
dig +short TUDOMINIO.com A        # debe dar las 4 IP 185.199.10x.153
dig +short TUDOMINIO.com AAAA     # las 4 IPv6 2606:50c0:800x::153
dig +short www.TUDOMINIO.com      # davidbf1.github.io. y después las IP
curl -I https://TUDOMINIO.com     # HTTP/2 200, server: GitHub.com
curl -I http://TUDOMINIO.com      # 301 a https:// (con Enforce HTTPS activado)
```

En el navegador:
- Abre `https://TUDOMINIO.com`, recorre varias pantallas y recarga en una ruta interna.
- DevTools → *Application*: el *service worker* `/sw.js` debe estar activo y el manifest sin errores.
- En el móvil, "Añadir a pantalla de inicio" debe mostrar el icono de Querencia.

## Problemas habituales

| Síntoma | Causa probable | Solución |
|---------|----------------|----------|
| "Domain's DNS record could not be retrieved" | Propagación DNS | Esperar hasta 24 h; comprobar con `dig`. |
| "Enforce HTTPS" desactivado/gris | Certificado aún no emitido, o CAA bloqueando | Esperar; quitar y volver a guardar el dominio; revisar CAA. |
| Página del registrador en vez de la web | Quedan registros de parking/forwarding | Borrarlos. |
| La web carga en blanco | Se está sirviendo en una subruta | Usar el dominio en la raíz, nunca `TUDOMINIO.com/querencia-web`. |
| Se ve una versión antigua | El *service worker* sirvió la caché sin red | Recargar con red; en DevTools → *Unregister*. |

## Después del cambio (opcional)

- Actualizar en el repo privado el enlace del aviso legal y cualquier URL absoluta a `TUDOMINIO.com`.
- Si quieres correo `hola@TUDOMINIO.com`, añade los registros MX/SPF/DKIM de tu proveedor de correo; no chocan con los de arriba.
