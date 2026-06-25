// auth helpers used across all pages

function getToken() {
  return localStorage.getItem('access');
}

function getHeaders() {
  return {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${getToken()}`,
  };
}

async function apiFetch(url, options = {}) {
  // wrapper around fetch that adds auth headers automatically
  const res = await fetch(url, {
    ...options,
    headers: {
      ...getHeaders(),
      ...(options.headers || {}),
    },
  });

  // if token expired try to refresh it
  if (res.status === 401) {
    const refreshed = await refreshToken();
    if (refreshed) {
      return apiFetch(url, options);
    } else {
      window.location.href = '/auth/login';
      return null;
    }
  }

  return res;
}

async function refreshToken() {
  const refresh = localStorage.getItem('refresh');
  if (!refresh) return false;

  const res = await fetch('/api/auth/token/refresh/', {
    method:  'POST',
    headers: {'Content-Type': 'application/json'},
    body:    JSON.stringify({refresh}),
  });

  if (res.ok) {
    const data = await res.json();
    localStorage.setItem('access', data.access);
    return true;
  }

  localStorage.clear();
  return false;
}

function logout() {
  const refresh = localStorage.getItem('refresh');
  fetch('/api/auth/logout/', {
    method:  'POST',
    headers: getHeaders(),
    body:    JSON.stringify({refresh}),
  }).finally(() => {
    localStorage.clear();
    window.location.href = '/auth/login';
  });
}

// redirect to login if not authenticated
function requireAuth() {
  if (!getToken()) {
    window.location.href = '/auth/login';
  }
}
