# Saves Dashboard

A lightweight system to save posts from Instagram and LinkedIn to a central Notion database via an iOS Share Sheet shortcut.

## How it works

```
Instagram / LinkedIn (or any app)
         |  tap Share -> "Save to Reads"
    iOS Shortcut
         |  HTTP POST to Notion API
    Notion Database  <-- browse here
```

## Notion Database

- **URL:** https://www.notion.so/02472aac408340a4b581784f014fdd05
- **Database ID:** `02472aac408340a4b581784f014fdd05`
- **Data Source ID:** `7c59d3ba-0e7f-4622-ac64-6d5f461fe865`

### Schema

| Field | Type | Options |
|-------|------|---------|
| Title | Text | Free text — fill in after saving |
| URL | URL | The saved link |
| Source | Select | Instagram, LinkedIn, Other |
| Category | Select | AI/Tech, Local & Places, Food, Reading, Video, Other |
| Notes | Text | Optional context |
| Date Saved | Date | Set automatically by the shortcut |
| Status | Select | Unread, Read, Done |

### Views

| View | Purpose |
|------|---------|
| Unread Queue | All Status = Unread items, newest first — your daily reading list |
| All Items | Everything, newest first |

---

## Setup

### 1. Notion Integration

1. Go to [notion.so/profile/integrations](https://notion.so/profile/integrations)
2. Click **+ New integration** → name it `Save to Reads` → Save
3. Copy the **Internal Integration Secret** (`secret_...`)
4. Open the Saved Items database → `...` menu → **Connections** → **Connect to** → **Save to Reads**

### 2. iOS Shortcut

See [shortcut-setup.md](./shortcut-setup.md) for full step-by-step instructions.

---

## Future Upgrades

- **AI enrichment:** Add a Claude API call in the shortcut to auto-generate a summary and category (~$0.001/save, no monthly fee)
- **Quick note prompt:** Add an optional "add a note?" step before saving
- **Weekly digest:** Make.com free tier — weekly email of unread saves
