/* Formulario de pago SIMULADO: da formato a los campos, actualiza la tarjeta visual
   y muestra una pantalla de "procesando" antes de enviar. */
(function () {
  const form = document.getElementById('form-pago');
  if (!form) return;
  const $ = (id) => document.getElementById(id);
  const numero = $('id_numero_tarjeta'), titular = $('id_titular'), vence = $('id_vencimiento'), cvv = $('id_cvv');
  const vNum = $('tv-numero'), vTit = $('tv-titular'), vVen = $('tv-vence'), vMarca = $('tv-marca');

  function marca(d) {
    if (/^4/.test(d)) return 'VISA';
    if (/^(5[1-5]|222[1-9]|22[3-9]\d|2[3-6]\d\d|27[01]\d|2720)/.test(d)) return 'MASTERCARD';
    if (/^3[47]/.test(d)) return 'AMEX';
    return 'TARJETA';
  }
  function pintarNumero() {
    const d = numero.value.replace(/\D/g, '').slice(0, 19);
    numero.value = d.replace(/(.{4})/g, '$1 ').trim();
    const relleno = (d + '••••••••••••••••').slice(0, Math.max(16, d.length));
    vNum.textContent = relleno.replace(/(.{4})/g, '$1 ').trim();
    vMarca.textContent = marca(d);
  }
  numero.addEventListener('input', pintarNumero);
  titular.addEventListener('input', () => { vTit.textContent = titular.value.trim().toUpperCase() || 'NOMBRE DEL TITULAR'; });
  vence.addEventListener('input', () => {
    let d = vence.value.replace(/\D/g, '').slice(0, 4);
    if (d.length >= 3) d = d.slice(0, 2) + '/' + d.slice(2);
    vence.value = d;
    vVen.textContent = d || 'MM/AA';
  });
  cvv.addEventListener('input', () => { cvv.value = cvv.value.replace(/\D/g, '').slice(0, 4); });
  pintarNumero();

  function validar() {
    const errores = [];
    const d = numero.value.replace(/\D/g, '');
    if (d.length < 13 || d.length > 19) errores.push('Escribe un número de tarjeta de 13 a 19 dígitos.');
    if (!/^(0[1-9]|1[0-2])\/\d{2}$/.test(vence.value)) errores.push('El vencimiento debe tener el formato MM/AA.');
    if (cvv.value.length < 3) errores.push('El CVV tiene 3 o 4 dígitos.');
    if (titular.value.trim().length < 3) errores.push('Escribe el nombre del titular.');
    if (!document.getElementById('id_direccion').value.trim()) errores.push('Escribe tu dirección de envío.');
    return errores;
  }

  let enviando = false;
  form.addEventListener('submit', (ev) => {
    if (enviando) return;
    ev.preventDefault();
    const errores = validar();
    if (errores.length) { alert(errores.join('\n')); return; }
    enviando = true;
    $('btn-pagar').disabled = true;
    $('overlay-pago').hidden = false;
    setTimeout(() => form.submit(), 1800);      // el servidor vuelve a validar todo
  });
})();
