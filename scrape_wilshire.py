from bs4 import BeautifulSoup
import requests
import re
import pandas as pd
import calc


def getPage(url):
    page = requests.get(url)
    return BeautifulSoup(page.text, 'lxml')

# get all page links
def get_all_links(first_url):
    links = []

    soup = getPage(first_url)
    # locate the section with the links
    list_of_a = soup.find('h2', text=('Performance of Wilshire 5000 Stocks')
                          ).parent.nextSibling.findAll('a')
    for a in list_of_a:
        links.append(a['href'])
    return links  # links contains all sites to scrape except first_url site


def digest_row(tablerow):
    data = tablerow.findAll('td')

    # extract data, skipping the two header rows
    try:
        str = re.split('[()]', data[0].text)
        rank = str[0]
        company = str[1].strip()
        symbol = str[2]
        cap = data[1].text
    except IndexError:  # if it's a header row return dummies
        return 0, 0, 0, 0, 0

    return 1, rank, company, symbol, cap


def digest_table(table):
    ranks = []
    companies = []
    symbols = []
    caps = []

    for row in table:
        status, rank, company, symbol, cap = digest_row(row)
        if status != 0:
            ranks.append(rank)
            companies.append(company)
            symbols.append(symbol)
            caps.append(cap)

    df = pd.DataFrame(
        {'Rank': ranks,
         'Company': companies,
         'Symbol': symbols,
         'Market Cap': caps
         }
    )

    return df


#single page scrape given url
def digest_page(url):
    soup = getPage(url)

    # locate the data table
    table = soup.body.find('td', text=re.compile(r'\d+\.')).parent.parent.findAll('tr')
    page_df = digest_table(table)  # get the basic info (rank, company, market cap)
    calc.add_indicators(page_df) # add technical analysis

    return page_df
