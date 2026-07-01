let currentUserId = null;

// styled toast notification instead of alert()
function showToast(msg, type='success'){
  let toast = document.getElementById('mkt-toast');
  if(!toast){
    toast = document.createElement('div');
    toast.id = 'mkt-toast';
    toast.style.cssText='position:fixed;bottom:24px;right:24px;padding:14px 22px;border-radius:10px;font-size:14px;font-weight:600;z-index:9999;opacity:0;transition:opacity .3s;max-width:320px;box-shadow:0 4px 20px rgba(0,0,0,.15)';
    document.body.appendChild(toast);
  }
  toast.style.background = type==='success'?'#1a3a1a':type==='error'?'#3a1a1a':'#1a2a3a';
  toast.style.color = type==='success'?'#a8d85c':type==='error'?'#e08080':'#80b0e0';
  toast.textContent = msg;
  toast.style.opacity='1';
  setTimeout(()=>toast.style.opacity='0', 3500);
}

// styled prompt popup
function showPrompt(msg, placeholder, callback){
  let overlay = document.getElementById('prompt-overlay');
  if(!overlay){
    overlay = document.createElement('div');
    overlay.id = 'prompt-overlay';
    overlay.className = 'modal-overlay';
    overlay.innerHTML=`<div class="modal" style="max-width:400px">
      <h3 id="prompt-title"></h3>
      <div class="form-group"><input type="text" id="prompt-input" style="width:100%"></div>
      <div class="form-actions">
        <button class="btn-outline" onclick="document.getElementById('prompt-overlay').classList.remove('open')">cancel</button>
        <button class="btn-primary" id="prompt-ok">confirm</button>
      </div>
    </div>`;
    document.body.appendChild(overlay);
  }
  document.getElementById('prompt-title').textContent = msg;
  document.getElementById('prompt-input').placeholder = placeholder;
  document.getElementById('prompt-input').value = '';
  overlay.classList.add('open');
  document.getElementById('prompt-ok').onclick = () => {
    const val = document.getElementById('prompt-input').value.trim();
    overlay.classList.remove('open');
    callback(val);
  };
}

document.addEventListener('DOMContentLoaded', async () => {
  const r = await apiFetch('/api/auth/profile/');
  if(r && r.ok){ const p = await r.json(); currentUserId = p.id; }
  loadListings();
  loadFarmsDropdown();

  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.tab-btn').forEach(b=>b.classList.remove('active'));
      document.querySelectorAll('.tab-content').forEach(t=>t.classList.remove('active'));
      btn.classList.add('active');
      document.getElementById(`tab-${btn.dataset.tab}`).classList.add('active');
      if(btn.dataset.tab==='my-listings') loadMyListings();
      if(btn.dataset.tab==='escrow') loadEscrow();
    });
  });

  document.getElementById('openAddListing').addEventListener('click',()=>document.getElementById('addListingModal').classList.add('open'));
  document.getElementById('closeAddListing').addEventListener('click',()=>document.getElementById('addListingModal').classList.remove('open'));

  document.getElementById('addListingForm').addEventListener('submit', async (e)=>{
    e.preventDefault(); const form=e.target; const error=document.getElementById('listingError'); error.textContent='';
    const body={farm:form.farm.value,crop:form.crop.value,grade:form.grade.value,
      quantity_kg:form.quantity_kg.value,price_per_kg:form.price_per_kg.value,
      description:form.description.value,is_auction:form.is_auction.checked};
    const res=await apiFetch('/api/marketplace/listings/',{method:'POST',body:JSON.stringify(body)});
    if(res&&res.ok){document.getElementById('addListingModal').classList.remove('open');form.reset();loadListings();loadMyListings();}
    else if(res){const d=await res.json();error.textContent=Object.values(d).flat().join(' ');}
  });
});

async function loadFarmsDropdown(){
  const res=await apiFetch('/api/farms/'); if(!res||!res.ok) return;
  const farms=(await res.json()).results||[];
  document.getElementById('listingFarmSelect').innerHTML=farms.map(f=>`<option value="${f.id}">${f.name}</option>`).join('');
}

function renderCard(l, isOwner){
  const soldBadge = l.status==='sold'?'<span style="background:#e05252;color:#fff;border-radius:20px;padding:2px 8px;font-size:10px;margin-left:6px">sold</span>':'';
  return `<div class="listing-card" onclick="openListing(${l.id},${isOwner})" style="cursor:pointer;${l.status==='sold'?'opacity:.7':''}">
    <h4>${l.crop} — grade ${l.grade} ${soldBadge}</h4>
    <p style="color:#888;font-size:13px">${l.quantity_kg} kg &bull; ksh ${l.price_per_kg}/kg</p>
    <p style="font-size:13px;color:#666">${l.description||''}</p>
    ${l.is_auction?'<span class="farm-badge">live auction</span>':''}
  </div>`;
}

async function loadListings(){
  const grid=document.getElementById('listingsGrid'); grid.innerHTML='<p class="loading-text">loading...</p>';
  const res=await apiFetch('/api/marketplace/listings/'); if(!res||!res.ok) return;
  const listings=(await res.json()).results||[];
  grid.innerHTML=listings.length?listings.map(l=>renderCard(l,false)).join(''):'<p class="loading-text">no active listings yet.</p>';
}

async function loadMyListings(){
  const grid=document.getElementById('myListingsGrid'); grid.innerHTML='<p class="loading-text">loading...</p>';
  const res=await apiFetch('/api/marketplace/listings/mine/'); if(!res||!res.ok){grid.innerHTML='<p class="loading-text">could not load.</p>';return;}
  const listings=await res.json();
  grid.innerHTML=listings.length?listings.map(l=>renderCard(l,true)).join(''):'<p class="loading-text">no listings yet.</p>';
}

async function openListing(id, isOwner){
  let modal=document.getElementById('listingDetailModal');
  if(!modal){
    modal=document.createElement('div'); modal.id='listingDetailModal'; modal.className='modal-overlay';
    modal.innerHTML=`<div class="modal" style="max-width:560px"><h3>listing details</h3>
      <div id="listingDetailBody"></div>
      <div class="form-actions" style="margin-top:14px">
        <button class="btn-outline" onclick="document.getElementById('listingDetailModal').classList.remove('open')">close</button>
      </div></div>`;
    document.body.appendChild(modal);
  }
  modal.classList.add('open');
  const body=document.getElementById('listingDetailBody');
  body.innerHTML='<p class="loading-text">loading...</p>';

  const [lr,br]=await Promise.all([apiFetch(`/api/marketplace/listings/${id}/`),apiFetch(`/api/marketplace/bids/?listing=${id}`)]);
  if(!lr||!lr.ok){body.innerHTML='<p>could not load listing.</p>';return;}
  const listing=await lr.json();
  const bids=br&&br.ok?(await br.json()).results||[]:[]; 

  let html=`<p><strong>${listing.crop}</strong> — ${listing.quantity_kg}kg @ ksh ${listing.price_per_kg}/kg</p>
    <p style="font-size:13px;color:#666;margin-bottom:14px">${listing.description||''}</p>`;

  if(bids.length){
    html+=`<h4 style="font-size:13px;margin-bottom:8px">bids (${bids.length})</h4>`;
    bids.forEach(b=>{
      const statusColor={accepted:'#4a7c3f',rejected:'#e05252',pending:'#e6a817'}[b.status]||'#888';
      html+=`<div style="padding:10px 0;border-bottom:1px solid #f0f0f0;display:flex;align-items:center;justify-content:space-between">
        <div>
          <strong style="font-size:14px">ksh ${b.amount}</strong>
          <span style="font-size:12px;color:#888;margin-left:8px">by ${b.buyer_name||'bidder'}</span>
          <span style="font-size:11px;color:${statusColor};margin-left:8px;font-weight:600">${b.status}</span>
        </div>
        ${isOwner&&b.status==='pending'?`
          <div style="display:flex;gap:6px">
            <button onclick="acceptBid(${b.id},${id})" class="btn-primary" style="font-size:11px;padding:4px 10px">accept</button>
            <button onclick="rejectBid(${b.id},${id})" class="btn-outline" style="font-size:11px;padding:4px 10px">reject</button>
          </div>`
        : b.status==='accepted'?'<span style="color:#4a7c3f;font-size:12px;font-weight:600">✓ accepted</span>':''}
      </div>`;
    });
  } else {
    html+='<p class="loading-text">no bids yet.</p>';
  }

  if(!isOwner&&listing.is_auction&&listing.status==='active'){
    html+=`<div style="display:flex;gap:8px;margin-top:14px">
      <input type="number" id="bidAmount" placeholder="your bid (ksh)" style="flex:1;padding:8px 12px;border:1px solid #ddd;border-radius:8px;font-size:13px">
      <button onclick="placeBid(${id})" class="btn-primary" style="font-size:12px;padding:8px 16px">place bid</button>
    </div><p class="form-error" id="bidError" style="margin-top:6px"></p>`;
  }
  if(isOwner) html+=`<p style="font-size:12px;color:#aaa;margin-top:10px">you cannot bid on your own listing. accept or reject bids above.</p>`;

  body.innerHTML=html;
}

async function acceptBid(bidId, listingId){
  const res=await apiFetch(`/api/marketplace/bids/${bidId}/accept/`,{method:'POST'});
  if(res&&res.ok){
    const d=await res.json();
    showToast(d.message||'bid accepted. escrow created.');
    document.getElementById('listingDetailModal').classList.remove('open');
    loadMyListings();
  }else if(res){const d=await res.json();showToast(d.detail||'error accepting bid','error');}
}

async function rejectBid(bidId, listingId){
  const res=await apiFetch(`/api/marketplace/bids/${bidId}/reject/`,{method:'POST'});
  if(res&&res.ok){showToast('bid rejected');openListing(listingId,true);}
}

async function placeBid(listingId){
  const amount=document.getElementById('bidAmount')?.value;
  const err=document.getElementById('bidError');
  if(!amount){if(err)err.textContent='enter a bid amount';return;}
  const res=await apiFetch('/api/marketplace/bids/',{method:'POST',body:JSON.stringify({listing:listingId,amount})});
  if(res&&res.ok){showToast('bid placed successfully');openListing(listingId,false);}
  else if(res){const d=await res.json();if(err)err.textContent=Object.values(d).flat().join(' ');}
}

async function loadEscrow(){
  const list=document.getElementById('escrowList'); list.innerHTML='<p class="loading-text">loading...</p>';
  const res=await apiFetch('/api/marketplace/escrow/'); if(!res||!res.ok)return;
  const escrows=(await res.json()).results||[];
  if(!escrows.length){list.innerHTML='<p class="loading-text">no escrow transactions. accept a bid to create one.</p>';return;}
  list.innerHTML=escrows.map(e=>{
    const isBuyer = e.buyer === currentUserId;
    const colors={pending:'#e6a817',held:'#4a7c3f',released:'#888',disputed:'#e05252'};
    let actions='';
    if(e.status==='pending'&&isBuyer){
      actions=`<p style="font-size:12px;color:#666;margin-top:8px">pay ksh ${e.amount} via m-pesa to hold funds in escrow until delivery.</p>
        <button onclick="payEscrow(${e.id})" class="btn-primary" style="font-size:12px;padding:6px 14px;margin-top:6px">pay with m-pesa</button>`;
    } else if(e.status==='pending'&&!isBuyer){
      actions=`<p style="font-size:12px;color:#888;margin-top:8px">waiting for buyer to pay ksh ${e.amount} into escrow.</p>`;
    } else if(e.status==='held'&&isBuyer){
      actions=`<p style="font-size:12px;color:#4a7c3f;margin-top:8px">payment held safely. release after you receive the goods.</p>
        <button onclick="releaseEscrow(${e.id})" class="btn-primary" style="font-size:12px;padding:6px 14px;margin-top:6px">confirm delivery &amp; release</button>`;
    } else if(e.status==='held'&&!isBuyer){
      actions=`<p style="font-size:12px;color:#4a7c3f;margin-top:8px">payment held in escrow. deliver goods so buyer can release funds.</p>`;
    } else if(e.status==='released'){
      actions=`<p style="font-size:12px;color:#888;margin-top:8px">transaction complete. funds sent to seller.</p>`;
    }
    return `<div class="scan-item">
      <div style="display:flex;justify-content:space-between;align-items:center">
        <strong>ksh ${e.amount}</strong>
        <span style="background:${colors[e.status]||'#888'};color:#fff;border-radius:20px;padding:3px 10px;font-size:11px">${e.status}</span>
      </div>
      <p style="font-size:12px;color:#888;margin-top:4px">${isBuyer?'you are the buyer':'you are the seller'}</p>
      ${actions}
    </div>`;
  }).join('');
}

async function payEscrow(id){
  showPrompt('enter your m-pesa phone number','e.g. 0712345678', async (phone)=>{
    if(!phone) return;
    const res=await apiFetch(`/api/marketplace/escrow/${id}/pay/`,{method:'POST',body:JSON.stringify({phone})});
    if(res&&res.ok){showToast('stk push sent. check your phone and enter your pin');}
    else if(res){const d=await res.json();showToast(d.detail||'payment failed','error');}
    loadEscrow();
  });
}

async function releaseEscrow(id){
  const res=await apiFetch(`/api/marketplace/escrow/${id}/release/`,{method:'POST'});
  if(res&&res.ok){showToast('funds released to seller. transaction complete.');loadEscrow();}
}
