// disease detection page
document.addEventListener('DOMContentLoaded', async () => {
  loadFarmsDropdown();
  loadScans();

  document.getElementById('scanForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const form  = e.target;
    const error = document.getElementById('scanError');
    const body  = {
      farm:           form.farm.value,
      cloudinary_url: form.cloudinary_url.value,
      notes:          form.notes.value,
    };

    const res = await apiFetch('/api/disease/', {
      method: 'POST',
      body:   JSON.stringify(body),
    });

    if (res && res.ok) {
      form.reset();
      loadScans();
    } else {
      const data    = await res.json();
      error.textContent = Object.values(data).flat().join(' ');
    }
  });
});

async function loadFarmsDropdown() {
  const select = document.getElementById('scanFarmSelect');
  const res    = await apiFetch('/api/farms/');
  if (!res || !res.ok) return;
  const data   = await res.json();
  const farms  = data.results || data;
  select.innerHTML = farms.map(f => `<option value="${f.id}">${f.name}</option>`).join('');
}

async function loadScans() {
  const list = document.getElementById('scansList');
  list.innerHTML = '<p class="loading-text">loading...</p>';
  const res  = await apiFetch('/api/disease/');
  if (!res || !res.ok) return;
  const data  = await res.json();
  const scans = data.results || data;
  list.innerHTML = '';

  if (!scans.length) {
    list.innerHTML = '<p class="loading-text">no scans yet. submit your first crop photo above.</p>';
    return;
  }

  scans.forEach(scan => {
    list.innerHTML += `
      <div class="scan-item">
        <h5>${scan.disease_detected || 'awaiting diagnosis'} <span class="badge badge-${scan.status}">${scan.status}</span></h5>
        <p>${scan.treatment_advice || 'ai is processing your scan...'}</p>
        <p style="font-size:12px;color:#aaa;margin-top:6px">${new Date(scan.created_at).toLocaleDateString()}</p>
      </div>`;
  });
}
