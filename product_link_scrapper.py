from bs4 import BeautifulSoup
import requests
parser = "html.parser"


def product_url_scrap(link):
    '''
    returns a list of links
    '''
    pagecounter = 1
    catItemLink = []
    catItemLinklength = 0

    while True:
        r = requests.get(link+"&page="+str(pagecounter))
        soup = BeautifulSoup(r.text, parser)
        b = soup.find('p', {'class': 'no-results-text'})
        if b != None:
            break
        try:
            tls = soup.find("div", {'class': 'supergrid-overlord'})
            tls = tls.find_all('a')
        except:
            tls = soup.find('div', {'id': 'ListViewList'})
            tls = soup.find_all('a')
        for l in tls:
            try:
                tl = "https://www.trademe.co.nz"+l['href']
                tl = tl.split('?')[0]
                if tl not in catItemLink:
                    catItemLink.append(tl)
            except:
                continue
        if catItemLinklength == len(catItemLink):
            break
        else:
            catItemLinklength = len(catItemLink)
            pagecounter += 1
    return catItemLink
