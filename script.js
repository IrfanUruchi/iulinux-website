const toggle = document.querySelector('.menu-toggle');
const nav = document.querySelector('#site-nav');
toggle?.addEventListener('click', () => {
  const open = nav.classList.toggle('is-open');
  toggle.setAttribute('aria-expanded', String(open));
});
nav?.querySelectorAll('a').forEach((link) => link.addEventListener('click', () => {
  nav.classList.remove('is-open');
  toggle?.setAttribute('aria-expanded', 'false');
}));

const installationHeading = [...document.querySelectorAll('.chapter h3')].find((heading) => heading.textContent.includes('USB, live environment'));
if (installationHeading) {
  const capture = document.createElement('figure');
  capture.className = 'handbook-screenshot';
  capture.innerHTML = '<img src="assets/screenshots/07-installer.png" alt="IULinux installer window showing the branded installation interface"><figcaption>07 / IULinux installer — authentic project capture</figcaption>';
  installationHeading.parentElement.insertBefore(capture, installationHeading.nextElementSibling);
}

const handbookNav = document.querySelector('.site-nav');
if (handbookNav && location.pathname.endsWith('handbook.html')) {
  const pdfLink = document.createElement('a');
  pdfLink.href = 'assets/downloads/IULinux-0.1-Alpha-Handbook.pdf';
  pdfLink.textContent = 'Download PDF ↘';
  handbookNav.appendChild(pdfLink);
}

const galleryFigures = document.querySelectorAll('.screenshot-gallery figure');
if (galleryFigures.length) {
  const dialog = document.createElement('dialog');
  dialog.className = 'screenshot-lightbox';
  dialog.innerHTML = '<button class="lightbox-close" type="button" aria-label="Close screenshot">Close</button><figure><img alt=""><figcaption></figcaption></figure>';
  document.body.appendChild(dialog);
  const lightboxImage = dialog.querySelector('img');
  const lightboxCaption = dialog.querySelector('figcaption');
  const closeLightbox = () => dialog.close();
  dialog.querySelector('.lightbox-close').addEventListener('click', closeLightbox);
  dialog.addEventListener('click', (event) => { if (event.target === dialog) closeLightbox(); });
  galleryFigures.forEach((figure) => {
    figure.tabIndex = 0;
    figure.setAttribute('role', 'button');
    figure.setAttribute('aria-label', `Open ${figure.querySelector('img')?.alt || 'screenshot'} at full size`);
    const open = () => {
      const image = figure.querySelector('img');
      lightboxImage.src = image.currentSrc || image.src;
      lightboxImage.alt = image.alt;
      lightboxCaption.textContent = figure.querySelector('figcaption')?.innerText || image.alt;
      dialog.showModal();
    };
    figure.addEventListener('click', open);
    figure.addEventListener('keydown', (event) => {
      if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); open(); }
    });
  });
}
