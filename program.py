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
    print("Possible reason:", str(e))
    print("="*5+"\n")


def process_store_link():
    global category, enddate
    global dbConnection, sleeptime

    print("="*5)
    print("Store Scrap START")
    print("="*5)
    for x in storeurl:
        urls = storedata.storescrap(x.strip())
        category += urls
        for y in urls:
            sql = "SELECT * FROM storeinfo WHERE category_url LIKE '"+y['category_url']+"'"
            try:
                dff = pd.read_sql_query(sql, dbConnection)
            except:
                dff = None
            if dff is None or len(dff.index) == 0:
                df = pd.DataFrame.from_dict([y])
                df.to_sql("storeinfo", dbConnection, if_exists='append')

        print("Scrapping finished for", x)
        if sleeptime != '':
            sleep(sleeptime)
        if enddate != '' and enddate >= datetime.now():
            break
    print("="*5)
    print("Store Scrap END")
    print("="*5)
    is_store_scrapping_complete = True


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
                print("Exception from process_pd_link")
                print("Program failed for category URL:", x['category_url'])
                show_exception_message(e)
            count += 1
        except Exception as d:
            if is_store_scrapping_complete:
                show_exception_message(d)
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
    try:
        sql = "SELECT product_url,closingdate, listingID, sold FROM productinfo"
        df = pd.read_sql_query(sql,dbConnection)
        for index,row in df.iterrows():
            d =dict(row)
            result.append(d)
        print("="*5)
        print("Recovered",len(result),"URLs")
        print("="*5)
    except:
        pass
    count = 0
    while True:
        try:
            x = productlinks[count]
            try:
                sql = "SELECT * FROM productinfo WHERE product_url LIKE '"+x+"'"
                try:
                    dff = pd.read_sql_query(sql, dbConnection)
                except:
                    dff = None
                if dff is None or len(dff.index) == 0:
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
                print("Program failed for product URL:", x)
                show_exception_message(f)
            count += 1
        except Exception as c:
            if is_product_link_scrapping_complete == True:
                is_data_scrapping_complete = True
                show_exception_message(c)
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
                if x['sold'] == "":
                    count += 1
                    if x['closingdate'] + timedelta(minutes=40) <= datetime.now():
                        closingtime, isSold, finalbid, visitcounter = revisit_product_page(
                            x['product_url'])
                        x['sold'] = isSold
                        x['finalbid'] = finalbid
                        x['closingdatetime'] = closingtime
                        x['visitcount'] = visitcounter
                        db = mysql.connector.connect(host=server, database='scraptable',
                                                     user=username, password=password)
                        mycursor = db.cursor(buffered=True)
                        mycursor.execute(
                            "UPDATE productinfo SET sold = '" + isSold + "' WHERE listingID = '"+x['listingID']+"'")
                        mycursor.execute(
                            "UPDATE productinfo SET finalbid = '" + finalbid + "' WHERE listingID = '"+x['listingID']+"'")
                        mycursor.execute(
                            "UPDATE productinfo SET closingdatetime = '" + closingtime + "' WHERE listingID = '"+x['listingID']+"'")
                        mycursor.execute(
                            "UPDATE productinfo SET visitcount = '" + visitcounter + "' WHERE listingID = '"+x['listingID']+"'")
                        mycursor.execute("SELECT * FROM productinfo ORDER BY 'closingdatetime' ASC")
                        db.commit()
                        
                        sql = "SELECT * FROM productinfo WHERE listingID LIKE '"+x['listingID']+"'"
                        dff = pd.read_sql_query(sql, dbConnection)
                        dff.to_sql("soldproducts", dbConnection, if_exists='append')
                        result.remove(x)
                        if sleeptime != '':
                            sleep(sleeptime)
            except Exception as e:
                print("Exception from Revisit Page:", x['product_url'])
                show_exception_message(e)
                sleep(10)
        if count == 0 and is_data_scrapping_complete == True:
            break
        elif len(result) < 1 and is_data_scrapping_complete == False:
            sleep(10)
        else:
            sleep(60)
    print("="*5)
    print("Product Page Revisit END")
    print("="*5)


def dbhandler():
    global username, password, server, dbConnection
    dbConnection = mysql.connector.connect(
        host=server,
        user=username,
        password=password
    )

    mycursor = dbConnection.cursor()
    mycursor.execute("CREATE DATABASE IF NOT EXISTS scraptable")
    mycursor.close()
    dbConnection.close()

    sqlEngine = create_engine(
        'mysql://'+username+':'+password+'@'+server+'/scraptable', pool_recycle=3600)

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
                        try:
                            with open('categoryurls.csv') as csv_file:
                                catcsv = reader(csv_file, delimiter=',')
                                for x in catcsv:
                                    for y in x:
                                        if y not in category:
                                            category.append(y)
                            print(len(category)," category URLs restored")
                        except Exception as e:
                            show_exception_message(e)
                            print(len(category)," category URLs restored")
                        startscrapping()                        
                except Exception as exx:
                    print(
                        "Formal Cause: File named \'storeurls.csv\' wasn\'t found. " +
                        "Please resolve the issue and try again. " +
                        "Make sure the file is in the root folder.")
                    print("ECause:",str(exx))
                    input("Press ENTER to continue.")
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
                except Exception as e:
                    input("Invalid Parameter(s)"+str(e)+". Press ENTER to try again.")
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
                    show_exception_message(e)
                    enddate = ''
                    input("Incorrect datetime. Press ENTER to return to the main menu.")
            else:
                input("Invalid choice. Press ENTER to return to the main menu.")
        elif c == '4':
            break
        else:
            input("Invalid Input. Press ENTER to try again.")
            clear()


if __name__ == "__main__":
    username = password = server = enddate = sleeptime = dbConnection = ''
    try:
        with open('credentials.csv') as credentials_csv:
            cred = list(reader(credentials_csv, delimiter=','))
            for x in cred:
                print(x)
            server = cred[0][0]
            password = cred[2][0]
            username = cred[1][0]
        print("Credntials restored")
        print(username,password,server)
    except Exception as e:
        show_exception_message(e)
    input("Press ENTER to cont.")
    main()