import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pandas as pd
import re
import time

BASE_URL = "https://ministers.treasury.gov.au"

LIST_URL = (
    "https://ministers.treasury.gov.au/"
    "ministers/jim-chalmers-2022/media-releases"
)

TARGET_COUNT = 50
MAX_PAGES = 5

OUTPUT = (
    "data/constructed/"
    "australian_gov_media/"
    "economy_finance.csv"
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
# STEP 1: Collect candidate URLs from archive pages
# --------------------------------------------------

print("Collecting Economy / Finance media release links...")

article_urls = []

for page in range(MAX_PAGES):

    page_url = f"{LIST_URL}?page={page}"

    try:

        response = requests.get(
            page_url,
            headers=headers,
            timeout=30
        )

        response.raise_for_status()

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        page_links = []

        for link in soup.find_all("a", href=True):

            href = link["href"]

            if (
                "/ministers/jim-chalmers-2022/"
                "media-releases/" in href
            ):

                full_url = urljoin(
                    BASE_URL,
                    href
                )

                full_url = full_url.split("?")[0]

                if full_url not in article_urls:
                    article_urls.append(full_url)
                    page_links.append(full_url)

        print(
            f"Page {page}: "
            f"{len(page_links)} new candidates"
        )

        time.sleep(0.3)

    except Exception as e:

        print(
            f"Could not process page {page}: {e}"
        )


print(
    f"\nTotal unique candidate links: "
    f"{len(article_urls)}"
)

print(
    f"Collecting up to {TARGET_COUNT} "
    f"valid releases...\n"
)


# --------------------------------------------------
# STEP 2: Visit individual releases
# --------------------------------------------------

rows = []

for url in article_urls:

    if len(rows) >= TARGET_COUNT:
        break

    try:

        response = requests.get(
            url,
            headers=headers,
            timeout=30
        )

        response.raise_for_status()

        article_soup = BeautifulSoup(
            response.text,
            "html.parser"
        )


        # ------------------------------------------
        # Title
        # ------------------------------------------

        h1 = article_soup.find("h1")

        if h1 is None:
            continue

        title = clean_text(
            h1.get_text(
                " ",
                strip=True
            )
        )

        if not title:
            continue


        # ------------------------------------------
        # Extract page text
        # Treasury pages do not use <main>
        # ------------------------------------------

        page_text = clean_text(
            " ".join(
                article_soup.stripped_strings
            )
        )


        # ------------------------------------------
        # Start at article heading rather than
        # navigation/page-title material
        # ------------------------------------------

        first_position = page_text.find(title)

        if first_position != -1:

            second_position = page_text.find(
                title,
                first_position + len(title)
            )

            if second_position != -1:
                text = page_text[second_position:]
            else:
                text = page_text[first_position:]

        else:
            text = page_text


        # ------------------------------------------
        # Remove common footer content
        # ------------------------------------------

        footer_markers = [
            "Subscribe RSS",
            "Footer menu",
            "Treasury FOI",
            "Copyright and disclaimer"
        ]

        for marker in footer_markers:

            position = text.find(marker)

            if position != -1:
                text = text[:position]


        text = clean_text(text)


        # ------------------------------------------
        # Date
        # ------------------------------------------

        date_match = re.search(
            r"(\d{1,2}\s+[A-Za-z]+\s+\d{4})",
            text
        )

        if date_match:
            date = date_match.group(1)
        else:
            date = ""


        # ------------------------------------------
        # Basic quality checks
        # ------------------------------------------

        if len(text) < 300:
            continue


        # ------------------------------------------
        # Store
        # ------------------------------------------

        rows.append({
            "title": title,
            "text": text,
            "date": date,
            "department":
                "Australian Government Treasury",
            "label": "economy_finance",
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
print("ECONOMY / FINANCE COLLECTION COMPLETE")
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
        round(
            df["text"].str.len().mean()
        )
    )


print("=" * 60)