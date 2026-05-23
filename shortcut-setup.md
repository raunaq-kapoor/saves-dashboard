# iOS Shortcut Setup — "Save to Reads"

This shortcut appears in the iOS Share Sheet. Tap Share from any app, select "Save to Reads", choose a source, and the URL is saved to your Notion database.

## Prerequisites

- Notion integration token (`secret_...`) from [notion.so/profile/integrations](https://notion.so/profile/integrations)
- Notion database connected to the integration (see README)

## Steps

Open the **Shortcuts** app on your iPhone → tap **+** → name it `Save to Reads`.

---

### Action 1 — Receive input from Share Sheet

- Search: `Receive`
- Action: **Receive input from Share Sheet**
- Set "Receive" to: **URLs** and **Text**
- Toggle "If there's no input" → **Continue**

---

### Action 2 — Get URLs from input

- Search: `Get URLs`
- Action: **Get URLs from Input**
- Input: **Shortcut Input**
- Store result → tap result → **Add to Variable** → name: `shared_url`

---

### Action 3 — Choose source

- Search: `Choose from list`
- Action: **Choose from List**
- Items: `Instagram`, `LinkedIn`, `Other`
- Store result → **Add to Variable** → name: `source`

---

### Action 4 — Format today's date

- Search: `Format Date`
- Action: **Format Date**
- Date: **Current Date**
- Format: **Custom** → type exactly: `yyyy-MM-dd`
- Store result → **Add to Variable** → name: `today`

---

### Action 5 — Build the JSON body

- Search: `Text`
- Action: **Text**
- Paste the content below, then tap each `[variable]` placeholder and replace it with the matching variable using the `{x}` variable picker:

```
{"parent":{"database_id":"02472aac408340a4b581784f014fdd05"},"properties":{"URL":{"url":"[shared_url]"},"Source":{"select":{"name":"[source]"}},"Status":{"select":{"name":"Unread"}},"Date Saved":{"date":{"start":"[today]"}}}}
```

The final text should have orange variable pills for `shared_url`, `source`, and `today` inside the JSON string.

- Store result → **Add to Variable** → name: `json_body`

---

### Action 6 — Send to Notion

- Search: `Get Contents of URL`
- Action: **Get Contents of URL**
- URL: `https://api.notion.com/v1/pages`
- Tap **Show More**:
  - Method: **POST**
  - Headers — add three entries:
    - `Authorization` → `Bearer secret_XXXX` ← paste your token
    - `Notion-Version` → `2022-06-28`
    - `Content-Type` → `application/json`
  - Request Body: **File**
  - File: select Variable → `json_body`

---

### Action 7 — Confirm notification

- Search: `Show Notification`
- Action: **Show Notification**
- Title: `Saved to Notion`
- Body: insert Variable → `source`

---

## Add to Share Sheet

In the Shortcuts app, open the shortcut → tap the **Info (i)** button → enable **"Show in Share Sheet"**.

---

## Rebuilding the shortcut

If you ever lose the shortcut or get a new phone, just follow these steps again. The Notion database and integration token are the only things you need to preserve — the token lives in your Notion integration settings.
