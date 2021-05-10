import scrape_wilshire
import write
from datetime import datetime

url = 'https://fknol.com/stock/list/wilshire-5000.php'


def digest_all(first_url):
    df = scrape_wilshire.digest_site(first_url)
    index = 2  # google sheet row to write to
    write.write_to_sheet(df, index)

    links = scrape_wilshire.get_all_links(first_url)

    for url in links:  # starting with url 2, onwards
        df = scrape_wilshire.digest_site(url)
        index += 100

        now = datetime.now().strftime("%H:%M:%S")
        print(f"{now}: row {index}")

        write.write_to_sheet(df, index)


digest_all(url)
