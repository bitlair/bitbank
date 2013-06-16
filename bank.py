from decimal import *
from random import randrange
import logging
import sys
import socket
import os
from time import sleep 
from threading import Thread

class CallBar(Thread):
    def run(self):
        udpsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        udpsock.sendto("""INVITE sip:101@192.168.88.4 SIP/2.0
Via: SIP/2.0/UDP 192.168.88.4;branch=z9hG4bKkjshdyff
Max-Forwards: 70
To: Bitlair <sip:101@192.168.88.4>
From: Troll <sip:troll@troll.com>;tag=1928301774
Call-ID: a84b4c76e66710
CSeq: 314159 INVITE
Contact: <sip:troll@troll.com>
Content-Type: application/sdp
Content-Length: 0
""", ("192.168.88.4", 5061))

        sleep(3)
        udpsock.sendto("""BYE sip:101@192.168.88.4 SIP/2.0
Via: SIP/2.0/UDP 192.168.88.4;branch=z9hG4bKnashds10
Max-Forwards: 70
From: Troll <sip:troll@troll.com>;tag=1928301774
To: Bitlair <sip:101@192.168.88.4>
Call-ID: a84b4c76e66710
CSeq: 314160 BYE
Content-Length: 0
""", ("192.168.88.4", 5061))

class Bank():
    def __init__(self,db):
        self.db = db
        self.member = 0
        self.username = "Mr/Ms Guest"
        self.total = Decimal('0.00')
        self.products = []
        self.plastic = []
    
    def account_add(self,username):
        usernumber = int("%s%s" % (1337,randrange(000000000,999999999)))
        cursor = self.db.cursor()
        cursor.execute ("""SELECT * from member WHERE barcode = %s""",(usernumber,))
        if cursor.rowcount == 0:
            cursor.execute("""INSERT INTO member (nick,barcode) VALUES(%s,%s)""",(username,str(usernumber)))
            print "200: User %s added barcode: %s" %(username,usernumber)
            logging.info("200: User %s added barcode: %s" %(username,usernumber))
            
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
        for plastic in self.plastic:
            cursor.execute("""INSERT INTO plastic (user,amount,price) VALUES(%s,%s,%s)""",(self.username,plastic[1],plastic[2]))
        self.plastic = []
        print "200: %s billed to your account new balance %s" % (self.total,self.balance)
        logging.info("200: %s billed to your account new balance %s" % (self.total,self.balance))
        self.total = Decimal('0.00')
        if self.member == 1:
            self.logout()
        self.products = []
    
    def shame(self):
        cursor = self.db.cursor()
        cursor.execute("""SELECT nick FROM member WHERE balance < "-13.37" ORDER BY  `member`.`balance` ASC ;""")
        result_set = cursor.fetchall ()
        i = 1 
        for row in result_set:
            print "%s %s" % (i, row[0])
            i = i + 1

    def deposit(self,amount):
        cursor = self.db.cursor()
        if self.member == 0:
            print "403: Forbidden"
            return
        self.balance = self.balance + Decimal(amount)
        cursor.execute("""UPDATE member SET balance = %s WHERE nick = %s LIMIT 1""", (self.balance,self.username))
        print "200: Your balance is: %s" % self.balance
        logging.info("200: Your balance is: %s" % self.balance)
    
    def withdraw(self,amount):
        cursor = self.db.cursor()
        if self.member == 0:
            print "403: Forbidden"
            return
        self.balance = self.balance - Decimal(amount)
        cursor.execute("""UPDATE member SET balance = %s WHERE nick = %s LIMIT 1""", (self.balance,self.username))
        print "200: Your balance is %s" % self.balance
        logging.info("200: Your balance is %s" % self.balance)

    def plastic_add(self,amount):
        if self.member == 1:
            price_pm = "0.80"
        else:
            price_pm = "1"
        self.total = self.total + Decimal(price_pm) * Decimal(amount) 
        self.products.append(["Plastic %s Meter"%amount,Decimal(price_pm) * Decimal(amount),'PLASTIC %s'%amount])
        self.plastic.append([self.username,amount,price_pm])
        for product in self.products:
            print "\t%s \t#%s\t DROP: %s Euro" % (self.username,product[0],product[1])
            logging.info("\t%s \t#%s\t DROP: %s Euro" % (self.username,product[0],product[1]))
        print "\t\t\t\tSubtotal: %s" % self.total
        logging.info("\t\t\t\tSubtotal: %s" % self.total)
        return True

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
            logging.info("\t%s \t#%s\t DROP: %s Euro" % (self.username,product[0],product[1]))
        print "\t\t\t\tSubtotal: %s" % self.total
        logging.info("\t\t\t\tSubtotal: %s" % self.total)
        return True

    def pay(self):
        cursor = self.db.cursor()
        for plastic in self.plastic:
            cursor.execute("""INSERT INTO plastic (user,amount,price) VALUES(%s,%s,%s)""",(self.username,plastic[1],plastic[2]))
        self.plastic = []

        print "200: %s payed %s euro to the register" % (self.username,self.total)
        logging.info("200: %s payed %s euro to the register" % (self.username,self.total))
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
            logging.info("200: User %s logged in" % self.username)
            return True
        else:
            return False
    def list(self):
        cursor = self.db.cursor()
        cursor.execute("""SELECT name,member_price,price FROM products""")
        result_set = cursor.fetchall ()
        print "Product\t\t\tMember price\tGuest price"
        for row in result_set:
            if len(row[0]) > 16:
                print "%s\t\t%s\t\t%s" % (row[0], row[1],row[2])
            elif len(row[0]) < 8:
                print "%s\t\t\t\t%s\t\t%s" % (row[0], row[1],row[2])
            else:
                print "%s\t\t\t%s\t\t%s" % (row[0], row[1],row[2])
        

    def logout(self):
        self.show_warning()
        try:
            del self.balance
        except:
            print "403: Not logged in"
            return
        print "200: User %s logged out" % self.username
        logging.info("200: User %s logged out" % self.username)
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
            logging.info("200: Transaction aborted")

    def show_warning(self):
        if self.balance >= Decimal("-13.37"):
            return
        CallBar().start()
        # set palette color 1 to our color
        print "\x1b]P1FD5A1E"

        logo = """
 W   W   AA   RRR    NN   I   NN    GGG
 W   W  A  A  R  R  N  N  I  N  N  G
 W W W  AAAA  RRR   N  N  I  N  N  G  GG
  W W   A  A  R  R  N  N  I  N  N   GGG

 BBB               K  k
 B  B   AA    NN   K K     L    I    MM MM   I  TTT
 BBB   A  A  N  N  KK      L    I   M  M  M  I   T
 B  B  AAAA  N  N  K K     L    I   M  M  M  I   T
 BBB   A  A  N  N  K  K    LLL  I   M  M  M  I   T
"""
        lines = logo.splitlines()

        for y, line in enumerate(lines):
            for x, char in enumerate(line):
                if char != ' ':
                    sys.stdout.write("\x1b[05;41m")
                    sys.stdout.write(char)
                    sys.stdout.write("\x1b[00;40m")
                else:
                    sys.stdout.write(" ")
            sys.stdout.write("\n")
            
