import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pandas as pd
import re
import time

BASE_URL = "https://www.foreignminister.gov.au"
LIST_URL = "https://www.foreignminister.gov.au/minister/penny-wong/media-releases"

headers = {
    "User-Agent": "Mozilla/5.0"
}

print("Checking Australian Foreign Minister media releases...")

response = requests.get(
    LIST_URL,
    headers=headers,
    timeout=30
)

response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

article_urls = []

# --------------------------------------------------
# Find individual media-release links
# --------------------------------------------------

for link in soup.find_all("a", href=True):

    href = link["href"]

    if "/minister/penny-wong/media-release/" in href:

        full_url = urljoin(BASE_URL, href)
        full_url = full_url.split("?")[0]

        if full_url not in article_urls:
            article_urls.append(full_url)


print(f"Candidate media release links found: {len(article_urls)}")


# --------------------------------------------------
# Visit articles
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

        main = article_soup.find("main")

        if main is None:
            continue

        text = re.sub(
            r"\s+",
            " ",
            " ".join(main.stripped_strings)
        ).strip()

        # Only keep actual media releases
        if (
            "Media release" not in text
            and "Joint media release" not in text
        ):
            continue


        # --------------------------------------------------
        # Title
        # --------------------------------------------------

        h1 = article_soup.find("h1")

        if h1 is not None:

            title = re.sub(
                r"\s+",
                " ",
                h1.get_text(" ", strip=True)
            ).strip()

        else:

            slug = url.split("/media-release/")[-1]

            title = (
                slug
                .replace("-", " ")
                .strip()
                .capitalize()
            )


        # --------------------------------------------------
        # Date
        # --------------------------------------------------

        date_match = re.search(
            r"(\d{1,2}\s+[A-Za-z]+\s+\d{4})",
            text
        )

        if date_match:
            date = date_match.group(1)
        else:
            date = ""


        # --------------------------------------------------
        # Store
        # --------------------------------------------------

        rows.append({
            "title": title,
            "text": text,
            "date": date,
            "department":
                "Australian Government Department of Foreign Affairs and Trade",
            "label": "foreign_affairs",
            "source_url": url
        })

        print(
            f"Collected {len(rows)}/5: "
            f"{title[:75]}"
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
    "foreign_affairs_test.csv"
)

df.to_csv(output, index=False)


# --------------------------------------------------
# Summary
# --------------------------------------------------

print("\n" + "=" * 60)
print("FOREIGN AFFAIRS TEST COMPLETE")
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