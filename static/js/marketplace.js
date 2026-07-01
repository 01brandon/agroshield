let currentUserEmail = null;

document.addEventListener('DOMContentLoaded', async () => {
  const profileRes = await apiFetch('/api/auth/profile/');
  if (profileRes && profileRes.ok) {
    const profile  = await profileRes.json();
    currentUserEmail = profile.email;
  }
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

  document.getElementById('openAddListing').addEventListener('click', () =>
    document.getElementById('addListingModal').classList.add('open'));
  document.getElementById('closeAddListing').addEventListener('click', () =>
    document.getElementById('addListingModal').classList.remove('open'));

  document.getElementById('addListingForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const form  = e.target;
    const error = document.getElementById('listingError');
    error.textContent = '';
    const body = {
      farm: form.farm.value, crop: form.crop.value, grade: form.grade.value,
      quantity_kg: form.quantity_kg.value, price_per_kg: form.price_per_kg.value,
      description: form.description.value, is_auction: form.is_auction.checked,
    };
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
  document.getElementById('listingFarmSelect').innerHTML =
    farms.map(f => `<option value="${f.id}">${f.name}</option>`).join('');
}

async function loadListings() {
  const grid = document.getElementById('listingsGrid');
  grid.innerHTML = '<p class="loading-text">loading...</p>';
  const res = await apiFetch('/api/marketplace/listings/'); if (!res || !res.ok) return;
  const data = await res.json(); const listings = data.results || data;
  grid.innerHTML = listings.length
    ? listings.map(l => renderCard(l, false)).join('')
    : '<p class="loading-text">no active listings yet.</p>';
}

async function loadMyListings() {
  const grid = document.getElementById('myListingsGrid');
  grid.innerHTML = '<p class="loading-text">loading...</p>';
  const res = await apiFetch('/api/marketplace/listings/mine/');
  if (!res || !res.ok) { grid.innerHTML = '<p class="loading-text">could not load.</p>'; return; }
  const data = await res.json(); const listings = data.results || data;
  grid.innerHTML = listings.length
    ? listings.map(l => renderCard(l, true)).join('')
    : '<p class="loading-text">no listings yet. create one above.</p>';
}

function renderCard(l, isOwner) {
  return `<div class="listing-card" onclick="openListing(${l.id},${isOwner})" style="cursor:pointer">
    <h4>${l.crop} — grade ${l.grade}</h4>
    <p style="color:#888;font-size:13px">${l.quantity_kg} kg available</p>
    <p class="price">ksh ${l.price_per_kg}/kg</p>
    <p style="font-size:13px;color:#666">${l.description || ''}</p>
    ${l.is_auction ? '<span class="farm-badge">live auction</span>' : ''}
    <p style="font-size:11px;color:#aaa;margin-top:6px">${l.status}</p>
  </div>`;
}

async function openListing(id, isOwner) {
  let modal = document.getElementById('listingDetailModal');
  if (!modal) {
    modal = document.createElement('div');
    modal.id = 'listingDetailModal';
    modal.className = 'modal-overlay';
    modal.innerHTML = `<div class="modal"><h3>listing details</h3>
      <div id="listingDetailBody"></div>
      <div class="form-actions" style="margin-top:14px">
        <button class="btn-outline" onclick="document.getElementById('listingDetailModal').classList.remove('open')">close</button>
      </div></div>`;
    document.body.appendChild(modal);
  }
  modal.classList.add('open');
  const body = document.getElementById('listingDetailBody');
  body.innerHTML = '<p class="loading-text">loading...</p>';

  const [lr, br] = await Promise.all([
    apiFetch(`/api/marketplace/listings/${id}/`),
    apiFetch(`/api/marketplace/bids/?listing=${id}`),
  ]);
  if (!lr || !lr.ok) { body.innerHTML = '<p>could not load listing.</p>'; return; }
  const listing = await lr.json();
  const bids    = br && br.ok ? (await br.json()).results || await br.json() : [];

  let html = `<p><strong>${listing.crop}</strong> — ${listing.quantity_kg}kg @ ksh ${listing.price_per_kg}/kg</p>
    <p style="font-size:13px;color:#666;margin-bottom:12px">${listing.description || ''}</p>`;

  if (bids.length) {
    html += `<h4 style="font-size:13px;margin-bottom:8px">bids (${bids.length})</h4>`;
    bids.forEach(b => {
      html += `<div style="padding:8px 0;border-bottom:1px solid #eee;display:flex;align-items:center;justify-content:space-between">
        <div>
          <strong style="font-size:13px">ksh ${b.amount}</strong>
          <span style="font-size:12px;color:#888;margin-left:8px">by ${b.buyer_name || 'bidder'}</span>
          <span style="font-size:11px;color:#aaa;margin-left:8px">${b.status || 'pending'}</span>
        </div>
        ${isOwner && b.status !== 'accepted' ? `<div style="display:flex;gap:6px">
          <button onclick="acceptBid(${b.id})" class="btn-primary" style="font-size:11px;padding:4px 10px">accept</button>
          <button onclick="rejectBid(${b.id})" class="btn-outline" style="font-size:11px;padding:4px 10px">reject</button>
        </div>` : b.status === 'accepted' ? '<span style="color:#4a7c3f;font-size:12px;font-weight:600">accepted</span>' : ''}
      </div>`;
    });
  } else {
    html += '<p class="loading-text">no bids yet.</p>';
  }

  if (!isOwner && listing.is_auction && listing.status === 'active') {
    html += `<div style="display:flex;gap:8px;margin-top:12px">
      <input type="number" id="bidAmount" placeholder="your bid in ksh"
        style="flex:1;padding:8px;border:1px solid #ddd;border-radius:8px;font-size:13px">
      <button onclick="placeBid(${id})" class="btn-primary" style="font-size:12px;padding:8px 16px">place bid</button>
    </div>
    <p class="form-error" id="bidError"></p>`;
  } else if (isOwner) {
    html += `<p style="font-size:12px;color:#888;margin-top:10px">you cannot bid on your own listing.</p>`;
  }

  body.innerHTML = html;
}

async function placeBid(listingId) {
  const amount    = document.getElementById('bidAmount')?.value;
  const bidError  = document.getElementById('bidError');
  if (!amount) { if (bidError) bidError.textContent = 'enter a bid amount'; return; }
  const res = await apiFetch('/api/marketplace/bids/', {
    method: 'POST', body: JSON.stringify({ listing: listingId, amount }),
  });
  if (res && res.ok) {
    openListing(listingId, false);
  } else if (res) {
    const data = await res.json();
    if (bidError) bidError.textContent = Object.values(data).flat().join(' ');
  }
}

async function acceptBid(bidId) {
  const res = await apiFetch(`/api/marketplace/bids/${bidId}/accept/`, { method: 'POST' });
  if (res && res.ok) {
    const data = await res.json();
    alert(data.message);
    document.getElementById('listingDetailModal').classList.remove('open');
    loadMyListings();
  }
}

async function rejectBid(bidId) {
  const res = await apiFetch(`/api/marketplace/bids/${bidId}/reject/`, { method: 'POST' });
  if (res && res.ok) { openListing(null, true); loadMyListings(); }
}

async function loadEscrow() {
  const list = document.getElementById('escrowList');
  list.innerHTML = '<p class="loading-text">loading...</p>';
  const res = await apiFetch('/api/marketplace/escrow/'); if (!res || !res.ok) return;
  const data = await res.json(); const escrows = data.results || data;
  list.innerHTML = escrows.length
    ? escrows.map(e => `<div class="scan-item">
        <h5>ksh ${e.amount} — ${e.status}</h5>
        ${e.status === 'held' ? `<button onclick="releaseEscrow(${e.id})" class="btn-primary" style="font-size:12px;padding:6px 14px;margin-top:8px">confirm delivery &amp; release funds</button>` : ''}
      </div>`).join('')
    : '<p class="loading-text">no escrow transactions yet.</p>';
}

async function releaseEscrow(id) {
  const res = await apiFetch(`/api/marketplace/escrow/${id}/release/`, { method: 'POST' });
  if (res && res.ok) loadEscrow();
}

async function loadEscrow() {
  const list = document.getElementById('escrowList');
  list.innerHTML = '<p class="loading-text">loading...</p>';
  const res = await apiFetch('/api/marketplace/escrow/');
  if (!res || !res.ok) { list.innerHTML = '<p class="loading-text">could not load escrow.</p>'; return; }
  const data = await res.json(); const escrows = data.results || data;
  if (!escrows.length) { list.innerHTML = '<p class="loading-text">no escrow transactions. accept a bid to create one.</p>'; return; }
  list.innerHTML = escrows.map(e => {
    const statusColors = {pending:'#e6a817', held:'#4a7c3f', released:'#888', disputed:'#e05252'};
    const color = statusColors[e.status] || '#888';
    let actions = '';
    if (e.status === 'pending') {
      actions = `<p style="font-size:12px;color:#666;margin-top:8px">buyer needs to pay ksh ${e.amount} via m-pesa to release funds into escrow.</p>
        <button onclick="payEscrow(${e.id})" class="btn-primary" style="font-size:12px;padding:6px 14px;margin-top:6px">pay with m-pesa</button>`;
    } else if (e.status === 'held') {
      actions = `<p style="font-size:12px;color:#4a7c3f;margin-top:8px">payment held in escrow. release to seller after delivery.</p>
        <button onclick="releaseEscrow(${e.id})" class="btn-primary" style="font-size:12px;padding:6px 14px;margin-top:6px">confirm delivery &amp; release funds</button>`;
    } else if (e.status === 'released') {
      actions = `<p style="font-size:12px;color:#888;margin-top:8px">funds released to seller. transaction complete.</p>`;
    }
    return `<div class="scan-item">
      <div style="display:flex;justify-content:space-between;align-items:center">
        <strong>ksh ${e.amount}</strong>
        <span style="background:${color};color:#fff;border-radius:20px;padding:3px 10px;font-size:11px">${e.status}</span>
      </div>
      ${actions}
    </div>`;
  }).join('');
}

async function payEscrow(id) {
  const phone = prompt('enter your m-pesa phone number (e.g. 0712345678):');
  if (!phone) return;
  const res = await apiFetch(`/api/marketplace/escrow/${id}/pay/`, {method:'POST', body: JSON.stringify({phone})});
  if (res && res.ok) {
    const data = await res.json();
    alert(data.message || 'check your phone and enter your m-pesa pin');
    loadEscrow();
  } else if (res) {
    const data = await res.json();
    alert(data.error || 'payment initiation failed');
  }
}

async function releaseEscrow(id) {
  if (!confirm('confirm delivery and release funds to seller?')) return;
  const res = await apiFetch(`/api/marketplace/escrow/${id}/release/`, {method:'POST'});
  if (res && res.ok) { alert('funds released to seller successfully'); loadEscrow(); }
}
