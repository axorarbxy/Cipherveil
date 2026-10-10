const API_BASE = "http://127.0.0.1:8000";

let authToken = null;

export function setToken(token) {
  authToken = token;
  localStorage.setItem("token", token);
}

export function loadToken() {
  authToken = localStorage.getItem("token");
  return authToken;
}

async function request(path, options = {}) {
  const headers = {
    "Content-Type": "application/json",
    ...(authToken ? { Authorization: `Bearer ${authToken}` } : {}),
    ...options.headers,
  };
  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`API ${path} failed: ${res.status} ${text}`);
  }
  return res.json();
}

export async function login(username, password) {
  const body = new URLSearchParams({ username, password });
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body,
  });
  if (!res.ok) throw new Error("Login failed");
  const data = await res.json();
  setToken(data.access_token);
  return data;
}

export function getAlerts() {
  return request("/alerts?limit=1000");
}

export function getDevices() {
  return request("/devices");
}

export function getIncidents() {
  return request("/incidents");
}

export function getEvents() {
  return request("/events?limit=100");
}

const SECURITY_DEVICE_KEY = import.meta.env.VITE_SECURITY_DEVICE_KEY;

async function simulateSecurityEvent(reason, baseRisk, fileType = "canary_trip") {
  if (!SECURITY_DEVICE_KEY) {
    throw new Error("Set VITE_SECURITY_DEVICE_KEY in frontend/.env.local to enable security simulations.");
  }

  const headers = { "Content-Type": "application/json", "X-Device-Key": SECURITY_DEVICE_KEY };

  const eventRes = await fetch(`${API_BASE}/events`, {
    method: "POST",
    headers,
    body: JSON.stringify({ event_type: fileType, file_path: null, features: null }),
  });
  const event = await eventRes.json();

  const alertRes = await fetch(`${API_BASE}/alerts`, {
    method: "POST",
    headers,
    body: JSON.stringify({
      event_id: event.id,
      reason,
      base_risk: baseRisk,
      ml_score: 0,
      shap_explanation: null,
    }),
  });
  return alertRes.json();
}

export function simulateCanaryHit() {
  return simulateSecurityEvent("CANARY FILE MODIFIED", 100, "canary_trip");
}

export function simulateHeartbeatLoss() {
  return simulateSecurityEvent("DEAD-MAN'S-SWITCH: heartbeat timeout", 98, "heartbeat");
}

export function simulateMassChange() {
  return simulateSecurityEvent("Mass file-change pattern detected", 92, "file_modified");
}

export function getDashboardOverview() {
  return request("/dashboard/overview");
}

export function getDashboardTimeline(hours = 24) {
  return request(`/dashboard/timeline?hours=${hours}`);
}

export async function exportCertInReport(incidentId) {
  const res = await fetch(`${API_BASE}/incidents/${incidentId}/cert-in-export`, {
    headers: { Authorization: `Bearer ${authToken}` },
  });
  if (!res.ok) throw new Error("Export failed");
  return res.json();
}

export function updateAlertStatus(alertId, status) {
  return request(`/alerts/${alertId}/status`, {
    method: "PATCH",
    body: JSON.stringify({ status }),
  });
}

export function updateIncidentStatus(incidentId, status) {
  return request(`/incidents/${incidentId}/status`, {
    method: "PATCH",
    body: JSON.stringify({ status }),
  });
}

export function isolateDevice(deviceId) {
  return request(`/devices/${deviceId}/isolate`, { method: "POST" });
}

export function restoreDevice(deviceId) {
  return request(`/devices/${deviceId}/restore`, { method: "POST" });
}

export function deleteDevice(deviceId) {
  return request(`/devices/${deviceId}`, { method: "DELETE" });
}

export function getCurrentUser() {
  return request("/auth/me");
}

export function getDevice(deviceId) {
  return request(`/devices/${deviceId}`);
}

const ML_SERVICE_URL = "http://127.0.0.1:8020";

export async function simulateMLRansomware() {
  const res = await fetch(`${ML_SERVICE_URL}/simulate/ransomware`, { method: "POST" });
  return res.json();
}

export async function simulateMLBenign() {
  const res = await fetch(`${ML_SERVICE_URL}/simulate/benign`, { method: "POST" });
  return res.json();
}