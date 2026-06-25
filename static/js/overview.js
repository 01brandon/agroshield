// dashboard overview page - loads summary stats and recent items
document.addEventListener('DOMContentLoaded', async () => {

  // load farms count
  const farmsRes = await apiFetch('/api/farms/');
  if (farmsRes && farmsRes.ok) {
    const data = await farmsRes.json();
    document.getElementById('statFarms').textContent = data.count || data.results?.length || 0;

    const farmsEl = document.getElementById('recentFarms');
    farmsEl.innerHTML = '';
    const farms = data.results || data;
    farms.slice(0, 3).forEach(farm => {
      farmsEl.innerHTML += `
        <div style="padding:10px 0;border-bottom:1px solid #f0f0f0">
          <strong style="font-size:14px">${farm.name}</strong>
          <p style="font-size:12px;color:#888;margin:2px 0">${farm.location_name} &bull; ${farm.primary_crop}</p>
        </div>`;
    });
    if (!farms.length) farmsEl.innerHTML = '<p class="loading-text">no farms yet. add your first farm.</p>';
  }

  // load scans
  const scansRes = await apiFetch('/api/disease/');
  if (scansRes && scansRes.ok) {
    const data = await scansRes.json();
    document.getElementById('statScans').textContent = data.count || data.results?.length || 0;

    const scansEl = document.getElementById('recentScans');
    scansEl.innerHTML = '';
    const scans = data.results || data;
    scans.slice(0, 3).forEach(scan => {
      scansEl.innerHTML += `
        <div style="padding:10px 0;border-bottom:1px solid #f0f0f0">
          <strong style="font-size:14px">${scan.disease_detected || 'pending diagnosis'}</strong>
          <p style="font-size:12px;color:#888;margin:2px 0">${new Date(scan.created_at).toLocaleDateString()}</p>
        </div>`;
    });
    if (!scans.length) scansEl.innerHTML = '<p class="loading-text">no scans yet.</p>';
  }

  // load weather alerts
  const alertsRes = await apiFetch('/api/weather/alerts/');
  if (alertsRes && alertsRes.ok) {
    const data = await alertsRes.json();
    document.getElementById('statAlerts').textContent = data.count || data.results?.length || 0;

    const alertsEl = document.getElementById('recentAlerts');
    alertsEl.innerHTML = '';
    const alerts = data.results || data;
    alerts.slice(0, 3).forEach(alert => {
      alertsEl.innerHTML += `
        <div style="padding:10px 0;border-bottom:1px solid #f0f0f0">
          <strong style="font-size:14px">${alert.alert_type} - severity ${alert.severity}</strong>
          <p style="font-size:12px;color:#888;margin:2px 0">${alert.message?.substring(0, 60)}...</p>
        </div>`;
    });
    if (!alerts.length) alertsEl.innerHTML = '<p class="loading-text">no alerts. all clear.</p>';
  }

  // load marketplace listings
  const listingsRes = await apiFetch('/api/marketplace/listings/');
  if (listingsRes && listingsRes.ok) {
    const data = await listingsRes.json();
    document.getElementById('statListings').textContent = data.count || data.results?.length || 0;

    const listingsEl = document.getElementById('recentListings');
    listingsEl.innerHTML = '';
    const listings = data.results || data;
    listings.slice(0, 3).forEach(listing => {
      listingsEl.innerHTML += `
        <div style="padding:10px 0;border-bottom:1px solid #f0f0f0">
          <strong style="font-size:14px">${listing.crop} - ${listing.quantity_kg}kg</strong>
          <p style="font-size:12px;color:#888;margin:2px 0">ksh ${listing.price_per_kg}/kg &bull; grade ${listing.grade}</p>
        </div>`;
    });
    if (!listings.length) listingsEl.innerHTML = '<p class="loading-text">no active listings.</p>';
  }
});
