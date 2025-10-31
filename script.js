document.addEventListener('DOMContentLoaded', () => {
  const animatedBlocks = document.querySelectorAll('[data-animate-on-load]');
  animatedBlocks.forEach((block, index) => {
    requestAnimationFrame(() => {
      block.style.transitionDelay = `${index * 80}ms`;
      block.classList.add('is-visible');
    });
  });

  const hoverCards = document.querySelectorAll('.service-card');
  hoverCards.forEach((card) => {
    card.addEventListener('mousemove', (event) => {
      const bounds = card.getBoundingClientRect();
      const x = event.clientX - bounds.left;
      const y = event.clientY - bounds.top;
      card.style.setProperty('--mouse-x', `${x}px`);
      card.style.setProperty('--mouse-y', `${y}px`);
    });
  });
});
