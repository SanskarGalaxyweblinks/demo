// Lightweight replacement for the Supabase client that proxies auth requests
// to your own backend. This avoids requiring Supabase env vars when you
// switched to a custom backend. Update the API endpoints below to match
// your backend's auth routes.

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "";

function getStoredSession() {
  try {
    return JSON.parse(localStorage.getItem("session") || "null");
  } catch { return null; }
}

function setStoredSession(session: any) {
  try {
    localStorage.setItem("session", JSON.stringify(session));
  } catch {}
}

function dispatchAuthChange(session: any) {
  try {
    const ev = new CustomEvent("jupiter_auth_change", { detail: session });
    window.dispatchEvent(ev as Event);
  } catch {}
}

function getAuthHeader() {
  const s = getStoredSession();
  const token = s?.token ?? s?.access_token ?? null;
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function post(path: string, body: any) {
  const headers = { "Content-Type": "application/json", ...getAuthHeader() };
  const res = await fetch(API_BASE + path, {
    method: "POST",
    headers,
    body: JSON.stringify(body),
    credentials: "include",
  });
  let json = null;
  try { json = await res.json(); } catch (e) { json = null; }
  return { ok: res.ok, status: res.status, body: json };
}

async function get(path: string) {
  const headers = { ...getAuthHeader() };
  const res = await fetch(API_BASE + path, {
    method: "GET",
    headers,
    credentials: "include",
  });
  let json = null;
  try { json = await res.json(); } catch { json = null; }
  return { ok: res.ok, status: res.status, body: json };
}

export const supabase = {
  auth: {
    // Sign in with email+password -> POST /auth/login
    async signInWithPassword({ email, password }: { email: string; password: string }) {
      const res = await post("/auth/login", { email, password });
      if (!res.ok) return { error: new Error(res.body?.detail || res.body?.message || "Login failed") };
      // backend returns { token, user }
      if (res.body?.token) {
        const session = { token: res.body.token, user: res.body.user };
        setStoredSession(session);
        dispatchAuthChange(session);
      }
      return { data: res.body, error: null };
    },

    // Sign up -> POST /auth/register
    async signUp({ email, password, options }: any) {
      const payload: any = { email, password };
      if (options?.data) payload.data = options.data;
      const res = await post("/auth/register", payload);
      if (!res.ok) return { error: new Error(res.body?.detail || res.body?.message || "Sign up failed") };
      if (res.body?.token) {
        const session = { token: res.body.token, user: res.body.user };
        setStoredSession(session);
        dispatchAuthChange(session);
      }
      return { data: res.body, error: null };
    },

    // OAuth -> redirect the browser to your backend OAuth entrypoint
    async signInWithOAuth({ provider, options }: { provider: string; options?: any }) {
      // Example: /auth/oauth/google?redirectTo=...
      const redirectTo = encodeURIComponent(options?.redirectTo ?? window.location.origin);
      const url = `${API_BASE}/auth/oauth/${provider}?redirectTo=${redirectTo}`;
      window.location.href = url;
      return { error: null };
    },

    // Sign out -> POST /auth/logout and clear local session
    async signOut() {
      try {
        await post("/auth/logout", {});
      } catch {}
      setStoredSession(null);
      dispatchAuthChange(null);
      return { error: null };
    },

    // Return current session (compatible shape)
    async getSession() {
      // If we have no locally stored token, avoid calling backend (prevents 401 spam)
      const local = getStoredSession();
      const token = local?.token ?? local?.access_token ?? null;
      if (!token) {
        return { data: { session: local } };
      }

      // We have a token; verify with backend and update stored user
      try {
        const res = await get("/auth/session");
        if (res.ok && res.body) {
          const session = { token, user: res.body };
          setStoredSession(session);
          return { data: { session } };
        }
      } catch {}

      // If backend verification failed, return local session (may be stale)
      return { data: { session: local } };
    },

    // Minimal onAuthStateChange shim: calls the callback once and returns
    // a subscription object with unsubscribe() to match supabase's shape.
    onAuthStateChange(callback: (event: string, session: any) => void) {
      const handler = (ev: Event) => {
        try {
          const detail = (ev as CustomEvent).detail;
          callback("AUTH_CHANGE", detail);
        } catch {}
      };

      // call initial state asynchronously
      const callInit = async () => {
        const { data: { session } } = await supabase.auth.getSession();
        setTimeout(() => callback("INITIAL_SESSION", session), 0);
      };
      callInit();

      window.addEventListener("jupiter_auth_change", handler as EventListener);
      const subscription = { unsubscribe: () => window.removeEventListener("jupiter_auth_change", handler as EventListener) };
      return { data: { subscription } };
    }
  }
};