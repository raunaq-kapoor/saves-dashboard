# Test Plan — Saves Dashboard

## Setup Verification

- [ ] **T1** — Open Notion on any device and confirm "Saved Items" database exists with all columns visible
- [ ] **T2** — Confirm "Unread Queue" view shows only Status = Unread items (empty at start)
- [ ] **T3** — Confirm shortcut appears in iOS share sheet (Safari → Share → scroll to find "Save to Reads")

## Core Save Flow

- [ ] **T4** — Open Instagram, find any post, tap Share → "Save to Reads" → select "Instagram" → confirm notification appears
- [ ] **T5** — Open Notion → verify new row appeared with correct URL and Source = Instagram, Status = Unread, Date = today
- [ ] **T6** — Open LinkedIn, find any post, tap Share → "Save to Reads" → select "LinkedIn" → verify in Notion
- [ ] **T7** — Share a URL from Safari (any article) → select "Other" → verify in Notion
- [ ] **T8** — Share plain text (not a URL) — shortcut should either extract a URL or handle gracefully without crashing

## Field Accuracy

- [ ] **T9** — Verify Source field matches what was selected (Instagram / LinkedIn / Other)
- [ ] **T10** — Verify Date Saved is today's date
- [ ] **T11** — Verify Status defaults to "Unread" for every new save

## Notion Views

- [ ] **T12** — Save 3 items → confirm all 3 appear in "All Items" view, newest first
- [ ] **T13** — Manually change one item's Status to "Read" → confirm it disappears from "Unread Queue" but stays in "All Items"
- [ ] **T14** — Filter "All Items" by Source = Instagram → confirm only Instagram saves show

## Edge Cases

- [ ] **T15** — Share an Instagram Story link (often expires) — shortcut should save it without error
- [ ] **T16** — Save 5 items rapidly in a row — confirm all 5 appear in Notion
- [ ] **T17** — Enter a wrong Notion token → try saving → shortcut should show a failure notification rather than silently failing

## Browsing / Usability

- [ ] **T18** — On a fresh day, open Notion → "Unread Queue" → confirm you can see all pending saves at a glance
- [ ] **T19** — Click a URL in Notion → confirm it opens the original post or article
