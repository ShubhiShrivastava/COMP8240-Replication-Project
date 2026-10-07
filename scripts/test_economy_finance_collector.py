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

headers = {
    "User-Agent": "Mozilla/5.0"
}

print("Checking Australian Treasurer media releases...")

response = requests.get(
    LIST_URL,
    headers=headers,
    timeout=30
)

response.raise_for_status()

soup = BeautifulSoup(
    response.text,
    "html.parser"
)

article_urls = []

# --------------------------------------------------
# Find individual media-release links
# --------------------------------------------------

for link in soup.find_all("a", href=True):

    href = link["href"]

    if (
        "/ministers/jim-chalmers-2022/"
        "media-releases/" in href
    ):

        full_url = urljoin(BASE_URL, href)
        full_url = full_url.split("?")[0]

        if full_url not in article_urls:
            article_urls.append(full_url)


print(
    f"Candidate media release links found: "
    f"{len(article_urls)}"
)


# --------------------------------------------------
# Visit individual releases
# --------------------------------------------------

rows = []

for url in article_urls:

    if len(rows) >= 5:
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

        title = re.sub(
            r"\s+",
            " ",
            h1.get_text(
                " ",
                strip=True
            )
        ).strip()


        # ------------------------------------------
        # Extract page text
        # Treasury site has no <main> element
        # ------------------------------------------

        page_text = re.sub(
            r"\s+",
            " ",
            " ".join(
                article_soup.stripped_strings
            )
        ).strip()


        # ------------------------------------------
        # Remove navigation before article title
        # ------------------------------------------

        title_position = page_text.find(title)

        if title_position != -1:

            # There may be title text in the HTML
            # <title> before the real article heading.
            second_position = page_text.find(
                title,
                title_position + len(title)
            )

            if second_position != -1:
                text = page_text[second_position:]
            else:
                text = page_text[title_position:]

        else:
            text = page_text


        # ------------------------------------------
        # Remove common footer material
        # ------------------------------------------

        footer_markers = [
            "Subscribe RSS",
            "Footer menu",
            "Treasury FOI"
        ]

        for marker in footer_markers:

            position = text.find(marker)

            if position != -1:
                text = text[:position]


        text = re.sub(
            r"\s+",
            " ",
            text
        ).strip()


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
        # Quality check
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
            f"Collected {len(rows)}/5: "
            f"{title[:80]}"
        )

        time.sleep(0.5)

    except Exception as e:

        print(f"Skipped: {url}")
        print(f"Reason: {e}")


# --------------------------------------------------
# Save test
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

output = (
    "data/constructed/"
    "australian_gov_media/"
    "economy_finance_test.csv"
)

df.to_csv(
    output,
    index=False
)


# --------------------------------------------------
# Summary
# --------------------------------------------------

print("\n" + "=" * 60)
print("ECONOMY / FINANCE TEST COMPLETE")
print("=" * 60)

print(f"Saved records: {len(df)}")
print(f"Output: {output}")

if len(df) > 0:

    print("\nCollected records:")

    print(
        df[
            ["title", "date", "label"]
        ].to_string(index=False)
    )

print("=" * 60)