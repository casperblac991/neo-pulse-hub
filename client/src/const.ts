export { COOKIE_NAME, ONE_YEAR_MS } from "@shared/const";

// Generate login URL at runtime so redirect URI reflects the current origin.
// If OAuth is not configured, return a safe same-origin URL instead of letting
// `new URL()` throw and crashing the entire React application.
export const isOAuthConfigured = () => {
  const oauthPortalUrl = String(import.meta.env.VITE_OAUTH_PORTAL_URL ?? "").trim();
  const appId = String(import.meta.env.VITE_APP_ID ?? "").trim();
  return Boolean(oauthPortalUrl && appId);
};

export const getLoginUrl = () => {
  const oauthPortalUrl = String(import.meta.env.VITE_OAUTH_PORTAL_URL ?? "").trim();
  const appId = String(import.meta.env.VITE_APP_ID ?? "").trim();
  const redirectUri = `${window.location.origin}/api/oauth/callback`;
  const state = btoa(redirectUri);

  if (!isOAuthConfigured()) {
    return `${window.location.origin}/?auth=not-configured`;
  }

  let url: URL;
  try {
    url = new URL(`${oauthPortalUrl.replace(/\/$/, "")}/app-auth`);
  } catch {
    return `${window.location.origin}/?auth=invalid-config`;
  }
  url.searchParams.set("appId", appId);
  url.searchParams.set("redirectUri", redirectUri);
  url.searchParams.set("state", state);
  url.searchParams.set("type", "signIn");

  return url.toString();
};
