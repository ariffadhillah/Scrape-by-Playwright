import asyncio
from playwright.async_api import async_playwright
import csv
import os

# Proxy data
proxy_host = ""
proxy_port = ""
proxy_user = ""
proxy_pass = ""

country = "Luxembourg"
base_url = "https://www.doctena.lu/fr/orthodontiste/luxembourg?sort_by=proximity&doctorLanguage=fr&page={}"

# Output CSV
csv_filename = "doctena_dokter.csv"

async def main():
    async with async_playwright() as p:
        user_data_dir = os.path.abspath("user_data")

        browser = await p.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            headless=False,
            proxy={
                "server": f"http://{proxy_host}:{proxy_port}",
                "username": proxy_user,
                "password": proxy_pass
            },
            args=["--disable-blink-features=AutomationControlled"]
        )

        page = await browser.new_page()

        results = []
        page_number = 1

        while True:
            url = base_url.format(page_number)
            print(f"🔄 Membuka halaman {page_number}: {url}")

            try:
                await page.goto(url, timeout=60000)
                await page.wait_for_timeout(5000)
            except Exception as e:
                print("❌ Gagal membuka halaman:", e)
                break

            dokter_blocks = await page.query_selector_all(".Search__result-infos")

            if not dokter_blocks:
                print("📭 Tidak ada data lagi, selesai.")
                break

            for block in dokter_blocks:
                try:
                    # Nama lengkap
                    nama_elem = await block.query_selector("h5 a")
                    nama_lengkap = await nama_elem.inner_text()

                    # Pecah nama
                    nama_parts = nama_lengkap.replace("Dr. ", "").strip().split()
                    first_name = nama_parts[0] if len(nama_parts) > 0 else ""
                    last_name = nama_parts[1] if len(nama_parts) > 1 else ""

                    # Alamat
                    alamat_elem = await block.query_selector("p.dsg-no-mg-bottom")
                    alamat_text = await alamat_elem.inner_text()
                    lines = alamat_text.strip().split("\n")
                    address2 = lines[0].strip() if len(lines) > 0 else ""
                    zipcode = ""
                    city = ""
                    if len(lines) > 1:
                        zipcode_city = lines[1].strip().split(" ", 1)
                        zipcode = zipcode_city[0]
                        city = zipcode_city[1] if len(zipcode_city) > 1 else ""

                    results.append({
                        "Nama Lengkap": nama_lengkap,
                        "First Name": first_name,
                        "Last Name": last_name,
                        "Address 2": address2,
                        "ZIP": zipcode,
                        "City": city,
                        "Country": country
                    })

                except Exception as e:
                    print("⚠️ Gagal parsing 1 dokter:", e)
                    continue

            print(f"✅ Halaman {page_number} selesai. Total data sejauh ini: {len(results)}\n")
            page_number += 1

        await browser.close()

        # Simpan ke CSV
        with open(csv_filename, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=[
                "Nama Lengkap", "First Name", "Last Name", "Address 2", "ZIP", "City", "Country"
            ])
            writer.writeheader()
            writer.writerows(results)

        print(f"✅ Data disimpan ke {csv_filename} ({len(results)} baris)")

asyncio.run(main())
