from db_config import mysql  # import sql

def cal_original_amount(original_amount,gate):
    mycursor = mysql.connection.cursor()
    sql_parking = "update parking_log set amount = %s where id=%s"
    val = (original_amount,gate)
    mycursor.execute(sql_parking, val)
    mysql.connection.commit()
    mycursor.close() 
    
    
def cal_excluding_vat(excluding_vat,gate):
    mycursor = mysql.connection.cursor()
    sql_parking = "update parking_log set excluding_vat = %s where id=%s"
    val = (excluding_vat,gate)
    mycursor.execute(sql_parking, val)
    mysql.connection.commit()
    mycursor.close()  


def cal_vat(vat,gate):
    mycursor = mysql.connection.cursor()
    sql_parking = "update parking_log set vat = %s where id=%s"
    val = (vat,gate)
    mycursor.execute(sql_parking, val)
    mysql.connection.commit()
    mycursor.close()  


def cal_fines(fines,gate):
    mycursor = mysql.connection.cursor()
    sql_parking = "update parking_log set fines = %s where id=%s"
    val = (fines,gate)
    mycursor.execute(sql_parking, val)
    mysql.connection.commit()
    mycursor.close()  


def cal_discount(discount, gate):
    mycursor = mysql.connection.cursor()
    sql_parking = "update parking_log set discount = %s where id=%s"
    val = (discount,gate)
    mycursor.execute(sql_parking, val)
    mysql.connection.commit()
    mycursor.close()
    
    
def cal_receieve(receieve ,gate):
    mycursor = mysql.connection.cursor()
    sql_parking = "update parking_log set earn = %s where id=%s"
    val = (receieve,gate)
    mycursor.execute(sql_parking, val)
    mysql.connection.commit()
    mycursor.close()
    
    
def cal_changes(changes,gate):
    mycursor = mysql.connection.cursor()
    sql_parking = "update parking_log set changes = %s where id=%s"
    val = (changes,gate)
    mycursor.execute(sql_parking, val)
    mysql.connection.commit()
    mycursor.close()
