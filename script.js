const TELEGRAM_PROXY_URL = "https://contactobot.175329.workers.dev";

const EMAILJS_PUBLIC_KEY         = "Kr6139fnMFe5NwZN7";
const EMAILJS_SERVICE_ID         = "service_4cqjacs";
const EMAILJS_TEMPLATE_AUTOREPLY = "template_5i9pggd"; 

const telegramReady = TELEGRAM_PROXY_URL !== "https://TU-WORKER.workers.dev";

const emailjsReady =
  typeof emailjs !== "undefined" &&
  EMAILJS_PUBLIC_KEY !== "TU_PUBLIC_KEY";

if (emailjsReady) {
  emailjs.init({ publicKey: EMAILJS_PUBLIC_KEY });
}

/* =========================================================
   AÑO EN EL FOOTER
   ========================================================= */
document.getElementById("year").textContent = new Date().getFullYear();

/* =========================================================
   TIMESTAMP "EN VIVO" DEL EVENT CARD
   ========================================================= */
function updateLiveTimestamp() {
  const el = document.getElementById("liveTimestamp");
  if (!el) return;
  const now = new Date();
  const pad = (n) => String(n).padStart(2, "0");
  const stamp = `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())} ${pad(now.getHours())}:${pad(now.getMinutes())}:${pad(now.getSeconds())}`;
  el.textContent = `Fecha: ${stamp}`;
}
updateLiveTimestamp();
setInterval(updateLiveTimestamp, 1000);

/* =========================================================
   MENÚ MÓVIL
   ========================================================= */
const navToggle = document.getElementById("navToggle");
const primaryNav = document.getElementById("primaryNav");

navToggle.addEventListener("click", () => {
  const isOpen = primaryNav.classList.toggle("is-open");
  navToggle.setAttribute("aria-expanded", String(isOpen));
});

primaryNav.querySelectorAll("a").forEach((link) => {
  link.addEventListener("click", () => {
    primaryNav.classList.remove("is-open");
    navToggle.setAttribute("aria-expanded", "false");
  });
});

/* Enlaces de apartados aún no publicados: no navegan */
document.querySelectorAll(".is-pending").forEach((link) => {
  link.addEventListener("click", (e) => e.preventDefault());
});

/* =========================================================
   REVEAL AL HACER SCROLL
   ========================================================= */
const revealEls = document.querySelectorAll(".reveal");
if ("IntersectionObserver" in window) {
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.15 }
  );
  revealEls.forEach((el) => observer.observe(el));
} else {
  revealEls.forEach((el) => el.classList.add("is-visible"));
}

/* =========================================================
   FORMULARIO DE CONTACTO
   ========================================================= */
const contactForm = document.getElementById("contactForm");
const submitBtn = document.getElementById("submitBtn");
const formStatus = document.getElementById("formStatus");

contactForm.addEventListener("submit", async (e) => {
  e.preventDefault();

  const data = {
    name: document.getElementById("name").value.trim(),
    email: document.getElementById("email").value.trim(),
    subject: document.getElementById("subject").value.trim(),
    message: document.getElementById("message").value.trim(),
  };

  if (!data.name || !data.email || !data.subject || !data.message) {
    setStatus("Completa todos los campos antes de enviar.", "err");
    return;
  }

  if (!telegramReady && !emailjsReady) {
    setStatus(
      "El envío automático aún no está configurado (faltan las claves en script.js).",
      "err"
    );
    return;
  }

  submitBtn.disabled = true;
  setStatus("Enviando…", "");

  try {
    const tasks = [];

    // 1) Aviso instantáneo para ti vía Telegram (a través del Worker)
    if (telegramReady) {
      tasks.push(
        fetch(TELEGRAM_PROXY_URL, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(data),
        }).then((res) => {
          if (!res.ok) throw new Error("Telegram proxy error");
        })
      );
    }

    // 2) Autorespuesta para quien llenó el formulario
    if (emailjsReady) {
      tasks.push(emailjs.send(EMAILJS_SERVICE_ID, EMAILJS_TEMPLATE_AUTOREPLY, data));
    }

    await Promise.all(tasks);

    setStatus("Reporte enviado. Te llegará una confirmación por correo en breve.", "ok");
    contactForm.reset();
  } catch (err) {
    console.error(err);
    setStatus("No se pudo enviar el mensaje. Intenta de nuevo más tarde.", "err");
  } finally {
    submitBtn.disabled = false;
  }
});

function setStatus(text, type) {
  formStatus.textContent = text;
  formStatus.className = "form-status" + (type ? " " + type : "");
}
