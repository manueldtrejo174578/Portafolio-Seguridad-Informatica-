# Portafolio — MDTS · Seguridad Informática (CNO IV)

Sitio estático (HTML/CSS/JS puro, sin dependencias de build) que sirve como Parcial 1
del portafolio digital: apartado **Inicio**.

## 1. Publicar en GitHub Pages (HTTPS incluido automáticamente)

1. Crea un repositorio nuevo en GitHub, por ejemplo `portafolio-seguridad-informatica`.
2. Sube `index.html` a la raíz del repositorio (puede ser por la web de GitHub con
   "Add file → Upload files", o por línea de comandos):
   ```bash
   git init
   git add index.html
   git commit -m "Parcial 1: apartado Inicio"
   git branch -M main
   git remote add origin https://github.com/TU_USUARIO/portafolio-seguridad-informatica.git
   git push -u origin main
   ```
3. En el repositorio: **Settings → Pages → Source → Deploy from a branch**,
   selecciona la rama `main` y la carpeta `/ (root)`. Guarda.
4. En un par de minutos tu sitio estará disponible en:
   `https://TU_USUARIO.github.io/portafolio-seguridad-informatica/`
   GitHub Pages sirve **siempre bajo HTTPS** con certificado SSL automático —
   no requiere configuración adicional. Esto cumple el requisito de certificado SSL.
5. Actualiza el enlace del repositorio en el propio sitio (`id="repoLink"` en
   `index.html`) para que apunte a tu repositorio real.

## 2. Activar la respuesta automática del formulario (EmailJS)

El formulario ya está integrado con [EmailJS](https://www.emailjs.com), un servicio
gratuito que permite enviar correos (incluida una auto-respuesta al remitente) desde
un sitio 100% estático, sin backend propio.

1. Crea una cuenta gratuita en https://www.emailjs.com
2. **Email Services** → conecta tu cuenta de Gmail/Outlook → copia el `SERVICE_ID`.
3. **Email Templates** → crea una plantilla cuyo destinatario sea `{{email}}`
   (el correo que la persona escribió en el formulario), con un mensaje de
   confirmación tipo "Gracias por tu mensaje, {{name}}, te responderé pronto."
   Copia el `TEMPLATE_ID`.
4. **Account → API Keys** → copia tu `PUBLIC_KEY`.
5. En `index.html`, al final del archivo, reemplaza:
   ```js
   const EMAILJS_PUBLIC_KEY  = "TU_PUBLIC_KEY";
   const EMAILJS_SERVICE_ID  = "TU_SERVICE_ID";
   const EMAILJS_TEMPLATE_ID = "TU_TEMPLATE_ID_AUTORESPUESTA";
   ```
   con tus valores reales y vuelve a publicar el cambio (`git push`).
6. Mientras no configures estos valores, el formulario sigue siendo funcional en
   apariencia (valida campos, muestra estados) pero avisa que falta activar el envío.

## 3. Estructura para los próximos parciales

El menú de navegación ya incluye los apartados **Sobre mí**, **Proyectos** y
**Certificaciones**, marcados como "pronto". En los siguientes parciales, crea un
archivo por apartado (por ejemplo `sobre-mi.html`, `proyectos.html`) y enlázalos
desde `nav.mainnav` reemplazando el `onclick="return false;"` por el `href`
correspondiente.

## 4. Personalización pendiente

- Reemplaza el bloque `MT` en `.avatar-box` por una foto real (`<img>`)
  si lo deseas.
- Ajusta el enlace de `#repoLink` a tu repositorio definitivo.
