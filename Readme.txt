-----------------------------------------------------------------Readme----------------------------------------------------------------

*************
Warning!
Some Modules/Libraries needs to be imported before running the program (If not present then needs to be installed before running the program)
*************

Modules used-

tkinter
os
fpdf
datetime
tkinter
io
pdfminer
cv2
numpy
pyzbar
sqlite3

*******************************

IMPORTANT!
database_creation.py needs to be executed First to ensure that database_used.db is created.

*******************************

uid_last.txt contains the latest updated UID of the Product.
Hence, can be changed and altered if necessary.

*******************************

The primary coding solution is main.py file. You need to execute the main.py file to view the solution.

*******************************

If reports need to be generated then database_extraction.py needs to be executed for generating a report for a specific product ID.

The program can be further modified for extraction of report by any columns or rows from the database.

*******************************

Inside Supplier_pdf all the pdfs should be named according to the QRCode generated text
(Example: if The outut of the of the QR Scanner is A1234 then pdf should be named A1234.pdf)

******************************** END *********************************