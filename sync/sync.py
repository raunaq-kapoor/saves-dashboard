import os
import logging
from datetime import date

import requests

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)
log = logging.getLogger(__name__)

NOTION_TOKEN = os.environ["NOTION_TOKEN"]
NOTION_DATABASE_ID = os.environ["NOTION_DATABASE_ID"]
INSTAGRAM_SESSION = os.environ["INSTAGRAM_SESSION"]       # sessionid cookie from instagram.com
INSTAGRAM_USERAGENT = os.environ.get("INSTAGRAM_USERAGENT", "")  # exact UA from your browser
LINKEDIN_LI_AT = os.environ["LINKEDIN_LI_AT"]            # li_at cookie from linkedin.com
LINKEDIN_JSESSIONID = os.environ["LINKEDIN_JSESSIONID"]  # JSESSIONID cookie from linkedin.com

NOTION_HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}


# ---------- Notion helpers ----------

def get_existing_urls():
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
        if not cursor:
            break

    log.info(f"Notion: {len(existing)} existing URLs")
    return existing


def save_to_notion(item):
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

    # Use instagram.com web API — works with the sessionid cookie from the browser.
    # This avoids the mobile API entirely (which rejects web cookies with 467).
    cookies = {"sessionid": INSTAGRAM_SESSION}
    ua = INSTAGRAM_USERAGENT or (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
    headers = {
        "User-Agent": ua,
        "Accept": "*/*",
        "Referer": "https://www.instagram.com/saved/",
        "X-Requested-With": "XMLHttpRequest",
    }

    # Preflight: verify the cookie is accepted before hitting the saved posts endpoint
    preflight = requests.get(
        "https://www.instagram.com/api/v1/accounts/current_user/?edit=true",
        headers=headers,
        cookies=cookies,
    )
    log.info(f"Instagram preflight status = {preflight.status_code}")
    if preflight.status_code == 200:
        log.info(f"Instagram preflight body preview = {preflight.text[:200]}")
    else:
        log.warning(f"Instagram preflight body preview = {preflight.text[:200]}")

    results = []
    next_max_id = None

    while True:
        params = {"count": 50}
        if next_max_id:
            params["max_id"] = next_max_id

        resp = requests.get(
            "https://www.instagram.com/api/v1/feed/saved/media/",
            params=params,
            headers=headers,
            cookies=cookies,
        )

        log.info(f"Instagram: status = {resp.status_code}")

        if resp.status_code == 401:
            raise RuntimeError(
                "Instagram: sessionid rejected — refresh INSTAGRAM_SESSION (see SETUP.md Section A)"
            )
        if resp.status_code != 200:
            raise RuntimeError(
                f"Instagram: unexpected status {resp.status_code}: {resp.text[:300]}"
            )

        data = resp.json()
        items = data.get("items", [])
        log.info(f"Instagram: got {len(items)} items in this page")

        for item in items:
            code = item.get("code") or item.get("shortcode")
            if not code:
                log.warning(f"Instagram: item {item.get('id')} has no shortcode, skipping")
                continue
            cap = item.get("caption")
            caption = cap.get("text", "") if isinstance(cap, dict) else ""
            results.append({
                "url": f"https://www.instagram.com/p/{code}/",
                "title": caption.replace("\n", " ")[:150],
                "source": "Instagram",
            })

        if not data.get("more_available") or not data.get("next_max_id"):
            break
        next_max_id = data["next_max_id"]

    log.info(f"Instagram: {len(results)} saved posts found total")
    return results


# ---------- LinkedIn ----------

def get_linkedin_saves():
    log.info("LinkedIn: fetching saved posts...")

    csrf = LINKEDIN_JSESSIONID.strip('"')
    cookies = {
        "li_at": LINKEDIN_LI_AT,
        "JSESSIONID": f'"{csrf}"',
    }
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "application/vnd.linkedin.normalized+json+2.1",
        "csrf-token": csrf,
        "x-restli-protocol-version": "2.0.0",
        "x-li-lang": "en_US",
        "Referer": "https://www.linkedin.com/feed/",
        "x-li-track": (
            '{"clientVersion":"1.13.1","mpVersion":"1.13.1","osName":"web",'
            '"timezoneOffset":0,"timezone":"UTC","appType":"VOYAGER",'
            '"displayDensity":2,"displayWidth":1920,"displayHeight":1080}'
        ),
    }

    # Preflight: verify auth works before hitting the saved posts endpoint
    preflight = requests.get(
        "https://www.linkedin.com/voyager/api/me",
        headers=headers,
        cookies=cookies,
    )
    log.info(f"LinkedIn preflight status = {preflight.status_code}")
    log.info(f"LinkedIn preflight body preview = {preflight.text[:200]}")

    # Try multiple known Voyager endpoints for saved posts
    candidate_endpoints = [
        (
            "https://www.linkedin.com/voyager/api/feed/saves",
            {"count": 100, "start": 0},
        ),
        (
            "https://www.linkedin.com/voyager/api/contentcollection/updatesV2",
            {"q": "savedItems", "count": 100, "start": 0},
        ),
    ]

    data = None
    for url_ep, params in candidate_endpoints:
        resp = requests.get(url_ep, params=params, headers=headers, cookies=cookies)
        log.info(f"LinkedIn endpoint {url_ep}: status = {resp.status_code}")
        if resp.status_code in (401, 403):
            raise RuntimeError(
                f"LinkedIn auth failure ({resp.status_code}) — "
                "refresh LINKEDIN_LI_AT and LINKEDIN_JSESSIONID (see SETUP.md Section B)"
            )
        if resp.status_code == 200:
            data = resp.json()
            log.info(f"LinkedIn: using endpoint {url_ep}")
            break
        log.warning(f"LinkedIn: {url_ep} → {resp.status_code}: {resp.text[:200]}")

    if data is None:
        raise RuntimeError("LinkedIn: no working saved-posts endpoint found — see logs above")

    elements = data.get("elements", [])
    log.info(f"LinkedIn: {len(elements)} saved items found")

    if elements:
        log.info(f"LinkedIn: first element keys = {list(elements[0].keys())}")

    results = []
    for el in elements:
        # Voyager wraps entities differently depending on the endpoint version
        inner = el.get("value") or el.get("savedContent") or el
        url = (
            el.get("entityUrl")
            or el.get("navigationUrl")
            or inner.get("entityUrl")
            or inner.get("navigationUrl")
            or inner.get("canonicalUrl")
            or ""
        )
        title_field = el.get("title") or inner.get("title") or ""
        title = (
            title_field.get("text", "") if isinstance(title_field, dict)
            else str(title_field)
        )
        if url:
            results.append({"url": url, "title": title[:150], "source": "LinkedIn"})
        else:
            log.warning(f"LinkedIn: no URL in element — keys: {list(el.keys())}")

    return results


# ---------- Main ----------

def main():
    try:
        existing_urls = get_existing_urls()
    except Exception as e:
        log.critical(f"Cannot fetch existing Notion URLs — aborting to avoid duplicates: {e}")
        raise SystemExit(1)

    all_saves = []
    instagram_ok = False
    linkedin_ok = False

    try:
        all_saves += get_instagram_saves()
        instagram_ok = True
    except Exception as e:
        log.error(f"Instagram sync failed: {e}")

    try:
        all_saves += get_linkedin_saves()
        linkedin_ok = True
    except Exception as e:
        log.error(f"LinkedIn sync failed: {e}")

    if not instagram_ok and not linkedin_ok:
        log.critical("Both sources failed — marking workflow as failed")
        raise SystemExit(1)

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
