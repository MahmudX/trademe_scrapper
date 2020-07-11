import ctypes
import store_data_scrapper as storedata
import product_link_scrapper as pdlink
import product_info_scrapper as productinfo
import pandas as pd
import concurrent.futures
from sqlalchemy import create_engine
from time import sleep
import menu
import mysql.connector
import os
from datetime import datetime, timedelta
from revisit_product import revisit_product_page
from csv import reader
def clear(): return os.system('cls')


ctypes.windll.kernel32.SetConsoleTitleW("Trademe Data Scrapper | MH_PSB")

category = []
productlinks = []
result = []
is_data_scrapping_complete = False
is_store_scrapping_complete = False
is_product_link_scrapping_complete = False
storeurl = []


def show_exception_message(e):
    print("\n"+"="*5)
    print("Couldn't retrieve product URLs.")
    print("Possible reason:", str(e))
    print("="*5+"\n")


def process_store_link():
    global category, enddate
    global dbConnection, sleeptime

    print("="*5)
    print("Store Scrap START")
    print("="*5)
    # storeurl = input("Enter a product link: ").split(',')
    for x in storeurl:
        category += storedata.storescrap(x.strip())
        print("Scrapping finished for", x)
        if sleeptime != '':
            sleep(sleeptime)
        if enddate != '' and enddate >= datetime.now():
            break
    print("="*5)
    print("Store Scrap END")
    print("="*5)
    is_store_scrapping_complete = True

    df = pd.DataFrame.from_dict(category)
    df.to_sql("storeinfo", dbConnection, if_exists='append')
    # df = df.sort_values(by='category_name',ascending=True)
    # print(df)
    # df.to_excel('output.xlsx')
    # with pd.ExcelWriter('storedata.xlsx', mode='w') as writer:
    #     df.to_excel(writer)


def process_pd_link():
    global category
    global productlinks, sleeptime, enddate
    sleep(10)
    print("="*5)
    print("Product Link Scrap START")
    print("="*5)
    count = 0
    while True:
        try:
            x = category[count]
            try:
                # print(x['category_url'])
                productlinks += pdlink.product_url_scrap(x['category_url'])
                if enddate != '' and enddate >= datetime.now():
                    break
                if sleeptime != '':
                    sleep(sleeptime)
            except Exception as e:
                print("Program failed for URL:", x['category_url'])
                show_exception_message(e)
            count += 1
        except Exception as d:
            if is_store_scrapping_complete:
                print(str(d))
                is_product_link_scrapping_complete = True
                break
            else:
                sleep(10)
    print("="*5)
    print("Product Link Scrap END")
    print("="*5)


def scrap_product_data():
    global productlinks
    global result
    sleep(30)
    print("="*5)
    print("Product Data Scrap START")
    print("="*5)
    count = 0
    while True:
        try:
            x = productlinks[count]
            # print(x)
            try:
                t = productinfo.getproductinfo(x)
                df = pd.DataFrame.from_dict([t])
                df.to_sql("productinfo", dbConnection, if_exists='append')
                result.append(
                    {"product_url": t["product_url"], "closingdate": t["closingdate"], 'sold': t['sold'], "listingID": t['listingID']})
                if sleeptime != '':
                    sleep(sleeptime)
                if enddate != '' and enddate >= datetime.now():
                    break
            except Exception as f:
                print("Program failed for cateory URL:", x)
                show_exception_message(f)
            count += 1
        except Exception as c:
            if is_product_link_scrapping_complete == True:
                is_data_scrapping_complete = True
                print(str(c))
                break
            else:
                sleep(10)
    print("="*5)
    print("Product Data Scrap END")
    print("="*5)


def revisit_page():
    global result, username, server, password
    sleep(130)
    print("="*5)
    print("Product Page Revisit START")
    print("="*5)
    item = 0
    while True:
        count = 0
        for x in result:
            try:
                if x['sold'] == "RE":
                    # sleep(10)
                    count += 1
                    if x['closingdate'] <= datetime.now():
                        closingtime, isSold, finalbid, visitcounter = revisit_product_page(
                            x['product_url'])
                        x['sold'] = isSold
                        x['finalbid'] = finalbid
                        x['closingdatetime'] = closingtime
                        x['visitcount'] = visitcounter
                        db = mysql.connector.connect(host=server, database='scraptable',
                                                     user=username, password=password)
                        mycursor = db.cursor()
                        mycursor.execute(
                            "UPDATE productinfo SET sold = '" + isSold + "' WHERE listingID = '"+x['listingID']+"'")
                        mycursor.execute(
                            "UPDATE productinfo SET finalbid = '" + finalbid + "' WHERE listingID = '"+x['listingID']+"'")
                        mycursor.execute(
                            "UPDATE productinfo SET closingdatetime = '" + closingtime + "' WHERE listingID = '"+x['listingID']+"'")
                        mycursor.execute(
                            "UPDATE productinfo SET visitcount = '" + visitcounter + "' WHERE listingID = '"+x['listingID']+"'")
                        db.commit()
                        result.remove(x)
                        if sleeptime != '':
                            sleep(sleeptime)

                    """
                    elif x['closingdate'] > datetime.now():
                        # print("="*5)
                        # print("Revisited for:", x['product_url'])
                        # print("="*5)
                        x['sold'] = 'Template SOLD'
                        x['finalbid'] = 'Templatefinalbid'
                        x['closingdatetime'] = 'Templateclosingtime'
                        x['visitcount'] = 'Templatevisitcounter'
                        db = mysql.connector.connect(host=server, database='scraptable',
                                                     user=username, password=password)
                        mycursor = db.cursor()
                        mycursor.execute(
                            "UPDATE productinfo SET sold = '" + x['sold'] + "' WHERE listingID = '"+x['listingID']+"'")
                        mycursor.execute(
                            "UPDATE productinfo SET finalbid = '" + x['finalbid'] + "' WHERE listingID = '"+x['listingID']+"'")
                        mycursor.execute(
                            "UPDATE productinfo SET closingdatetime = '" + x['closingdatetime'] + "' WHERE listingID = '"+x['listingID']+"'")
                        mycursor.execute(
                            "UPDATE productinfo SET visitcount = '" + x['visitcount'] + "' WHERE listingID = '"+x['listingID']+"'")
                        db.commit()
                        result.remove(x)
                    """

            except Exception as e:
                print("Exception from Revisit Page:", x['product_url'])
                print(str(e))
                sleep(10)
        if count == 0 and is_data_scrapping_complete == True:
            break
        elif len(result) < 1 and is_data_scrapping_complete == False:
            sleep(10)
    print("="*5)
    print("Product Page Revisit END")
    print("="*5)


def dbhandler():
    global username, password, server, dbConnection
    dbConnection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="admin"
    )

    mycursor = dbConnection.cursor()
    mycursor.execute("CREATE DATABASE IF NOT EXISTS scraptable")
    mycursor.close()
    dbConnection.close()

    sqlEngine = create_engine(
        'mysql+pymysql://'+username+':'+password+'@'+server+'/scraptable', pool_recycle=3600)

    dbConnection = sqlEngine.connect()


def startscrapping():
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        executor.submit(process_store_link)
        executor.submit(process_pd_link)
        executor.submit(scrap_product_data)
        executor.submit(revisit_page)


def main():
    global username, password, server, sleeptime, enddate

    isdbset = False
    while True:
        clear()
        menu.showmenu()
        c = input("Enter your choice: ")
        if c == '1':
            clear()
            if isdbset:
                try:
                    with open('storeurls.csv') as csv_file:
                        storeurlcsv = reader(csv_file, delimiter=',')

                        # storeurl = ["https://www.trademe.co.nz/Members/Listings.aspx?member=1049924",
                        #             "https://www.trademe.co.nz/stores/bigface"]
                        for x in storeurlcsv:
                            for y in x:
                                if y not in storeurl:
                                    storeurl.append(y)
                        if sleeptime != '':
                            print("The programm will wait "+str(sleeptime) +
                                  " seconds before making any request.")
                        if enddate != '':
                            print("The programm will end at ", str(enddate))
                        input(str(len(storeurl)) +
                              " store link(s) found. Press ENTER to proceed.")
                        startscrapping()
                except:
                    input(
                        "File named \'storeurls.csv\' wasn\'t found. " +
                        "Please resolve the issue and try again. " +
                        "Make sure the file is in the root folder." +
                        "Press ENTER to continue.")
            else:
                input("You must set MySQL before starting.\nPress ENTER to try again.")
        elif c == '2':
            while True:
                clear()
                menu.mysql_settings_menu()
                server = input("Enter Server: ")
                username = input("Enter Username: ")
                password = input("Enter Password: ")
                try:
                    mydb = mysql.connector.connect(
                        host=server.strip(),
                        user=username.strip(),
                        password=password.strip())
                    # print(mydb)
                    dbhandler()
                    isdbset = True
                    input("Connection Success. Press ENTER to go back.")
                    break
                except:
                    input("Invalid Parameter(s). Press ENTER to try again.")
        elif c == '3':
            clear()
            menu.inturruption_settings_menu()
            choice = input("Enter your choice: ")
            if choice == '1':
                try:
                    sleeptime = int(
                        input("How many seconds you want to wait before each requests: "))
                except:
                    sleeptime = ''
                    input(
                        "Input value must be an integer. Press ENTER to return to the main menu.")
            elif choice == '2':
                try:
                    enddate = input(
                        "Enter a date time formatted as \'mm/dd/yyyy h[24]/m\': ")
                    enddate = datetime.strptime(
                        enddate.strip(), '%m/%d/%Y %H/%M')
                    if enddate < datetime.now():
                        print("End date must be greater than current date.")
                        input("Press ENTER to return to the main menu.")
                        enddate = ''
                except Exception as e:
                    print(str(e))
                    enddate = ''
                    input("Incorrect datetime. Press ENTER to return to the main menu.")
            else:
                input("Invalid choice. Press ENTER to return to the main menu.")
        elif c == '4':
            clear()
            menu.show_about()
            input("\tPress Enter to go back.")
        elif c == '5':
            break
        else:
            input("Invalid Input. Press ENTER to try again.")
            clear()


if __name__ == "__main__":
    username = password = server = enddate = sleeptime = dbConnection = ''
    main()
