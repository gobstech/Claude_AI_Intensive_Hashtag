document.addEventListener('DOMContentLoaded', function () {
  var toggle = document.querySelector('.menu-toggle');
  var menu = document.querySelector('.menu');
  if (toggle && menu) {
    toggle.addEventListener('click', function () {
      menu.classList.toggle('aberto');
      var aberto = menu.classList.contains('aberto');
      toggle.setAttribute('aria-expanded', aberto ? 'true' : 'false');
    });
  }
});
