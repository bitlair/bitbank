import MySQLdb
import ConfigParser
import sys
from bank import Bank

def reset():
    global member,total,username
    member = 0
    try:
        del total
    except:
        pass
    try:
        del balance
    except:
        pass
    username = "Mr/Ms Guest"

def deposit(username,amount):
    global db
    cursor = db.cursor()
    balance = balance + float(amount)
    print "Your balance is: %s" % balance
    cursor.execute("""UPDATE member SET balance = %s WHERE nick = %s LIMIT 1""", (balance,username))

def run():
    _Runner = True

    config = ConfigParser.ConfigParser()
    config.read('bitbank.cfg')

    db = MySQLdb.connect(host=config.get('Database', 'hostname'),
        user=config.get('Database', 'username'),
        passwd=config.get('Database', 'password'),
        db=config.get('Database', 'database'))
 
    bank = Bank(db)
    while _Runner == True:
        barcode=raw_input('Please scan [usercard,product barcode]: ')

        if barcode.startswith('1337'):
            bank.login(barcode)

        elif barcode == "clear":
            print "Aborted not payed"
            reset()

        elif barcode == "pay":
            print "Payed %s " % total
            reset()

        elif barcode == "logout":
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

        elif barcode == "exit":
            _Runner = False
        
        else:
            cursor = db.cursor()
            if bank.member == 1:
                cursor.execute("""SELECT name,member_price FROM products WHERE barcode = %s LIMIT 1""" , (barcode,))
            else:
                cursor.execute("""SELECT name,price FROM products WHERE barcode = %s LIMIT 1""" , (barcode,))
    
            if cursor.rowcount == 0:
                print "Not found"
                continue

            result = cursor.fetchone()
            print "\t\t %s \t\t DROP: %s # %s" % (username,result[1],result[0])
            try:
                bank.total = bank.total + result[1]
            except:
                bank.total = result[1]
            print "Subtotal: %s" % total

if __name__ ==  '__main__':
    sys.exit(run())
           
