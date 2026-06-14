const BASE = "/api";

async function request(path) {
  const res = await fetch(BASE + path);
  if (!res.ok) throw new Error(`Request failed: ${res.status}`);
  return res.json();
}

export const api = {
  getReport: () => request("/report"),
  getLineItems: (department) =>
    request("/line-items" + (department ? `?department=${encodeURIComponent(department)}` : "")),
};
