from bs4 import BeautifulSoup
import requests
from datetime import datetime
parser = "html.parser"


def storescrap(url):
    """
    Takes an URL, and returns a list of dict object.

    storename	

    storeurl	

    category_name	

    category_url

    item_no

    datetime = "input datetime" [returns ""]

    location = "needs to be updated" [returns ""]

    feedback = "needs to be updated" [returns ""]

    totallisting
    """
    output = []
    total_item_count = 0
    r = requests.get(url)
    soup = BeautifulSoup(r.text, parser)

    ##
    # Store Name
    ##

    try:
        storename = soup.find('a', {'id': 'MemberLink'}).text
    except:
        storename = str(url).split('/')[-1]
    categoryTable = soup.find('table', {'id': 'CategoryTable'})
    tableItems = categoryTable.find_all('a')
    table_toatl_item = categoryTable.find_all('span')

    
    try:
        firstproducturl = soup.find(
            'div', {'class': 'supergrid-bucket medium'})

        firstproducturl = "https://www.trademe.co.nz" + \
            firstproducturl.find('a')['href']
    except:
        firstproducturl = "https://www.trademe.co.nz" + soup.find(
            'div', {'class': 'supergrid-bucket largelist'}).find('a')['href']
    r = requests.get(firstproducturl)
    tsoup = BeautifulSoup(r.text, parser)
    try:
        feedback = tsoup.find(
            'span', {'id': 'SellerProfile_PercentPositiveFeedback'}).text + '%'
    except:
        feedback = ''
    try:
        storelocation = tsoup.find(
            'li', {'id': 'ShippingDetails_SellerLocation'}).find('strong').text.strip()
    except:
        storelocation = ''
    
    for x in range(len(tableItems)):
        item = {"storename": storename, "storeurl": url}
        item['category_name'] = str(tableItems[x].text)
        item["category_url"] = str(
            "https://www.trademe.co.nz"+tableItems[x]['href'])
        listing = str(table_toatl_item[x].text).replace(
            '(', '').replace(')', '')
        item["item_no"] = listing
        total_item_count += int(listing)
        item["datetime"] = datetime.now()
        item["location"] = storelocation
        item["feedback"] = feedback
        output.append(item)
    for x in output:
        x["totallisting"] = total_item_count

    return output
