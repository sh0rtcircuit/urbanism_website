(function () {
  const AUTOPLAY_MS = 3000;

  const initCarousel = (carousel) => {
    const track = carousel.querySelector('[data-carousel-track]');
    const slides = Array.from(carousel.querySelectorAll('[data-slide]'));
    const dots = Array.from(carousel.querySelectorAll('[data-dot]'));
    const prev = carousel.querySelector('[data-carousel-prev]');
    const next = carousel.querySelector('[data-carousel-next]');

    if (!track || slides.length === 0 || carousel.dataset.carouselReady === 'true') {
      return;
    }

    carousel.dataset.carouselReady = 'true';

    let index = 0;
    let autoplayId = null;

    const render = () => {
      track.style.transform = `translateX(-${index * 100}%)`;

      slides.forEach((slide, slideIndex) => {
        slide.classList.toggle('is-active', slideIndex === index);
      });

      dots.forEach((dot, dotIndex) => {
        dot.classList.toggle('is-active', dotIndex === index);
        dot.setAttribute('aria-current', dotIndex === index ? 'true' : 'false');
      });
    };

    const goTo = (newIndex) => {
      const last = slides.length - 1;
      if (newIndex < 0) {
        index = last;
      } else if (newIndex > last) {
        index = 0;
      } else {
        index = newIndex;
      }
      render();
    };

    const stopAutoplay = () => {
      if (autoplayId) {
        window.clearInterval(autoplayId);
        autoplayId = null;
      }
    };

    const startAutoplay = () => {
      if (slides.length <= 1) {
        return;
      }
      stopAutoplay();
      autoplayId = window.setInterval(() => {
        goTo(index + 1);
      }, AUTOPLAY_MS);
    };

    prev?.addEventListener('click', () => {
      goTo(index - 1);
      startAutoplay();
    });

    next?.addEventListener('click', () => {
      goTo(index + 1);
      startAutoplay();
    });

    dots.forEach((dot) => {
      dot.addEventListener('click', () => {
        const dotIndex = Number(dot.getAttribute('data-dot'));
        goTo(dotIndex);
        startAutoplay();
      });
    });

    carousel.addEventListener('mouseenter', stopAutoplay);
    carousel.addEventListener('mouseleave', startAutoplay);

    render();
    startAutoplay();
  };

  window.initGalleryCarousels = (root) => {
    const scope = root && root.querySelectorAll ? root : document;
    const carousels = [];

    if (scope.matches && scope.matches('[data-carousel]')) {
      carousels.push(scope);
    }

    scope.querySelectorAll('[data-carousel]').forEach((node) => carousels.push(node));
    carousels.forEach(initCarousel);
  };

  window.initGalleryCarousels(document);
})();
