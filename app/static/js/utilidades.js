// utilidades.js
function mostrarMensaje(tipo, texto, tiempo = 2500) {
  const claseBase = 'alert';
  let claseTipo = '';

  switch (tipo) {
    case 'success': claseTipo = 'alert-success'; break;
    case 'warning': claseTipo = 'alert-warning'; break;
    case 'error': claseTipo = 'alert-error'; break;
    default: claseTipo = 'alert-warning';
  }

  $('#mensajeGlobal')
    .removeClass()
    .addClass(`${claseBase} ${claseTipo}`)
    .html(texto)
    .fadeIn();

  setTimeout(() => {
    $('#mensajeGlobal').fadeOut();
  }, tiempo);
}