const revealElements = document.querySelectorAll(".reveal-left, .reveal-right");

const observer = new IntersectionObserver(entries => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add("active");
    }
  });
}, { threshold: 0.2 });

revealElements.forEach(el => observer.observe(el));

const contactForm = document.querySelector('.contact-form');
if (contactForm) {
  contactForm.addEventListener('submit', function (e) {
    e.preventDefault();
    alert("Thank you for reaching out! We'll get back to you soon.");
    this.reset();
  });
}

// Minimal, clean, responsive image carousel (vanilla JS)
(function() {
  const slides = Array.from(document.querySelectorAll('.simple-carousel-slide'));
  const left = document.querySelector('.simple-carousel-arrow.left');
  const right = document.querySelector('.simple-carousel-arrow.right');
  let current = 0, autoSlide;
  function show(idx) {
    slides.forEach((s, i) => {
      s.classList.toggle('active', i === idx);
      s.style.zIndex = i === idx ? 2 : 1;
    });
    current = idx;
  }
  if (left && right && slides.length) {
    left.onclick = () => { show((current - 1 + slides.length) % slides.length); resetAuto(); };
    right.onclick = () => { show((current + 1) % slides.length); resetAuto(); };
    function resetAuto() {
      clearInterval(autoSlide);
      autoSlide = setInterval(() => show((current + 1) % slides.length), 5000);
    }
    resetAuto();
  }
})();

// Starry sky effect (vanilla, no inline script)
(function() {
  const sky = document.querySelector('.starry-sky');
  if (!sky) return;
  const STAR_COUNT = 90;
  const stars = [];
  function random(min, max) { return Math.random() * (max - min) + min; }
  function createStar() {
    const star = document.createElement('div');
    star.className = 'star';
    resetStar(star, true);
    sky.appendChild(star);
    stars.push({el: star, life: random(2, 6), born: performance.now()});
  }
  function resetStar(star, first = false) {
    const size = random(1.5, 3);
    star.style.width = `${size}px`;
    star.style.height = `${size}px`;
    star.style.left = `${random(2, 98)}%`;
    star.style.top = `${random(5, 80)}%`;
    star.style.opacity = first ? random(0.2, 0.5) : 0;
    star._fadeIn = true;
    star._fadeStart = performance.now();
    star._fadeDuration = random(1.5, 3.5) * 1000;
    star._life = random(2, 5) * 1000;
    star._born = performance.now();
  }
  for (let i = 0; i < STAR_COUNT; i++) createStar();
  function animateTwinkle(now) {
    for (const s of stars) {
      const star = s.el;
      const age = now - (star._born || 0);
      let opacity = parseFloat(star.style.opacity) || 0;
      if (star._fadeIn) {
        opacity = Math.min(1, (now - star._fadeStart) / star._fadeDuration);
        star.style.opacity = (0.3 + 0.5 * opacity).toFixed(2);
        if (opacity >= 1) {
          star._fadeIn = false;
        }
      } else if (age > star._life) {
        opacity -= 0.02;
        star.style.opacity = Math.max(0, opacity).toFixed(2);
        if (opacity <= 0.01) {
          resetStar(star);
        }
      } else {
        // Subtle shimmer while alive
        const shimmer = 0.05 * Math.sin(now / 700 + Math.random() * 10);
        star.style.opacity = (parseFloat(star.style.opacity) + shimmer).toFixed(2);
      }
    }
    requestAnimationFrame(animateTwinkle);
  }
  animateTwinkle(performance.now());
})();