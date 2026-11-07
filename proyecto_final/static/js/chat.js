/* Chat en vivo (consulta al servidor cada 2 segundos). Los mensajes viven solo en la memoria del servidor. */
(function () {
  const caja = document.getElementById('chat-caja');
  const form = document.getElementById('chat-form');
  const input = document.getElementById('chat-texto');
  const boton = document.getElementById('chat-enviar');
  const csrf = document.getElementById('chat-csrf').value;
  const datos = document.getElementById('chat-datos').dataset;

  let ultimo = 0;
  let arranque = null;
  let ocupado = false;

  function pintar(m) {
    const div = document.createElement('div');
    div.className = 'msg' + (m.staff ? ' msg-staff' : '');
    const autor = document.createElement('strong');
    autor.textContent = m.usuario;                       // textContent: evita inyectar HTML
    div.appendChild(autor);
    if (m.staff) {
      const ins = document.createElement('span');
      ins.className = 'insignia';
      ins.textContent = 'Equipo';
      div.appendChild(ins);
    }
    const hora = document.createElement('small');
    hora.textContent = ' ' + m.hora;
    div.appendChild(hora);
    const texto = document.createElement('p');
    texto.textContent = m.texto;
    div.appendChild(texto);
    caja.appendChild(div);
  }

  async function traer() {
    if (ocupado || document.hidden) return;
    ocupado = true;
    try {
      const r = await fetch(datos.urlMensajes + '?desde=' + ultimo, { headers: { 'Accept': 'application/json' } });
      if (!r.ok) return;
      const d = await r.json();
      if (arranque !== null && d.arranque !== arranque) {   // el servidor se reinició: empezar de cero
        caja.innerHTML = '';
        ultimo = 0;
        arranque = d.arranque;
        return;
      }
      arranque = d.arranque;
      const abajo = caja.scrollTop + caja.clientHeight >= caja.scrollHeight - 40;
      d.mensajes.forEach(m => { pintar(m); ultimo = Math.max(ultimo, m.id); });
      if (d.mensajes.length && abajo) caja.scrollTop = caja.scrollHeight;
    } catch (e) { /* sin conexión: se reintenta en el siguiente ciclo */ }
    finally { ocupado = false; }
  }

  form.addEventListener('submit', async (ev) => {
    ev.preventDefault();
    const texto = input.value.trim();
    if (!texto) return;
    boton.disabled = true;
    try {
      const r = await fetch(datos.urlEnviar, {
        method: 'POST',
        headers: { 'X-CSRFToken': csrf, 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({ texto }),
      });
      if (r.ok) {
        input.value = '';
        await traer();
        caja.scrollTop = caja.scrollHeight;
      }
    } catch (e) { /* se puede volver a intentar */ }
    finally { boton.disabled = false; input.focus(); }
  });

  traer();
  setInterval(traer, 2000);
})();
