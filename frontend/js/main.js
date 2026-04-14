/*
  main.js — Global JavaScript
  Safari Beauty Salon

  This file runs on every page (linked in every HTML file).
  It handles interactions that are the same across all pages:
  - Mobile hamburger menu toggle
  - Scroll-based nav styling
  - Fade-in animations on scroll

  JavaScript runs in the browser after the HTML is loaded.
  It finds HTML elements and adds behavior to them.
*/


/* ── MOBILE MENU TOGGLE ───────────────────────────────────────
   When someone taps the hamburger icon on mobile,
   this toggles the nav links open and closed.
──────────────────────────────────────────────────────────────── */
const navToggle = document.getElementById('navToggle');
const navLinks  = document.getElementById('navLinks');

if (navToggle && navLinks) {
  navToggle.addEventListener('click', function() {
    // .toggle() adds the class if missing, removes it if present
    navLinks.classList.toggle('open');
  });

  // Close menu when a link is clicked (good UX on mobile)
  navLinks.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', function() {
      navLinks.classList.remove('open');
    });
  });
}


/* ── SCROLL-BASED NAV SHADOW ──────────────────────────────────
   Adds a subtle shadow to the nav when the user scrolls down,
   so it stands out from the content behind it.
──────────────────────────────────────────────────────────────── */
const nav = document.querySelector('.nav');

if (nav) {
  window.addEventListener('scroll', function() {
    if (window.scrollY > 20) {
      nav.style.boxShadow = '0 2px 20px rgba(92, 74, 50, 0.10)';
    } else {
      nav.style.boxShadow = 'none';
    }
  });
}


/* ── SCROLL-TRIGGERED FADE-IN ANIMATIONS ─────────────────────
   Elements with the class .fade-up start invisible.
   As they scroll into view, they fade in smoothly.

   IntersectionObserver watches when elements enter the viewport.
──────────────────────────────────────────────────────────────── */
const fadeElements = document.querySelectorAll(
  '.service-card, .feature, .testimonial, .remodel-card, .contact-block'
);

if (fadeElements.length > 0) {
  const observer = new IntersectionObserver(
    function(entries) {
      entries.forEach(function(entry) {
        if (entry.isIntersecting) {
          // Element is now visible — add animation class
          entry.target.style.opacity = '1';
          entry.target.style.transform = 'translateY(0)';
          // Stop watching once animated
          observer.unobserve(entry.target);
        }
      });
    },
    {
      threshold: 0.1,      // Trigger when 10% of element is visible
      rootMargin: '0px 0px -40px 0px'  // Trigger slightly before fully in view
    }
  );

  fadeElements.forEach(function(el) {
    // Start elements invisible and shifted down
    el.style.opacity = '0';
    el.style.transform = 'translateY(20px)';
    el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    observer.observe(el);
  });
}


/* ── ACTIVE NAV LINK ──────────────────────────────────────────
   Automatically highlights the correct nav link
   based on the current page URL.
──────────────────────────────────────────────────────────────── */
const currentPage = window.location.pathname.split('/').pop() || 'index.html';

document.querySelectorAll('.nav__links a').forEach(function(link) {
  const linkPage = link.getAttribute('href');
  if (linkPage === currentPage) {
    link.classList.add('active');
  } else {
    link.classList.remove('active');
  }
});


/* ── FOOTER: DYNAMIC YEAR ────────────────────────────────────
   Keeps the copyright year in the footer always current.
   No need to manually update it each year.
──────────────────────────────────────────────────────────────── */
const yearElements = document.querySelectorAll('.footer__bottom');
yearElements.forEach(function(el) {
  el.textContent = el.textContent.replace('2025', new Date().getFullYear());
});
