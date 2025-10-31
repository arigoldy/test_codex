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

  const productCatalog = {
    '0000000000000': {
      name: 'Salon de jardin « Riviera »',
      category: 'Mobilier extérieur',
      ean: '0000000000000',
      image:
        'https://images.unsplash.com/photo-1505691723518-36a5ac3be353?auto=format&fit=crop&w=320&q=80',
      imageAlt: 'Salon de jardin avec table basse et fauteuils en bois clair',
    },
    '1111111111111': {
      name: 'Croquettes premium pour chien',
      category: 'Alimentation animale',
      ean: '1111111111111',
      image:
        'https://images.unsplash.com/photo-1589923188900-85dae523342b?auto=format&fit=crop&w=320&q=80',
      imageAlt: 'Sachet de croquettes pour chien posé sur un plan de travail',
    },
  };

  const productInput = document.querySelector('.search-field__input');
  const productPreview = document.querySelector('.product-preview');

  if (productInput && productPreview) {
    const previewImage = productPreview.querySelector('img');
    const previewName = productPreview.querySelector('.product-preview__name');
    const previewCategory = productPreview.querySelector('.product-preview__category');
    const previewEAN = productPreview.querySelector('.product-preview__ean');

    const hidePreview = () => {
      productPreview.classList.remove('is-visible');
      productPreview.setAttribute('hidden', '');
      if (previewImage) {
        previewImage.src = '';
        previewImage.alt = '';
      }
      if (previewName) {
        previewName.textContent = '';
      }
      if (previewCategory) {
        previewCategory.textContent = '';
      }
      if (previewEAN) {
        previewEAN.textContent = '';
      }
    };

    const showPreview = (product) => {
      if (previewImage) {
        previewImage.src = product.image;
        previewImage.alt = product.imageAlt || product.name;
      }
      if (previewName) {
        previewName.textContent = product.name;
      }
      if (previewCategory) {
        previewCategory.textContent = product.category;
      }
      if (previewEAN) {
        previewEAN.textContent = `EAN : ${product.ean}`;
      }

      productPreview.classList.add('is-visible');
      productPreview.removeAttribute('hidden');
    };

    productInput.addEventListener('input', (event) => {
      const target = event.currentTarget;
      if (!(target instanceof HTMLInputElement)) {
        return;
      }

      const sanitizedValue = target.value.replace(/\D/g, '');
      if (sanitizedValue !== target.value) {
        target.value = sanitizedValue;
      }

      const product = productCatalog[sanitizedValue];
      if (product) {
        showPreview(product);
      } else {
        hidePreview();
      }
    });

    hidePreview();
  }
});
