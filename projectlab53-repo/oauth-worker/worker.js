/**
 * LAB53 Decap CMS OAuth "doorman" — Cloudflare Worker
 * ----------------------------------------------------
 * Decap CMS's GitHub backend needs a small server to complete the OAuth
 * handshake (GitHub requires a client secret, which can never live in the
 * browser). This Worker is that server. It does exactly two things:
 *
 *   GET /auth       -> redirects the browser to GitHub's login screen
 *   GET /callback    -> GitHub redirects back here with a one-time code;
 *                        this exchanges it for an access token and hands
 *                        that token back to the Decap CMS popup window
 *
 * It never sees or stores your posts — it only brokers the login. Nothing
 * is logged or persisted; CLIENT_ID and CLIENT_SECRET are the only secrets
 * it needs, set as Worker environment variables (see SETUP.md).
 */

const GITHUB_AUTHORIZE_URL = "https://github.com/login/oauth/authorize";
const GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token";

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (url.pathname === "/auth") {
      const state = crypto.randomUUID();
      const authorizeUrl = new URL(GITHUB_AUTHORIZE_URL);
      authorizeUrl.searchParams.set("client_id", env.OAUTH_CLIENT_ID);
      authorizeUrl.searchParams.set("scope", "repo,user");
      authorizeUrl.searchParams.set("state", state);
      authorizeUrl.searchParams.set(
        "redirect_uri",
        new URL("/callback", url).toString()
      );
      return Response.redirect(authorizeUrl.toString(), 302);
    }

    if (url.pathname === "/callback") {
      const code = url.searchParams.get("code");
      if (!code) {
        return new Response("Missing ?code from GitHub.", { status: 400 });
      }

      const tokenResp = await fetch(GITHUB_TOKEN_URL, {
        method: "POST",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          client_id: env.OAUTH_CLIENT_ID,
          client_secret: env.OAUTH_CLIENT_SECRET,
          code,
        }),
      });
      const tokenData = await tokenResp.json();

      if (tokenData.error) {
        return new Response(
          `GitHub OAuth error: ${tokenData.error_description || tokenData.error}`,
          { status: 400 }
        );
      }

      // Hand the token back to the Decap CMS popup via postMessage, using
      // the exact message format Decap's github backend listens for.
      const payload = JSON.stringify({
        token: tokenData.access_token,
        provider: "github",
      });
      const html = `<!doctype html>
<html><body>
<script>
  (function () {
    function receiveMessage(message) {
      window.opener.postMessage(
        'authorization:github:success:${escapeForScript(payload)}',
        message.origin
      );
      window.removeEventListener("message", receiveMessage, false);
    }
    window.addEventListener("message", receiveMessage, false);
    window.opener.postMessage("authorizing:github", "*");
  })();
</script>
You can close this window.
</body></html>`;

      return new Response(html, {
        headers: { "Content-Type": "text/html;charset=UTF-8" },
      });
    }

    return new Response(
      "LAB53 OAuth doorman is running. Use /auth to start a login.",
      { status: 200 }
    );
  },
};

function escapeForScript(s) {
  return s.replace(/\\/g, "\\\\").replace(/'/g, "\\'");
}
