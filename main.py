import os
import getpass
import hashlib
import sqlite3
import hidepass
import base64
import string
import random

from datetime import datetime
from time import sleep
from random import randint

usern = getpass.getuser()

basePath = "/media/"+usern

key = """
        8 8 8 8                     ,oooo.
        8a8 8a8                    oP    ?b
        dXXXaXXXxxxxxxxxxxxxxxxxxxxx8    8b
        `""^""'                    ?oooooP'
    """

def sha256Hash(string):
    return hashlib.sha256((string).encode()).hexdigest()

def isPrime(num):
    for i in range(2,num):
        if(num%i == 0):
            return False
    return True
def prmList(lnth):
    i=0
    j=1
    prmLst = []
    while(i<lnth):
        j+=1
        if(isPrime(j)):
            prmLst.append(j)
        else:
            continue
        i+=1
    return prmLst
def cookKey(key):
    key = sha256Hash(key)
    num = 0
    cnt = 0
    for i in key:
        if(cnt%2 == 1 or num < 10):
            num += ord(i)
        else:
            num -= ord(i)
        cnt+=1
    return num
def encryptAlgo(txt,passKey):
    txt = txt[::-1]
    encTxt = ""
    prmNums = prmList(len(txt))
    cnt = 0
    for i in txt:
        encTxt += (chr(ord(i)+prmNums[cnt]+cookKey(passKey)))
        cnt+=1
    return base64.b64encode(encTxt.encode()).decode()

def decryptAlgo(txt,passKey):
    txt = base64.b64decode(txt).decode()
    encTxt = ""
    prmNums = prmList(len(txt))
    cnt = 0
    for i in txt:
        encTxt += (chr(ord(i)-prmNums[cnt]-cookKey(passKey)))
        cnt+=1
    encTxt = encTxt[::-1].strip()
    return encTxt
def encryptText(txt,passKey):
    return encryptAlgo(encryptAlgo(encryptAlgo(txt,passKey),passKey),passKey)
def decryptText(txt,passKey):
    return decryptAlgo(decryptAlgo(decryptAlgo(txt,passKey),passKey),passKey)


def logToDB(msg):
    conn.execute("insert into appLogs (desc, dateTime) values('"+msg+"','"+getCrntDataTime()+"')")
    conn.commit()
def genKey():
    hostid = os.popen("hostid").read().replace("\n","")
    hostname = os.popen("hostname").read().replace("\n","")
    scrnResol = os.popen("xrandr | grep '*'").read().replace("\n","")
    uuidgen = os.popen("uuidgen").read().replace("\n","")
    return sha256Hash(hostid+hostname+scrnResol+str(randint(100000,999999)))

def getCrntDataTime():
    return datetime.now().strftime("%d-%m-%y|%H:%M:%S")
def genRandVerif():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k = 4))
def storeRetrivePass(dir):
    global conn, mstrPswd
    devName = dir
    print(len("Device selected:  ")*" "+Fore.YELLOW+(len(devName)+2)*"-")
    print(Fore.WHITE+"Device selected: "+Fore.YELLOW+"| "+Fore.GREEN+devName+Style.RESET_ALL+Fore.YELLOW+" |")
    print(len("Device selected:  ")*" "+Fore.YELLOW+(len(devName)+2)*"-")
    dir = os.path.join(basePath,devName)
    print(Fore.YELLOW+"\nLooking if a password file exists....")
    print()
    if(os.path.exists(dir+"/.seKeyYourPasses.db")):
        print(Fore.GREEN+"File found")

        conn = sqlite3.connect(dir+"/.seKeyYourPasses.db")
        datab = conn.execute('select * from userInfo')
        for i in datab:
            if(i[1] != sha256Hash(compKey+"HOHAHA131346647979")):
                print(Fore.RED+Back.WHITE+" This device was not programmed from this computer, hence you can't access it.  \n  ( Either this is not the computer or you have deleted some important files )  "+Style.RESET_ALL)
                logToDB("Someone attempted to retrieve passwords from another computer")
                exit(1)
            while(True):
                try:
                    mstrPswd = hidepass.getpass(prompt=Fore.CYAN+"Enter master password    : "+Fore.WHITE)
                    if(sha256Hash(mstrPswd+"saltyLakeBOIS@314159265") != i[0]):
                        print(Fore.RED+Back.WHITE+" Incorrect password !! Try again "+Style.RESET_ALL)
                        logToDB("Someone entered an incorrect password")
                        continue
                    break
                except:
                    print("\n!! CANCELLED !!")
                    if(len(listMedia) == 1):
                        exit(1)
                    return
    else:
        print(Fore.RED+"File not found")
        print(Fore.GREEN+"Creating new one....\n")
        try:
            while(True):
                mstrPswd = hidepass.getpass(prompt=Fore.CYAN+"Enter a master password    : "+Fore.WHITE)
                if(len(mstrPswd.replace(" ","")) < 8):
                    print(Fore.RED+Back.WHITE+" Please enter a valid password!! (min 8 characters) "+Style.RESET_ALL)
                    continue
                confPswd = hidepass.getpass(prompt=Fore.CYAN+"Confirm the master password: "+Fore.WHITE)
                if(confPswd != mstrPswd):
                    print(Fore.RED+Back.WHITE+" Password confirmation mismatch "+Style.RESET_ALL)
                    continue
                break
        except KeyboardInterrupt:
            print("\n!! CANCELLED !!")
            if(len(listMedia) == 1):
                exit(1)
            return
        conn = sqlite3.connect(dir+"/.seKeyYourPasses.db")
        conn.execute("""
        CREATE TABLE userInfo(
            mstrpswd text,
            cmptrUId text
        )
        """)
        conn.execute("""
        CREATE TABLE appLogs(
            logId integer PRIMARY KEY AUTOINCREMENT NOT NULL,
            desc TEXT,
            dateTime TEXT
        )
        """)
        conn.execute("""
        CREATE TABLE pswdData(
            pswdId integer PRIMARY KEY AUTOINCREMENT NOT NULL,
            site text,
            mail text,
            pswd text
        )
        """)
        try:
            logToDB("Database created")
        except Exception as e:
            print(e)
            exit()
        conn.execute("insert into userInfo values('"+sha256Hash(mstrPswd+"saltyLakeBOIS@314159265")+"','"+sha256Hash(compKey+"HOHAHA131346647979")+"')")
        conn.commit()
    sleep(0.5)
    os.system("clear")

    print(Fore.CYAN+figlet_format("SeKeyYour",font="univers",width=1000),end="\r")
    print(key+Style.RESET_ALL)
    print("Press ctrl+c to exit or cancel, type \\h for help and \\a for abouts")
    print(len("Device selected:  ")*" "+Fore.YELLOW+(len(devName)+2)*"-")
    print(Fore.WHITE+"Device selected: "+Fore.YELLOW+"| "+Fore.GREEN+devName+Style.RESET_ALL+Fore.YELLOW+" |")
    print(len("Device selected:  ")*" "+Fore.YELLOW+(len(devName)+2)*"-")

    while(True):
        try:
            inp = input(Fore.YELLOW+"sekeyyour/"+devName.lower().replace(" ","_")+":$ "+Fore.WHITE)
            if(inp.replace(" ","") == "exit"):
                print("!! EXITED !!")
                if(len(listMedia) == 1):
                    exit(1)
                return
            elif(inp == "logs"):
                logs = conn.execute("select * from appLogs")
                t = Texttable()
                t.set_cols_align(['c','c','c'])
                for i in logs:
                    t.add_rows([['Date','Time','Description'],[i[2].split("|")[0],i[2].split("|")[1],i[1]]])
                    pass
                if(t.draw() == None):
                    print("No activities recorded yet!")
                    continue
                print(t.draw())
            elif(inp[:3] == "see"):
                t = Texttable()
                t.set_cols_align(['c','c','c','c'])
                if(inp[4:] == "all" or inp[3:] == ""):
                    logs = conn.execute("select * from pswdData")
                elif(inp[4:7] == "id "):
                    try:
                        int(inp[7:])
                    except:
                        print(Fore.RED+Back.WHITE+" Please enter an integer as an argument "+Style.RESET_ALL)
                        continue
                    logs = conn.execute("select * from pswdData where pswdId = "+inp[7:])
                elif(inp[4:9] == "site "):
                    logs = conn.execute("select * from pswdData where site = '"+encryptText(inp[9:].strip(),sha256Hash(compKey+"\b"+mstrPswd))+"'")
                elif(inp[4:9] == "usrn "):
                    logs = conn.execute("select * from pswdData where mail = '"+encryptText(inp[9:].strip(),sha256Hash(compKey+"\b"+mstrPswd))+"'")
                else:
                    print(Fore.RED+Back.WHITE+" Please enter a valid argument "+Style.RESET_ALL)
                    continue
                for i in logs:
                    pswd = decryptText(i[3],sha256Hash(compKey+"\b"+mstrPswd))
                    if(inp.strip() == "see"):
                        pswd = "*"*8
                    t.add_rows([["ID","Site Name","Email/Username","Password"],[i[0],decryptText(i[1],sha256Hash(compKey+"\b"+mstrPswd)),decryptText(i[2],sha256Hash(compKey+"\b"+mstrPswd)),pswd]])
                if(t.draw() == None):
                    print(Fore.RED+Back.WHITE+" Nothing found :-( "+Style.RESET_ALL)
                    continue
                print(t.draw())
            elif(inp == "ent"):
                try:
                    while(1):
                        site = input(Fore.CYAN+"Enter site/app name           : "+Fore.WHITE)
                        if(len(site.strip()) == 0):
                            print(Fore.RED+Back.WHITE+" Please enter a valid site/app name "+Style.RESET_ALL)
                            continue
                        break
                    usrn = input(Fore.CYAN+"Enter username/email address (leave blank if not applicable)  : "+Fore.WHITE)
                    while(1):
                        pswd = input(Fore.CYAN+"Enter password                : "+Fore.WHITE)
                        if(len(pswd.strip()) == 0):
                            print(Fore.RED+Back.WHITE+" Please enter a valid password!!"+Style.RESET_ALL)
                            continue
                        break
                    conn.execute("insert into pswdData (site,mail,pswd) values ('"+encryptText(site,sha256Hash(compKey+"\b"+mstrPswd))+"','"+encryptText(usrn,sha256Hash(compKey+"\b"+mstrPswd))+"','"+encryptText(pswd,sha256Hash(compKey+"\b"+mstrPswd))+"')")
                    conn.commit()
                    print(Fore.GREEN+"Entry successful")
                    logToDB("New entry made")
                except KeyboardInterrupt:
                    print("\n!! CANCELLED !!")
            elif(inp[:3] == "dlt"):
                try:
                    int(inp[4:])
                except:
                    print(Fore.RED+Back.WHITE+" Please enter an integer as an argument "+Style.RESET_ALL)
                    continue
                try:
                    t = Texttable()
                    t.set_cols_align(['c','c','c','c'])
                    for i in conn.execute("select * from pswdData where pswdId = "+inp[4:]):
                        t.add_rows([["ID","Site Name","Email/Username","Password"],[i[0],decryptText(i[1],sha256Hash(compKey+"\b"+mstrPswd)),decryptText(i[2],sha256Hash(compKey+"\b"+mstrPswd)),decryptText(i[3],sha256Hash(compKey+"\b"+mstrPswd))]])
                    if(t.draw() == None):
                        print(Fore.RED+Back.WHITE+" Nothing found :-( "+Style.RESET_ALL)
                        continue
                    print("Delete the following entry?")
                    print(t.draw())
                    verifKey = genRandVerif()
                    q = input("Type the following for confirmation ( "+verifKey+" ): ")
                    if(q == verifKey):
                        conn.execute("delete from pswdData where pswdId = "+inp[4:])
                        conn.commit()
                        print(Fore.GREEN+"Entry deleted successfully")
                        logToDB("Entry deleted")
                        continue
                    print("!!CANCELLED!!")
                except KeyboardInterrupt:
                    print("\n!!CANCELLED!!")
            elif(inp[:4] == "updt"):
                try:
                    int(inp [5:])
                except:
                    print(Fore.RED+Back.WHITE+" Please enter an integer as an argument "+Style.RESET_ALL)
                    continue
                try:
                    t = Texttable()
                    t.set_cols_align(['c','c','c','c'])
                    for i in conn.execute("select * from pswdData where pswdId = "+inp[5:]):
                        t.add_rows([["ID","Site Name","Email/Username","Password"],[i[0],decryptText(i[1],sha256Hash(compKey+"\b"+mstrPswd)),decryptText(i[2],sha256Hash(compKey+"\b"+mstrPswd)),decryptText(i[3],sha256Hash(compKey+"\b"+mstrPswd))]])
                    if(t.draw() == None):
                        print(Fore.RED+Back.WHITE+" Nothing found :-( "+Style.RESET_ALL)
                        continue
                    print("Update the following entry?")
                    print(t.draw())
                    q = input("(Y)es/(N)o: ")
                    if(q.lower() == "y"):
                        print("\nLeave blank if not to be changed")
                        qId = str(i[0])
                        site = decryptText(i[1],sha256Hash(compKey+"\b"+mstrPswd))
                        usrn = decryptText(i[2],sha256Hash(compKey+"\b"+mstrPswd))
                        pswd = decryptText(i[3],sha256Hash(compKey+"\b"+mstrPswd))
                        updt_site = input(Fore.CYAN+"Enter new site/app name (currently '"+site+"'): "+Fore.WHITE)
                        updt_usrn = input(Fore.CYAN+"Enter new username/mail id (currently '"+usrn+"')(leave an asteriks(*) if making it blank): "+Fore.WHITE)
                        updt_pswd = input(Fore.CYAN+"Enter new password (currently '"+pswd+"'): "+Fore.WHITE)
                        if(updt_site.strip() == ""):
                            updt_site = site
                        if(updt_pswd.strip() == ""):
                            updt_pswd = pswd
                        if(updt_usrn.strip() == ""):
                            updt_usrn = usrn
                        elif(updt_usrn.strip() == "*"):
                            updt_usrn = ""
                        conn.execute("update pswdData set site='"+encryptText(updt_site,sha256Hash(compKey+"\b"+mstrPswd))+"', mail='"+encryptText(updt_usrn,sha256Hash(compKey+"\b"+mstrPswd))+"', pswd = '"+encryptText(updt_pswd,sha256Hash(compKey+"\b"+mstrPswd))+"' where pswdId = "+qId)
                        conn.commit()
                        logToDB("An entry was updated")
                        continue
                    print("!!CANCELLED!!")
                except KeyboardInterrupt:
                    print("\n!!CANCELLED!!")
            elif(inp[:3] == "cpy"):
                try:
                    int(inp[4:])
                except:
                    print(Fore.RED+Back.WHITE+" Please enter an integer as an argument "+Style.RESET_ALL)  
                    continue
                for i in conn.execute("select * from pswdData where pswdId = "+str(inp[4:])):
                    copy(decryptText(i[3],sha256Hash(compKey+"\b"+mstrPswd)))
                print(Fore.GREEN+"Password copied for site/app name "+decryptText(i[1],sha256Hash(compKey+"\b"+mstrPswd)),end="")
                if(i[2]!=""):
                    print(" and username/mail id "+decryptText(i[2],sha256Hash(compKey+"\b"+mstrPswd)),end="")
                print(" successfully")
            elif(inp == "xlog"):
                conn.execute("delete from appLogs")
                conn.commit()
                print(Fore.GREEN+"All logs deleted successfully")
            elif(inp == "clear"):
                os.system("clear")
            elif(inp == "cmp"):
                try:
                    mPswd = hidepass.getpass(prompt=Fore.CYAN+"Enter current master password: "+Fore.WHITE)
                    if(mPswd == mstrPswd):
                        while(1):
                            nPswd = hidepass.getpass(prompt=Fore.CYAN+"Enter new master password    : "+Fore.WHITE)
                            if(len(nPswd) < 8):
                                print(Fore.RED+Back.WHITE+" Please enter a valid password (min 8 characters) "+Style.RESET_ALL)
                                continue
                            cPswd = hidepass.getpass(prompt=Fore.CYAN+"Confirm new master password  : "+Fore.WHITE)
                            if(nPswd != cPswd):
                                print(Fore.RED+Back.WHITE+" Password confirmation mismatch "+Style.RESET_ALL)
                                continue
                            break
                        print("Wait!! Do not quit the program.....")
                        for i in conn.execute("select * from pswdData"):
                            qId = str(i[0])
                            site = decryptText(i[1],sha256Hash(compKey+"\b"+mPswd))
                            usrn = decryptText(i[2],sha256Hash(compKey+"\b"+mPswd))
                            pswd = decryptText(i[3],sha256Hash(compKey+"\b"+mPswd))
                            conn.execute("update pswdData set site='"+encryptText(site,sha256Hash(compKey+"\b"+nPswd))+"',mail='"+encryptText(usrn,sha256Hash(compKey+"\b"+nPswd))+"',pswd='"+encryptText(pswd,sha256Hash(compKey+"\b"+nPswd))+"' where pswdId = "+qId)
                            conn.commit()
                        conn.execute("update userInfo set mstrpswd = '"+sha256Hash(nPswd+"saltyLakeBOIS@314159265")+"'")
                        conn.commit()
                        print(Fore.GREEN+"Password changed successfully")
                        logToDB("Password changed")
                        mstrPswd = nPswd
                    else:
                        print(Fore.RED+Back.WHITE+" Incorrect password "+Style.RESET_ALL)
                        continue
                except KeyboardInterrupt:
                    print("\n!!CANCELLED!!")
            elif(inp == "reset"):
                print("Reset the application !?")
                mPswd = hidepass.getpass(prompt=Fore.CYAN+"Enter master password for confirmation: "+Fore.WHITE)
                if(mPswd == mstrPswd):
                    os.system("rm "+dir+"/.seKeyYourPasses.db")
                    print(Fore.GREEN+"\nDatabase deleted and all entries cleared successfully !!\n")
                    print(Fore.CYAN+figlet_format("GoodBye!",font="nancyj",width=1000),end="\r")
                    exit(1)
                else:
                    print(Fore.RED+Back.WHITE+" Incorrect password "+Style.RESET_ALL)

            elif(inp == "\\h"):
                print("""\n|HELP|
                -> clear - clear screen
                -> exit  - exits the program
                -> logs  - display application usage logs
                -> ent   - make an entry to the password manager
                -> see   - displays passwords along with site name and username/email, use it as follows:
                        (*) see                      - show all entries but blocking the password
                        (*) see all                  - shows all the entries
                        (*) see id <query id>        - shows entry corresponding to the id
                        (*) see site <site name>     - shows all entries corresponding to the site name
                        (*) see usrn <username name> - shows all entries corresponding to the username/email id
                -> dlt   - deletes an entry with the corresponding id, use it as follows:
                        (*) dlt <query id>
                -> cpy   - copy the password from entry with the corresponding id, use it as follows:
                        (*) cpy <query id>
                -> updt  - updates an entry with the corresponding id, use it as follows:
                        (*) updt <query id>
                -> cmp   - change master password
                -> xlog  - deletes all the application usage logs
                -> reset - resets the whole application (deletes all the entries and logs and clears the master password too)
                            ⚠ use with caution
                -> \\h    - help
                -> \\a    - about\n
                    """+Fore.CYAN+"get <query id> via 'see' command\n")
            elif(inp == "\\a"):
                print("""\n|ABOUT|\n\tThis is a CLI, python based external device password manager created by Rhiddhi Prasad Das.\n\tYou can use this software to securely store all your passwords on an external device\n\tthat can only be accessed by the computer the database was created by.\n
                Github : https://github.com/rpd-512/
                Twitter: https://twitter.com/RhiddhiD
                Fiverr : https://www.fiverr.com/rpd_512
                Email  : rhiddhiprasad@gmail.com\n""")
        except KeyboardInterrupt:
            print("\n!! EXITED !!")
            if(len(listMedia) == 1):
                exit(1)
            return


if(not os.path.isfile("/var/log/.sekeyyour/.keystore")):
    if(os.geteuid()!=0):
        print("Please run as superuser")
    else:
        try:
            try:
                os.mkdir("/var/log/.sekeyyour/")
            except:
                pass
            with open("/var/log/.sekeyyour/.keystore","w") as kFile:
                kFile.write(genKey())
            print("Rerun (as the current user)")
        except Exception as e:
            print(e)
            pass
    exit(1)
else:
    with open("/var/log/.sekeyyour/.keystore","r") as kFile:
        compKey = kFile.read()


from colorama import Fore, Back, Style
from pyfiglet import figlet_format
from pyperclip import copy
from texttable import Texttable

listMedia = os.listdir(basePath)

if(len(listMedia) == 0):
    print("No devices found")
    exit(1)
print("Starting ......")

copy("")
os.system("clear")

print(Fore.CYAN+figlet_format("SeKeyYour",font="univers",width=1000),end="\r")
print(key+Style.RESET_ALL)
print("Press ctrl+c to exit or cancel")

while(1):
    if(len(listMedia) == 1):
        storeRetrivePass(listMedia[0])
        continue
    cnt = 1
    try:
        print()
        listMedia.sort(key=len,reverse=True)
        print(Fore.WHITE+(len(listMedia[0])+8)*"-")
        for m in listMedia:
            print(Fore.WHITE+"| "+Fore.YELLOW+"("+str(cnt)+") "+Fore.GREEN+m+" "*((len(listMedia[0])+1)-len(m))+Fore.WHITE+"|")
            cnt+=1
        print(Fore.WHITE+(len(listMedia[0])+8)*"-")
        print()
        while(1):
            try:
                inp = 0
                inp = int(input("\nSelect a media device to store/retrieve your passwords (select a number between 1 and "+str(cnt-1)+", type `0` to exit) : "))
                if(inp == 0):
                    exit(1)
                print()
                storeRetrivePass(listMedia[inp-1])
                break
            except KeyboardInterrupt:
                print()
                exit(1)
            except Exception as e:
                print(" "+len(" Please enter a valid input ")*"-")
                print("|"+Back.WHITE+Fore.RED+" Please enter a valid input "+Style.RESET_ALL+"|")
                print(" "+len(" Please enter a valid input ")*"-")
                print(e)

    except KeyboardInterrupt:
        break
