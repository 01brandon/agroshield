// marketplace page
document.addEventListener('DOMContentLoaded', () => {
  loadListings();
  loadFarmsDropdown();

  // tab switching
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
      btn.classList.add('active');
      document.getElementById(`tab-${btn.dataset.tab}`).classList.add('active');

      if (btn.dataset.tab === 'escrow') loadEscrow();
    });
  });

  document.getElementById('openAddListing').addEventListener('click', () => {
    document.getElementById('addListingModal').classList.add('open');
  });

  document.getElementById('closeAddListing').addEventListener('click', () => {
    document.getElementById('addListingModal').classList.remove('open');
  });

  document.getElementById('addListingForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const form  = e.target;
    const error = document.getElementById('listingError');
    const body  = {
      farm:         form.farm.value,
      crop:         form.crop.value,
      grade:        form.grade.value,
      quantity_kg:  form.quantity_kg.value,
      price_per_kg: form.price_per_kg.value,
      description:  form.description.value,
      is_auction:   form.is_auction.checked,
    };

    const res = await apiFetch('/api/marketplace/listings/', {
      method: 'POST',
      body:   JSON.stringify(body),
    });

    if (res && res.ok) {
      document.getElementById('addListingModal').classList.remove('open');
      form.reset();
      loadListings();
    } else {
      const data    = await res.json();
      error.textContent = Object.values(data).flat().join(' ');
    }
  });
});

async function loadFarmsDropdown() {
  const select = document.getElementById('listingFarmSelect');
  const res    = await apiFetch('/api/farms/');
  if (!res || !res.ok) return;
  const data   = await res.json();
  const farms  = data.results || data;
  select.innerHTML = farms.map(f => `<option value="${f.id}">${f.name}</option>`).join('');
}

async function loadListings() {
  const grid = document.getElementById('listingsGrid');
  grid.innerHTML = '<p class="loading-text">loading listings...</p>';
  const res  = await apiFetch('/api/marketplace/listings/');
  if (!res || !res.ok) return;
  const data     = await res.json();
  const listings = data.results || data;
  grid.innerHTML = '';

  if (!listings.length) {
    grid.innerHTML = '<p class="loading-text">no active listings found.</p>';
    return;
  }

  listings.forEach(listing => {
    grid.innerHTML += `
      <div class="listing-card">
        <h4>${listing.crop} - grade ${listing.grade}</h4>
        <p style="color:#888;font-size:13px">${listing.quantity_kg} kg available</p>
        <p class="price">ksh ${listing.price_per_kg}/kg</p>
        <p style="font-size:13px;color:#666;margin-top:8px">${listing.description || ''}</p>
        ${listing.is_auction ? '<span class="farm-badge">live auction</span>' : ''}
      </div>`;
  });
}

async function loadEscrow() {
  const list = document.getElementById('escrowList');
  list.innerHTML = '<p class="loading-text">loading...</p>';
  const res  = await apiFetch('/api/marketplace/escrow/');
  if (!res || !res.ok) return;
  const data      = await res.json();
  const escrows   = data.results || data;
  list.innerHTML  = '';

  if (!escrows.length) {
    list.innerHTML = '<p class="loading-text">no escrow transactions yet.</p>';
    return;
  }

  escrows.forEach(e => {
    list.innerHTML += `
      <div class="scan-item">
        <h5>ksh ${e.amount} <span class="badge badge-${e.status === 'held' ? 'pending' : 'confirmed'}">${e.status}</span></h5>
        <p>m-pesa ref: ${e.mpesa_reference || 'pending'}</p>
        ${e.status === 'held' ? `<button onclick="releaseEscrow(${e.id})" class="btn-primary" style="margin-top:8px;font-size:12px;padding:6px 14px">release funds</button>` : ''}
      </div>`;
  });
}

async function releaseEscrow(id) {
  const res = await apiFetch(`/api/marketplace/escrow/${id}/release/`, {method: 'POST'});
  if (res && res.ok) loadEscrow();
}
