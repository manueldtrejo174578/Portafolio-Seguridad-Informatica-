/**
 * Cloudflare Worker — proxy seguro entre el formulario del portafolio
 * y la API de Telegram.
 *
 * Por qué existe: el sitio (GitHub Pages) es estático, así que todo su
 * JS es público. Si el token del bot viviera en ese JS, cualquiera que
 * abriera el código fuente podría usarlo. Este Worker guarda el token
 * como variable secreta del lado del servidor; el navegador nunca lo ve.
 *
 * Variables/secretos que debes configurar en Cloudflare (Settings > Variables):
 *   TELEGRAM_BOT_TOKEN   (secret)  -> token que te da @BotFather
 *   TELEGRAM_CHAT_ID     (secret)  -> tu chat_id numérico
 *   ALLOWED_ORIGIN        (var)    -> ej. https://tu-usuario.github.io
 *
 * Instrucciones completas de despliegue: ver README.md.
 */

export default {
  async fetch(request, env) {
    const cors = corsHeaders(env);

    if (request.method === "OPTIONS") {
      return new Response(null, { headers: cors });
    }

    if (request.method !== "POST") {
      return new Response("Method not allowed", { status: 405, headers: cors });
    }

    let data;
    try {
      data = await request.json();
    } catch {
      return new Response("Invalid JSON", { status: 400, headers: cors });
    }

    const name = (data.name || "").toString().slice(0, 200);
    const email = (data.email || "").toString().slice(0, 200);
    const subject = (data.subject || "").toString().slice(0, 200);
    const message = (data.message || "").toString().slice(0, 4000);

    if (!name || !email || !subject || !message) {
      return new Response("Missing fields", { status: 400, headers: cors });
    }

    const text =
      `📥 Nuevo mensaje del portafolio\n\n` +
      `Nombre: ${name}\n` +
      `Correo: ${email}\n` +
      `Asunto: ${subject}\n\n` +
      `${message}`;

    const tgUrl = `https://api.telegram.org/bot${env.TELEGRAM_BOT_TOKEN}/sendMessage`;

    const tgRes = await fetch(tgUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        chat_id: env.TELEGRAM_CHAT_ID,
        text,
      }),
    });

    if (!tgRes.ok) {
      return new Response("Telegram error", { status: 502, headers: cors });
    }

    return new Response("OK", { status: 200, headers: cors });
  },
};

function corsHeaders(env) {
  return {
    "Access-Control-Allow-Origin": env.ALLOWED_ORIGIN || "*",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
  };
}
