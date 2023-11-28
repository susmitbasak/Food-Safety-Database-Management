import sqlite3
conn = sqlite3.connect('Material_used/material_used.db')
c=conn.cursor()
c.execute("""CREATE TABLE databaseManagement (
            Supplier text,
            Materials text,
            Regulation text,
            Material_ID text,
            Product_ID text,
            Supplied_to text)""")

conn.commit()
conn.close()