# Modules imported
from tkinter import *
import os
from fpdf import FPDF
import datetime
import tkinter.font as font
import io
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
import cv2
import numpy as np
from pyzbar.pyzbar import decode
import sqlite3


# Colour palette
WHITE = "#FFFFFF"
BLUE = "#2B3372"
LIGHT_BLUE = "#ADB3C6"
GREEN = "#228B22"
RED = "#8B0000"


# Tkinter object creation
window = Tk()
window.title("Food Safety and Database Management")
window.config(bg=WHITE, padx=40, pady=50)


# Set minimum window size value
window.minsize(820, 660) 
# Set maximum window size value
window.maxsize(820, 660)


# Font
new_product = font.Font(family='Microsoft YaHei', size=20, weight='bold')
new_material = font.Font(family='Microsoft YaHei', size=17, weight='bold')
status_correct = font.Font(family='Microsoft YaHei', size=12, weight='bold')
uid = font.Font(family='Microsoft YaHei', size=12, weight='bold')
label_font = font.Font(family='Microsoft YaHei')


# Icons
generate_icon = PhotoImage(file="Icons/generate.png")
scan_icon = PhotoImage(file="Icons/scan.png")
finish_icon = PhotoImage(file="Icons/finish.png")


# Global constants
initial_uid = 0
finished = 1
material_qty = 0
active_id = 0
material_uid = []
cp = cv2.VideoCapture(0)
cp.set(3,640)
cp.set(4,480)
invalid_entry=['',' ', '   ','\t','\n']


# Scanning QR Code to get the unique code for each material
def photoscan():
    global cp
    decoded_txt=[]
    while True:

        success, img = cp.read()
        for barcode in decode(img):
            if barcode.data.decode('utf-8') in decoded_txt:
                pass
            else:
                decoded_txt=[]
                decoded_txt.append(barcode.data.decode('utf-8'))
            
            pts = np.array([barcode.polygon],np.int32)
            pts = pts.reshape((-1,1,2))
            cv2.polylines(img,[pts],True,(255,0,255),5)
            
        print(decoded_txt)

        cv2.imshow("QRDecoder",img)
        cv2.waitKey(1)
        if len(decoded_txt)>0:
            return decoded_txt[0]



# .pdf to .txt conversion of Supplier Certificates
def convert(fname, pages=None):
    if not pages:
        pagenums = set()
    else:
        pagenums = set(pages)
    output = io.StringIO()
    manager = PDFResourceManager()
    converter = TextConverter(manager, output, laparams=LAParams())
    interpreter = PDFPageInterpreter(manager, converter)
    infile = open(fname, 'rb')
    for page in PDFPage.get_pages(infile, pagenums):
        interpreter.process_page(page)
    infile.close()
    converter.close()
    text = output.getvalue()
    output.close
    text1 = text.replace(" \n", "")
    return text1


# Creation of UID for individual products
def on_generate():
    global initial_uid, active_id, finished
    if(finished):
        with open('UID/uid_last.txt','r') as u:
            initial_uid = u.read()
        initial_uid = int(initial_uid)+1
        uid_label.config(text=initial_uid)
        active_id = 1
        finished = 0
    else:
        statusbar_label.config(text="Tap on FINISH to finish building the current product.", fg=RED)


# Finish creating a product
def on_finish():
    global active_id, material_qty, finished, material_uid, initial_uid
    if supplied_entry.get() in invalid_entry:
        statusbar_label.config(text="Please enter a VALID entry in the \"Supplied to:\" field!", fg=RED)
    else:
        if material_qty > 0:
            statusbar_label.config(text="Finished building product! \n New UID generated. Add new materials.", fg=GREEN)
            active_id = 0
            material_qty = 0
            finished = 1
            material_uid = []
            final_certificate(initial_uid)
            with open ('UID/uid_last.txt','w') as u:
                u.write(str(initial_uid))
            supplied_entry.delete(0,END)
            on_generate()
        else:
            statusbar_label.config(text="No material added to current product.", fg=RED)


# Using buffer file to process information from supplier certificate
def input_directory(dict_input):
    def f_name(file_name):
        with open(file_name,'r') as myF:
            data_f = myF.read()
            with open ('Input_text/info.txt','w') as myR:
                myR.write(data_f)
    f_name(dict_input)


# Scan the material certificate and store the information if requirements are satisfied
def scan():
    eq=[]
    def file_read(fname):
        global material_qty
        with open(fname,'r') as myFile:
            check=0
            data = myFile.readlines()
            uid = data[1]                                         # appending the UID
            eq.append(data[3])                                    # appending the materials
            if (len(data)>5):                                     # to check if there are regulations available
                cerf = data[5].split(", ")
            else:
                cerf = ""   
            with open ('Certificates/certificates.txt') as c:     # getting the valid regulations
                dcer = c.readlines()
            if uid in material_uid:                               # to check if material has been scanned before
                statusbar_label.config(text=f"{uid} STATUS: Already scanned and added to database.", fg=RED)
            else:
                material_uid.append(uid)
                for i in cerf:
                    for j in dcer:
                        j=j.strip()
                        i=i.strip()
                        if i==j:                                  # check if given regulations meet the requirements
                            check=1
                if check==1:                                      # if valid regulations have been found
                    statusbar_label.config(text=f"{uid} STATUS: Scan Successful! Requirements satisfied.", fg=GREEN)
                    material_qty=material_qty+1
                    with open("Save_text/final.txt","a") as f:    # to append the information of material passing the criteria
                        sup_self=str(data[2])
                        sup_self=sup_self[:len(sup_self)-1]
                        materials_self=str(data[3])
                        materials_self=materials_self[:len(materials_self)-1]
                        f.write(str(sup_self+"- "+materials_self+"- "+data[5]))

                        sup_s=str(sup_self)
                        materials_s=str(materials_self)
                        reg=str(data[5])
                        #supplied_entry.get()
                        conn = sqlite3.connect('Material_used/material_used.db')
                        c=conn.cursor()
                        c.execute("INSERT INTO databaseManagement VALUES (?, ?, ?, ?, ?, ?)",(sup_s, materials_s, reg, uid, initial_uid, supplied_entry.get()))
                        conn.commit()
                        conn.close()
                        
                else:
                    statusbar_label.config(text=f"{uid}STATUS: Scan unsuccessful! Doesn't meet the requirements. Choose a different material.", fg=RED)

    file_read("Input_text/info.txt")


# Generation of Final Certificate in .pdf format and storing it
def final_certificate(uid):
    fin_pdf=[]
    cer=[]
    mat=[]
    cert_pdf=[]

    da=str("Date: "+str(datetime.datetime.now())[:10])
    fin_pdf.append('\n\n')
    fin_pdf.append(da)
    fin_pdf.append('\n')
    fin_pdf.append(f"UID:{uid}\n")
    fin_pdf.append('\n')

    with open ('Save_text/final.txt','r') as final:
        data=final.readlines()
        for i in data:
            info=i
            info=info.split('-')
            cer.append(info[2].split(','))
            mat.append(info[1].split(','))
    b=[]
    for i in cer:
        for j in range(len(i)):
            b.append(i[j].strip('\n'))
    mat_updated=[]
    for i in mat:
        for j in range(len(i)):
            mat_updated.append(i[j].strip())
    fin_pdf.append("We hereby declare that the following parts / equipment:\n")
    m=set(mat_updated)
    for i in m:
        fin_pdf.append(i)
    fin_pdf.append('\n')
    fin_pdf.append('\n')
    cert_pdf.append("Are supplied in accordance with the relevant requirements of:\n")
    f=set(b)
    for i in f:
        cert_pdf.append(i)
    open('Save_text/final.txt', "w").close()                     # to close the final txt file and new entery of materials for the next product 
    pdf=FPDF()                                                   # To generate a .pdf certificate from the obtained information
    pdf.add_page()
    pdf.set_font("Times", "B", 23)
    pdf.image('Icons/certificate_background.png', x = 0, y = 0, w = 210, h = 297, type = '', link = '')
    x=pdf.get_x()
    y=pdf.get_y()
    pdf.set_xy(x,y+20)
    pdf.cell(0,15,txt="FOOD CONTACT MATERIAL CERTIFICATE\n",ln=1,align="C",fill=False, border=0)
    if (len(fin_pdf)<14):
        pdf.set_font("Times", size=20)
    else:
        pdf.set_font("Times", size=16)
    for i in fin_pdf:
        pdf.cell(ln=1, h=10, align='C', w=0, txt=i, border=0,fill = False)
    pdf.set_font("Times", size=18)
    pdf.cell(ln=1, h=7, align='C', w=0, txt=f"Supplied to: {supplied_entry.get()}", border=0,fill = False)
    x=pdf.get_x()
    y=pdf.get_y()
    if (len(cert_pdf)<5) and (y<220):
        pdf.set_xy(x,230.0)
    pdf.set_font("Times", "B", 20)
    for i in cert_pdf:
        pdf.cell(ln=1, h=10, align='C', w=0, txt=i, border=0,fill = False)
    pdf.output(f"Final Certificates/{uid}.pdf")
    

# Function to get triggered after clicking SCAN button
def on_scan():
    if(active_id):
        found=0       
        FOLDER_PATH = r'Supplier\\Supplier_pdf'        
        fileNames = os.listdir(FOLDER_PATH)
        scanned_text = photoscan()
        for fileName in fileNames:
            if fileName==f"{scanned_text}.pdf":
                path=f'Supplier/Supplier_pdf/{fileName}'
                a=convert(path)
                f=open(f'Supplier/Supplier_txt/{scanned_text}.txt','w',encoding='utf-8')
                f.write(a)
                f.close()
                found=1
                input_directory(f'Supplier/Supplier_txt/{scanned_text}.txt')
                scan()            
        if found==0:
            statusbar_label.config(text="No certificate found corresponding to the material. \nCheck and try again or Contact supplier.", fg=RED)
    else:
        statusbar_label.config(text="Generate an unique ID first to add material.", fg=BLUE)


# Labels
product_label=Label(text="New Product",bg=WHITE, pady=10, font=new_product)
product_label.grid(row=1, column=1, columnspan=3)
generate_label=Label(text="Generate an unique ID for product:", bg=WHITE, font=label_font)
generate_label.grid(row=2, column=1)
uid_label=Label(text="XXXXXX", bg=WHITE, font=uid, pady=30)
uid_label.grid(row=2, column=2)
material_label=Label(text="New Material", bg=WHITE, pady=10, font=new_material)
material_label.grid(row=3, column=1, columnspan=3)
supplied_label=Label(text="Supplied to: ", bg=WHITE, pady=10, font=label_font)
supplied_label.grid(row=4, column=1, columnspan=2)
scan_label=Label(text="Scan for required certificates from supplier:", bg=WHITE, pady=20, font=label_font)
scan_label.grid(row=5, column=1, columnspan=3)
statusbar_label=Label(text="Generate an unique ID and add materials!", bg=WHITE, fg=BLUE, font=status_correct, width=72,pady=40)
statusbar_label.grid(row=7, column=1, columnspan=3)


# Entries
supplied_entry = Entry(width=25, bg=LIGHT_BLUE)
supplied_entry.grid(row=4, column=2, pady=10)


# Buttons
generate_button = Button(bg=WHITE, border=0, image=generate_icon, command=on_generate)
generate_button.grid(row=2, column=3)
scan_button = Button(bg=WHITE, border=0, image=scan_icon, command=on_scan)
scan_button.grid(row=6, column=1,columnspan=3)
finish_button = Button(bg=WHITE, height=50, pady=20, border=0, image=finish_icon, command=on_finish)
finish_button.grid(row=8, column=1, columnspan=3)


window.mainloop()