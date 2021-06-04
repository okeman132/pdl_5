import pymysql.cursors 
from datetime import datetime
connection = pymysql.connect(host='us-cdbr-east-03.cleardb.com',
                                    user='b73e8cc68166ea',
                                    password='77ad9b49',                             
                                    db='heroku_2e6d56b8e4b0ff6',
                                    charset='utf8mb4',
                                    cursorclass=pymysql.cursors.DictCursor)
        
print ("connect successful!!")

try:
    with connection.cursor() as cursor:
        now = datetime.now()
        dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
        sql = "SELECT  * FROM user "
        # Thực thi câu lệnh truy vấn (Execute Query).
        cursor.execute(sql)
        connection.commit()
        print ("cursor.description: ", cursor.description)
 
        print()
 
        for row in cursor:
            print(row)
except :
    print("Error")
                    
finally:
            # Đóng kết nối (Close connection).       
        connection.close()

