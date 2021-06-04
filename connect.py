import pymysql.cursors  
from datetime import datetime
#from Temperature import TEMPERATURE
# Kết nối vào database.
class CONNECTION(object):
    def __init__(self):
        self.connection = pymysql.connect(host='us-cdbr-east-03.cleardb.com',
                                    user='b73e8cc68166ea',
                                    password='77ad9b49',                             
                                    db='heroku_2e6d56b8e4b0ff6',
                                    charset='utf8mb4',
                                    cursorclass=pymysql.cursors.DictCursor)
        
        print ("connect successful!!")
    def connectmySQL(self,id):
        try:
            with self.connection.cursor() as cursor:
                #temperature=TEMPERATURE()
                temperature = 36
                now = datetime.now()
                dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
                sql = "INSERT INTO Result(id, idUser, createAtTime, temperature, image, isQualified)" +"VALUES (%s, %s, %s, %s,%s,%s)"
                #val = ("NULL", id, dt_string, temperature.gettemperature(), "NULL",True)  
                val = ("NULL", id, dt_string, temperature, "NULL",True)  
                print(sql,val)
                # Thực thi câu lệnh truy vấn (Execute Query).
                cursor.execute(sql,val)
                self.connection.commit()
        except:
            print('Erros')           
        finally:
            # Đóng kết nối (Close connection).       
            self.connection.close()
    def insert(self,id,name,age,sex,address,idFaculty,image):
        try:
            with self.connection.cursor() as cursor:
                sql = "INSERT INTO user " +"VALUES (%s, %s, %s, %s, %s ,%s ,%s ,%s)"
                val = (id, name, age, sex,address,idFaculty,1,image)  
                print(sql,val)
                # Thực thi câu lệnh truy vấn (Execute Query).
                cursor.execute(sql,val)
                self.connection.commit()         
        finally:
            # Đóng kết nối (Close connection).       
            self.connection.close()
