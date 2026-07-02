import asyncio
import json
from playwright.async_api import async_playwright
from pathlib import Path
from datetime import datetime, timezone
import glob
import re
import sys
import logging

logging.basicConfig(
    level=logging.INFO,          # <-- sem isto, INFO fica escondido por defeito (default é WARNING)
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)
# Configuração
ITEMS_PER_FILE = 1000
BATCH_SIZE = 100
HEADLESS = True  # Muda para False para ver os browsers
DOCUMENTS_DIR = Path("documents")

CURRENT_YEAR = datetime.now().year

# Years to scrape (one browser per year)
YEARS_TO_SCRAPE = [CURRENT_YEAR, CURRENT_YEAR-1, CURRENT_YEAR-2, CURRENT_YEAR-3, CURRENT_YEAR-4, CURRENT_YEAR-5]  # Periodo de 5 anos + o atual
#YEARS_TO_SCRAPE = [CURRENT_YEAR-5]
# Global variables
current_file_index = 1
items_in_current_file = 0
file_lock = asyncio.Lock()

def get_data_filename(index):
    return str(DOCUMENTS_DIR / "repo_cientifico" / f"repo_cientifico_{index}.json")

def get_current_file_index():
    existing_files = glob.glob(str(DOCUMENTS_DIR / "repo_cientifico" / "repo_cientifico_*.json"))
    if not existing_files:
        return 1
    indices = []
    for file in existing_files:
        try:
            idx = int(file.replace("repo_cientifico_", "").replace(".json", ""))
            indices.append(idx)
        except:
            pass
    return max(indices) if indices else 1

def load_all_existing_data():
    """Load all existing data from all files"""
    done_links = set()
    total_count = 0

    existing_files = glob.glob(str(DOCUMENTS_DIR / "repo_cientifico" / "repo_cientifico_*.json"))
    for file in existing_files:
        try:
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    done_links.update(data.keys())
                    total_count += len(data)
        except:
            pass

    return done_links, total_count

async def save_to_rotating_file(data_batch):
    """Save items to rotating files (1000 items per file)"""
    global current_file_index, items_in_current_file

    async with file_lock:
        remaining_items = dict(data_batch)

        while remaining_items:
            current_filename = get_data_filename(current_file_index)

            try:
                with open(current_filename, "r", encoding="utf-8") as f:
                    current_data = json.load(f)
            except:
                current_data = {}

            items_in_current_file = len(current_data)
            space_available = ITEMS_PER_FILE - items_in_current_file

            if space_available <= 0:
                current_file_index += 1
                print(f"Rotating to {get_data_filename(current_file_index)}")
                continue

            items_to_add = dict(list(remaining_items.items())[:space_available])
            current_data.update(items_to_add)

            with open(current_filename, "w", encoding="utf-8") as f:
                json.dump(current_data, f, ensure_ascii=False, indent=2)

            print(f"Saved to {current_filename} ({len(current_data)} items)")

            for key in items_to_add:
                del remaining_items[key]

            if len(current_data) >= ITEMS_PER_FILE:
                current_file_index += 1
                print(f"  File full → Rotating to {get_data_filename(current_file_index)}")

def extract_year_from_date(date_str):
    """Extract year from date string"""
    if not date_str or not isinstance(date_str, (str, int, float)):
        return None
    year_match = re.search(r'\b(19|20)\d{2}\b', str(date_str))
    if not year_match:
        return None
    try:
        return int(year_match.group())
    except ValueError:
        return None

EXTRACT_ITEM_JS = """el => {
    const getText = (selector) => {
        const elem = el.querySelector(selector);
        return elem ? elem.textContent.trim() : "";
    };

    const titleElem = el.querySelector('a');
    if (!titleElem) return null;

    const titleText = titleElem.textContent.trim();
    const titleMatch = titleText.match(/^(.*?)(?:19|20)\\d{2}\\s*$/);
    const title = titleMatch ? titleMatch[1].trim() : titleText;

    const href = titleElem.getAttribute('href');
    const link = href ? (href.startsWith('/') ? 'https://repositorio.ipl.pt' + href : href) : null;
    if (!link) return null;

    const tagElements = el.querySelectorAll('.tag_elements a');
    const dataPublicacao = tagElements[0]?.textContent.trim() || "";
    const tipo = tagElements[1]?.textContent.trim() || "";

    return {
        titulo: title,
        autores: getText('.clamp-default-2 .item-list-authors'),
        texto: getText('.clamp-default-3 .content span'),
        dataPublicacao: dataPublicacao,
        tipo: tipo,
        acesso: getText('.access-status-list-element-badge a'),
        link: link
    };
}"""

async def extract_item_data(element):
    """Extract item data from HTML element using evaluate for efficiency"""
    try:
        # Use evaluate to extract all data at once from the element
        data = await element.evaluate(EXTRACT_ITEM_JS);

        if not data or not data.get('link'):
            return None, None
        
        link = data.pop('link')
        data['dateChecked'] = datetime.now(timezone.utc).isoformat()
        return link, data
    
    except Exception as e:
        log.warning("Failed to extract item data: %s", e)
        return None, None

# ---------------------------------------------------------------------------
# STEP 1 — Navegar para a página base
# ---------------------------------------------------------------------------

async def access_base_url(page, base_url):
    """Access the base URL and handle potential errors"""
    log.info("[1/14] Navigating to %s...", base_url)
    try:
        await page.goto(base_url, wait_until='networkidle', timeout=15000)
        await page.wait_for_timeout(1000)
        return True
    except Exception as e:
        log.error("Failed to load base URL %s: %s", base_url, e)
        return False

# ---------------------------------------------------------------------------
# STEPS 2-3 — Botão "Carregar mais"
# ---------------------------------------------------------------------------

async def click_and_load_more_button(page):
    """Find and click 'Carregar mais' button. Returns True on success."""
    log.info("[2/14] Looking for 'Carregar mais' button...")
    try:
        # Use locator which is more reliable than query_selector
        load_more_locator = page.locator('button:has-text("Carregar mais")')
        count = await load_more_locator.count()

        if count == 0:
            # Try English label if Portuguese one not found
            load_more_locator = page.locator('input[aria-label="Load more"]')
            count = await load_more_locator.count()

        if count == 0:
            log.info("'Carregar mais' button not found on initial load")
            return False

        # STEP 3: Click "Carregar mais" button
        log.info("[3/14] Clicking 'Carregar mais' button...")
        await load_more_locator.first.wait_for(state='visible', timeout=5000)
        await load_more_locator.first.scroll_into_view_if_needed()
        await page.wait_for_timeout(300)
        await load_more_locator.first.click()
        return True
    except Exception as e:
        log.error("Error with 'Carregar mais' button: %s", e)
        return False

# ---------------------------------------------------------------------------
# STEPS 5-6 — Localizar e expandir o filtro de data
# ---------------------------------------------------------------------------

async def find_and_expand_date_filter(page):
    """Find the date facet-filter and click its toggle to expand.
    Returns the filter element handle, or None if not found / failed.
    """
    log.info("[5/14] Looking for facet-filter with date range...")
    all_filters = await page.query_selector_all(".facet-filter")
    log.info("Found %d facet-filter elements", len(all_filters))
    for i, filt in enumerate(all_filters):
        filter_text = await filt.text_content()
        if "Data" in filter_text or "Date" in filter_text:
            log.info("[6/14] Found date filter at index %d, clicking toggle to expand...", i)
            try:
                toggle_btn = await filt.query_selector("button.filter-name")
                if not toggle_btn:
                    log.warning("Toggle button not found")
                    return None
 
                await toggle_btn.scroll_into_view_if_needed()
                await page.wait_for_timeout(500)
                await toggle_btn.click()
                await page.wait_for_timeout(1500)
                return filt
 
            except Exception as e:
                log.error("Error clicking toggle: %s", e)
                return None
 
    log.warning("Date filter not found")
    return None

# ---------------------------------------------------------------------------
# STEPS 7-8 e 9-10 — Preencher data mínima / máxima
# ---------------------------------------------------------------------------
async def fill_date_field(page, year_str, aria_labels, step_label):
    """
    Generic helper for STEPS 7 and 9: locate an input by one of several
    possible aria-label values (PT/EN fallback), clear it, fill the year,
    and press Enter. aria_labels is a list of possible aria-labels to try.
    step_label is a string for logging (e.g., "[7/14]").
    Returns True on success, False on failure.
    """
    log.info("%s Writing '%s' to field...", step_label, year_str)
    try:
        locator = None
        count = 0
        for label in aria_labels:
            locator = page.locator(f'input[aria-label="{label}"]')
            count = await locator.count()
            if count > 0:
                break
 
        if count == 0:
            log.warning("Input field not found for labels %s", aria_labels)
            return False
 
        await locator.first.clear()
        await page.wait_for_timeout(300)
        await locator.first.fill(year_str)
        await page.wait_for_timeout(500)
        await locator.first.press("Enter")
        return True
 
    except Exception as e:
        log.error("Error filling field (%s): %s", aria_labels, e)
        return False

async def fill_min_date(page, year_str):
    """Write year to 'Data mínima' field."""
    return await fill_date_field(
        page, year_str,
        aria_labels=["Data mínima", "Minimum Date"],
        step_label="[7/14]",
    )
 
async def fill_max_date(page, year_str):
    """Write year to 'Data máxima' field."""
    return await fill_date_field(
        page, year_str,
        aria_labels=["Data máxima", "Maximum Date"],
        step_label="[9/14]",
    )

# ---------------------------------------------------------------------------
# STEP 11 — Extrair itens da página actual
# ---------------------------------------------------------------------------

async def scrape_items_from_page(page, year, done_links, batch, items_skipped, page_count, force_full):
    """
    Scrape items from the current page into `batch` (mutated in place).
    Returns (found_in_page, updated_items_skipped, reached_duplicate).
    """
    log.info("[11/14] (%s) Scraping items from page %d...", year, page_count)
    items = await page.query_selector_all(".mt-4.mb-4.d-flex")
    log.info("Found %d items on page %d", len(items), page_count)
    max_items_can_skip = 3  # Limit logging for skipped items
 
    found_in_page = 0
    reached_duplicate = False
 
    for element in items:
        link, data = await extract_item_data(element)
        if not link or not data:
            continue
 
        item_year = extract_year_from_date(data.get("dataPublicacao", ""))
        if item_year and item_year != year:
            items_skipped += 1
            if items_skipped <= max_items_can_skip:
                log.debug(
                    "Skipped item - Title: %s, Date: %r, Year: %s",
                    data.get("titulo", "N/A")[:40], data.get("dataPublicacao", ""), item_year,
                )
            continue
 
        if not force_full and link in done_links:
            log.info("Found duplicate: %s", data.get("titulo", "N/A")[:50])
            reached_duplicate = True
            break
 
        if link not in batch:
            batch[link] = data
            found_in_page += 1
 
    log.info("New items from page %d: %d", page_count, found_in_page)
    return found_in_page, items_skipped, reached_duplicate

# ---------------------------------------------------------------------------
# STEPS 12-13-14 — Paginação
# ---------------------------------------------------------------------------

async def go_next_page(page):
    """
    Find, validate and click the '»' next-page button.
    Returns True if navigation happened, False if there is no next page
    or an error occurred.
    """
    log.info("[12/14] Looking for next '»' button...")
    try:
        next_btn_locator = page.locator('.page-link:has-text("»")')
 
        if await next_btn_locator.count() == 0:
            log.info("No more pages - '»' button not found")
            return False
 
        is_disabled = await next_btn_locator.first.get_attribute("aria-disabled") == "true"
        if is_disabled:
            log.info("No more pages - '»' button is disabled")
            return False
 
        log.info("[13/14] Clicking '»' button...")
        await next_btn_locator.first.wait_for(state="visible", timeout=5000)
        await next_btn_locator.first.scroll_into_view_if_needed()
        await page.wait_for_timeout(500)
        await next_btn_locator.first.click()
 
        log.info("[14/14] Waiting for page reload...")
        await page.wait_for_timeout(4000)
        return True
 
    except Exception as e:
        log.error("Error with pagination: %s", e)
        return False


async def scrape_collection_by_year(page, year, done_links, force_full=False):
    """Scrape publications for a specific year - orchestrates the  14-STEP FLOW"""

    log.info("[YEAR %s] Starting scrape for year %s", year, year)
    base_url = "https://repositorio.ipl.pt"

    if not await access_base_url(page, base_url):
        return 0
    if not await click_and_load_more_button(page):
        return 0
    log.info("[4/14] Waiting for page reload...")
    await page.wait_for_timeout(3000)

    filter_region = await find_and_expand_date_filter(page)
    if not filter_region:
        return 0

    year_str = str(year)
    if not await fill_min_date(page, year_str):
        return 0
    log.info("[8/14] Waiting for page reload...")
    await page.wait_for_timeout(3000)
    if not await fill_max_date(page, year_str):
        return 0
    log.info("[10/14] Waiting for page reload...")
    await page.wait_for_timeout(3000)
 
    batch = {}
    items_found = 0
    items_skipped = 0
    page_count = 1

    while True:
        found_in_page, items_skipped, reached_duplicate = await scrape_items_from_page(
            page, year, done_links, batch, items_skipped, page_count, force_full
        )
        items_found += found_in_page
        if found_in_page == 0:
            log.info("No new items on page %d → Already scraped previously, stopping", page_count)
            break
        if len(batch) >= BATCH_SIZE:
            await save_to_rotating_file(batch)
            done_links.update(batch.keys())
            batch = {}
        if reached_duplicate:
            log.info("Year %s complete (duplicates found)", year)
            break
        if not await go_next_page(page):
            break
 
        page_count += 1
 
    if batch:
        await save_to_rotating_file(batch)
        done_links.update(batch.keys())
 
    log.info("[YEAR %s] Complete: %d items found, %d skipped", year, items_found, items_skipped)
    return items_found


async def scrape_with_year_filter(year, done_links, force_full=False):
    """Scrape a single year using a Playwright browser"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=HEADLESS,
            args=['--disable-blink-features=AutomationControlled']
        )
        page = await browser.new_page(
            viewport={'width': 1280, 'height': 720}
        )

        try:
            items = await scrape_collection_by_year(page, year, done_links, force_full=force_full)
            return items
        except Exception as e:
            log.error("Error scraping year %s: %s", year, e)
            return 0
        finally:
            await browser.close()

async def main():
    global current_file_index

    DOCUMENTS_DIR.mkdir(exist_ok=True)

    force_full = len(sys.argv) > 1 and sys.argv[1].strip().lower() == "true"

    # Delete all existing repo_cientifico_*.json files if force_full is enabled
    if force_full:
        existing_files = glob.glob(str(DOCUMENTS_DIR / "repo_cientifico" / "repo_cientifico_*.json"))
        if existing_files:
            print("Force mode: Deleting existing repo files...")
            for file in existing_files:
                try:
                    import os
                    os.remove(file)
                    print(f"  Deleted: {file}")
                except Exception as e:
                    print(f"  Failed to delete {file}: {e}")
        current_file_index = 1
        print("Reset file index to 1\n")
    else:
        current_file_index = get_current_file_index()

    print(f"\n{'='*100}")
    print(f"PLAYWRIGHT SCRAPER - Scraping All Publications by Year")
    print(f"{'='*100}\n")

    # Load existing data
    done_links, total_existing = load_all_existing_data()
    print(f"Existing data: {total_existing} items in {len(glob.glob(f'{DOCUMENTS_DIR}/repo_cientifico/repo_cientifico_*.json'))} files")
    print(f"Next file: {get_data_filename(current_file_index)}")
    print(f"Already scraped links: {len(done_links)}\n")

    print(f"Years to scrape: {YEARS_TO_SCRAPE}")
    if force_full:
        print("Force mode enabled: full scrape from scratch (ignoring existing items)")
    print(f"{'='*100}\n")

    # Run all years in parallel
    print(f"Starting {len(YEARS_TO_SCRAPE)} browsers in parallel...\n")

    tasks = [
        scrape_with_year_filter(year, done_links, force_full=force_full)
        for year in YEARS_TO_SCRAPE
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Print results
    print(f"\n{'='*100}\n")
    total_items_scraped = 0
    for year, result in zip(YEARS_TO_SCRAPE, results):
        if isinstance(result, int):
            total_items_scraped += result
            print(f"Year {year}: {result} items")
        else:
            print(f"Year {year}: Error - {result}")

    # Final info
    all_files = glob.glob(f'{DOCUMENTS_DIR}/repo_cientifico/repo_cientifico_*.json')
    total_items = 0
    for file in all_files:
        try:
            with open(file, "r", encoding="utf-8") as f:
                total_items += len(json.load(f))
        except:
            pass

    print(f"\n{'='*100}")
    print(f"SCRAPE COMPLETE!")
    print(f"Files: {len(all_files)}")
    print(f"Total items: {total_items}")
    print(f"Items in this run: {total_items_scraped}")
    print(f"{'='*100}\n")

if __name__ == "__main__":
    asyncio.run(main())