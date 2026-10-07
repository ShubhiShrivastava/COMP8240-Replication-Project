import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pandas as pd
import time

BASE_URL = "https://www.health.gov.au"
LIST_URL = "https://www.health.gov.au/ministers/media-centre"

headers = {
    "User-Agent": "Mozilla/5.0"
}

print("Checking Australian Government Health media centre...")

# --------------------------------------------------
# STEP 1: Get the main media-centre page
# --------------------------------------------------

response = requests.get(
    LIST_URL,
    headers=headers,
    timeout=30
)

response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

article_urls = []

# Individual Health minister media items use /media/
for link in soup.find_all("a", href=True):

    href = link["href"]

    if "/ministers/" in href and "/media/" in href:

        full_url = urljoin(BASE_URL, href)

        if full_url not in article_urls:
            article_urls.append(full_url)


print(f"Candidate article links found: {len(article_urls)}")


# --------------------------------------------------
# STEP 2: Visit candidate articles
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
            print(f"\nNo <main> found: {url}")
            continue

        text = " ".join(main.stripped_strings)

        # ------------------------------------------
        # DEBUG
        # Shows us exactly what Python can see
        # ------------------------------------------

        print("\n" + "-" * 60)
        print("DEBUG URL:")
        print(url)

        print("\nTEXT START:")
        print(text[:500])

        print("-" * 60)

        # ------------------------------------------
        # Only keep actual Media Releases
        # ------------------------------------------

        if "media release" not in text.lower():
            print("Skipped: page does not contain 'Media release'")
            continue


        # ------------------------------------------
        # Extract title
        # ------------------------------------------
        # Try to get the title from the page
        h1 = article_soup.find("h1")

        if h1 is not None:
            title = h1.get_text(" ", strip=True)
        else:
            # Fallback: create title from URL slug
            slug = url.split("/media/")[-1].split("?")[0]
            title = slug.replace("-", " ").strip().title()
        # ------------------------------------------
        # Extract date
        # ------------------------------------------

        time_tag = main.find("time")

        if time_tag:
            date = time_tag.get_text(
                " ",
                strip=True
            )
        else:
            date = ""


        # ------------------------------------------
        # Store record
        # ------------------------------------------

        rows.append({
            "title": title,
            "text": text,
            "date": date,
            "department":
                "Australian Government Health, Disability and Ageing Portfolio",
            "label": "health",
            "source_url": url
        })


        print(
            f"\nCollected {len(rows)}/5: "
            f"{title[:70]}"
        )

        time.sleep(1)


    except Exception as e:

        print(f"\nSkipped: {url}")
        print(f"Reason: {e}")


# --------------------------------------------------
# STEP 3: Save test dataset
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
    "health_test.csv"
)

df.to_csv(
    output,
    index=False
)


# --------------------------------------------------
# STEP 4: Print results
# --------------------------------------------------

print("\n" + "=" * 60)

print("HEALTH TEST COMPLETE")

print("=" * 60)

print(
    f"Saved records: {len(df)}"
)

print(
    f"Output: {output}"
)


if len(df) > 0:

    print("\nCollected records:")

    print(
        df[
            [
                "title",
                "date",
                "label"
            ]
        ].to_string(
            index=False
        )
    )


print("=" * 60)