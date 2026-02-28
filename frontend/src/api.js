const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || "").replace(/\/$/, "");

function withBase(path) {
  if (!API_BASE_URL) return path;
  return `${API_BASE_URL}${path}`;
}

function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(";").shift();
  return "";
}

async function ensureCsrfToken() {
  let token = getCookie("csrftoken");
  if (token) {
    return token;
  }

  await fetch(withBase("/api/session/"), { credentials: "include" });
  token = getCookie("csrftoken");
  return token;
}

async function request(path, options = {}) {
  const method = options.method || "GET";
  const config = {
    method,
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {})
    }
  };

  if (method !== "GET") {
    const csrfToken = await ensureCsrfToken();
    if (csrfToken) {
      config.headers["X-CSRFToken"] = csrfToken;
    }
  }

  if (options.body !== undefined) {
    config.body = JSON.stringify(options.body);
  }

  let response;
  try {
    response = await fetch(withBase(path), config);
  } catch {
    throw new Error("Backend haipatikani. Hakikisha python manage.py runserver inaendelea.");
  }

  const contentType = response.headers.get("content-type") || "";
  let data = {};

  if (contentType.includes("application/json")) {
    data = await response.json().catch(() => ({}));
  } else {
    const text = await response.text().catch(() => "");
    if (text) {
      data.message = text.slice(0, 200);
    }
  }

  if (!response.ok) {
    throw new Error(data.message || `Request failed (${response.status})`);
  }

  return data;
}

async function requestBlob(path) {
  let response;
  try {
    response = await fetch(withBase(path), { method: "GET", credentials: "include" });
  } catch {
    throw new Error("Backend haipatikani. Hakikisha python manage.py runserver inaendelea.");
  }

  if (!response.ok) {
    throw new Error(`Request failed (${response.status})`);
  }

  return response.blob();
}

export const api = {
  session: () => request("/api/session/"),
  login: (payload) => request("/api/login/", { method: "POST", body: payload }),
  register: (payload) => request("/api/register/", { method: "POST", body: payload }),
  logout: () => request("/api/logout/", { method: "POST", body: {} }),
  hostels: () => request("/api/hostels/"),
  status: () => request("/api/status/"),
  apply: (payload) => request("/api/allocate/", { method: "POST", body: payload }),
  dashboard: () => request("/api/dashboard/"),
  adminDashboard: () => request("/api/admin/dashboard/"),
  adminDeleteUser: (userId) => request(`/api/admin/users/${userId}/delete/`, { method: "POST", body: {} }),
  adminUpdateRoom: (allocationId, roomNumber) =>
    request(`/api/admin/allocations/${allocationId}/room/`, {
      method: "POST",
      body: { room_number: roomNumber }
    }),
  exportAllocationsCsv: () => requestBlob("/api/export/allocations.csv")
};
