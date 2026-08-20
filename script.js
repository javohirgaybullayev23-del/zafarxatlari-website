const menuButton = document.querySelector('.menu-toggle');
const mobileNav = document.querySelector('.mobile-nav');
const orderModal = document.querySelector('.order-modal');
const orderForm = document.querySelector('.order-form');
const paymentStep = document.querySelector('.payment-step');
const orderFields = document.querySelector('.order-fields');
const totalPrice = document.querySelector('.total-price');
const orderSummary = document.querySelector('.order-summary');
const orderStatus = document.querySelector('.order-status');
const paymentStatus = document.querySelector('.payment-status');
const pricePerLetter = 25000;
let orderData = {};

menuButton.addEventListener('click', () => {
  const isOpen = mobileNav.classList.toggle('open');
  menuButton.setAttribute('aria-expanded', String(isOpen));
});

document.querySelectorAll('.mobile-nav a').forEach((link) => {
  link.addEventListener('click', () => {
    mobileNav.classList.remove('open');
    menuButton.setAttribute('aria-expanded', 'false');
  });
});

const openOrder = () => { orderModal.classList.add('open'); orderModal.setAttribute('aria-hidden', 'false'); document.body.classList.add('modal-open'); };
const closeOrder = () => { orderModal.classList.remove('open'); orderModal.setAttribute('aria-hidden', 'true'); document.body.classList.remove('modal-open'); };
document.querySelectorAll('[data-open-order]').forEach((button) => button.addEventListener('click', openOrder));
document.querySelectorAll('[data-close-order]').forEach((button) => button.addEventListener('click', closeOrder));

const updatePrice = () => { const quantity = Math.max(1, Number(orderForm.elements.quantity.value) || 1); totalPrice.textContent = (quantity * pricePerLetter).toLocaleString('uz-UZ').replace(/\u00a0/g, ' '); };
orderForm.elements.quantity.addEventListener('input', updatePrice);
orderForm.addEventListener('submit', (event) => {
  event.preventDefault();
  orderData = Object.fromEntries(new FormData(orderForm));
  const quantity = Number(orderData.quantity) || 1;
  orderData.total = quantity * pricePerLetter;
  orderSummary.innerHTML = `<span>${quantity} ta ${orderData.letterType}</span><strong>${orderData.total.toLocaleString('uz-UZ').replace(/\u00a0/g, ' ')} so‘m</strong><small>${orderData.deliveryDate} / ${orderData.deliveryTime} · ${orderData.address}</small>`;
  orderForm.hidden = true; paymentStep.hidden = false; document.querySelector('.step-label').textContent = '2 / 2   To‘lov va tasdiqlash'; document.querySelector('.progress-fill').style.width = '100%';
});
document.querySelector('.order-back').addEventListener('click', () => { orderForm.hidden = false; paymentStep.hidden = true; document.querySelector('.step-label').textContent = '1 / 2   Buyurtma tafsilotlari'; document.querySelector('.progress-fill').style.width = '50%'; });
document.querySelector('.send-order').addEventListener('click', () => {
  const message = `YANGI BUYURTMA%0AIsm: ${orderData.orderName}%0ATelefon: ${orderData.orderPhone}%0AKuyov: ${orderData.groom}%0AKelin: ${orderData.bride}%0AXat: ${orderData.letterType}, ${orderData.quantity} ta%0AKun/vaqt: ${orderData.deliveryDate} ${orderData.deliveryTime}%0AManzil: ${orderData.address}%0AMazmun: ${orderData.brief}%0ATo‘lov: ${orderData.total.toLocaleString('uz-UZ')} so‘m`;
  paymentStatus.textContent = 'Buyurtma tayyorlandi. Telegram oynasi ochilmoqda...';
  window.open(`https://t.me/zafar5503?text=${message}`, '_blank', 'noopener');
});

const revealObserver = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) {
      entry.target.classList.add('visible');
      revealObserver.unobserve(entry.target);
    }
  });
}, { threshold: 0.15 });

document.querySelectorAll('.reveal').forEach((element) => revealObserver.observe(element));

const sections = document.querySelectorAll('main section[id]');
const navLinks = document.querySelectorAll('.desktop-nav a');
const activeObserver = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) {
      navLinks.forEach((link) => link.classList.toggle('active', link.getAttribute('href') === `#${entry.target.id}`));
    }
  });
}, { rootMargin: '-35% 0px -55% 0px' });
sections.forEach((section) => activeObserver.observe(section));
