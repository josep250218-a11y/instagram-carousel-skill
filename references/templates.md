# Los 6 templates

Todos a 1080×1350 (4:5). Fuente default: Outfit (300–900). Tech Terminal suma JetBrains Mono. Los colores salen de `config.json` → `brand` y entran como variables CSS `--brand-*`. Cada template define sus propias variables locales con fallback:

```css
--primary: var(--brand-primary, #4F46E5);
```

Placeholders: `{{HANDLE}}` (footer) y `{{SIGNATURE}}` (firma en Diary y Soft Poetic). El script los reemplaza.

Variables de marca que usa cada template:

| Template | Variables `--brand-*` |
|---|---|
| Card Pop | primary, dark, bg, text, text-dim, accent |
| Tech Terminal | bg-dark, text-on-dark, neon, accent-yellow |
| Numbered Steps | primary, dark, bg, text, text-dim |
| Sticky Note | primary, dark, bg, text, text-dim, accent-yellow, neon |
| Diary | primary, dark, bg, text, text-dim |
| Soft Poetic | primary, dark, bg, text-dim, neon |

---

## NOTICIA

### Card Pop *(default)*
**Archivo:** `templates/card-pop.html` · **template_tag:** `card-pop`

- **Paleta:** fondo pálido (`--bg`), card blanca con sombra suave, headline en `--dark`, eyebrow en `--primary`, `--accent` para el "Desliza →".
- **Vibe:** friendly, pulido, tipo Notion/Linear. Audiencia general.
- **Componentes CSS:**
  - `.top-bar` con `.pill` (badge oscuro con dot) + `.meta` (fecha o "N / 5")
  - `.card` — contenedor central blanco, `border-radius: 48px`
  - `.eyebrow` — label en mayúsculas, color primary
  - `.headline` — 96px, weight 800
  - `.subhead` — 36px, color text-dim
  - `.stat` + `.stat-label` + `.stat-desc` — slides con número grande (220px)
  - `.cta-card` — variante de `.card` con fondo primary y texto blanco (cierre)
  - `.footer` — `.handle` a la izquierda, `.pages` o `.swipe` a la derecha
- **Estructura típica:** Portada → Resumen ("3 cosas") → Punto 1 con stat → Punto 2 con stat → CTA card.

### Tech Terminal *(alternativa)*
**Archivo:** `templates/tech-terminal.html` · **template_tag:** `tech-terminal`

- **Paleta:** fondo casi negro (`--bg-dark`) con grilla sutil, texto claro, accent neón (`--neon`). Outfit para títulos, JetBrains Mono para prompts, data y footer.
- **Vibe:** hacker, dev, cyberpunk. Releases técnicos, benchmarks, CLI.
- **Componentes CSS:**
  - `.top` — barra tipo ventana con path + 3 dots
  - `.prompt` — línea `$ comando`; `.cursor` agrega cursor parpadeante
  - `.headline` — 132px, con `.underline` para subrayar palabras
  - `.subhead` — 34px
  - `.data-block` — card con borde neón; contiene `.data-key`, `.data-value` (200px, admite `<sup>`), `.data-label`, `.data-desc`
  - `.closing-text` + `.closing-cta` — cierre con borde tipo botón
  - `.footer` — monospace, formato `[ 01 / 05 ]`
- **Estructura típica:** Portada con prompt → Resumen con otro prompt → 2–3 data-blocks → Cierre `echo "tu turno"` + CTA.

---

## TIP

### Numbered Steps *(default)*
**Archivo:** `templates/numbered-steps.html` · **template_tag:** `numbered-steps`

- **Paleta:** fondo blanco, círculos primary con número blanco, headline dark, `.closing-card` con fondo dark.
- **Vibe:** tutorial limpio, jerárquico. "Cómo hacer X paso a paso".
- **Componentes CSS:**
  - `.pill` — badge pálido con dot primary
  - `.cover-headline` — 132px, `<em>` en color primary
  - `.cover-sub` — 38px
  - `.step-row` — flex con `.step-num` (círculo 220px) + `.step-text`
  - `.step-title` — 88px (bajar a 76px si va a dos líneas)
  - `.step-desc` — 34px (32px si son 4–5 líneas)
  - `.quote-block` + `.quote-text` — bloque pálido con borde izquierdo primary. **Debe ser accionable** (el comando, el path, el ejemplo).
  - `.closing-card` — card dark con `.closing-text` + `.closing-sub`
- **Estructura típica:** Portada → (opcional) "El problema" → Paso 1 con quote → Paso 2 → … → Closing card.
- El slide "El problema" es opcional. Omitirlo cuando el pedido es directo ("4 tips para X").

### Sticky Note *(alternativa)*
**Archivo:** `templates/sticky-note.html` · **template_tag:** `sticky-note`

- **Paleta:** fondo pálido con textura punteada, notas blancas con rotación leve y cinta amarilla (`--accent-yellow`).
- **Vibe:** artesanal, casual, cálido. Tips lifestyle, productividad, personales.
- **Componentes CSS:**
  - `.note` / `.note--rot-r` / `.note--rot-l` — la nota con cinta
  - `.headline` — 116px, `.underline` con subrayado amarillo
  - `.sub` — subhead
  - `.tip-row` — `.tip-num` (180px) + `.tip-text` con `.tip-title` + `.tip-quote`
  - `.closing-text` — 96px centrado, `<em>` primary
- **Estructura típica:** Portada en nota → "El problema" en nota rotada → Tips con número gigante → Cierre centrado.

---

## REFLEXIÓN

### Diary *(default)*
**Archivo:** `templates/diary.html` · **template_tag:** `diary`

- **Paleta:** fondo pálido, hoja blanca con renglones reales (`repeating-linear-gradient`), fecha en primary, firma en cursiva primary.
- **Vibe:** íntimo, conversacional, entrada de diario. Opiniones personales con contexto.
- **Componentes CSS:**
  - `.paper` — hoja con renglones
  - `.paper-meta` — `.date` + `.entry-num`
  - `.entry-title` — 64px
  - `.entry-text` — 36px, line-height 1.55, admite `<em>` (cursiva primary) y `<strong>` (dark)
  - `.entry-large` — 80px para slides con poco texto
  - `.signature` — `{{SIGNATURE}}`
  - `.closing-text` + `.closing-cta` — cierre con botón dark
- **Estructura típica:** Entrada 01 (hook con `.entry-large`) → Entradas 02–04 (título + párrafo) → Cierre (pregunta + CTA).

### Soft Poetic *(alternativa)*
**Archivo:** `templates/soft-poetic.html` · **template_tag:** `soft-poetic`

- **Paleta:** gradient diagonal pálido → blanco, orbes radiales con `--neon` y `--primary`, texto centrado, weight 200–300.
- **Vibe:** zen, contemplativo. Una respiración por slide.
- **Componentes CSS:**
  - `.top` — badge centrado con swatch
  - `.verse` — 84px weight 300, `<em>` weight 600 primary, `.pause` como salto visual
  - `.verse--big` — 116px
  - `.divider` — línea primary 80px
  - `.meta-line` — "02 / 05" centrado
  - `.signature`, `.closing-cta`
- **Estructura típica:** Portada con verso grande + firma → 3 slides con UN verso + divider → Cierre con pregunta + CTA.
- **Límite duro:** 1–3 líneas por slide. Si el contenido es largo, usar Diary.

---

## Cómo armar un slide nuevo

1. Abrir el archivo del template elegido.
2. Copiar el bloque `<style id="slide-css">...</style>` completo, sin modificar. Ese es el `style` del spec. El bloque `<style id="preview-only">` es solo para el navegador: no copiarlo.
3. Para cada slide aprobado:
   - Buscar el `<article class="slide">` de ejemplo con el rol más parecido (portada / contenido / cierre).
   - Copiarlo. Mantener el esqueleto (top + content + footer). Reemplazar solo el texto.
   - Usar las clases existentes. No inventar clases.
4. Cada slide queda como un `body` en el spec.

## Chrome opcional

Para piezas promocionales o colaboraciones: borrar `<div class="top">` (o `.top-bar` / `<header class="top">`) y `<div class="footer">` del article. El contenido queda solo y respira mejor.
