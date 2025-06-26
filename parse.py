import requests
from bs4 import BeautifulSoup
import pandas as pd

url = "https://docs.tenable.com/nessus/compliance-checks-reference/Content/UnixFILE_CHECK.htm"
res = requests.get(url)
soup = BeautifulSoup(res.text, "html.parser")

table = soup.find("ul")
rows = table.tbody.find_all("tr")

keywords = {}
for row in table:
    cols = [c.get_text(strip=True) for c in row.find_all("li")]
    if len(cols) >= 2:
        keyword, desc = cols[0], cols[1]
        keywords[keyword] = desc

print(keywords)
df = pd.DataFrame(list(keywords.items()), columns=['Keyword', 'Description'])
df.to_csv('nessus_keywords.csv', index=False, encoding='utf-8')