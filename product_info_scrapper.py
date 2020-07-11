from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import requests
import pandas as pd
import re
import csv
parser = 'html.parser'
na = "N/A"


def datetime_parser(closingdatestr):
    dt_format = '%a %d %b %Y, %I:%M %p'
    try:
        closingdate = datetime.strptime(closingdatestr, dt_format)
    except:
        pass
    try:
        closingdate_temp = closingdatestr.split()
        closingdate_temp[2] = str(datetime.now().year)+','
        closingdate_temp = " ".join(closingdate_temp)
        closingdate = datetime.strptime(closingdate_temp, dt_format)
    except:
        pass
    try:
        closingdate_temp = closingdatestr.replace(
            ',', ' '+str(datetime.now().year)+',')
        closingdate = datetime.strptime(closingdate_temp, dt_format)
    except:
        pass
    try:
        if ('hours' or 'hour') in closingdatestr:
            h = int(closingdatestr.split()[0])
            closingdate = datetime.now() + timedelta(hours=h)
        elif ('mins' or 'min') in closingdatestr:
            m = int(closingdatestr.split()[0])
            closingdate = datetime.now() + timedelta(minutes=m)
    except:
        raise Exception('Something Bad happen to the closing date')

    return closingdate


def getproductinfo(url):
    product_url = url
    product_html = requests.get(product_url).text
    product_soup = BeautifulSoup(product_html, parser)

    ##
    # Breadcrumb(D), Category(E), Username(F)
    ##
    try:
        bredcrumb = str(product_soup.find(
            'ul', {'class': 'breadCrumbs'}).text).strip()
        bredcrumbforcat = bredcrumb.split('>')
        category = bredcrumbforcat[1].strip()
        bredcrumb = " ".join(bredcrumb.split())
    except:
        category = na
        bredcrumb = na
    try:
        username = product_soup.find('a', {'class': 'seller-name'}).text
    except:
        username = na

    # Phone Number(G)
    pass

    # Listing ID(H), Title(I), Image URL(J)

    listingid = product_soup.find(
        'div', {'class': 'listing-id'}).text.split()[-1].strip()
    title = product_soup.find(
        'div', {'id': 'ListingTitleBox_TitleText'}).text.strip()
    try:
        imageurl = product_soup.find('img', {'class': 'main-image'})['src']
    except:
        imageurl = na

    ##
    # NewItme(K), Ping(L)
    ##
    newitem = product_soup.find('span', {'class': 'new-flag'})
    if newitem != None:
        newitem = "Yes"
    else:
        newitem = "No"

    ping = product_soup.find('span', {'class': 'bluefish-flag'})
    if ping != None:
        ping = "Yes"
    else:
        ping = "No"

    ##
    # Closing Date (M), Buy Now(N), Buy Now Price(O)
    ##
    closingdate = product_soup.find(
        'span', {'class': 'formatted-time'}).text.strip()
    closingdate = datetime_parser(closingdate)
    buynow = product_soup.find('div', {'class': 'buynow-title'})
    if buynow != None:
        buynow = "Yes"
    else:
        buynow = "No"

    buynowprice = product_soup.find(
        'div', {'class': 'large-text buynow-details buy-now-price-text'})
    if buynowprice != None:
        buynowprice = buynowprice.text
    else:
        buynowprice = "Empty"

    ##
    # Sold(P), Final Bid(Q), Closing Date+Time(R)
    # Refills when the scrapper visits this page second time
    ##
    try:
        closingtime = product_soup.find(
            'span', {'id': 'ClosingTime_ClosingTime'}).text
        closingtime = datetime_parser(closingtime)
        finalbid = product_soup.find(
            'div', {'class': 'bidding-title bidding-title-closed'})
        if finalbid != None and str(finalbid.text).strip() == "Final bid":
            sold = "Yes"
            finalbid = product_soup.find(
                'div', {'id': 'Bidding_CurrentBidValue'}).text
        else:
            finalbid = "Empty"
            sold = "No"
        visitcount = product_soup.find(
            'div', {'class': 'page-count'}).find_all('span', {'class': 'digit'})
        visitcounter = ''
        for x in visitcount:
            visitcounter += x.text
    except:
        sold = ''
        finalbid = ''
        closingtime = ''

    ##
    # No of bids(S),	Reserve met(T)
    ##
    totalbid = product_soup.find('div', {'id': 'Bidding_TotalBids'})
    if totalbid != None:
        try:
            try:
                totalbid = totalbid.find('strong').text
            except:
                totalbid = product_soup.find(
                    'div', {'id': "Bidding_CurrentBidValue"}).text
        except:
            totalbid = 'N/A'
        reservedmet = "No"
    else:
        totalbid = "N/A"
        reservedmet = "Yes"

    ##
    # Description(U), Shipping 1 and 2 (V,W), Store Location (X)
    ##
    description = str(product_soup.find(
        'div', {'class': 'bd padding-top'}).text)
    shippings = product_soup.find_all(
        'span', {'class': 'custom-shipping-price'})
    shippingone = ''
    shippingtwo = ''
    try:
        shippingone = shippings[0].text
        shippingtwo = shippings[1].text
    except:
        pass
    storelocation = product_soup.find(
        'li', {'id': 'ShippingDetails_SellerLocation'}).find('strong').text.strip()

    ##
    # Feedback(Y), Visit Counter(Z), Pickup Allow(AA), Member Since(AB), Entry Time(AC)
    ##
    feedback = product_soup.find(
        'span', {'id': 'SellerProfile_PercentPositiveFeedback'}).text + '%'
    visitcount = product_soup.find(
        'div', {'class': 'page-count'}).find_all('span', {'class': 'digit'})
    visitcounter = ''
    for x in visitcount:
        visitcounter += x.text
    pickup = product_soup.find(
        'li', {'id': 'ShippingDetails_DoesntAllowPickup'})
    if pickup != None and ("not allow" in pickup.text):
        pickup = "No"
    else:
        pickup = "Yes"
    membersince = product_soup.find(
        'span', {'class': 'member-info-list-content'}).text.strip()
    entrytime = datetime.now()

    ##
    # Other Requests
    ##
    try:
        quantity = product_soup.find(
            'span', {'id': 'BuyNow_QuantityAvailableLabel'}).text
    except:
        quantity = na

    try:
        store_name = product_soup.find(
            'div', {'id': 'SellerProfile_MemberText'}).find('a').text
        store_url = "https://www.trademe.co.nz" + product_soup.find(
            'div', {'id': 'SellerProfile_MemberText'}).find('a')['href']
    except:
        store_name = na

    ##
    # Prints all the field scrapped form the product page
    ##
    result = {"store_name": store_name, "store_url": store_url, 'product_url': product_url, "bredcrumb": bredcrumb, "category": category, "username": username, "phone": '', 'listingID': listingid, 'title': title, 'imageurl':
              imageurl, 'newitem': newitem, 'ping': ping, 'closingdate': closingdate, 'buynow': buynow, 'buynowprice': buynowprice, 'sold': "RE", 'finalbid': "RE", 'closingdatetime': "RE", 'totalbid': totalbid, 'reservedmet': reservedmet, 'description': description.strip(), 'shippingone': shippingone, 'shippingtwo': shippingtwo, 'storelocation': storelocation, 'feedback': feedback, 'visitcount': visitcounter, 'pickup': pickup, 'membersince': membersince, 'entrytime': entrytime}
    """
    print("Store (A):")
    print("Store URL (B):")
    print("Product URL (C):", product_url)
    print("Breadcrumb (D):", bredcrumb)
    print("Category Name (E):", category)
    print("Username (F):", username)
    print("Phone Number (G):")
    print("List ID (H):", listingid)
    print("Title (I):", title)
    print("Image URL (J):", imageurl)
    print("New Item (K):", newitem)
    print("Ping (L):", ping)
    print("Closing Date (M):", closingdate)
    print("Buy Now? (N):", buynow)
    print("Price (O):", buynowprice)
    print("Sold (P):")
    print("Final Bid (Q):")
    print("Closed Time and Date (R):")
    print("No of Bid (S):", totalbid)
    print("Reserve Met (T):", reservedmet)
    print("Details (U):", description.strip())
    print("Shipping 1 (V):", shippingone)
    print("Shipping 2 (W):", shippingtwo)
    print("Store Location (X):", storelocation)
    print("Feedback (Y):", feedback)
    print("Visit Count (Z):", visitcounter)
    print("Pickup (AA):", pickup)
    print("Member Since (AB):", membersince)
    print("Entry Time (AC):", entrytime)
    """
    return result
