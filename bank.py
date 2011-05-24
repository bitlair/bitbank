class Bank():
    def __init__(self,db):
        self.db = db
        self.member = 0
        self.username = "Mr/Ms Guest"
        self.total = float(0.00)
        self.products = []

    def account(self):
        if self.member == 0:
            print "403: Forbidden"
            return
        try:
            self.balance = self.balance - self.total
        except:
            self.balance = self.balance - float(self.total)
        cursor = self.db.cursor()
        cursor.execute("""UPDATE member SET balance = %s WHERE nick = %s LIMIT 1""", (self.balance,self.username))
        print "%s billed to your account" % self.total

    def deposit(self,amount):
        cursor = self.db.cursor()
        if self.member == 0:
            print "403: Forbidden"
            return
        self.balance = self.balance + float(amount)
        cursor.execute("""UPDATE member SET balance = %s WHERE nick = %s LIMIT 1""", (self.balance,self.username))
        print "Your balance is: %s" % self.balance
    
    def withdraw(self,amount):
        cursor = self.db.cursor()
        if self.member == 0:
            print "403: Forbidden"
            return
        self.balance = self.balance - float(amount)
        cursor.execute("""UPDATE member SET balance = %s WHERE nick = %s LIMIT 1""", (self.balance,self.username))
        print "200: Your balance is %s" % self.balance

    def product_add(self,barcode):
        cursor = self.db.cursor()
        if self.member == 1:
            cursor.execute("""SELECT name,member_price FROM products WHERE barcode = %s LIMIT 1""" , (barcode,))
        else:
            cursor.execute("""SELECT name,price FROM products WHERE barcode = %s LIMIT 1""" , (barcode,))

        if cursor.rowcount == 0:
            print "Not found"
            return 

        result = cursor.fetchone()
        self.total = self.total + float(result[1])
        self.products.append([result[0],result[1],barcode])
        for product in self.products:
            print "\t%s \t#%s\t DROP: %s Euro" % (self.username,product[0],product[1])
        print "\t\t\t\tSubtotal: %s" % self.total

    def pay(self):
        print "%s payed %s euro to the register" % (self.username,self.total)
        try:
            self.total = float(0.00)
        except:
            pass
        if self.member == 1:
            self.logout()
        self.products = []


    def login(self,barcode):
        cursor = self.db.cursor()
        cursor.execute("""SELECT nick,balance FROM member WHERE barcode = %s LIMIT 1""" , (barcode,))
        if cursor.rowcount == 1:
            self.member = 1
            result = cursor.fetchone()
            self.username = result[0]
            self.balance = result[1]
            print "200: User %s logged in" % self.username
        else:
            print "403: Forbidden"

    def logout(self):
        try:
            del self.balance
        except:
            print "Not logged in"
            return
        self.member = 0
        self.username = "Mr/Ms Guest"
        print "User logged out"
        if self.total > 0.00:
            self.reset()

    def reset(self):
        try:
            self.total = float(0.00)
        except:
            pass
        self.products = []
        print "Transaction aborted"
        
