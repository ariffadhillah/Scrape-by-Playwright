# import asyncio
# from playwright.async_api import async_playwright
# from bs4 import BeautifulSoup

# TARGET_URL = "https://www.invisalign.ch/fr/find-a-doctor#v=results&c=Vaud&cy=ch&pr=2&s=e"

# page pertama
# https://www.invisalign.ch/fr/find-a-doctor#v=results&c=Vaud&cy=ch&s=e
# page kedua
# https://www.invisalign.ch/fr/find-a-doctor#v=results&c=Vaud&cy=ch&pr=1&s=e
# page ketiga
# https://www.invisalign.ch/fr/find-a-doctor#v=results&c=Vaud&cy=ch&pr=2&s=e

# # async def fetch_rendered_html(url: str) -> str:
# #     """Fetch fully-rendered HTML using Playwright browser after handling modals."""
# #     async with async_playwright() as p:
# #         browser = await p.chromium.launch(headless=False)
# #         context = await browser.new_context()
# #         page = await context.new_page()

# #         print(f"🌐 Membuka halaman: {url}")
# #         await page.goto(url)

# #         # ✅ 1. Klik modal popup jika ada
# #         try:
# #             await page.wait_for_selector('.modal-header .btn-close', timeout=5000)
# #             await page.click('.modal-header .btn-close')
# #             print("✅ Modal popup ditutup")
# #         except:
# #             print("⏭️ Tidak ada modal popup")

# #         # ✅ 2. Klik tombol cookie "Tout accepter"
# #         try:
# #             await page.wait_for_selector('#truste-consent-button', timeout=5000)
# #             await page.click('#truste-consent-button')
# #             print("✅ Cookie consent disetujui")
# #         except:
# #             print("⏭️ Tidak ada consent popup")

# #         # ✅ 3. Tunggu konten dokter muncul
# #         await page.wait_for_selector('.item-cell-info', timeout=10000)

# #         # ✅ 4. Ambil HTML setelah semua interaksi selesai
# #         html = await page.content()
# #         await browser.close()
# #         return html



# async def fetch_rendered_html(url: str) -> str:
#     """Fetch fully-rendered HTML using Playwright browser after handling modals."""
#     async with async_playwright() as p:
#         browser = await p.chromium.launch(headless=False)
#         context = await browser.new_context(
#             no_viewport=False  # Fullscreen seperti desktop asli
#         )
#         page = await context.new_page()

#         print(f"🌐 Membuka halaman: {url}")
#         await page.goto(url)

#         # ✅ 1. Tutup modal popup jika ada
#         try:
#             await page.wait_for_selector('.modal-header .btn-close', timeout=5000)
#             await page.click('.modal-header .btn-close')
#             print("✅ Modal popup ditutup")
#         except:
#             print("⏭️ Tidak ada modal popup")

#         # ✅ 2. Setujui cookie
#         try:
#             await page.wait_for_selector('#truste-consent-button', timeout=5000)
#             await page.click('#truste-consent-button')
#             print("✅ Cookie consent disetujui")
#         except:
#             print("⏭️ Tidak ada consent popup")

#         # ✅ 3. Tunggu hasil dokter muncul
#         await page.wait_for_selector('.item-cell-info', timeout=10000)

#         # ✅ 4. Ambil HTML
#         html = await page.content()

#         # 🕒 Biarkan browser terbuka (untuk debugging atau visualisasi)
#         await asyncio.sleep(9)

#         await browser.close()
#         return html


# def parse_doctor_items(html: str) -> list:
#     soup = BeautifulSoup(html, "html.parser")
#     items = soup.find_all("div", class_="dl-results-item-container")

#     results = []
#     for item in items:
#         # === Ambil nama
#         name_tag = item.select_one(".dl-full-name")
#         name = name_tag.get_text(strip=True) if name_tag else ""

#         # === Ambil baris-baris alamat
#         address_divs = item.select(".dl-info-section")[0].find_all("div") if item.select(".dl-info-section") else []
#         address_line1 = address_divs[0].get_text(strip=True) if len(address_divs) > 0 else ""
#         address_line2 = address_divs[1].get_text(strip=True) if len(address_divs) > 1 else ""
#         zip_city_country = address_divs[2].get_text(strip=True) if len(address_divs) > 2 else ""

#         # === Pisahkan ZIP, City, Country
#         zip_code, city, country = "", "", ""
#         if "," in zip_city_country:
#             parts = zip_city_country.split(",")
#             if len(parts) == 3:
#                 zip_code = parts[0].strip()
#                 city = parts[1].strip()
#                 country = parts[2].strip()

#         # === Gabungkan alamat lengkap
#         alamat_lengkap = f"{address_line1}, {address_line2}, {zip_code}, {city}, {country}"

#         # === Ambil no telp
#         tel_tag = item.select_one(".dl-phone-link")
#         tel = tel_tag.get_text(strip=True) if tel_tag else ""

#         # === Ambil website
#         site_tag = item.select_one(".dl-info-url a")
#         site = site_tag['href'].strip() if site_tag else ""

#         # === Tambahkan ke hasil
#         results.append({
#             "name": name,
#             "address": f"{address_line1}, {address_line2}",
#             "city": city,
#             "zip": zip_code,
#             "country": country,
#             "tel": tel,
#             "site": site,
#             "alamat lengkap": alamat_lengkap
#         })

#     return results



# async def main():
#     html = await fetch_rendered_html(TARGET_URL)
#     results = parse_doctor_items(html)

#     # Tampilkan hasil
#     for r in results:
#         print(r)

# if __name__ == "__main__":
#     asyncio.run(main())



import csv
import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

BASE_URL = "https://www.invisalign.ch/fr/find-a-doctor"
QUERY_BASE = "#v=results&c=Valais&cy=ch"
QUERY_SUFFIX = "&s=e"

async def fetch_rendered_html(url: str, playwright) -> str:
    """Fetch HTML with Playwright after handling modal & cookie popup."""
    browser = await playwright.chromium.launch(headless=False)
    context = await browser.new_context()

    # context = await browser.new_context(
    #     viewport=None  # ✅ biarkan browser gunakan ukuran asli OS
    # )

    # browser = await playwright.chromium.launch(headless=False, args=["--start-maximized"])
    # context = await browser.new_context(viewport={"width": 1920, "height": 1080})
    page = await context.new_page()
    await page.goto(url)


    # Tutup modal
    try:
        await page.wait_for_selector('.modal-header .btn-close', timeout=3000)
        await page.click('.modal-header .btn-close')
    except:
        pass

    # Klik cookie
    try:
        await page.wait_for_selector('#truste-consent-button', timeout=3000)
        await page.click('#truste-consent-button')
    except:
        pass

    # 🔁 Tambahkan penundaan ekstra agar konten sempat render
    try:
        await page.wait_for_selector('.dl-results-item-container', timeout=10000)
        await page.wait_for_timeout(2000)  # ⏱️ Tambahan delay 2 detik
    except:
        print("⚠️ Tidak menemukan .dl-results-item-container dalam batas waktu.")

    # await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    # await page.wait_for_timeout(3000)  # biarkan konten termuat

    await page.goto(url)
    await page.wait_for_load_state("load")  # ✅ pastikan selesai load
    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")


    html = await page.content()
    await browser.close()
    return html


def parse_doctor_items(html: str) -> list:
    soup = BeautifulSoup(html, "html.parser")
    items = soup.find_all("div", class_="dl-results-item-container")
    results = []

    for item in items:
        name_tag = item.select_one(".dl-full-name")
        name = name_tag.get_text(strip=True) if name_tag else ""

        address_divs = item.select(".dl-info-section")[0].find_all("div") if item.select(".dl-info-section") else []
        address1 = address_divs[0].get_text(strip=True) if len(address_divs) > 0 else ""
        address2 = address_divs[1].get_text(strip=True) if len(address_divs) > 1 else ""
        zip_city_country = address_divs[2].get_text(strip=True) if len(address_divs) > 2 else ""
        zip_code, city, country = "", "", ""
        if "," in zip_city_country:
            parts = zip_city_country.split(",")
            if len(parts) == 3:
                zip_code = parts[0].strip()
                city = parts[1].strip()
                country = parts[2].strip()

        tel_tag = item.select_one(".dl-phone-link")
        tel = tel_tag.get_text(strip=True) if tel_tag else ""

        site_tag = item.select_one(".dl-info-url a")
        site = site_tag['href'].strip() if site_tag else ""

        alamat_lengkap = f"{address1}, {address2}, {zip_code}, {city}, {country}"

        results.append({
            "name": name,
            "address": f"{address1}, {address2}",
            "city": city,
            "zip": zip_code,
            "country": country,
            "tel": tel,
            "site": site,
            "alamat lengkap": alamat_lengkap
        })

    return results

async def scrape_all_pages():
    all_results = []
    page_number = 0

    async with async_playwright() as playwright:
        while True:
            # Bangun URL
            if page_number == 0:
                url = f"{BASE_URL}{QUERY_BASE}{QUERY_SUFFIX}"
            else:
                url = f"{BASE_URL}{QUERY_BASE}&pr={page_number}{QUERY_SUFFIX}"

            print(f"\n🔄 Scraping Page {page_number + 1}: {url}")
            # print(f"✅ Ditemukan {parsed} dokter di halaman {page_number + 1}")
            html = await fetch_rendered_html(url, playwright)
            parsed = parse_doctor_items(html)

            if not parsed:
                print(f"🚫 Tidak ada data ditemukan di page {page_number + 1}. Stop.")
                break

            print(f"✅ {len(parsed)} dokter ditemukan di page {page_number + 1}")
            print(f"✅ {parsed} dokter ditemukan di page {page_number + 1}")
            all_results.extend(parsed)
            page_number += 1

        return all_results



def save_to_csv(results: list, filename: str = "doctors_Valais.csv"):
    headers = [
        "Name", "Address", "City", "Zip Code", "Country", "Tel", "Site", "Alamat Lengkap"
    ]
    
    with open(filename, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for row in results:
            writer.writerow({
                "Name": row["name"],
                "Address": row["address"],
                "City": row["city"],
                "Zip Code": row["zip"],
                "Country": row["country"],
                "Tel": f"'{row['tel']}", 
                "Site": row["site"],
                "Alamat Lengkap": row["alamat lengkap"]
            })

async def main():
    results = await scrape_all_pages()
    print(f"\n✅ Total dokter ditemukan: {len(results)}")

    # Tampilkan sebagian di terminal (optional)
    for r in results[:3]:
        print(r)

    # Simpan ke CSV
    save_to_csv(results)
    print("📁 Data berhasil disimpan ke 'doctors_vaud.csv'")


if __name__ == "__main__":
    asyncio.run(main())
