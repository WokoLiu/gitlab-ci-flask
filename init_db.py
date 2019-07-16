from app import app

import pymysql

connection = pymysql.connect(
        host=app.config['MYSQL_HOST'],
        port=app.config['MYSQL_PORT'],
        user=app.config['MYSQL_USER'],
        passwd=app.config['MYSQL_PSWD'],
        cursorclass=pymysql.cursors.DictCursor)

cursor = connection.cursor()

with open('init_db.sql', 'r') as f:
    for sql in f:
        cursor.execute(sql)

cursor.close()
connection.commit()
connection.close()
