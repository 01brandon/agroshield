/* faq accordion */
document.querySelectorAll('.faq-q').forEach(btn => {
  btn.addEventListener('click', () => {
    const item = btn.closest('.faq-item');
    const isActive = item.classList.contains('active');
    document.querySelectorAll('.faq-item').forEach(i => i.classList.remove('active'));
    if (!isActive) item.classList.add('active');
  });
});

/* mobile nav */
const toggle = document.getElementById('navToggle');
const links = document.querySelector('.nav-links');
if (toggle) {
  toggle.addEventListener('click', () => {
    links.style.display = links.style.display === 'flex' ? 'none' : 'flex';
    links.style.flexDirection = 'column';
    links.style.position = 'absolute';
    links.style.top = '68px';
    links.style.left = '0';
    links.style.right = '0';
    links.style.background = 'rgba(10,20,10,.97)';
    links.style.padding = '20px 24px';
    links.style.gap = '16px';
  });
}

/* nav scroll effect */
window.addEventListener('scroll', () => {
  const nav = document.querySelector('.nav');
  if (window.scrollY > 40) {
    nav.style.background = 'rgba(10,20,10,.97)';
  } else {
    nav.style.background = 'rgba(10,20,10,.85)';
  }
});

document.addEventListener('DOMContentLoaded', () => {
  const signInBtn = document.querySelector('.nav-actions a.btn-primary');
  if (signInBtn && localStorage.getItem('access')) {
    signInBtn.textContent = 'dashboard';
    signInBtn.href = '/dashboard/';
  }
});

// scroll animations
document.addEventListener('DOMContentLoaded', () => {
  // add fade-up to key sections
  document.querySelectorAll('.feature-card, .step, .stat-card, .faq-item, .partner-logo').forEach((el, i) => {
    el.classList.add('fade-up');
    if (i % 3 === 1) el.classList.add('fade-up-delay-1');
    if (i % 3 === 2) el.classList.add('fade-up-delay-2');
  });
  document.querySelectorAll('.stats-text, .stats-cards, .faq-left, .faq-list, .cta-inner').forEach(el => {
    el.classList.add('fade-up');
  });

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12 });

  document.querySelectorAll('.fade-up').forEach(el => observer.observe(el));

  // mobile nav toggle
  const toggle = document.getElementById('navToggle');
  const links  = document.querySelector('.nav-links');
  if (toggle && links) {
    toggle.addEventListener('click', () => links.classList.toggle('open'));
  }

  // navbar shows dashboard if logged in
  const signInBtn = document.querySelector('.nav-actions a.btn-primary');
  if (signInBtn && localStorage.getItem('access')) {
    signInBtn.textContent = 'dashboard';
    signInBtn.href = '/dashboard/';
  }
});
