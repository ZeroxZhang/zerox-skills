// 导航与引用增强；正文和 SVG 在关闭脚本时仍可阅读。
const tocButton = document.getElementById('toc-toggle');
tocButton.addEventListener('click', () => {
  const expanded = document.body.classList.toggle('nav-open');
  tocButton.setAttribute('aria-expanded', String(expanded));
});
document.querySelector('.print-button').addEventListener('click', () => window.print());
document.addEventListener('keydown', event => {
  if (event.key === 'Escape') {
    document.body.classList.remove('nav-open');
    tocButton.setAttribute('aria-expanded', 'false');
  }
});
document.querySelectorAll('a[href^="#"]').forEach(link => {
  link.addEventListener('click', () => {
    const target = document.getElementById(link.getAttribute('href').slice(1));
    if (target && target.closest('details')) target.closest('details').open = true;
    document.body.classList.remove('nav-open');
    tocButton.setAttribute('aria-expanded', 'false');
  });
});
function revealReference() {
  const target = document.getElementById(location.hash.slice(1));
  if (target && target.closest('details')) target.closest('details').open = true;
}
window.addEventListener('hashchange', revealReference);
revealReference();
if ('IntersectionObserver' in window) {
  const links = [...document.querySelectorAll('.sidebar nav a')];
  const observer = new IntersectionObserver(entries => {
    for (const entry of entries) {
      if (entry.isIntersecting) links.forEach(link => {
        const active = link.hash === '#' + entry.target.id;
        link.classList.toggle('section-nav-active', active);
        if (active) link.setAttribute('aria-current', 'location');
        else link.removeAttribute('aria-current');
      });
    }
  }, { rootMargin: '-5% 0px -65% 0px' });
  document.querySelectorAll('main > [id]').forEach(section => observer.observe(section));
}
