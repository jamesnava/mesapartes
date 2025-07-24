// utilidades.js
function mostrarMensaje(tipo, texto, tiempo = 2500) {
  const claseBase = 'toast-mensaje';
  let claseTipo = '';

  switch (tipo) {
    case 'success': claseTipo = 'bg-success text-white'; break;
    case 'warning': claseTipo = 'bg-warning text-dark'; break;
    case 'error': claseTipo = 'bg-danger text-white'; break;
    default: claseTipo = 'bg-secondary text-white';
  }

  const $mensaje = $('#mensajeGlobal');

  $mensaje
    .removeClass()
    .addClass(`${claseBase} ${claseTipo}`)
    .html(texto)
    .fadeIn();

  setTimeout(() => {
    $mensaje.fadeOut();
  }, tiempo);
}