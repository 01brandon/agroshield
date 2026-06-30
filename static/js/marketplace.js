let currentUserId = null;

document.addEventListener('DOMContentLoaded', async () => {
  const profileRes = await apiFetch('/api/auth/profile/');
  if (profileRes && profileRes.ok) currentUserId = (await profileRes.json()).id;

  loadListings();
  loadFarmsDropdown();

  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
      btn.classList.add('active');
      document.getElementById(`tab-${btn.dataset.tab}`).classList.add('active');
      if (btn.dataset.tab === 'my-listings') loadMyListings();
      if (btn.dataset.tab === 'escrow') loadEscrow();
    });
  });

  document.getElementById('openAddListing').addEventListener('click', () => document.getElementById('addListingModal').classList.add('open'));
  document.getElementById('closeAddListing').addEventListener('click', () => document.getElementById('addListingModal').classList.remove('open'));

  document.getElementById('addListingForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const form = e.target, error = document.getElementById('listingError');
    error.textContent = '';
    const body = { farm: form.farm.value, crop: form.crop.value, grade: form.grade.value,
      quantity_kg: form.quantity_kg.value, price_per_kg: form.price_per_kg.value,
      description: form.description.value, is_auction: form.is_auction.checked };
    const res = await apiFetch('/api/marketplace/listings/', { method: 'POST', body: JSON.stringify(body) });
    if (res && res.ok) {
      document.getElementById('addListingModal').classList.remove('open');
      form.reset(); loadListings(); loadMyListings();
    } else if (res) {
      const data = await res.json();
      error.textContent = Object.values(data).flat().join(' ');
    }
  });
});

async function loadFarmsDropdown() {
  const res = await apiFetch('/api/farms/'); if (!res || !res.ok) return;
  const data = await res.json(); const farms = data.results || data;
  document.getElementById('listingFarmSelect').innerHTML = farms.map(f => `<option value="${f.id}">${f.name}</option>`).join('');
}

function renderListing(listing, clickable=true) {
  return `<div class="listing-card" ${clickable ? `onclick="openListing(${listing.id})" style="cursor:pointer"` : ''}>
    <h4>${listing.crop} - grade ${listing.grade}</h4>
    <p style="color:#888;font-size:13px">${listing.quantity_kg} kg available</p>
    <p class="price">ksh ${listing.price_per_kg}/kg</p>
    <p style="font-size:13px;color:#666;margin-top:8px">${listing.description || ''}</p>
    ${listing.is_auction ? '<span class="farm-badge">live auction</span>' : ''}
    <p style="font-size:11px;color:#aaa;margin-top:8px">${listing.status}</p>
  </div>`;
}

async function loadListings() {
  const grid = document.getElementById('listingsGrid');
  grid.innerHTML = '<p class="loading-text">loading...</p>';
  const res = await apiFetch('/api/marketplace/listings/'); if (!res || !res.ok) return;
  const data = await res.json(); const listings = data.results || data;
  grid.innerHTML = listings.length ? listings.map(l => renderListing(l)).join('') : '<p class="loading-text">no active listings.</p>';
}

async function loadMyListings() {
  const grid = document.getElementById('myListingsGrid');
  grid.innerHTML = '<p class="loading-text">loading...</p>';
  const res = await apiFetch('/api/marketplace/listings/mine/'); if (!res || !res.ok) { grid.innerHTML = '<p class="loading-text">could not load.</p>'; return; }
  const data = await res.json(); const listings = data.results || data;
  grid.innerHTML = listings.length ? listings.map(l => renderListing(l)).join('') : '<p class="loading-text">you have no listings yet. create one above.</p>';
}

async function openListing(id) {
  let modal = document.getElementById('listingDetailModal');
  if (!modal) {
    modal = document.createElement('div');
    modal.id = 'listingDetailModal';
    modal.className = 'modal-overlay';
    modal.innerHTML = `<div class="modal"><h3>listing details</h3><div id="listingDetailBody"></div>
      <div class="form-actions"><button class="btn-outline" onclick="document.getElementById('listingDetailModal').classList.remove('open')">close</button></div></div>`;
    document.body.appendChild(modal);
  }
  const body = document.getElementById('listingDetailBody');
  body.innerHTML = '<p class="loading-text">loading...</p>';
  modal.classList.add('open');

  const [listingRes, bidsRes] = await Promise.all([
    apiFetch(`/api/marketplace/listings/${id}/`),
    apiFetch(`/api/marketplace/bids/?listing=${id}`),
  ]);
  const listing = listingRes && listingRes.ok ? await listingRes.json() : null;
  const bidsData = bidsRes && bidsRes.ok ? await bidsRes.json() : { results: [] };
  const bids = bidsData.results || bidsData;

  let html = `<p><strong>${listing.crop}</strong> — ${listing.quantity_kg}kg @ ksh ${listing.price_per_kg}/kg</p>
    <p style="font-size:13px;color:#666">${listing.description || ''}</p>`;
  if (listing.is_auction) {
    html += `<h4 style="margin-top:14px;font-size:13px">bid history</h4>`;
    html += bids.length ? bids.map(b => `<div style="padding:6px 0;border-bottom:1px solid #eee;font-size:13px">ksh ${b.amount}</div>`).join('') : '<p class="loading-text">no bids yet.</p>';
    html += `<div style="display:flex;gap:8px;margin-top:10px"><input type="number" id="bidAmount" placeholder="your bid (ksh)" style="flex:1;padding:8px;border:1px solid #ddd;border-radius:8px">
      <button class="btn-primary" onclick="placeBid(${id})" style="font-size:12px;padding:8px 16px">place bid</button></div>`;
  }
  body.innerHTML = html;
}

async function placeBid(listingId) {
  const amount = document.getElementById('bidAmount').value;
  if (!amount) return;
  const res = await apiFetch('/api/marketplace/bids/', { method: 'POST', body: JSON.stringify({ listing: listingId, amount }) });
  if (res && res.ok) openListing(listingId);
}

async function loadEscrow() {
  const list = document.getElementById('escrowList');
  list.innerHTML = '<p class="loading-text">loading...</p>';
  const res = await apiFetch('/api/marketplace/escrow/'); if (!res || !res.ok) return;
  const data = await res.json(); const escrows = data.results || data;
  list.innerHTML = escrows.length ? escrows.map(e => `<div class="scan-item"><h5>ksh ${e.amount} <span class="badge badge-${e.status === 'held' ? 'pending' : 'confirmed'}">${e.status}</span></h5></div>`).join('') : '<p class="loading-text">no escrow transactions yet.</p>';
}
