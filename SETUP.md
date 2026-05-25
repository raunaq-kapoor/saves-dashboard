# Setup Guide

Complete instructions for setting up and maintaining the Saves Dashboard.
Refer back here whenever credentials expire and need refreshing.

---

## How it works

A GitHub Actions workflow runs daily at 8am UTC. It uses browser cookies
(copied from your logged-in browser) to fetch your saved posts from Instagram
and LinkedIn without triggering security challenges, then syncs new items to
your Notion database.

---

## One-time setup

### 1. Notion integration

1. Go to **notion.so/profile/integrations**
2. Click **+ New integration** → name it `Save to Reads` → Save
3. Copy the **Internal Integration Secret** (starts with `secret_...`)
4. Open the **Saved Items** Notion database → `...` menu (top right) → **Connections** → **Connect to** → select **Save to Reads**

### 2. GitHub secrets

Go to **github.com/raunaq-kapoor/saves-dashboard/settings/secrets/actions**
and add each secret below.

| Secret | How to get it |
|--------|--------------|
| `NOTION_TOKEN` | The `secret_...` token from Step 1 |
| `NOTION_DATABASE_ID` | `02472aac408340a4b581784f014fdd05` (fixed, never changes) |
| `INSTAGRAM_SESSIONID` | See Section A below |
| `LINKEDIN_LI_AT` | See Section B below |
| `LINKEDIN_JSESSIONID` | See Section B below |

---

## Section A — Getting the Instagram session cookie

Instagram's `sessionid` cookie lets the script log in without a password
or verification code. It typically lasts 90 days.

**Steps (Chrome):**
1. Open **instagram.com** in Chrome and make sure you are logged in
2. Press `Cmd+Option+I` to open DevTools
3. Click the **Application** tab
4. In the left sidebar: **Cookies** → **https://www.instagram.com**
5. Find the row named **`sessionid`**
6. Copy the entire **Value** column for that row
7. Paste it as the `INSTAGRAM_SESSIONID` GitHub secret

**Steps (Safari):**
1. Open **instagram.com** in Safari and make sure you are logged in
2. Enable the Develop menu: Safari → Settings → Advanced → tick "Show features for web developers"
3. Develop menu → Show Web Inspector → **Storage** tab → **Cookies** → **instagram.com**
4. Find **`sessionid`** → copy its value
5. Paste it as the `INSTAGRAM_SESSIONID` GitHub secret

**When to refresh:** If the sync logs show `LoginRequired` or `sessionid invalid`,
the cookie has expired. Repeat the steps above to get a fresh one.

---

## Section B — Getting LinkedIn browser cookies

LinkedIn uses two cookies together. They typically last 1–2 years.

**Steps (Chrome):**
1. Open **linkedin.com** in Chrome and make sure you are logged in
2. Press `Cmd+Option+I` → **Application** tab → **Cookies** → **https://www.linkedin.com**
3. Find **`li_at`** → copy its Value → paste as `LINKEDIN_LI_AT` secret
4. Find **`JSESSIONID`** → copy its Value (it looks like `ajax:1234567890123456789`) → paste as `LINKEDIN_JSESSIONID` secret

**Steps (Safari):**
1. Open **linkedin.com** in Safari and make sure you are logged in
2. Web Inspector → **Storage** tab → **Cookies** → **linkedin.com**
3. Find `li_at` and `JSESSIONID` → copy and save as above

**When to refresh:** If the sync logs show `CHALLENGE` or `403`, the cookies
have expired. Repeat the steps above.

---

## Triggering a sync run

**Automatic:** Runs every day at 8am UTC (no action needed).

**Manual (to test or force a sync):**
1. Go to **github.com/raunaq-kapoor/saves-dashboard/actions**
2. Click **Daily Saves Sync** in the left sidebar
3. Click **Run workflow** → **Run workflow**

---

## Reading the logs

After a run, click the run in the Actions tab → click the **sync** job → expand **Run sync**.

What healthy output looks like:
```
Notion: 12 existing URLs
Instagram: fetching saved posts...
Instagram: logged in via session cookie
Instagram: 27 saved posts found
LinkedIn: fetching saved posts...
LinkedIn: 8 saved items found
Sync: 4 new items (out of 35 total fetched)
  + Instagram: https://www.instagram.com/p/XXXXX/
  + LinkedIn: https://www.linkedin.com/...
Sync complete: 4 new items added to Notion
```

Common errors and fixes:

| Error in logs | Fix |
|---------------|-----|
| `LoginRequired` or `sessionid invalid` | Refresh `INSTAGRAM_SESSIONID` (Section A) |
| `CHALLENGE` or `403` on LinkedIn | Refresh `LINKEDIN_LI_AT` and `LINKEDIN_JSESSIONID` (Section B) |
| `Notion: 401` | Refresh `NOTION_TOKEN` (Section 1 above) |
| `0 saved posts found` on Instagram | Session cookie may be expired even without an error — refresh it |

---

## Notion database reference

- **URL:** https://www.notion.so/02472aac408340a4b581784f014fdd05
- **Unread Queue view:** filtered to Status = Unread, sorted newest first
- **All Items view:** everything, sorted newest first

To mark something as read: open the Notion database → change **Status** from `Unread` to `Read`.

---

## Credential expiry schedule

| Credential | Typical lifespan | Secret name |
|------------|-----------------|-------------|
| Instagram sessionid | ~90 days | `INSTAGRAM_SESSIONID` |
| LinkedIn li_at | 1–2 years | `LINKEDIN_LI_AT` |
| LinkedIn JSESSIONID | 1–2 years | `LINKEDIN_JSESSIONID` |
| Notion integration token | Never expires | `NOTION_TOKEN` |
