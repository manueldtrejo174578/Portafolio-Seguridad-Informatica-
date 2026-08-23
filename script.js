document.addEventListener('DOMContentLoaded', function () {

document.getElementById('year').textContent = new Date().getFullYear();

/* -----------------------------------------------------------
   CONFIGURACIÓN
   ----------------------------------------------------------- */

// Cloudflare Worker: reenvía el mensaje a tu bot de Telegram (ver README)
const WORKER_URL = 'https://telegrambot.174578.workers.dev';

// EmailJS: envía la confirmación automática al remitente (ver README)
const EMAILJS_PUBLIC_KEY  = '0g-l-qTxh5xUitFsd';
const EMAILJS_SERVICE_ID  = 'service_41hb0e5';
const EMAILJS_TEMPLATE_ID = 'template_27s7ezq';

const workerReady = WORKER_URL && WORKER_URL !== 'https://TU-WORKER.workers.dev';
const emailjsReady =
  typeof emailjs !== 'undefined' && EMAILJS_PUBLIC_KEY !== 'TU_PUBLIC_KEY';

if (emailjsReady) {
  emailjs.init({ publicKey: EMAILJS_PUBLIC_KEY });
}

const form = document.getElementById('contactForm');
const statusEl = document.getElementById('formStatus');
const submitBtn = document.getElementById('submitBtn');

if (!form) {
  console.error('No se encontró el formulario (#contactForm). Revisa que el id en el HTML coincida.');
  return;
}

function sendToTelegram(name, email, message) {
  return fetch(WORKER_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, email, message })
  })
    .then(function (response) {
      if (!response.ok) throw new Error('HTTP ' + response.status);
      return response.json();
    })
    .then(function (data) {
      if (!data.success) throw new Error(data.error || 'telegram_failed');
      return data;
    });
}

function sendAutoReply(name, email, message) {
  if (!emailjsReady) return Promise.resolve({ skipped: true });
  return emailjs.send(EMAILJS_SERVICE_ID, EMAILJS_TEMPLATE_ID, {
    name: name,
    email: email,
    message: message,
    time: new Date().toLocaleString('es-MX')
  });
}

form.addEventListener('submit', function (e) {
  e.preventDefault();
  statusEl.textContent = '';
  statusEl.style.color = 'inherit';

  const name = form.name.value.trim();
  const email = form.email.value.trim();
  const message = form.message.value.trim();

  if (!name || !email || !message) {
    statusEl.textContent = '> ERROR: Faltan parámetros en la solicitud.';
    statusEl.style.color = '#ff6b6b';
    return;
  }

  if (!workerReady) {
    statusEl.textContent = '> WARNING: Configura la URL de tu Cloudflare Worker en script.js.';
    statusEl.style.color = '#feca57';
    return;
  }

  submitBtn.disabled = true;
  statusEl.textContent = '> INICIANDO CONEXIÓN SEGURA...';
  statusEl.style.color = 'inherit';

  Promise.allSettled([
    sendToTelegram(name, email, message),
    sendAutoReply(name, email, message)
  ])
    .then(function (results) {
      const telegramOk = results[0].status === 'fulfilled';

      if (telegramOk) {
        statusEl.textContent = '> ÉXITO: Payload entregado y ofuscado correctamente.';
        statusEl.style.color = 'var(--accent-bright)';
        form.reset();
      } else {
        statusEl.textContent = '> ERROR: Fallo en el gateway de seguridad.';
        statusEl.style.color = '#ff6b6b';
        console.error(results[0].reason);
      }

      if (results[1].status === 'rejected') {
        console.error('EmailJS error:', results[1].reason);
      }
    })
    .finally(function () {
      submitBtn.disabled = false;
    });
});

}); // fin DOMContentLoaded
