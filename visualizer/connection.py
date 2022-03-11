import mysql.connector
import os
import sys
from urllib.parse import uses_netloc, urlparse

uses_netloc.append('mysql')

try:
    #if 'DATABASE_URL' in os.environ:
    #    url = urlparse(os.environ['DATABASE_URL'])
    url = urlparse(#)
except Exception:
    print('Error:', sys.exc_info())

def create_connection(name=url.username, passwd=url.password, hostname=url.hostname, db_name=url.path.lstrip('/')):
    #print(name, passwd, hostname, db_name)
    return mysql.connector.connect(user=name, password=passwd,
                                    host=hostname, database=db_name)
    
def create_cursor(connection):
    return connection.cursor()

def get_user_tables(cursor):
    # Trimitem o cerere care intoarce tabelele generate de utilizator
    # Nu intoarcem nimic, le vom citi din cursor
    q = "SHOW TABLES"
    cursor.execute(q)

def connection_wrapper():
    conn = create_connection()
    curs = create_cursor(conn)
    return conn, curs

if __name__ == '__main__':
    #print('''Conexiunea cu baza de date. 
    #        A nu se rula direct!''')
    
    a = create_connection()
    b = create_cursor(a)
    #b.execute("CREATE TABLE `test2` (`id` int(2) NOT NULL) ENGINE=InnoDB")
    query = "SELECT * FROM test"
    b.execute(query)
    #get_user_tables(b)
    for row in b:
        print(row)

    a.close()
    b.close()
