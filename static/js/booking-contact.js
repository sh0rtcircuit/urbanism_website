(function () {
  const node = document.querySelector('[data-obfuscated-email]');
  if (!node) {
    return;
  }

  node.textContent = 'urbanism.band[ät]outlook.de';
  node.classList.add('subtle-link', 'pseudo-link');
})();
