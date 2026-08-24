# Portafolio — MDTS · CNO IV Seguridad Informática

Sitio estático (HTML/JS) para el portafolio digital de la asignatura CNO IV.

## Publicación

1. Crea un repo en GitHub y sube los archivos.
2. Activa GitHub Pages: *Settings → Pages → Deploy from branch → main*.
3. Marca *Enforce HTTPS*. Listo.

URL: `https://manueldtrejo174578.github.io/Portafolio-Seguridad-Informatica-/`

## Formulario de contacto

- **Notificación a mí:** vía Worker de Cloudflare (proxy a Telegram). El token del bot se guarda como secreto en el Worker, nunca en el código del navegador.
- **Autorespuesta al visitante:** vía EmailJS. Configura tu `PUBLIC_KEY`, `SERVICE_ID` y `TEMPLATE_ID` en `index.html`.

> Mientras no configures las claves, el formulario valida campos pero no envía correos. El sitio sigue funcionando.

Para activar un enlace futuro, reemplaza `onclick="return false;"` por el `href` correspondiente.

## Pendiente

- [ ] Incluir mi direccion de correo en `index.html`.
- [ ] Configurar Worker de Cloudflare y EmailJS.
- [ ] Verificar en móvil y confirmar el candado 🔒 en la URL.

*Manuel Darío Trejo Salazar (MDTS) — UPSLP · 7.º Semestre*
