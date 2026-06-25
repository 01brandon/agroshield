// farms page - load, display, and create farms
document.addEventListener('DOMContentLoaded', async () => {
  loadFarms();

  document.getElementById('openAddFarm').addEventListener('click', () => {
    document.getElementById('addFarmModal').classList.add('open');
  });

  document.getElementById('closeAddFarm').addEventListener('click', () => {
    document.getElementById('addFarmModal').classList.remove('open');
  });

  document.getElementById('addFarmForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const form  = e.target;
    const error = document.getElementById('farmError');
    const body  = {
      name:          form.name.value,
      location_name: form.location_name.value,
      latitude:      parseFloat(form.latitude.value),
      longitude:     parseFloat(form.longitude.value),
      size_hectares: form.size_hectares.value,
      primary_crop:  form.primary_crop.value,
      description:   form.description.value,
    };

    const res = await apiFetch('/api/farms/', {
      method: 'POST',
      body:   JSON.stringify(body),
    });

    if (res && res.ok) {
      document.getElementById('addFarmModal').classList.remove('open');
      form.reset();
      loadFarms();
    } else {
      const data = await res.json();
      error.textContent = Object.values(data).flat().join(' ');
    }
  });
});

async function loadFarms() {
  const grid = document.getElementById('farmsGrid');
  grid.innerHTML = '<p class="loading-text">loading your farms...</p>';

  const res = await apiFetch('/api/farms/');
  if (!res || !res.ok) {
    grid.innerHTML = '<p class="loading-text">error loading farms.</p>';
    return;
  }

  const data  = await res.json();
  const farms = data.results || data;
  grid.innerHTML = '';

  if (!farms.length) {
    grid.innerHTML = '<p class="loading-text">no farms yet. add your first farm above.</p>';
    return;
  }

  farms.forEach(farm => {
    grid.innerHTML += `
      <div class="farm-card">
        <h4>${farm.name}</h4>
        <p>${farm.location_name}</p>
        <p>${farm.size_hectares} hectares</p>
        <p>lat: ${farm.latitude} &bull; lng: ${farm.longitude}</p>
        <span class="farm-badge">${farm.primary_crop}</span>
      </div>`;
  });
}
