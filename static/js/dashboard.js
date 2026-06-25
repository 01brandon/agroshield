// runs on every dashboard page
document.addEventListener('DOMContentLoaded', () => {
  requireAuth();

  // load and display the current user's name
  apiFetch('/api/auth/profile/').then(res => {
    if (res && res.ok) {
      res.json().then(data => {
        const el = document.getElementById('dashUser');
        if (el) el.textContent = data.full_name || data.email;
      });
    }
  });

  // logout button
  const logoutBtn = document.getElementById('logoutBtn');
  if (logoutBtn) {
    logoutBtn.addEventListener('click', (e) => {
      e.preventDefault();
      logout();
    });
  }
});
