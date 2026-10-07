import requests
from bs4 import BeautifulSoup
import csv
import time

BASE_URL = "https://ministers.education.gov.au"
LIST_URL = "https://ministers.education.gov.au/?page=0&release_type=15"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(LIST_URL, headers=headers, timeout=30)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

links = []

for a in soup.find_all("a", href=True):
    href = a["href"]
    text = a.get_text(strip=True)

    if href.startswith("/") and text:
        if "/minister/" in href or "/clare/" in href:
            full_url = BASE_URL + href

            if full_url not in links:
                links.append(full_url)

# Keep only first 5 candidate article links
links = links[:5]

print(f"Found {len(links)} candidate links")

rows = []

for i, url in enumerate(links, start=1):
    print(f"Collecting {i}/5: {url}")

    r = requests.get(url, headers=headers, timeout=30)
    r.raise_for_status()

    page = BeautifulSoup(r.text, "html.parser")

    title_tag = page.find("h1")
    title = title_tag.get_text(" ", strip=True) if title_tag else ""

    main = page.find("main")

    if main:
        text = main.get_text(" ", strip=True)
    else:
        text = page.get_text(" ", strip=True)

    rows.append({
        "title": title,
        "text": text,
        "label": "education",
        "source_url": url
    })

    time.sleep(1)

output_file = "data/constructed/australian_gov_media/education_test.csv"

with open(output_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=["title", "text", "label", "source_url"]
    )
    writer.writeheader()
    writer.writerows(rows)

print()
print("Done!")
print(f"Saved {len(rows)} records to:")
print(output_file)