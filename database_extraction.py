import sqlite3
conn = sqlite3.connect('Material_used/material_used.db')
c=conn.cursor()
uid=int(input("Enter the product UID to get information: "))
c.execute("SELECT * FROM databaseManagement WHERE Product_ID=?", (f'{uid}',))
print(f"\nUID: {uid}\n")
for each_data in c.fetchall():
    print(each_data)
conn.commit()
conn.close()