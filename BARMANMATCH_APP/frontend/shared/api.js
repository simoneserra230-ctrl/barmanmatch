/**
 * BarmanMatch — API client
 * Chiama il backend FastAPI con il token JWT dalla sessione corrente.
 */

const API_BASE = "http://127.0.0.1:8000";

function getToken() {
  return localStorage.getItem("bm_token");
}

function getSession() {
  try { return JSON.parse(localStorage.getItem("bm_session") || "null"); }
  catch { return null; }
}

function setSession(data) {
  localStorage.setItem("bm_token", data.access_token);
  localStorage.setItem("bm_session", JSON.stringify(data));
}

function clearSession() {
  localStorage.removeItem("bm_token");
  localStorage.removeItem("bm_session");
}

function requireAuth(redirectTo = "../index.html") {
  if (!getToken()) {
    window.location.href = redirectTo;
    return false;
  }
  return true;
}

async function api(method, path, body = null, raw = false) {
  const token = getToken();
  const headers = { "Content-Type": "application/json" };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const opts = { method, headers };
  if (body) opts.body = JSON.stringify(body);

  const res = await fetch(`${API_BASE}${path}`, opts);

  if (res.status === 401) {
    clearSession();
    window.location.href = "../index.html";
    return null;
  }

  if (!res.ok) {
    let detail = "Errore sconosciuto";
    try { detail = (await res.json()).detail || detail; } catch {}
    throw new Error(detail);
  }

  return raw ? res : res.json();
}

const API = {
  get:    (path) => api("GET", path),
  post:   (path, body) => api("POST", path, body),
  patch:  (path, body) => api("PATCH", path, body),
  delete: (path) => api("DELETE", path),
};

// ── Utility UI ───────────────────────────────────────────────────
function showAlert(containerId, message, type = "error") {
  const el = document.getElementById(containerId);
  if (!el) return;
  el.innerHTML = `<div class="alert alert-${type}">${message}</div>`;
  setTimeout(() => { el.innerHTML = ""; }, 5000);
}

function setLoading(btnId, loading) {
  const btn = document.getElementById(btnId);
  if (!btn) return;
  btn.disabled = loading;
  btn.innerHTML = loading
    ? '<span class="spinner"></span>'
    : btn.dataset.label || btn.textContent;
}

function formatDate(dateStr) {
  return new Date(dateStr).toLocaleDateString("it-IT", {
    weekday: "short", day: "numeric", month: "short",
  });
}

function formatTime(timeStr) {
  return timeStr ? timeStr.slice(0, 5) : "";
}

function calcHours(start, end) {
  const [sh, sm] = start.split(":").map(Number);
  const [eh, em] = end.split(":").map(Number);
  return ((eh * 60 + em) - (sh * 60 + sm)) / 60;
}

function starsHtml(score, max = 5) {
  let h = "";
  for (let i = 1; i <= max; i++) {
    h += `<span class="star ${i <= Math.round(score) ? "active" : "inactive"}">★</span>`;
  }
  return h;
}

function scoreBar(score) {
  return `
    <div class="shift-score">
      <span>Match ${score}%</span>
      <div class="score-bar"><div class="score-fill" style="width:${score}%"></div></div>
    </div>`;
}

function statusBadge(status) {
  const map = {
    open:      ["green",  "● Aperto"],
    filled:    ["gold",   "● Coperto"],
    cancelled: ["red",    "● Annullato"],
    completed: ["teal",   "✓ Completato"],
    pending:   ["violet", "⏳ In attesa"],
    confirmed: ["green",  "✓ Confermato"],
    withdrawn: ["red",    "✗ Ritirata"],
    no_show:   ["red",    "✗ No-show"],
  };
  const [color, label] = map[status] || ["violet", status];
  return `<span class="badge badge-${color}">${label}</span>`;
}
