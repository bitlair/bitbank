import MySQLdb
import ConfigParser
import sys

from decimal import *
from bank import Bank
from ansi import clear, cursor, Color
from wifi import Wifi
from time import sleep

def open_la():
    from subprocess import call
    call("./open")

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
    user_input = line.split(" ")
    if "deposit" in user_input:
        indexje = user_input.index("deposit")+1
        bank.deposit(user_input[indexje])
        bank.logout()
        return bank

    if "withdraw" in user_input:
        indexje = user_input.index("withdraw")+1
        bank.withdraw(user_input[indexje])
        bank.logout()
        return bank

    if Decimal(user_input[0]) < 1000:
        bank.withdraw(user_input[0])
        bank.logout()
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

    If you're unsure of the syntax, just type the command, press enter, and
    read the instructions.
    """

def run():
    show_logo() 
    _Runner = True

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

        line = barcode.split(" ")
        if bank.login(line[-1]) == True:
            bank = process_line(bank,barcode)
            continue
        bank.login(barcode)

        if barcode == "clear" or barcode == "abort" or barcode == "reset":
            bank.reset()

        elif barcode == "pay":
            print "\x1b[H\x1b[J"
            show_logo()
            bank.pay()
            open_la()

        elif barcode == "logout":
            print "\x1b[H\x1b[J"
            show_logo() 
            bank.logout()

        elif barcode == "bank":
            print "\x1b[H\x1b[J"
            show_logo()
            bank.account()

        elif barcode.startswith('deposit'):
            temp = barcode.split(' ')
            amount = temp[1]
            bank.deposit(amount)

        elif barcode.startswith('withdraw'):
            temp = barcode.split(' ')
            amount = temp[1]
            bank.withdraw(amount)

        elif barcode.startswith('adduser'):
            temp = barcode.split(' ')
            bank.account_add(temp[1])

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
            if bank.product_add(barcode) != True:
                print "404: Not found"

if __name__ ==  '__main__':
    print "\x1b[H\x1b[J"
    sys.exit(run())
           
