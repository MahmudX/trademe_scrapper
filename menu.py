def showmenu():
    print("1. Start Scraping")
    print("2. MySQL Settings")
    print("3. Interruption Settings")
    print("4. About")
    print("5. Exit")


def inturruption_settings_menu():
    print("1. Set Interval Time")
    print("\tIn seconds. 0 sec is the default.")
    print("2. Set Ending Time")
    print("\tEntered value must be formatted as mm/dd/yyyy h[24]/m")


def mysql_settings_menu():
    print("1. Enter Server Address")
    print("2. Enter User Name")
    print("3. Enter Password")
    print("4. Test Connection String")


def show_about():
    print("\n\n")
    print("\t"+'='*5)
    print('\tAbout the Author -')
    print('\tMahmudul Hasan')
    print('\tmahmudnotes@outlook.com')
    print('\tmahmudx.com')
    print('\tmahmudnotes.com\n')
    print("\tIn association with -")
    print("\tPritom Sarker Bishal")
    print('\tme.pritom@gmail.com')
    print('\t'+"="*5+'\n\n')
