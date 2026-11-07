/* Tracker de GOLDEN LUXURY (equivale a tracker.js del proyecto PHP).
   Registra vistas, clics en botones/enlaces y tiempo en página, solo si el usuario acepta cookies. */
(function () {
  const body = document.body;
  const URL_EVENTO = body.dataset.eventoUrl;

  function getCookie(name) {
    const m = document.cookie.match('(^|;)\\s*' + name + '=([^;]+)');
    return m ? decodeURIComponent(m[2]) : '';
  }

  function consentimiento() { return localStorage.getItem('gl_cookies'); }

  function mostrarBanner() {
    const b = document.getElementById('cookies');
    if (!b) return;
    b.style.display = 'flex';
    b.querySelector('[data-si]').onclick = () => { localStorage.setItem('gl_cookies', 'si'); b.style.display = 'none'; iniciar(); };
    b.querySelector('[data-no]').onclick = () => { localStorage.setItem('gl_cookies', 'no'); b.style.display = 'none'; };
  }

  function sessionId() {
    let id = sessionStorage.getItem('gl_session');
    if (!id) { id = 's_' + Math.random().toString(36).slice(2) + Date.now().toString(36); sessionStorage.setItem('gl_session', id); }
    return id;
  }

  function enviar(datos) {
    fetch(URL_EVENTO, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') },
      body: JSON.stringify(Object.assign({ session_id: sessionId(), page: location.pathname }, datos)),
      keepalive: true,
    }).catch(() => {});
  }

  let iniciado = false;
  function iniciar() {
    if (iniciado) return;
    iniciado = true;
    const t0 = Date.now();
    enviar({ action_type: 'vista' });

    document.addEventListener('click', (ev) => {
      const el = ev.target.closest('button, a, input[type="submit"]');
      if (!el) return;
      const tipo = el.tagName === 'A' ? 'enlace' : (el.tagName === 'INPUT' ? 'botón de envío' : 'botón');
      const texto = (el.innerText || el.value || el.getAttribute('aria-label') || '').replace(/\s+/g, ' ').trim().slice(0, 35);
      enviar({ action_type: 'clic', element_details: texto ? `Clic en ${tipo}: "${texto}"` : `Clic en ${tipo} (sin texto)` });
    });

    let enviado = false;
    function cerrar() {
      if (enviado) return;
      enviado = true;
      enviar({ action_type: 'tiempo_pagina', time_spent: Math.round((Date.now() - t0) / 1000) });
    }
    window.addEventListener('pagehide', cerrar);
    document.addEventListener('visibilitychange', () => { if (document.visibilityState === 'hidden') cerrar(); });
  }

  document.addEventListener('DOMContentLoaded', () => {
    const c = consentimiento();
    if (c === 'si') iniciar();
    else if (c === null) mostrarBanner();
  });
})();
