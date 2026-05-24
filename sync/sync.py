import os
import logging
from datetime import date

import requests
from instagrapi import Client as InstaClient
from linkedin_api import Linkedin

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)
log = logging.getLogger(__name__)

NOTION_TOKEN = os.environ["NOTION_TOKEN"]
NOTION_DATABASE_ID = os.environ["NOTION_DATABASE_ID"]
INSTAGRAM_USERNAME = os.environ["INSTAGRAM_USERNAME"]
INSTAGRAM_PASSWORD = os.environ["INSTAGRAM_PASSWORD"]
LINKEDIN_USERNAME = os.environ["LINKEDIN_USERNAME"]
LINKEDIN_PASSWORD = os.environ["LINKEDIN_PASSWORD"]

NOTION_HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}


# ---------- Notion helpers ----------

def get_existing_urls():
    """Return the set of URLs already in the Notion database."""
    endpoint = f"https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}/query"
    existing = set()
    cursor = None

    while True:
        body = {"page_size": 100}
        if cursor:
            body["start_cursor"] = cursor
        resp = requests.post(endpoint, headers=NOTION_HEADERS, json=body)
        resp.raise_for_status()
        data = resp.json()

        for page in data.get("results", []):
            url_val = page.get("properties", {}).get("URL", {}).get("url")
            if url_val:
                existing.add(url_val)

        if not data.get("has_more"):
            break
        cursor = data.get("next_cursor")

    log.info(f"Notion: {len(existing)} existing URLs")
    return existing


def save_to_notion(item):
    """Create a new row in the Notion database for a saved item."""
    title = (item.get("title") or "").strip()[:200] or item["url"]
    body = {
        "parent": {"database_id": NOTION_DATABASE_ID},
        "properties": {
            "Title": {"title": [{"text": {"content": title}}]},
            "URL": {"url": item["url"]},
            "Source": {"select": {"name": item["source"]}},
            "Status": {"select": {"name": "Unread"}},
            "Date Saved": {"date": {"start": date.today().isoformat()}},
        },
    }
    resp = requests.post(
        "https://api.notion.com/v1/pages", headers=NOTION_HEADERS, json=body
    )
    resp.raise_for_status()


# ---------- Instagram ----------

def get_instagram_saves():
    log.info("Instagram: fetching saved posts...")
    cl = InstaClient()

    # Reuse a saved session to avoid triggering Instagram's security checks.
    # INSTAGRAM_SESSION is a JSON string exported with cl.get_settings().
    session_json = os.environ.get("INSTAGRAM_SESSION", "")
    session_file = "/tmp/ig_session.json"

    if session_json:
        with open(session_file, "w") as f:
            f.write(session_json)
        try:
            cl.load_settings(session_file)
            cl.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
            log.info("Instagram: logged in via saved session")
        except Exception as e:
            log.warning(f"Instagram: session reload failed ({e}), retrying fresh login")
            cl = InstaClient()
            cl.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
    else:
        cl.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
        log.info("Instagram: logged in fresh (no saved session)")

    saved = cl.user_saved_medias()
    log.info(f"Instagram: {len(saved)} saved posts found")

    results = []
    for media in saved:
        caption = (media.caption_text or "").replace("\n", " ")
        results.append({
            "url": f"https://www.instagram.com/p/{media.code}/",
            "title": caption[:150],
            "source": "Instagram",
        })
    return results


# ---------- LinkedIn ----------

def get_linkedin_saves():
    log.info("LinkedIn: fetching saved posts...")
    api = Linkedin(LINKEDIN_USERNAME, LINKEDIN_PASSWORD)

    try:
        # LinkedIn Voyager internal endpoint for saved items
        response = api._fetch(
            "/identity/dash/lists",
            params={
                "count": 100,
                "listType": "SAVE",
                "q": "savedItems",
            },
        )

        elements = response.get("elements", [])
        log.info(f"LinkedIn: {len(elements)} saved items found")

        # Log the raw shape of the first element so we can debug if needed
        if elements:
            log.info(f"LinkedIn: first element keys = {list(elements[0].keys())}")

        results = []
        for el in elements:
            # LinkedIn's response shape can vary; try several known field paths
            url = (
                el.get("entityUrl")
                or el.get("navigationUrl")
                or (el.get("savedContent") or {}).get("canonicalUrl")
                or ""
            )
            title_field = el.get("title", "")
            title = (
                title_field.get("text", "") if isinstance(title_field, dict)
                else str(title_field)
            )
            if url:
                results.append({
                    "url": url,
                    "title": title[:150],
                    "source": "LinkedIn",
                })
            else:
                log.warning(f"LinkedIn: could not extract URL from element: {el}")

        return results

    except Exception as e:
        log.error(f"LinkedIn: fetch failed — {e}")
        return []


# ---------- Main ----------

def main():
    existing_urls = get_existing_urls()

    all_saves = []

    try:
        all_saves += get_instagram_saves()
    except Exception as e:
        log.error(f"Instagram sync failed: {e}")

    try:
        all_saves += get_linkedin_saves()
    except Exception as e:
        log.error(f"LinkedIn sync failed: {e}")

    new_items = [item for item in all_saves if item["url"] not in existing_urls]
    log.info(f"Sync: {len(new_items)} new items (out of {len(all_saves)} total fetched)")

    synced = 0
    for item in new_items:
        try:
            save_to_notion(item)
            log.info(f"  + {item['source']}: {item['url']}")
            synced += 1
        except Exception as e:
            log.error(f"  ! Failed to save {item['url']}: {e}")

    log.info(f"Sync complete: {synced} new items added to Notion")


if __name__ == "__main__":
    main()
