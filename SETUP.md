# Setting up the LAB53 journal dashboard

This is the one-time setup for the `/admin` dashboard — after this, adding
or editing a post is just: log in, write, hit Publish. No terminal, no git,
no Claude required.

Everything below needs to happen from **your own accounts** (GitHub,
Cloudflare) — these are login/credential steps I can't do on your behalf.
It's about 15–20 minutes, once.

## What you're setting up, in plain terms

- **`/admin`** — a page on your site that's a full post editor (Decap CMS).
- A **tiny helper server** ("the doorman") that lets `/admin` log in with
  your GitHub account. GitHub requires this for security — a plain web page
  can't do a login handshake on its own. It runs free on Cloudflare and
  never sees your posts, only the login step.
- Your existing GitHub Pages hosting stays exactly as-is; it just switches
  from "publish whatever's committed" to "publish whatever `build.py`
  produces," rebuilt automatically by GitHub Actions on every commit —
  whether that commit comes from you pushing, or from the dashboard.

**Who can log in:** only your GitHub account (or anyone you add as a
collaborator on the repo). That's the "password protection" — GitHub's own
login, which you can also put 2FA on.

---

## Step 1 — Deploy the doorman (Cloudflare Worker)

1. If you don't have a Cloudflare account, make a free one at
   [dash.cloudflare.com/sign-up](https://dash.cloudflare.com/sign-up) —
   no credit card needed for this.
2. You'll need Node.js installed (check with `node -v` in Terminal; if
   missing, get it from [nodejs.org](https://nodejs.org)).
3. In Terminal:
   ```
   cd "Project LAB53/projectlab53-repo/oauth-worker"
   npx wrangler login
   ```
   This opens a browser tab — click Allow.
4. Deploy it:
   ```
   npx wrangler deploy
   ```
   This prints a URL like:
   ```
   https://lab53-cms-oauth.<your-subdomain>.workers.dev
   ```
   **Copy that URL down** — you'll need it twice below.

## Step 2 — Create a GitHub OAuth App

1. Go to [github.com/settings/developers](https://github.com/settings/developers)
   → **OAuth Apps** → **New OAuth App**.
2. Fill in:
   - **Application name**: `LAB53 CMS`
   - **Homepage URL**: `https://projectlab53.com`
   - **Authorization callback URL**: the Worker URL from Step 1, with
     `/callback` on the end, e.g.
     `https://lab53-cms-oauth.<your-subdomain>.workers.dev/callback`
3. Click **Register application**.
4. Copy the **Client ID** shown on the app's page.
5. Click **Generate a new client secret** and copy that too — GitHub only
   shows it once.

## Step 3 — Give the doorman those credentials

Back in Terminal, still in the `oauth-worker` folder:
```
npx wrangler secret put OAUTH_CLIENT_ID
```
(paste the Client ID from Step 2 when prompted, press Enter)
```
npx wrangler secret put OAUTH_CLIENT_SECRET
```
(paste the Client Secret, press Enter)

## Step 4 — Point the dashboard at the doorman

Open `Project LAB53/projectlab53-repo/admin/config.yml` and find this line:
```yaml
  base_url: https://REPLACE-WITH-YOUR-WORKER.workers.dev
```
Replace it with your actual Worker URL from Step 1 (no `/callback` here,
just the base address), e.g.:
```yaml
  base_url: https://lab53-cms-oauth.your-subdomain.workers.dev
```
Save the file.

## Step 5 — Switch GitHub Pages to build with Actions

1. Go to your repo on GitHub → **Settings** → **Pages**.
2. Under **Build and deployment** → **Source**, change it from
   *"Deploy from a branch"* to **"GitHub Actions"**.

(Your custom domain / `projectlab53.com` setting doesn't need to change —
the `CNAME` file stays in the repo and the new workflow carries it along.)

## Step 6 — Push everything

```
cd "Project LAB53/projectlab53-repo"
git add -A
git commit -m "Set up the /admin journal dashboard"
git push
```

Watch the **Actions** tab on GitHub — you'll see "Build and deploy LAB53
site" run. When it turns green, the dashboard is live.

## Step 7 — Log in and try it

1. Visit `https://projectlab53.com/admin/`.
2. Click **Login with GitHub**, authorize the app (first time only).
3. You'll see all 13 existing posts, editable. Click **New Journal Posts**
   to write one from scratch — fill in the fields, drop in images, hit
   **Publish**. Give it a minute or two for the Actions rebuild, then check
   the live site.

## Notes for later

- **Editing an old post**: click it in the list, change anything, Publish —
  same rebuild-and-go flow.
- **Editorial guidelines**: the Category field is a fixed dropdown
  (Exhibitions / Interview / Essay) so the color-coding never breaks, and
  the Body field's hint text reminds whoever's writing about this site's
  caption/quote/question conventions. It's field-level guardrails, not a
  style checker — it won't catch tone or voice issues, just keeps the
  structure consistent.
- **Adding another editor**: add them as a collaborator on the GitHub repo
  (Settings → Collaborators) — they log in with their own GitHub account,
  no shared password to hand out.
- **If something breaks**: the dashboard only ever *commits to GitHub* —
  it never touches anything directly. Worst case, revert the bad commit
  with `git revert` and push, same as any other mistake.
