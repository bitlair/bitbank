import MySQLdb
import ConfigParser

config = ConfigParser.ConfigParser()
config.read('bitbank.cfg')

db = MySQLdb.connect(host=config.get('Database', 'hostname'),
    user=config.get('Database', 'username'), 
    passwd=config.get('Database', 'password'), 
    db=config.get('Database', 'database'))

total = 0.00
member = 0
username = "Mr/Ms Guest"

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

while True:
    barcode=raw_input('Please scan [usercard,product barcode]: ')

    if barcode.startswith('1337'):
        cursor = db.cursor()
        cursor.execute("""SELECT nick,balance FROM member WHERE barcode = %s LIMIT 1""" , (barcode,))
        if cursor.rowcount == 1:
            member = 1
            result = cursor.fetchone()
            username = result[0]
            balance = result[1]
            print "User %s logged in" % username

    elif barcode == "clear":
        print "Aborted not payed"
        reset()

    elif barcode == "pay":
        print "Payed %s " % total
        reset()

    elif barcode == "done":
        print "User logged out"
        reset()

    elif barcode == "bank":
        if member == 0:
            print "Error 403: Forbidden"
            continue
        try:
            balance = balance - total
        except:
            balance = balance - float(total)
        cursor = db.cursor()
        cursor.execute("""UPDATE member SET balance = %s WHERE nick = %s LIMIT 1""", (balance,username))
        print "%s billed to your account" % total
        reset()
    
    elif barcode.startswith('deposit'):
        temp = barcode.split(' ')
        amount = temp[1]
        cursor = db.cursor()
        balance = balance + float(amount)
        print "Your balance is: %s" % balance
        cursor.execute("""UPDATE member SET balance = %s WHERE nick = %s LIMIT 1""", (balance,username))

        
    else:
        cursor = db.cursor()

        if member == 1:
            cursor.execute("""SELECT name,member_price FROM products WHERE barcode = %s LIMIT 1""" , (barcode,))
        else:
            cursor.execute("""SELECT name,price FROM products WHERE barcode = %s LIMIT 1""" , (barcode,))

        if cursor.rowcount == 0:
            print "Not found"
            continue

        result = cursor.fetchone()
        print "\t\t %s \t\t DROP: %s # %s" % (username,result[1],result[0])
        try:
            total = total + result[1]
        except:
            total = result[1]
        print "Subtotal: %s" % total

           

