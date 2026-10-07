import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pandas as pd
import re
import time

BASE_URL = "https://www.health.gov.au"
LIST_URL = "https://www.health.gov.au/ministers/media-centre"

TARGET_COUNT = 50
MAX_PAGES = 15

OUTPUT = (
    "data/constructed/"
    "australian_gov_media/"
    "health.csv"
)

headers = {
    "User-Agent": "Mozilla/5.0"
}


# --------------------------------------------------
# Helper: clean whitespace
# --------------------------------------------------

def clean_text(text):
    return re.sub(r"\s+", " ", text).strip()


# --------------------------------------------------
# STEP 1: Collect candidate article URLs
# --------------------------------------------------

print("Collecting Health media release links...")

article_urls = []

for page in range(MAX_PAGES):

    print(f"Checking listing page {page + 1}...")

    try:
        params = {
            "page": page
        }

        response = requests.get(
            LIST_URL,
            params=params,
            headers=headers,
            timeout=30
        )

        response.raise_for_status()

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        links_before = len(article_urls)

        for link in soup.find_all("a", href=True):

            href = link["href"]

            # Individual minister media pages
            if "/ministers/" in href and "/media/" in href:

                full_url = urljoin(
                    BASE_URL,
                    href
                )

                # Remove query parameters so duplicate URLs
                # are treated as the same article
                full_url = full_url.split("?")[0]

                if full_url not in article_urls:
                    article_urls.append(full_url)

        new_links = len(article_urls) - links_before

        print(
            f"New candidate links: {new_links} | "
            f"Total: {len(article_urls)}"
        )

        # Stop if pagination no longer produces new articles
        if new_links == 0:
            print("No new links found. Stopping listing search.")
            break

        time.sleep(0.5)

    except Exception as e:

        print(
            f"Could not process listing page {page + 1}: {e}"
        )


print(
    f"\nCollecting valid media releases from "
    f"{len(article_urls)} candidate links...\n"
)


# --------------------------------------------------
# STEP 2: Visit articles and keep Media Releases
# --------------------------------------------------

rows = []

for url in article_urls:

    if len(rows) >= TARGET_COUNT:
        break

    try:

        response = requests.get(
            url,
            params={"language": "en"},
            headers=headers,
            timeout=30
        )

        response.raise_for_status()

        article_soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        main = article_soup.find("main")

        if main is None:
            continue

        text = clean_text(
            " ".join(main.stripped_strings)
        )

        # ------------------------------------------
        # Keep only actual Media Releases
        # ------------------------------------------

        if "Media type: Media release" not in text:
            continue


        # ------------------------------------------
        # Extract title
        # ------------------------------------------

        h1 = article_soup.find("h1")

        if h1 is not None:

            title = clean_text(
                h1.get_text(" ", strip=True)
            )

        else:

            # Reliable fallback from URL slug
            slug = (
                url
                .split("/media/")[-1]
                .split("?")[0]
            )

            title = clean_text(
                slug.replace("-", " ")
            ).capitalize()


        # ------------------------------------------
        # Extract publication date
        # ------------------------------------------

        date_match = re.search(
            r"Date published:\s*"
            r"(\d{1,2}\s+[A-Za-z]+\s+\d{4})",
            text
        )

        if date_match:
            date = date_match.group(1)
        else:

            time_tag = main.find("time")

            if time_tag:
                date = clean_text(
                    time_tag.get_text(
                        " ",
                        strip=True
                    )
                )
            else:
                date = ""


        # ------------------------------------------
        # Basic quality checks
        # ------------------------------------------

        if len(text) < 300:
            continue

        if not title:
            continue


        # ------------------------------------------
        # Store record
        # ------------------------------------------

        rows.append({
            "title": title,
            "text": text,
            "date": date,
            "department":
                "Australian Government Health, "
                "Disability and Ageing Portfolio",
            "label": "health",
            "source_url": url
        })

        print(
            f"Collected {len(rows)}/{TARGET_COUNT}: "
            f"{title[:70]}"
        )

        time.sleep(0.5)

    except Exception as e:

        print(
            f"Skipped {url}: {e}"
        )


# --------------------------------------------------
# STEP 3: Create dataframe
# --------------------------------------------------

df = pd.DataFrame(
    rows,
    columns=[
        "title",
        "text",
        "date",
        "department",
        "label",
        "source_url"
    ]
)


# --------------------------------------------------
# STEP 4: Remove duplicates
# --------------------------------------------------

if len(df) > 0:

    df = df.drop_duplicates(
        subset=["source_url"]
    )

    df = df.drop_duplicates(
        subset=["text"]
    )

    df = df[
        df["text"].str.len() >= 300
    ]

    df = df.reset_index(drop=True)


# --------------------------------------------------
# STEP 5: Save
# --------------------------------------------------

df.to_csv(
    OUTPUT,
    index=False
)


# --------------------------------------------------
# STEP 6: Summary
# --------------------------------------------------

print("\n" + "=" * 60)

print("HEALTH COLLECTION COMPLETE")

print("=" * 60)

print(
    f"Saved records: {len(df)}"
)

print(
    f"Output: {OUTPUT}"
)


if len(df) > 0:

    print("\nDate range:")

    print(
        f"{df['date'].iloc[0]} "
        f"to "
        f"{df['date'].iloc[-1]}"
    )

    print("\nInitial quality checks:")

    print(
        "Duplicate source URLs:",
        df["source_url"].duplicated().sum()
    )

    print(
        "Missing text:",
        df["text"].isna().sum()
    )

    print(
        "Minimum text length:",
        df["text"].str.len().min()
    )

    print(
        "Average text length:",
        round(df["text"].str.len().mean())
    )


print("=" * 60)