import MySQLdb
import ConfigParser
import sys
from bank import Bank
from ansi import clear, cursor, Color
from wifi import Wifi
from time import sleep

def open_la():
    import parallel
    p = parallel.Parallel()
    p.setData(0xFF)
    sleep(3)
    p.setData(0x00)

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

        if barcode.startswith('1337'):
            bank.login(barcode)

        elif barcode == "clear" or barcode == "abort" or barcode == "reset":
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

        elif barcode == "exit":
            _Runner = False
        elif barcode == "":
            continue
        else:
            if bank.product_add(barcode) != True:
                if bank.login(barcode) != True:
                    print "404: Not found"

if __name__ ==  '__main__':
    print "\x1b[H\x1b[J"
    sys.exit(run())
           
