from decimal import *
from random import randrange

class Bank():
    def __init__(self,db):
        self.db = db
        self.member = 0
        self.username = "Mr/Ms Guest"
        self.total = Decimal('0.00')
        self.products = []
    
    def account_add(self,username):
        usernumber = int("%s%s" % (1337,randrange(000000000,999999999)))
        cursor = self.db.cursor()
        cursor.execute ("""SELECT * from member WHERE barcode = %s""",(usernumber,))
        if cursor.rowcount == 0:
            cursor.execute("""INSERT INTO member (nick,barcode) VALUES(%s,%s)""",(username,str(usernumber)))
            print "200: User %s added barcode: %s" %(username,usernumber)
        else:
            self.account_add(username) 

    def account(self):
        if self.member == 0:
            print "403: Forbidden"
            return
        try:
            self.balance = self.balance - self.total
        except:
            self.balance = self.balance - Decimal(self.total)
        cursor = self.db.cursor()
        cursor.execute("""UPDATE member SET balance = %s WHERE nick = %s LIMIT 1""", (self.balance,self.username))
        print "200: %s billed to your account new balance %s" % (self.total,self.balance)
        self.total = Decimal('0.00')
        if self.member == 1:
            self.logout()
        self.products = []

    def deposit(self,amount):
        cursor = self.db.cursor()
        if self.member == 0:
            print "403: Forbidden"
            return
        self.balance = self.balance + Decimal(amount)
        cursor.execute("""UPDATE member SET balance = %s WHERE nick = %s LIMIT 1""", (self.balance,self.username))
        print "200: Your balance is: %s" % self.balance
    
    def withdraw(self,amount):
        cursor = self.db.cursor()
        if self.member == 0:
            print "403: Forbidden"
            return
        self.balance = self.balance - Decimal(amount)
        cursor.execute("""UPDATE member SET balance = %s WHERE nick = %s LIMIT 1""", (self.balance,self.username))
        print "200: Your balance is %s" % self.balance

    def product_add(self,barcode):
        cursor = self.db.cursor()
        if self.member == 1:
            cursor.execute("""SELECT name,member_price FROM products WHERE barcode = %s LIMIT 1""" , (barcode,))
        else:
            cursor.execute("""SELECT name,price FROM products WHERE barcode = %s LIMIT 1""" , (barcode,))

        if cursor.rowcount == 0:
            return False 

        result = cursor.fetchone()
        self.total = self.total + Decimal(result[1])
        self.products.append([result[0],result[1],barcode])
        for product in self.products:
            print "\t%s \t#%s\t DROP: %s Euro" % (self.username,product[0],product[1])
        print "\t\t\t\tSubtotal: %s" % self.total
        return True

    def pay(self):
        print "200: %s payed %s euro to the register" % (self.username,self.total)
        try:
            self.total = Decimal(0.00)
        except:
            pass
        if self.member == 1:
            self.logout()
        self.products = []
        self.total = Decimal('0.00')


    def login(self,barcode):
        cursor = self.db.cursor()
        cursor.execute("""SELECT nick,balance FROM member WHERE barcode = %s OR nick = %s LIMIT 1""" , (barcode,barcode))
        if cursor.rowcount == 1:
            self.member = 1
            result = cursor.fetchone()
            self.username = result[0]
            self.balance = Decimal(result[1])
            print "200: User %s logged in" % self.username
            return True
        else:
            return False

    def logout(self):
        try:
            del self.balance
        except:
            print "403: Not logged in"
            return
        print "200: User %s logged out" % self.username
        self.member = 0
        self.username = "Mr/Ms Guest"
        if self.total > 0.00:
            self.reset(0)

    def reset(self,abort=1):
        try:
            self.total = Decimal('0.00')
        except:
            pass
        self.products = []
        if abort == 1:
            print "200: Transaction aborted"
        
