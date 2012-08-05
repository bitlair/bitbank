import MySQLdb
import ConfigParser
import sys

from decimal import *
from bank import Bank
from ansi import clear, cursor, Color
from wifi import Wifi
from time import sleep
from subprocess import call

try:
    import RPi.GPIO as GPIO
    GPIO.setup(24, GPIO.OUT)
except:
    print("No RPi.GRIO")

import logging
logging.basicConfig(filename='bitbank.log',level=logging.DEBUG)

config = ""

def open_la():
    global config
    if config.get('Kassa','kassala') == "True":
        GPIO.output(24, True)
        sleep(1)
        GPIO.output(24, False)

def show_logo():
    # set palette color 1 to our color
    print "\x1b]P1FD5A1E"

    logo = """
#                         #
#     #   #               #
### # ##  #    #  #  ##   ###  #   ##
# # # #   #     # # #     # #   # #
### #  ##  ## ### # #     ### ### #

"""
    lines = logo.splitlines()

    for y, line in enumerate(lines):
        for x, char in enumerate(line):
            if char != ' ':
                sys.stdout.write("\x1b[00;41m \x1b[00;40m")
            else:
                sys.stdout.write(" ")
        sys.stdout.write("\n")

def process_line(bank,line):
    user_input = filter (lambda a: a != "", line.split(" "))
    if "deposit" in user_input:
        indexje = user_input.index("deposit")+1
        bank.deposit(user_input[indexje])
        bank.logout()
        open_la()
        return bank

    if "withdraw" in user_input:
        indexje = user_input.index("withdraw")+1
        bank.withdraw(user_input[indexje])
        bank.logout()
        open_la()
        return bank

    if "plastic" in user_input:
        indexje = user_input.index("plastic")+1
        bank.plastic_add(user_input[indexje])
        return bank

    if Decimal(user_input[0]) < 1000:
        bank.withdraw(user_input[0])
        bank.logout()
        if user_input[0] < 0:
            open_la()
        return bank

    for x in user_input:
        if bank.product_add(x) == True:
            continue
    bank.account()
    bank.logout()
    return bank

def help():
    return """
Examples:
    4029764001807 jdoe          John pays for one Club Mate.
    5 jdoe                      John withdraws EUR 5.00.
    deposit 5 jdoe              John deposits EUR 5.00 into his account.

    <username> or <userbarcode> Login
    4029764001807               Add 1 Mate to your tab
    bank                        Pay your tab with your bank account
    pay/kas                     Pay your tab to the register
    list                        Price list
    """

def run():
    show_logo() 
    _Runner = True
    global config
    config = ConfigParser.ConfigParser()
    config.read('bitbank.cfg')

    db = MySQLdb.connect(host=config.get('Database', 'hostname'),
        user=config.get('Database', 'username'),
        passwd=config.get('Database', 'password'),
        db=config.get('Database', 'database'))
 
    bank = Bank(db)

    if config.get('Bitwifi','enable') == "True":
        wifi = Wifi(config)

    defaultusername = bank.username
    while _Runner == True:
        if bank.username != defaultusername:
            barcode=raw_input('%s%s%s please scan [product barcode]: ' % (str(Color('yellow')),bank.username,str(Color('reset'))))
        else:
            barcode=raw_input('Please scan [usercard,product barcode]: ')

        line = filter (lambda a: a != "", barcode.split(" "))
        if len(line) > 1 and bank.login(line[-1]) == True:
            bank = process_line(bank,barcode)
            continue

        if barcode == "clear" or barcode == "abort" or barcode == "reset" or barcode.startswith('ABORT'):
            bank.reset()

        elif barcode == "pay" or barcode == "kas" or barcode.startswith('KAS'):
            print "\x1b[H\x1b[J"
            show_logo()
            bank.pay()
            open_la()

        elif barcode == "logout" or barcode.startswith('LOGOUT'):
            print "\x1b[H\x1b[J"
            show_logo() 
            bank.logout()

        elif barcode == "bank" or barcode.startswith('BANK'):
            print "\x1b[H\x1b[J"
            show_logo()
            bank.account()

        elif barcode.startswith('deposit'):
            temp = barcode.split(' ')
            amount = temp[1]
            bank.deposit(amount)
            open_la()

        elif barcode.startswith('withdraw'):
            temp = barcode.split(' ')
            amount = temp[1]
            bank.withdraw(amount)
            open_la()

        elif barcode.startswith('plastic'):
            temp = barcode.split(' ')
            amount = temp[1]
            bank.plastic_add(amount)

        elif barcode.startswith('adduser'):
            temp = barcode.split(' ')
            bank.account_add(temp[1])
        elif barcode.startswith('list'):
            bank.list() 

        elif barcode.startswith('mac') and config.get('Bitwifi','enable') == "True":
            wifi.unregister_list()

        elif barcode.startswith('register') and config.get('Bitwifi','enable') == "True":
            temp = barcode.split(' ')
            if bank.member==0:
                print "403: Access denied"
                continue
            wifi.registration(bank.username,temp[1],temp[2])

        elif barcode == "help":
            print help()

        elif barcode == "exit":
            _Runner = False
        elif barcode == "":
            continue
        else:
            if bank.login(barcode) != True:
                if bank.product_add(barcode) != True:
                    print "404: Not found"

if __name__ ==  '__main__':
    print "\x1b[H\x1b[J"
    sys.exit(run())
           
