from bs4 import BeautifulSoup
import requests
from product_info_scrapper import datetime_parser
parser = 'html.parser'


def revisit_product_page(url):
    html = requests.get(url).text
    soup = BeautifulSoup(html, parser)
    closingtime = soup.find('span', {'id': 'ClosingTime_ClosingTime'}).text

    finalbid = soup.find(
        'div', {'class': 'bidding-title bidding-title-closed'})
    if finalbid != None and str(finalbid.text).strip() == "Final bid":
        isSold = "Yes"
        finalbid = soup.find('div', {'id': 'Bidding_CurrentBidValue'}).text
    else:
        finalbid = "Empty"
        isSold = "No"
    visitcount = soup.find(
        'div', {'class': 'page-count'}).find_all('span', {'class': 'digit'})
    visitcounter = ''
    for x in visitcount:
        visitcounter += x.text

    return closingtime, isSold, finalbid, visitcounter
