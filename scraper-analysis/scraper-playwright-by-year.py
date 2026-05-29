import asyncio
import json
from playwright.async_api import async_playwright
from pathlib import Path
from datetime import datetime, timezone
import glob
import re
import sys

# Configuração
CONCURRENT_BROWSERS = 1
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
    return str(DOCUMENTS_DIR / f"repo_cientifico_{index}.json")

def get_current_file_index():
    existing_files = glob.glob(str(DOCUMENTS_DIR / "repo_cientifico_*.json"))
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

    existing_files = glob.glob(str(DOCUMENTS_DIR / "repo_cientifico_*.json"))
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
                print(f"  ↻ File full → Rotating to {get_data_filename(current_file_index)}")

def extract_year_from_date(date_str):
    """Extract year from date string"""
    if not date_str:
        return None
    
    year_match = re.search(r'\b(19|20)\d{2}\b', str(date_str))
    if year_match:
        try:
            return int(year_match.group())
        except:
            return None
    return None

async def extract_item_data(element):
    """Extract item data from HTML element using evaluate for efficiency"""
    try:
        # Use evaluate to extract all data at once from the element
        data = await element.evaluate("""el => {
            const titleElem = el.querySelector('a');
            if (!titleElem) return null;
            
            const titleText = titleElem.textContent.trim();
            const titleMatch = titleText.match(/^(.*?)\\d{4}/);
            const title = titleMatch ? titleMatch[1].trim() : titleText;
            
            const href = titleElem.getAttribute('href');
            const link = href ? (href.startsWith('/') ? 'https://repositorio.ipl.pt' + href : href) : null;
            
            if (!link) return null;
            
            const tagElements = el.querySelectorAll('.tag_elements a');
            const dataPublicacao = tagElements.length > 0 ? tagElements[0].textContent.trim() : "";
            const tipo = tagElements.length > 1 ? tagElements[1].textContent.trim() : "";
            
            const authorsElem = el.querySelector('.clamp-default-2 .item-list-authors');
            const autores = authorsElem ? authorsElem.textContent.trim() : "";
            
            const descElem = el.querySelector('.clamp-default-3 .content span');
            const texto = descElem ? descElem.textContent.trim() : "";
            
            const acessoElem = el.querySelector('.access-status-list-element-badge a');
            const acesso = acessoElem ? acessoElem.textContent.trim() : "";
            
            return {
                titulo: title,
                autores: autores,
                texto: texto,
                dataPublicacao: dataPublicacao,
                tipo: tipo,
                acesso: acesso,
                link: link
            };
        }""")

        if not data or not data.get('link'):
            return None, None
        
        link = data['link']
        data['dateChecked'] = datetime.now(timezone.utc).isoformat()
        del data['link']

        return link, data
    
    except Exception:
        return None, None

async def scrape_collection_by_year(page, year, done_links, force_full=False):
    """Scrape publications for a specific year - ORDERED 14 STEP FLOW"""
    print(f"\n  [YEAR {year}] Starting scrape for year {year}")
    
    # STEP 1: Access base URL
    base_url = "https://repositorio.ipl.pt"
    print(f"    [1/14] Navigating to {base_url}...")
    try:
        await page.goto(base_url, wait_until='networkidle', timeout=15000)
        await page.wait_for_timeout(1000)
    except Exception as e:
        print(f"     Failed to load page: {e}")
        return 0

    # STEP 2: Look for "Carregar mais" button
    print(f"    [2/14] Looking for 'Carregar mais' button...")
    try:
        # Use locator which is more reliable than query_selector
        load_more_locator = page.locator('button:has-text("Carregar mais")')
        count = await load_more_locator.count()

        if count == 0:
            print(f"     'Carregar mais' button not found on initial load")
            return 0

        # STEP 3: Click "Carregar mais" button
        print(f"    [3/14] Clicking 'Carregar mais' button...")
        await load_more_locator.first.wait_for(state='visible', timeout=5000)
        await load_more_locator.first.scroll_into_view_if_needed()
        await page.wait_for_timeout(300)
        await load_more_locator.first.click()
    except Exception as e:
        print(f"     Error with 'Carregar mais' button: {e}")
        return 0

    # STEP 4: Wait for page reload
    print(f"    [4/14] Waiting for page reload...")
    await page.wait_for_timeout(3000)

    # STEP 5: Look for facet-filter with date range
    print(f"    [5/14] Looking for facet-filter with date range...")
    all_filters = await page.query_selector_all('.facet-filter')
    print(f"    Found {len(all_filters)} facet-filter elements")
    
    # STEP 6: Find date filter and click toggle to expand
    filter_region = None
    for i, filt in enumerate(all_filters):
        filter_text = await filt.text_content()
        if "Data" in filter_text or "Date" in filter_text:
            filter_region = filt
            print(f"    [6/14] Found date filter at index {i}, clicking toggle to expand...")
            
            # Click the toggle button to expand the filter
            try:
                toggle_btn = await filter_region.query_selector('button.filter-name')
                if toggle_btn:
                    await toggle_btn.scroll_into_view_if_needed()
                    await page.wait_for_timeout(500)
                    await toggle_btn.click()
                    await page.wait_for_timeout(1500)  # Wait for fields to appear
                    break
                else:
                    print(f"     Toggle button not found")
                    return 0
            except Exception as e:
                print(f"     Error clicking toggle: {e}")
                return 0
    
    if not filter_region:
        print(f"     Date filter not found")
        return 0
    
    year_str = str(year)

    # STEP 7: Write year to first field (Data mínima)
    print(f"    [7/14] Writing '{year_str}' to first field (Data mínima)...")
    try:
        min_input_locator = page.locator('input[aria-label="Data mínima"]')
        count = await min_input_locator.count()

        if count == 0:
            print(f"     Min input field not found")
            return 0

        await min_input_locator.first.clear()
        await page.wait_for_timeout(300)
        await min_input_locator.first.fill(year_str)
        await min_input_locator.first.press('Enter')  # Pressionar Enter após preencher
        await page.wait_for_timeout(500)
        #await min_input_locator.first.click()
    except Exception as e:
        print(f"     Error filling first field: {e}")
        return 0

    # STEP 8: Wait for page reload
    print(f"    [8/14] Waiting for page reload...")
    await page.wait_for_timeout(3000)

    # STEP 9: Write year to second field (Data máxima)
    print(f"    [9/14] Writing '{year_str}' to second field (Data máxima)...")
    try:
        # Use locator for the second input (more reliable after page reload)
        max_input_locator = page.locator('input[aria-label="Data máxima"]')
        count = await max_input_locator.count()

        if count == 0:
            print(f"     Max input field not found after reload")
            return 0

        # Clear the field first before filling
        await max_input_locator.first.clear()
        await page.wait_for_timeout(300)
        await max_input_locator.first.fill(year_str)
        await page.wait_for_timeout(500)
        await max_input_locator.first.press('Enter')  # Pressionar Enter após preencher
    except Exception as e:
        print(f"     Error filling second field: {e}")
        return 0

    # STEP 10: Wait for page reload
    print(f"    [10/14] Waiting for page reload...")
    await page.wait_for_timeout(3000)

    # STEPS 11-14: Loop for scraping
    batch = {}
    items_found = 0
    items_skipped = 0
    local_page_count = 1  # LOCAL counter per scraper
    reached_duplicate = False

    while True:
        # STEP 11: Scrape items from current page
        print(f"    [11/14] ({year_str}) Scraping items from page {local_page_count}...")
        items = await page.query_selector_all('.mt-4.mb-4.d-flex')
        print(f"    Found {len(items)} items on page {local_page_count}")

        found_in_page = 0
        
        for element in items:
            link, data = await extract_item_data(element)
            
            if not link or not data:
                continue
            
            # Check year
            data_pub = data.get("dataPublicacao", "")
            item_year = extract_year_from_date(data_pub)
            if item_year and item_year != year:
                items_skipped += 1
                # Debug: print first few skipped items to see the date format
                if items_skipped <= 3:
                    print(f"    [DEBUG] Skipped item - Title: {data.get('titulo', 'N/A')[:40]}, Date: '{data_pub}', Year: {item_year}")
                continue
            
            # Check if already scraped
            if not force_full and link in done_links:
                print(f"    Found duplicate: {data.get('titulo', 'N/A')[:50]}")
                reached_duplicate = True
                break
            
            if link not in batch:
                batch[link] = data
                found_in_page += 1
                items_found += 1
        
        print(f"    New items from page {local_page_count}: {found_in_page}")

        # Stop if no new items found (already scraped previously)
        if found_in_page == 0:
            print(f"    No new items found on page {local_page_count} → Already scraped previously, stopping")
            break

        # Save batch if full
        if len(batch) >= BATCH_SIZE:
            await save_to_rotating_file(batch)
            done_links.update(batch.keys())
            batch = {}
        
        # Stop if found duplicate
        if reached_duplicate:
            print(f"    Year {year} complete (duplicates found)")
            break
        
        # STEP 12: Look for next page button
        print(f"    [12/14] Looking for next '»' button...")
        try:
            next_btn_locator = page.locator('.page-link:has-text("»")')

            # Check if button exists AND is enabled (not disabled)
            btn_exists = await next_btn_locator.count() > 0

            if not btn_exists:
                print(f"    [12/14] No more pages - '»' button not found")
                break

            # Check if button is disabled
            is_disabled = await next_btn_locator.first.get_attribute("aria-disabled") == "true"

            if is_disabled:
                print(f"    [12/14] No more pages - '»' button is disabled")
                break

            # STEP 13: Click next page button
            print(f"    [13/14] Clicking '»' button...")
            await next_btn_locator.first.wait_for(state='visible', timeout=5000)
            await next_btn_locator.first.scroll_into_view_if_needed()
            await page.wait_for_timeout(500)
            await next_btn_locator.first.click()
            local_page_count += 1

            # STEP 14: Wait for page reload
            print(f"    [14/14] Waiting for page reload...")
            await page.wait_for_timeout(4000)

        except Exception as e:
            print(f"     Error with pagination: {e}")
            break

    # Save remaining items
    if batch:
        await save_to_rotating_file(batch)
        done_links.update(batch.keys())
    
    print(f"  [YEAR {year}] Complete: {items_found} items found, {items_skipped} skipped")
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
        finally:
            await browser.close()

async def main():
    global current_file_index

    DOCUMENTS_DIR.mkdir(exist_ok=True)

    force_full = len(sys.argv) > 1 and sys.argv[1].strip().lower() == "true"

    # Delete all existing repo_cientifico_*.json files if force_full is enabled
    if force_full:
        existing_files = glob.glob(str(DOCUMENTS_DIR / "repo_cientifico_*.json"))
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
    print(f"Existing data: {total_existing} items in {len(glob.glob(f'{DOCUMENTS_DIR}/repo_cientifico_*.json'))} files")
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
    all_files = glob.glob(f'{DOCUMENTS_DIR}/repo_cientifico_*.json')
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

asyncio.run(main())