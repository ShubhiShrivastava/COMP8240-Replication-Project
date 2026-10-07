import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
from urllib.parse import urljoin

BASE_URL = "https://ministers.education.gov.au"
TARGET_COUNT = 100

headers = {
    "User-Agent": "Mozilla/5.0"
}

article_urls = []

print("Collecting Education media release links...")

page_number = 0

while len(article_urls) < TARGET_COUNT:
    list_url = (
        f"https://ministers.education.gov.au/"
        f"?page={page_number}&release_type=15"
    )

    print(f"Checking listing page {page_number + 1}...")

    response = requests.get(list_url, headers=headers, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    page_links = []

    for a in soup.find_all("a", href=True):
        href = a["href"]

        if not href.startswith("/"):
            continue

        # Individual minister article URLs usually look like:
        # /clare/article-name
        parts = href.strip("/").split("/")

        if len(parts) == 2:
            full_url = urljoin(BASE_URL, href)

            if full_url not in article_urls and full_url not in page_links:
                page_links.append(full_url)

    if not page_links:
        print("No more article links found.")
        break

    article_urls.extend(page_links)

    print(f"Total candidate links found: {len(article_urls)}")

    page_number += 1
    time.sleep(1)

print()
print(f"Collecting valid media releases from {len(article_urls)} candidate links...")
print()

rows = []

for i, url in enumerate(article_urls, start=1):

    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        main = soup.find("main")

        if not main:
            print(f"Skipping {i}: no main content")
            continue

        full_text = main.get_text(" ", strip=True)

        # Only keep actual Media Releases / Joint Media Releases
        if (
            "Release type: Media Release" not in full_text
            and "Release type: Joint Media Release" not in full_text
        ):
            continue

        title_tag = main.find("h1")

        if not title_tag:
            continue

        title = title_tag.get_text(" ", strip=True)

        # Extract date
        date_match = re.search(
            r"Date:\s*([0-9]{1,2}\s+[A-Za-z]+\s+[0-9]{4})",
            full_text
        )

        date = date_match.group(1) if date_match else ""

        rows.append({
            "title": title,
            "text": full_text,
            "date": date,
            "department": "Australian Government Education Portfolio",
            "label": "education",
            "source_url": url
        })

        print(
            f"Collected {len(rows)}/{TARGET_COUNT}: "
            f"{title[:70]}"
        )

        if len(rows) >= TARGET_COUNT:
            break

        time.sleep(1)

    except Exception as error:
        print(f"Error with {url}: {error}")

output_file = (
    "data/constructed/australian_gov_media/"
    "education.csv"
)

df = pd.DataFrame(rows)

# Remove exact duplicate URLs
df = df.drop_duplicates(subset="source_url")

# Remove empty text records
df = df[df["text"].str.len() > 100]

df.to_csv(
    output_file,
    index=False,
    encoding="utf-8"
)

print()
print("=" * 60)
print("EDUCATION COLLECTION COMPLETE")
print("=" * 60)
print(f"Saved records: {len(df)}")
print(f"Output: {output_file}")

if len(df) > 0:
    print()
    print("Date range:")
    print(df["date"].iloc[0], "to", df["date"].iloc[-1])

print("=" * 60)