const navToggle = document.querySelector('[data-nav-toggle]');
const navMenu = document.querySelector('[data-nav-menu]');
const loaderOverlay = document.getElementById('loaderOverlay');

if (navToggle && navMenu) {
  navToggle.addEventListener('click', () => {
    navMenu.classList.toggle('open');
  });
}

document.querySelectorAll('a[data-loading], .pulse[href], .primary-btn[href]').forEach((link) => {
  link.addEventListener('click', () => {
    if (loaderOverlay) {
      loaderOverlay.classList.add('active');
    }
  });
});

const revealItems = document.querySelectorAll('.reveal');

if (revealItems.length) {
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.14 }
  );

  revealItems.forEach((item) => observer.observe(item));
}