'use strict';

// Public portfolio settings. Set only a confirmed professional contact.
// Accepted destinations: mailto: or an absolute https:// URL, without credentials.
const PORTFOLIO_CONFIG = Object.freeze({ contactUrl: '' });

// Synthetic fixtures only. No backend, storage, clock dependency or network access.
// This demo represents purchase_count, not the monthly_consecutive campaign.
(() => {
  const goal = 5;
  const fixtures = [
    { id: 'ana', name: 'Ana Martins', initials: 'AM', purchases: 3, recent: true },
    { id: 'lucas', name: 'Lucas Costa', initials: 'LC', purchases: 1, recent: false },
    { id: 'beatriz', name: 'Beatriz Souza', initials: 'BS', purchases: 4, recent: true },
  ];
  const element = (id) => document.getElementById(id);
  const selection = element('demo-customer');
  const buyButton = element('add-purchase');
  const redeemButton = element('redeem');
  const resetButton = element('reset-demo');
  let customers;

  function freshCustomers() {
    return Object.fromEntries(fixtures.map((customer) => [customer.id, {
      ...customer,
      redemptions: 0,
      history: [`${customer.purchases} compra${customer.purchases === 1 ? '' : 's'} fictícia${customer.purchases === 1 ? '' : 's'} no ciclo inicial.`],
    }]));
  }

  function selectedCustomer() { return customers[selection.value]; }

  function render(message) {
    const customer = selectedCustomer();
    const ready = customer.purchases >= goal;
    const remaining = Math.max(goal - customer.purchases, 0);
    const progress = Math.min(customer.purchases, goal);
    element('customer-name').textContent = customer.name;
    element('customer-initials').textContent = customer.initials;
    element('public-name').textContent = customer.name.split(' ')[0];
    element('operator-summary').textContent = `${customer.purchases} compra${customer.purchases === 1 ? '' : 's'} neste ciclo · ${customer.redemptions} resgate${customer.redemptions === 1 ? '' : 's'}`;
    element('customer-status').textContent = ready ? 'Pronto para resgate' : 'Em progresso';
    element('customer-status').classList.toggle('ready', ready);
    element('recency-status').textContent = customer.recent ? 'Comprou neste mês' : '32 dias sem comprar · cenário fictício';
    element('recency-status').classList.toggle('attention', !customer.recent);
    // The original app allows further purchases before redemption. There is no
    // surplus carryover: redemption starts a new count after that event.
    buyButton.disabled = false;
    redeemButton.disabled = !ready;
    element('progress-text').textContent = ready
      ? 'Meta atingida! Sua recompensa está disponível.'
      : `Falta${remaining === 1 ? '' : 'm'} ${remaining} compra${remaining === 1 ? '' : 's'} para sua recompensa.`;
    element('demo-progress').setAttribute('aria-valuenow', progress);
    element('demo-progress').setAttribute('aria-valuetext', `${customer.purchases} de ${goal} compras${ready ? '. Recompensa disponível' : ''}`);
    element('progress-fill').className = `progress-fill progress-${progress}`;
    element('cycle-number').textContent = `Ciclo ${customer.redemptions + 1}`;
    element('demo-stamps').replaceChildren(...Array.from({ length: goal }, (_, index) => {
      const stamp = document.createElement('span');
      stamp.textContent = index < progress ? '✓' : String(index + 1);
      stamp.classList.toggle('filled', index < progress);
      return stamp;
    }));
    element('activity-log').replaceChildren(...customer.history.slice(0, 4).map((text) => {
      const item = document.createElement('li');
      item.textContent = text;
      return item;
    }));
    if (message) element('demo-feedback').textContent = message;
  }

  selection.addEventListener('change', () => {
    render(`Cliente selecionado: ${selectedCustomer().name}. O cartão e o histórico foram atualizados.`);
  });

  buyButton.addEventListener('click', () => {
    const customer = selectedCustomer();
    customer.purchases += 1;
    customer.recent = true;
    customer.history.unshift(`Compra fictícia registrada · ${customer.purchases} no ciclo ${customer.redemptions + 1}.`);
    customer.history = customer.history.slice(0, 4);
    render(`${customer.name}: compra registrada. ${customer.purchases} compra${customer.purchases === 1 ? '' : 's'} neste ciclo. ${customer.purchases >= goal ? 'Meta atingida! A recompensa já pode ser resgatada.' : `O cartão agora mostra ${customer.purchases} de ${goal} compras.`}`);
    if (customer.purchases === goal) redeemButton.focus();
  });

  redeemButton.addEventListener('click', () => {
    const customer = selectedCustomer();
    if (customer.purchases < goal) return;
    customer.redemptions += 1;
    customer.purchases = 0;
    customer.history.unshift(`Recompensa fictícia resgatada · ciclo ${customer.redemptions} encerrado.`);
    customer.history = customer.history.slice(0, 4);
    render(`${customer.name}: recompensa resgatada. Ciclo ${customer.redemptions + 1} iniciado, com 0 de ${goal} compras. O histórico foi preservado.`);
    buyButton.focus();
  });

  resetButton.addEventListener('click', () => {
    customers = freshCustomers();
    selection.value = 'ana';
    render('Simulação reiniciada. Todos os clientes, compras e resgates fictícios voltaram ao estado inicial.');
  });

  function configureContact() {
    if (!PORTFOLIO_CONFIG.contactUrl) return;
    try {
      const url = new URL(PORTFOLIO_CONFIG.contactUrl);
      if (!['https:', 'mailto:'].includes(url.protocol) || url.username || url.password) return;
      element('contact-link').href = url.href;
      element('contact-link').hidden = false;
      element('contact-pending').hidden = true;
    } catch {
      // An absent or invalid contact leaves the honest placeholder visible.
    }
  }

  customers = freshCustomers();
  selection.disabled = false;
  resetButton.disabled = false;
  render('Simulação pronta. Ana está a 2 compras da meta. Registre uma compra para começar.');
  configureContact();
})();
