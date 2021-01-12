from db_config import mysql  # import sql

def record_receipt(TAX_ID, POS_ID, REG_ID, today, cashier_box,original_license_plate,original_amount, date_in, date_out, time_in, time_out ,discount ,fines ,changes ,receieve ,user):

    mycursor = mysql.connection.cursor()
    sql_parking = "INSERT INTO receipt(tax_id ,pos_id ,reg_id ,today_date_time ,cashier_box  ,license_plate ,amount ,datetime_in ,datetime_out ,time_in ,time_out ,discount, fines ,changess ,receieve ,cashier) VALUES ( % s, %s,%s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s, %s)"
    val = (TAX_ID, POS_ID, REG_ID, today, cashier_box,original_license_plate,original_amount , date_in, date_out, time_in, time_out ,discount,fines ,changes ,receieve ,user )
    mycursor.execute(sql_parking, val)
    mysql.connection.commit()
    mycursor.close()  
