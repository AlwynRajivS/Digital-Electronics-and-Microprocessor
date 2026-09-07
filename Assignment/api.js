/*************************************************************
 *  API HELPER
 *  Wraps fetch() calls to the Google Apps Script Web App.
 *  Uses text/plain content-type to avoid CORS pre-flight,
 *  which Apps Script web apps do not support.
 *************************************************************/
async function api(action, payload = {}) {
  if (!CONFIG.GAS_URL || CONFIG.GAS_URL.indexOf("PASTE_YOUR") === 0) {
    throw new Error("Backend not configured yet. Set CONFIG.GAS_URL in config.js");
  }
  const res = await fetch(CONFIG.GAS_URL, {
    method: "POST",
    headers: { "Content-Type": "text/plain;charset=utf-8" },
    body: JSON.stringify({ action, ...payload })
  });
  if (!res.ok) throw new Error("Network error: " + res.status);
  const data = await res.json();
  if (data && data.error) throw new Error(data.error);
  return data;
}

function currentUser() {
  const raw = sessionStorage.getItem("pp_user");
  if (!raw) {
    window.location.href = "Assignindex.html";
    return null;
  }
  return JSON.parse(raw);
}

function logout() {
  sessionStorage.removeItem("pp_user");
  window.location.href = "Assignindex.html";
}

function toast(message, type = "info") {
  const stack = document.getElementById("toast-stack");
  if (!stack) return;
  const el = document.createElement("div");
  el.className = "toast " + type;
  el.textContent = message;
  stack.appendChild(el);
  setTimeout(() => {
    el.style.opacity = "0";
    el.style.transform = "translateX(30px)";
    el.style.transition = "all .3s ease";
    setTimeout(() => el.remove(), 300);
  }, 3800);
}

function fileToBase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result.split(",")[1]);
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}

function fmtDate(d) {
  if (!d) return "—";
  const date = new Date(d);
  if (isNaN(date)) return d;
  return date.toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "numeric" });
}

function escapeHtml(str) {
  if (str === null || str === undefined) return "";
  return String(str)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}
