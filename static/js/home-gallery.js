(function () {
  const root = document.getElementById('homeGallery');
  const heroVisual = document.getElementById('heroVisual');
  if (!root) {
    return;
  }

  const buildImageUrl = (fileName) => `static/images/photos/${encodeURIComponent(fileName)}`;
  const altFromName = (fileName) =>
    `Urbanism Foto: ${fileName
      .replace(/\.[^.]+$/, '')
      .replace(/[_-]+/g, ' ')
      .trim()}`;

  const render = (files) => {
    if (files.length === 0) {
      root.innerHTML = '<p class="empty-state">Keine Gallery-Bilder gefunden.</p>';
      return;
    }

    const firstImage = buildImageUrl(files[0]);
    if (heroVisual) {
      heroVisual.style.setProperty('--hero-image', `url('${firstImage}')`);
    }

    const slides = files
      .map((file, idx) => {
        const imageUrl = buildImageUrl(file);
        return `
          <figure class="gallery-slide${idx === 0 ? ' is-active' : ''}" data-slide>
            <img src="${imageUrl}" alt="${altFromName(file)}" loading="lazy" />
          </figure>
        `;
      })
      .join('');

    const controls =
      files.length > 1
        ? `
          <div class="gallery-controls">
            <button class="gallery-arrow" type="button" data-carousel-prev aria-label="Vorheriges Bild">
              <i class="bi bi-chevron-left" aria-hidden="true"></i>
            </button>
            <button class="gallery-arrow" type="button" data-carousel-next aria-label="Nächstes Bild">
              <i class="bi bi-chevron-right" aria-hidden="true"></i>
            </button>
          </div>
          <div class="gallery-dots" role="tablist" aria-label="Gallery Navigation">
            ${files
              .map(
                (_, idx) =>
                  `<button type="button" class="gallery-dot${idx === 0 ? ' is-active' : ''}" data-dot="${idx}" aria-label="Bild ${
                    idx + 1
                  }" aria-current="${idx === 0 ? 'true' : 'false'}"></button>`
              )
              .join('')}
          </div>
        `
        : '';

    root.innerHTML = `
      <div class="gallery-track-wrap">
        <div class="gallery-track" data-carousel-track>
          ${slides}
        </div>
      </div>
      ${controls}
    `;

    if (typeof window.initGalleryCarousels === 'function') {
      window.initGalleryCarousels(root);
    }
  };

  const load = async () => {
    try {
      const response = await fetch('static/data/gallery.json', { cache: 'no-store' });
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      const payload = await response.json();
      const files = payload.map((item) => item.file).filter(Boolean);
      render(files);
    } catch (error) {
      root.innerHTML = '<p class="empty-state">Gallery konnte nicht geladen werden.</p>';
    }
  };

  load();
})();
