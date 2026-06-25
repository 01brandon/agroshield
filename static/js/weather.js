// weather page
document.addEventListener('DOMContentLoaded', async () => {
  loadAlerts();
  loadReadings();
});

async function loadAlerts() {
  const list = document.getElementById('alertsList');
  const res  = await apiFetch('/api/weather/alerts/');
  if (!res || !res.ok) return;
  const data   = await res.json();
  const alerts = data.results || data;
  list.innerHTML = '';

  if (!alerts.length) {
    list.innerHTML = '<p class="loading-text">no active alerts. all conditions are normal.</p>';
    return;
  }

  alerts.forEach(alert => {
    list.innerHTML += `
      <div class="alert-item ${alert.alert_type}">
        <strong>${alert.alert_type.toUpperCase()} - severity ${alert.severity}/5</strong>
        <p style="font-size:14px;margin-top:4px">${alert.message}</p>
        <p style="font-size:12px;color:#888;margin-top:6px">${new Date(alert.created_at).toLocaleDateString()}</p>
      </div>`;
  });
}

async function loadReadings() {
  const list = document.getElementById('readingsList');
  const res  = await apiFetch('/api/weather/readings/');
  if (!res || !res.ok) return;
  const data     = await res.json();
  const readings = data.results || data;
  list.innerHTML = '';

  if (!readings.length) {
    list.innerHTML = '<p class="loading-text">no weather readings yet.</p>';
    return;
  }

  readings.forEach(r => {
    list.innerHTML += `
      <div class="reading-item">
        <strong>${r.description}</strong>
        <p style="font-size:13px;color:#666;margin-top:4px">
          temp: ${r.temperature}c &bull;
          humidity: ${r.humidity}% &bull;
          wind: ${r.wind_speed} m/s &bull;
          rain: ${r.rainfall_mm}mm
        </p>
        <p style="font-size:12px;color:#aaa;margin-top:4px">${new Date(r.recorded_at).toLocaleDateString()}</p>
      </div>`;
  });
}
