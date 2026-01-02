const dataStore = {
  contracts: [
    {
      id: 'CTR-001',
      clientId: 'CL-ASI-01',
      reference: 'SAV-2024',
      status: 'active',
      startDate: '2024-01-01',
      endDate: '2026-12-31',
      billingRatePercent: 6.0,
      billingBase: 'purchase_cost',
      currency: 'EUR',
      notes: 'Contrat principal Europe Ouest.',
    },
    {
      id: 'CTR-002',
      clientId: 'CL-ASI-02',
      reference: 'SAV-2025',
      status: 'draft',
      startDate: '2025-01-01',
      endDate: '2027-12-31',
      billingRatePercent: 5.5,
      billingBase: 'purchase_cost',
      currency: 'EUR',
      notes: 'Contrat en cours de négociation.',
    },
  ],
  appendices: [
    {
      id: 'APP-01',
      contractId: 'CTR-001',
      name: 'Gamme Jardin 2024',
      code: 'GJ-2024',
      status: 'active',
      startDate: '2024-01-01',
      endDate: '2025-12-31',
      description: 'Produits jardinage saison 2024/2025.',
    },
    {
      id: 'APP-02',
      contractId: 'CTR-001',
      name: 'Gamme Bricolage 2024',
      code: 'GB-2024',
      status: 'active',
      startDate: '2024-01-01',
      endDate: '2026-06-30',
      description: 'Produits bricolage pour grandes surfaces.',
    },
  ],
  products: [
    { id: 'PR-1001', name: 'Tondeuse électrique AX14' },
    { id: 'PR-1002', name: 'Taille-haies ProCut' },
    { id: 'PR-2001', name: 'Perceuse sans fil XR20' },
    { id: 'PR-2002', name: 'Scie circulaire TurboCut' },
    { id: 'PR-3001', name: 'Nettoyeur haute pression AquaJet' },
    { id: 'PR-4001', name: 'Aspirateur atelier MaxiVac' },
  ],
  lines: [
    {
      id: 'LINE-01',
      appendixId: 'APP-01',
      productId: 'PR-1001',
      status: 'active',
      startDate: '2024-01-01',
      endDate: '2025-12-31',
      serialRequired: true,
      serialPattern: '^SAV-\\d{4}-\\d{3}$',
      warrantyStartRule: 'purchase_date',
      warrantyMonths: 24,
      proofRequired: true,
      allowedCountries: ['FR', 'BE', 'ES'],
      allowedChannels: ['retail', 'online'],
      allowRepairStation: true,
      allowPartsShipment: true,
      allowRefund: false,
      allowReplacement: true,
      allowPaidRepair: true,
      allowPartsSale: true,
    },
    {
      id: 'LINE-02',
      appendixId: 'APP-01',
      productId: 'PR-1002',
      status: 'active',
      startDate: '2024-01-01',
      endDate: '2025-12-31',
      serialRequired: false,
      serialPattern: null,
      warrantyStartRule: 'activation_date',
      warrantyMonths: 18,
      proofRequired: false,
      allowedCountries: [],
      allowedChannels: [],
      allowRepairStation: true,
      allowPartsShipment: false,
      allowRefund: true,
      allowReplacement: false,
      allowPaidRepair: true,
      allowPartsSale: false,
    },
    {
      id: 'LINE-03',
      appendixId: 'APP-02',
      productId: 'PR-2001',
      status: 'active',
      startDate: '2024-01-01',
      endDate: '2026-06-30',
      serialRequired: true,
      serialPattern: '^[A-Z]{2}-\\d{6}$',
      warrantyStartRule: 'manufacture_date',
      warrantyMonths: 36,
      proofRequired: true,
      allowedCountries: ['FR', 'DE'],
      allowedChannels: ['retail'],
      allowRepairStation: true,
      allowPartsShipment: true,
      allowRefund: false,
      allowReplacement: true,
      allowPaidRepair: false,
      allowPartsSale: true,
    },
    {
      id: 'LINE-04',
      appendixId: 'APP-02',
      productId: 'PR-2002',
      status: 'active',
      startDate: '2024-01-01',
      endDate: '2026-06-30',
      serialRequired: false,
      serialPattern: null,
      warrantyStartRule: 'purchase_date',
      warrantyMonths: 12,
      proofRequired: true,
      allowedCountries: ['FR'],
      allowedChannels: ['online'],
      allowRepairStation: false,
      allowPartsShipment: true,
      allowRefund: true,
      allowReplacement: false,
      allowPaidRepair: true,
      allowPartsSale: true,
    },
  ],
};

const elements = {
  scope: document.getElementById('scope'),
  contract: document.getElementById('contract'),
  appendix: document.getElementById('appendix'),
  product: document.getElementById('product'),
  eventDate: document.getElementById('event-date'),
  serial: document.getElementById('serial'),
  purchaseDate: document.getElementById('purchase-date'),
  activationDate: document.getElementById('activation-date'),
  manufactureDate: document.getElementById('manufacture-date'),
  proof: document.getElementById('proof'),
  country: document.getElementById('country'),
  channel: document.getElementById('channel'),
  form: document.getElementById('decision-form'),
  outputEligible: document.getElementById('output-eligible'),
  outputWarranty: document.getElementById('output-warranty'),
  outputWarrantyEnd: document.getElementById('output-warranty-end'),
  outputRequired: document.getElementById('output-required'),
  outputOptions: document.getElementById('output-options'),
  outputReasons: document.getElementById('output-reasons'),
  navLinks: document.querySelectorAll('.nav-link'),
};

const formatBoolean = (value) => {
  if (value === null) return 'Non déterminé';
  return value ? 'Oui' : 'Non';
};

const formatDate = (value) => {
  if (!value) return '-';
  return new Date(value).toLocaleDateString('fr-FR');
};

const addMonths = (date, months) => {
  const copy = new Date(date);
  copy.setMonth(copy.getMonth() + months);
  return copy;
};

const clearTags = (container) => {
  container.innerHTML = '';
};

const addTag = (container, text) => {
  const tag = document.createElement('span');
  tag.className = 'tag';
  tag.textContent = text;
  container.appendChild(tag);
};

const findContract = (id) => dataStore.contracts.find((contract) => contract.id === id);
const findAppendix = (id) => dataStore.appendices.find((appendix) => appendix.id === id);

const resolveLine = ({ contractId, appendixId, productId }) => {
  if (appendixId) {
    return dataStore.lines.find(
      (line) => line.appendixId === appendixId && line.productId === productId && line.status === 'active',
    );
  }

  if (contractId) {
    const activeAppendices = dataStore.appendices.filter(
      (appendix) => appendix.contractId === contractId && appendix.status === 'active',
    );
    for (const appendix of activeAppendices) {
      const line = dataStore.lines.find(
        (entry) => entry.appendixId === appendix.id && entry.productId === productId && entry.status === 'active',
      );
      if (line) return line;
    }
  }

  return null;
};

const computeDecision = ({ contractId, appendixId, productId, eventDate, inputs }) => {
  const requiredInputs = new Set();
  const reasonCodes = new Set();

  const line = resolveLine({ contractId, appendixId, productId });
  if (!line) {
    return {
      eligible: false,
      inWarranty: null,
      requiredInputs: [],
      allowedResolutions: [],
      reasonCodes: ['NO_ACTIVE_LINE'],
    };
  }

  const appendix = findAppendix(line.appendixId);
  const contract = appendix ? findContract(appendix.contractId) : null;

  const event = new Date(eventDate);
  const withinLine = event >= new Date(line.startDate) && event <= new Date(line.endDate);
  const withinAppendix = appendix
    ? event >= new Date(appendix.startDate) && event <= new Date(appendix.endDate)
    : false;
  const withinContract = contract
    ? event >= new Date(contract.startDate) && event <= new Date(contract.endDate)
    : false;

  if (!withinLine || !withinAppendix || !withinContract) {
    return {
      eligible: false,
      inWarranty: null,
      requiredInputs: [],
      allowedResolutions: [],
      reasonCodes: ['OUTSIDE_VALIDITY'],
      resolvedContractId: contract?.id,
      resolvedAppendixId: appendix?.id,
      resolvedLineId: line.id,
    };
  }

  if (contract?.status === 'suspended') {
    return {
      eligible: true,
      inWarranty: null,
      requiredInputs: [],
      allowedResolutions: [],
      reasonCodes: ['CONTRACT_SUSPENDED'],
      resolvedContractId: contract.id,
      resolvedAppendixId: appendix.id,
      resolvedLineId: line.id,
    };
  }

  if (contract?.status === 'expired') {
    return {
      eligible: true,
      inWarranty: null,
      requiredInputs: [],
      allowedResolutions: [],
      reasonCodes: ['CONTRACT_EXPIRED'],
      resolvedContractId: contract.id,
      resolvedAppendixId: appendix.id,
      resolvedLineId: line.id,
    };
  }

  if (line.serialRequired && !inputs.serialNumber) {
    reasonCodes.add('MISSING_SERIAL');
    requiredInputs.add('serial_number');
  }

  if (line.serialPattern && inputs.serialNumber) {
    const regex = new RegExp(line.serialPattern);
    if (!regex.test(inputs.serialNumber)) {
      reasonCodes.add('INVALID_SERIAL_FORMAT');
    }
  }

  if (line.proofRequired && inputs.proofProvided !== true) {
    reasonCodes.add('MISSING_PROOF');
    requiredInputs.add('proof_provided');
  }

  if (line.allowedCountries?.length) {
    if (!inputs.country) {
      requiredInputs.add('country');
    } else if (!line.allowedCountries.includes(inputs.country)) {
      reasonCodes.add('COUNTRY_NOT_ALLOWED');
    }
  }

  if (line.allowedChannels?.length) {
    if (!inputs.channel) {
      requiredInputs.add('channel');
    } else if (!line.allowedChannels.includes(inputs.channel)) {
      reasonCodes.add('CHANNEL_NOT_ALLOWED');
    }
  }

  if (reasonCodes.size > 0 || requiredInputs.size > 0) {
    return {
      eligible: true,
      inWarranty: null,
      requiredInputs: Array.from(requiredInputs),
      allowedResolutions: [],
      reasonCodes: Array.from(reasonCodes),
      resolvedContractId: contract?.id,
      resolvedAppendixId: appendix?.id,
      resolvedLineId: line.id,
    };
  }

  const warrantyStartDateKey = {
    purchase_date: 'purchaseDate',
    activation_date: 'activationDate',
    manufacture_date: 'manufactureDate',
  }[line.warrantyStartRule];

  const selectedStart = inputs[warrantyStartDateKey];
  if (!selectedStart) {
    reasonCodes.add('MISSING_WARRANTY_DATE');
    requiredInputs.add(line.warrantyStartRule);
    return {
      eligible: true,
      inWarranty: null,
      requiredInputs: Array.from(requiredInputs),
      allowedResolutions: [],
      reasonCodes: Array.from(reasonCodes),
      resolvedContractId: contract?.id,
      resolvedAppendixId: appendix?.id,
      resolvedLineId: line.id,
    };
  }

  const warrantyEnd = addMonths(new Date(selectedStart), line.warrantyMonths);
  const inWarranty = event <= warrantyEnd;
  const allowedResolutions = [];

  if (inWarranty) {
    if (line.allowRepairStation) allowedResolutions.push('repair_station');
    if (line.allowPartsShipment) allowedResolutions.push('parts_shipment');
    if (line.allowRefund) allowedResolutions.push('refund');
    if (line.allowReplacement) allowedResolutions.push('replacement');
  } else {
    if (line.allowPaidRepair) allowedResolutions.push('paid_repair');
    if (line.allowPartsSale) allowedResolutions.push('parts_sale');
  }

  return {
    eligible: true,
    inWarranty,
    requiredInputs: Array.from(requiredInputs),
    allowedResolutions,
    reasonCodes: Array.from(reasonCodes),
    resolvedContractId: contract?.id,
    resolvedAppendixId: appendix?.id,
    resolvedLineId: line.id,
    warrantyEndDate: warrantyEnd.toISOString().split('T')[0],
  };
};

const fillSelect = (select, options, defaultValue) => {
  select.innerHTML = '';
  options.forEach((option) => {
    const item = document.createElement('option');
    item.value = option.value;
    item.textContent = option.label;
    select.appendChild(item);
  });
  if (defaultValue) {
    select.value = defaultValue;
  }
};

const initSelectors = () => {
  fillSelect(
    elements.contract,
    dataStore.contracts.map((contract) => ({
      value: contract.id,
      label: `${contract.reference} (${contract.status})`,
    })),
    dataStore.contracts[0]?.id,
  );

  fillSelect(
    elements.appendix,
    dataStore.appendices.map((appendix) => ({
      value: appendix.id,
      label: `${appendix.name} (${appendix.code})`,
    })),
    dataStore.appendices[0]?.id,
  );

  fillSelect(
    elements.product,
    dataStore.products.map((product) => ({
      value: product.id,
      label: `${product.name} (${product.id})`,
    })),
    dataStore.products[0]?.id,
  );

  const today = new Date().toISOString().split('T')[0];
  elements.eventDate.value = today;
};

const updateNavHighlight = () => {
  const sections = document.querySelectorAll('main .section, .page-header');
  const scrollPosition = window.scrollY + 120;
  let activeId = 'overview';
  sections.forEach((section) => {
    if (section.offsetTop <= scrollPosition) {
      activeId = section.getAttribute('id') || 'overview';
    }
  });
  elements.navLinks.forEach((link) => {
    link.classList.toggle('is-active', link.getAttribute('href') === `#${activeId}`);
  });
};

const renderDecision = (result) => {
  elements.outputEligible.textContent = formatBoolean(result.eligible);
  elements.outputWarranty.textContent = result.inWarranty === null ? 'Non déterminé' : formatBoolean(result.inWarranty);
  elements.outputWarrantyEnd.textContent = formatDate(result.warrantyEndDate);

  clearTags(elements.outputRequired);
  clearTags(elements.outputOptions);
  clearTags(elements.outputReasons);

  if (result.requiredInputs.length === 0) {
    addTag(elements.outputRequired, 'Aucun');
  } else {
    result.requiredInputs.forEach((input) => addTag(elements.outputRequired, input));
  }

  if (result.allowedResolutions.length === 0) {
    addTag(elements.outputOptions, 'Aucune');
  } else {
    result.allowedResolutions.forEach((option) => addTag(elements.outputOptions, option));
  }

  if (result.reasonCodes.length === 0) {
    addTag(elements.outputReasons, 'Aucun');
  } else {
    result.reasonCodes.forEach((code) => addTag(elements.outputReasons, code));
  }
};

const handleDecisionSubmit = (event) => {
  event.preventDefault();

  const inputs = {
    serialNumber: elements.serial.value.trim() || null,
    purchaseDate: elements.purchaseDate.value || null,
    activationDate: elements.activationDate.value || null,
    manufactureDate: elements.manufactureDate.value || null,
    proofProvided: elements.proof.value === '' ? null : elements.proof.value === 'true',
    country: elements.country.value.trim().toUpperCase() || null,
    channel: elements.channel.value.trim().toLowerCase() || null,
  };

  const scope = elements.scope.value;
  const contractId = scope === 'contract' ? elements.contract.value : null;
  const appendixId = scope === 'appendix' ? elements.appendix.value : null;

  const result = computeDecision({
    contractId,
    appendixId,
    productId: elements.product.value,
    eventDate: elements.eventDate.value,
    inputs,
  });

  renderDecision(result);
};

const handleScopeChange = () => {
  const isContract = elements.scope.value === 'contract';
  elements.contract.disabled = !isContract;
  elements.appendix.disabled = isContract;
};

initSelectors();
handleScopeChange();

window.addEventListener('scroll', updateNavHighlight);
elements.scope.addEventListener('change', handleScopeChange);
elements.form.addEventListener('submit', handleDecisionSubmit);

const initialResult = computeDecision({
  contractId: elements.contract.value,
  appendixId: null,
  productId: elements.product.value,
  eventDate: elements.eventDate.value,
  inputs: {
    serialNumber: null,
    purchaseDate: null,
    activationDate: null,
    manufactureDate: null,
    proofProvided: null,
    country: null,
    channel: null,
  },
});

renderDecision(initialResult);
updateNavHighlight();
