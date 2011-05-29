import MySQLdb


class Wifi():
    def __init__(self,config):
        self.db = MySQLdb.connect(host=config.get('Bitwifi', 'hostname'),
            user=config.get('Bitwifi', 'username'),
            passwd=config.get('Bitwifi', 'password'),
            db=config.get('Bitwifi', 'database'))
        self.db.autocommit(True)

    def registration(self,nick,id,device):
        cursor = self.db.cursor()
        cursor.execute("""SELECT e . id, e.mac_address FROM wifi_event e 
            LEFT JOIN user_mac_address m ON m.mac_address = e.mac_address
            LEFT JOIN user u ON m.user_id = u.id
            WHERE e.join_date > 0
            AND u.username IS NULL 
            AND e.part_date =0
            AND e.id = %s
            ORDER BY e.join_date ASC""",(id))
        if cursor.rowcount == 0:
            print "500: Mac not found"
            return
        result = cursor.fetchone()
        mac_address = result[1]

        cursor.execute("""SELECT * from user WHERE username = %s""",(nick))
        if cursor.rowcount == 0:
            cursor.execute("""INSERT INTO user (username,real_name,sex) VALUES(%s,%s,%s)""",(nick,nick,'male'))
        cursor.execute("""SELECT id FROM user WHERE username=%s""",(nick))
        result = cursor.fetchone()
        user_id = result[0]

        cursor.execute("""INSERT INTO user_mac_address (user_id,mac_address,device) VALUES(%s,%s,%s)""",(user_id,mac_address,device))
        print "%s %s %s"%(user_id,mac_address,device)
        print "200: Usermac added"


    def unregister_list(self):
        cursor = self.db.cursor()
        cursor.execute("""SELECT e . id, e.mac_address FROM wifi_event e 
            LEFT JOIN user_mac_address m ON m.mac_address = e.mac_address
            LEFT JOIN user u ON m.user_id = u.id
            WHERE e.join_date > 0
            AND u.username IS NULL 
            AND e.part_date =0
            ORDER BY e.join_date ASC""")
        result = cursor.fetchall()
        print "\t id\tmac"
        for record in result:
            print "\t %s\t%s" %(record[0], record[1])
        print "enter register <id> <device>"
 
