import MySQLdb
import ConfigParser
import sys
from bank import Bank
from ansi import clear, cursor, Color
from wifi import Wifi

def run():
    LOGO = '''
#
#     #   #
### # ##  #    #  #  ##
# # # #   #     # # #
### #  ##  ## ### # #
'''

    print str(Color('yellow'))+LOGO+str(Color('reset'))
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
            bank.pay()

        elif barcode == "logout":
            print "\x1b[H\x1b[J" 
            bank.logout()

        elif barcode == "bank":
            bank.account()

        elif barcode.startswith('deposit'):
            temp = barcode.split(' ')
            amount = temp[1]
            bank.deposit(amount)

        elif barcode.startswith('widthdraw'):
            temp = barcode.split(' ')
            amount = temp[1]
            bank.widthdraw(amount)

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
           
