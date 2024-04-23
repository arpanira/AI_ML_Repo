import pyodbc
dsn='SQLServerDSN'
from decimal import Decimal

#Connect to database

# Define your connection string
#connection_string = 'DRIVER={SQL Server};SERVER=localhost;DATABASE=food_delivery;Trusted_Connection=yes;'
#connection = pyodbc.connect(connection_string)

# Establish a connection to the database using configured DSN
conn=pyodbc.connect('DSN='+dsn)
cursor=conn.cursor()

def get_order_status(order_id:int):
    print("Checking backend database")
    # Define your SQL query to retrieve order status
    sql_query = "SELECT status FROM food_delivery.dbo.order_tracking WHERE order_id = ?"

    cursor.execute(sql_query,order_id)

    result=cursor.fetchone()


    #cursor.close()
    #conn.close()

    if result is not None:
        return result[0]
    else:
        return None

def get_new_order(order:dict):
    print("Getting maximum order_id")
    get_max_order_id_query="select max(order_id) from food_delivery.dbo.[order]"
    cursor.execute(get_max_order_id_query)
    result=cursor.fetchone()
    if result is None:
        max_order_id=1
    else:
        max_order_id=result[0]+1
    return max_order_id

def save_to_db(order_id:int,order:dict):
    sql_query = "SELECT item_id, price  FROM food_delivery.dbo.[food_item] WHERE name = ?"
    insert_query = "INSERT INTO food_delivery.dbo.[order] (order_id,item_id, quantity,total_price)  VALUES (?, ?, ?, ?)"

    for food,quantity in order.items():
        cursor.execute(sql_query, food)
        row=cursor.fetchone()
        if row:
            item_id,price=row
            #Execute insert query

            cursor.execute(insert_query, (order_id,item_id,quantity,(Decimal(price)*Decimal(quantity))))
            cursor.commit()
            cursor.execute("INSERT INTO  food_delivery.dbo.order_tracking(order_id,status) VALUES (?,?)",(order_id ,"Initiated"))
            cursor.commit()
def get_bill_Amount(order_id:int):
    get_bill_query="SELECT SUM(A.total_price) from (SELECT * from  food_delivery.dbo.[order] where order_id=?)A"
    cursor.execute(get_bill_query,order_id)
    result=cursor.fetchone()
    return result[0]


"""if __name__=="__main__":
    #save_to_db(1000,{"Upma":2,"Masala Dosa":1})
    #bill=get_bill_Amount(1000)
    #print(bill)"""
