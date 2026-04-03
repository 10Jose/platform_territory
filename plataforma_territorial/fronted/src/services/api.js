/**
 * Base URL del BFF.
 * - Desarrollo sin REACT_APP_API_URL: rutas relativas → proxy de CRA (package.json) → localhost:8000
 * - Producción o con REACT_APP_API_URL definida: URL explícita
 */
function getApiBase() {
  const fromEnv = process.env.REACT_APP_API_URL;
  if (fromEnv != null && String(fromEnv).trim() !== '') {
    return String(fromEnv).replace(/\/$/, '');
  }
  if (process.env.NODE_ENV === 'development') {
    return '';
  }
  return 'http://localhost:8000';
}

const API_BASE = getApiBase();

async function fetchWithNetworkHelp(url, options) {
  try {
    return await fetch(url, options);
  } catch (e) {
    const msg = e && e.message ? e.message : String(e);
    if (
      msg === 'Failed to fetch' ||
      msg.includes('NetworkError') ||
      msg.includes('Load failed')
    ) {
      throw new Error(
        'No hay conexión con el servidor (BFF). Levanta los servicios con Docker: ' +
          'desde la carpeta plataforma_territorial ejecuta ' +
          '"docker compose -f Docker-compose.yaml up -d" y espera unos segundos. ' +
          'El BFF debe responder en http://localhost:8000/health'
      );
    }
    throw e;
  }
}

const handleResponse = async (response) => {
  if (!response.ok) {
    let errorMessage = `Error ${response.status}: ${response.statusText}`;
    try {
      const data = await response.json();
      if (data.detail && Array.isArray(data.detail)) {
        errorMessage = data.detail.map((err) => err.msg).join(', ');
      } else if (data.detail && typeof data.detail === 'string') {
        errorMessage = data.detail;
      } else if (data.message) {
        errorMessage = data.message;
      }
    } catch {
      /* ignore */
    }
    const err = new Error(errorMessage);
    err.status = response.status;
    throw err;
  }
  return response.json();
};

export const api = {
  logout() {
    localStorage.removeItem('token');
  },

  async login(username, password) {
    const body = new URLSearchParams();
    body.set('username', username);
    body.set('password', password);

    const response = await fetchWithNetworkHelp(`${API_BASE}/api/auth/token`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: body.toString(),
    });

    const data = await handleResponse(response);
    if (data.access_token) {
      localStorage.setItem('token', data.access_token);
    }
    return data;
  },

  async register({ username, email, password, full_name }) {
    const response = await fetchWithNetworkHelp(`${API_BASE}/api/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        username,
        email,
        password,
        full_name: full_name || null,
      }),
    });
    return handleResponse(response);
  },

  async loadFile(file) {
    const formData = new FormData();
    formData.append('file', file);

    const token = localStorage.getItem('token');
    const headers = {};
    if (token) {
      headers.Authorization = `Bearer ${token}`;
    }

    const response = await fetchWithNetworkHelp(`${API_BASE}/api/load/`, {
      method: 'POST',
      headers,
      body: formData,
    });

    return handleResponse(response);
  },

  async getZones(skip = 0, limit = 100) {
    const token = localStorage.getItem('token');
    const headers = {};
    if (token) {
      headers.Authorization = `Bearer ${token}`;
    }

    const response = await fetchWithNetworkHelp(
      `${API_BASE}/api/zones/?skip=${skip}&limit=${limit}`,
      { headers }
    );
    return handleResponse(response);
  },
};
