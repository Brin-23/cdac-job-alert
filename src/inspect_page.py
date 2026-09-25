import requests
from bs4 import BeautifulSoup

URL = "https://www.cdac.in/index.aspx?id=current_jobs"

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/153.0.0.0 Safari/537.36"
    )
}

response = requests.get(
    URL,
    headers=headers,
    timeout=20,
)

print("HTTP status:", response.status_code)
print("Downloaded:", len(response.text), "characters")

response.raise_for_status()

with open("cdac_page.html", "w", encoding="utf-8") as f:
    f.write(response.text)

soup = BeautifulSoup(response.text, "html.parser")

print("\n" + "=" * 70)
print("PAGE TITLE")
print("=" * 70)

print(soup.title.get_text(strip=True) if soup.title else "No title")


print("\n" + "=" * 70)
print("HEADINGS")
print("=" * 70)

for heading in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]):
    text = heading.get_text(" ", strip=True)

    if text:
        print(f"{heading.name}: {text}")


print("\n" + "=" * 70)
print("POTENTIAL JOB/RECRUITMENT LINKS")
print("=" * 70)

keywords = [
    "job",
    "recruit",
    "project engineer",
    "project manager",
    "engineer",
    "walk-in",
    "advertisement",
    "career",
]

count = 0

for link in soup.find_all("a"):
    text = link.get_text(" ", strip=True)
    href = link.get("href")

    if not text or not href:
        continue

    combined = f"{text} {href}".lower()

    if any(keyword in combined for keyword in keywords):
        count += 1

        print(f"\n[{count}]")
        print("TEXT :", text)
        print("HREF :", href)

print("\nTotal potential links:", count)