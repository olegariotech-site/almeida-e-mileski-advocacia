/* Progressive enhancement only. Native disclosure and all routes work without JS. */
(() => {
  'use strict';
  const menu = document.querySelector('#mobile-menu');
  const toggle = document.querySelector('#menu-toggle');
  if (menu && toggle) {
    menu.addEventListener('toggle', () => {
      toggle.setAttribute('aria-label', menu.open ? 'Fechar menu' : 'Abrir menu');
    });
    document.addEventListener('keydown', event => {
      if (event.key !== 'Escape') return;
      document.querySelectorAll('.nav-disclosure[open]').forEach(el => { el.open = false; });
      if (menu.open) { menu.open = false; toggle.focus(); }
    });
    document.addEventListener('click', event => {
      if (!event.target.closest('.nav-disclosure')) {
        document.querySelectorAll('.nav-disclosure[open]').forEach(el => { el.open = false; });
      }
    });
  }

  document.querySelectorAll('[data-accordion-group]').forEach(group => {
    const controls = group.querySelector('.accordion-tools');
    if (!controls) return;
    const disclosures = [...group.querySelectorAll('details.signature')];
    // Native <summary> owns keyboard support and the announced expanded state.
    controls.hidden = false;
    controls.querySelectorAll('button[data-expand]').forEach(button => {
      button.addEventListener('click', () => {
        const open = button.dataset.expand === 'true';
        disclosures.forEach(disclosure => { disclosure.open = open; });
        const status = group.querySelector('[role="status"]');
        if (status) status.textContent = open ? 'Todas as seções foram expandidas.' : 'Todas as seções foram recolhidas.';
      });
    });
  });

  const revealHash = () => {
    let id;
    try { id = decodeURIComponent(location.hash.slice(1)); } catch { return; }
    const target = id && document.getElementById(id);
    if (target && target.matches('details')) target.open = true;
  };
  revealHash();
  window.addEventListener('hashchange', revealHash);
  document.querySelectorAll('.context-nav a[href^="#"]').forEach(link => {
    link.addEventListener('click', () => {
      const target = document.getElementById(link.getAttribute('href').slice(1));
      if (target) target.open = true;
    });
  });

  const progress = document.querySelector('.progress');
  let scheduled = false;
  const update = () => {
    const distance = document.documentElement.scrollHeight - innerHeight;
    if (progress) progress.style.transform = `scaleX(${distance > 0 ? Math.min(1, Math.max(0, scrollY / distance)) : 1})`;
    scheduled = false;
  };
  const queueUpdate = () => { if (!scheduled) { scheduled = true; requestAnimationFrame(update); } };
  window.addEventListener('scroll', queueUpdate, {passive: true});
  window.addEventListener('resize', queueUpdate, {passive: true});
  document.addEventListener('toggle', queueUpdate, true);
  update();

  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
  if ('IntersectionObserver' in window && !reduced.matches) {
    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) { entry.target.classList.add('is-visible'); observer.unobserve(entry.target); }
      });
    }, {threshold: .08});
    document.querySelectorAll('.reveal').forEach(el => observer.observe(el));
    reduced.addEventListener('change', () => { if (reduced.matches) observer.disconnect(); });
  }
  // Keep attribution in the address bar when moving between this site's pages.
  // No cookie, storage, analytics event, network request or outbound propagation.
  const allowed = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term'];
  const current = new URLSearchParams(location.search);
  document.querySelectorAll('a[data-internal]').forEach(link => {
    const next = new URL(link.href, location.href);
    if (next.origin !== location.origin) return;
    allowed.forEach(key => { if (current.has(key)) next.searchParams.set(key, current.get(key).slice(0, 200)); });
    link.href = next.href;
  });
})();
