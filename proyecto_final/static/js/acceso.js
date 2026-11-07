/* Visitantes sin sesión: pueden ver la página, pero al intentar usar cualquier
   botón o enlace se muestra el aviso de "Inicia sesión o crea tu cuenta".
   Lo que lleve el atributo data-libre (login, registro, cookies...) no se bloquea. */
(function () {
  if (document.body.dataset.auth === '1') return;
  const modal = document.getElementById('modal-acceso');
  if (!modal) return;

  const abrir = () => { modal.classList.add('abierto'); const b = modal.querySelector('a'); if (b) b.focus(); };
  const cerrar = () => modal.classList.remove('abierto');
  const libre = (el) => el.closest('[data-libre]') !== null;

  document.addEventListener('click', (ev) => {
    const el = ev.target.closest('a, button, input[type="submit"], [role="button"]');
    if (!el || libre(el)) return;
    ev.preventDefault();
    abrir();
  }, true);

  document.addEventListener('submit', (ev) => {
    if (libre(ev.target)) return;
    ev.preventDefault();
    abrir();
  }, true);

  modal.addEventListener('click', (ev) => { if (ev.target === modal) cerrar(); });
  modal.querySelector('[data-cerrar]').addEventListener('click', cerrar);
  document.addEventListener('keydown', (ev) => { if (ev.key === 'Escape') cerrar(); });
})();
