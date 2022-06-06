import pandas as pd
import numpy as np
import os
from yattag import Doc
from datetime import datetime
from datetime import date
import shutil
from pathlib import Path
import os.path
import pprint
import time
from git import Repo
import string
import random # define the random module
import openpyxl
from openpyxl_image_loader import SheetImageLoader
from PIL import Image
import PIL
import threading
from time import sleep
import pynotion_curl as pyn_c

class pynotion:

    def __init__(self,DIR_ASM=None,SUB_DIR=None):

        self.pp = pprint.PrettyPrinter(indent=4)

        doc, tag, text = Doc().tagtext()
        self.GIT_URL = "https://vitrotem.github.io/vitronotion/"
        self.SUB_DIR = SUB_DIR
        # self.SUB_DIR = "MVP_02"

        # self.DIR_ASM = r"C:\Users\tomgr\OneDrive\13 R&D\1. Device\MVP 02"
        self.DIR_ASM = DIR_ASM
        self.DIR_BOM = os.path.join(self.DIR_ASM, 'BOM')
        self.DIR_STP = os.path.join(self.DIR_ASM, 'STEP')
        self.DIR_PDF = os.path.join(self.DIR_ASM, 'DRAWINGS')
        self.DIR_ORDERS = os.path.join(self.DIR_ASM, 'ORDERS')
        self.DIR_SHOPPING_LIST = os.path.join(self.DIR_ASM, 'SHOPPING_LISTS')

        self.DIR_GIT = os.path.join(r"C:\Users\tomgr\Documents\GitHub\VitroNotion")
        self.SUB_DIR_GIT = os.path.join(self.DIR_GIT,self.SUB_DIR)

        self.DIR_GIT_STP = os.path.join(self.SUB_DIR_GIT, 'STP')
        self.DIR_GIT_PDF = os.path.join(self.SUB_DIR_GIT, 'PDF')
        self.DIR_GIT_BOM = os.path.join(self.SUB_DIR_GIT, 'BOM')
        self.DIR_GIT_BOM_IMG = os.path.join(self.DIR_GIT_BOM, 'IMG')
        self.DIR_GIT_SHOPPING_LIST = os.path.join(self.SUB_DIR_GIT, 'SHOPPING_LISTS')
        self.DIR_GIT_ORDERS = os.path.join(self.SUB_DIR_GIT, 'ORDERS')
        self.DIR_GIT_ORDERS_QUOTES = os.path.join(self.DIR_GIT_ORDERS, 'QUOTES')
        self.DIR_GIT_ORDERS_PURCHASE_ORDERS = os.path.join(self.DIR_GIT_ORDERS, 'PURCHASE_ORDERS')
        self.DIR_GIT_ORDERS_INVOICES = os.path.join(self.DIR_GIT_ORDERS, 'INVOICES')

        self.PATH_GIT_STP_HTML = os.path.join(self.DIR_GIT_STP, 'index.html')
        self.PATH_GIT_PDF_HTML = os.path.join(self.DIR_GIT_PDF, 'index.html')
        self.PATH_GIT_BOM_HTML = os.path.join(self.DIR_GIT_BOM, 'index.html')
        self.PATH_GIT_ORDERS_HTML = os.path.join(self.DIR_GIT_ORDERS, 'index.html')

        self.popup_html = """window.open(this.href,'targetWindow',
                                           `toolbar=no,
                                            location=no,
                                            status=no,
                                            menubar=no,
                                            scrollbars=no,
                                            top=200px,
                                            left=200px,
                                            resizable=no,
                                            width=400px,
                                            height=400px`);return false;
            """
        # for x in [self.SUB_DIR_GIT,self.DIR_GIT_STP,
        #           self.DIR_GIT_PDF,
        #           self.DIR_GIT_BOM,
        #           self.DIR_GIT_BOM_IMG,
        #           self.DIR_GIT_ORDERS,
        #           self.DIR_GIT_ORDERS_QUOTES,
        #           self.DIR_GIT_ORDERS_PURCHASE_ORDERS,
        #           self.DIR_GIT_ORDERS_INVOICES]:
        #
        #     self.genPath(x)
        self.main()

    def main(self):
        while True:
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")

            # self.copy_directories()
            df = self.GET_BOM()

            response = self.create_BOM_db(df)

            self.add_db_page(df, response["id"])

            # self.bom_html_str = self.ydump_BOM(df)
            # self.orders_html_str = self.ydump_ORDERS(df)
            # self.pdf_html_str = self.ydump_PDF_STEP(df)

            # self.write_html_files()

            print("Pushing.... :", current_time)
            print("=================+++++++++++++++++++=================")

            # git_push(os.path.join(self.DIR_GIT,".git"))
            time.sleep(60*30) # wait one minute


    def genPath(self,path):
        isExist = os.path.exists(path)
        if not isExist:
          os.mkdir(path)

    # def copy_directories(self):
    #     shutil.copytree(self.DIR_STP, self.DIR_GIT_STP, dirs_exist_ok=True)
    #     shutil.copytree(self.DIR_PDF, self.DIR_GIT_PDF, dirs_exist_ok=True)
    #     shutil.copytree(self.DIR_ORDERS, self.DIR_GIT_ORDERS, dirs_exist_ok=True)
    #     shutil.copytree(self.DIR_SHOPPING_LIST, self.DIR_GIT_SHOPPING_LIST, dirs_exist_ok=True)

    def GET_BOM(self):
        highest_v = 0
        highest_v_file = ""
        output_file = ''

        for file in os.listdir(self.DIR_BOM):
            if ".v" in file and file.endswith(".xlsx"):
                temp_v = int(file.split(".v")[1].replace(".xlsx",""))
                if temp_v > highest_v:
                    highest_v = temp_v
                    highest_v_file = file

        bom_path = os.path.join(self.DIR_BOM, file)
        BOM = pd.read_excel(bom_path,dtype=str).replace(r'\n','', regex=True)

        self.dumpBOMimages(BOM, bom_path)

        return BOM

    # def ydump_table(self,headings, rows, **kwargs):
        """Dump an html table using yatag

        Args:
            doc: yatag Doc instance
            headings: [str]
            rows: [[str]]

        """
        doc, tag, text, line = Doc().ttl()
        with tag('table', **kwargs):
            with tag('tr'):
                for x in headings:
                    line('th', str(x))
            for row in rows:
                with tag('tr'):
                    for x in row:
                        line('td', str(x))
        return doc.getvalue()

    def create_BOM_db(self,df, **kwargs):
        # df = df.drop('column_name', 1)
        headings = df.columns.values
        rows = df.to_numpy()
        BOM_properties = {}
        for i,h in enumerate(headings):
            if h == "ITEM NO.": BOM_properties[h] = {"title": {}}
            elif h == "DOCUMENT PREVIEW": BOM_properties[h] = {"files": {}}
            else: BOM_properties[h] = {"rich_text": {}}
        # for row in rows:
        #     i = 1
        #     for x in row:
        #         if i==1:
        #             'img',src=("IMG/"+row[2]+".jpg")
        #                 text('')
        #         else:
        #             line('td', str(x), klass="bom_table")
        #
        #         i+=1
        response = pyn_c.create_db(BOM_properties)
        print(response)
        return response

    def add_db_page(self,df, db_id=None):
        # df = df.drop('column_name', 1)
        headings = df.columns.values
        df = df.fillna("")
        for i,r in df.iterrows():
            page_data = {}
            img_url = os.path.join(self.GIT_URL, 'MVP_02', 'BOM', 'IMG',r["PartNo"]+".jpg")

            for j,h in enumerate(headings):
                # img_url = ''
                if h == "ITEM NO.":
                    page_data[h] = {"title": [{"text":{"content":str(df.iloc[i][h])}}]}
                elif h == "DOCUMENT PREVIEW": page_data[h] =  {"files": [{"name":img_url, "external":{"url": str(img_url)}}]}
                else: page_data[h] = {"rich_text": [{"text":{"content":str(df.iloc[i][h])}}]}
            # page_data.replace("\'","\"").replace("\n","")
            # self.pp.pprint(page_data)
            print(pyn_c.add_db_page(db_id, page_data))
            sleep(.3)

        # return BOM_properties
    #
    # def writeHTML(self,title,body):
    #     now = datetime.now()
    #     dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    #
    #     doc, tag, text, line = Doc().ttl()
    #     style_str = """
    # a {
    # display: block;
    #     background-color: #f5f5f5;
    #     color: #225ca8;
    #     text-decoration: none;
    #     /* font-family: Verdana, Geneva, sans-serif; */
    #     font-size: 1em;
    #     border-right: 1px solid #999999;
    #     border-bottom: 1px solid #999999;
    #     border-top-width: 0px;
    #     margin: 1px;
    #     padding: 1px;
    #     border-radius: 3px;
    #     border-left-width: 0px;
    #     }
    # .bom_image
    # {
    #     margin-left: 15px;
    #     width: auto;
    #     height:50px;
    # }
    #
    # a:hover
    # {
    # color: #030;
    # background-color: #eafddd;
    #
    # }
    #
    # a:active
    # {
    # color: #aca;
    # border-left: 1px solid #030;
    # border-top: 1px solid #030;
    # border-right-width: 0px;
    # border-bottom-width: 0px;
    # }
    #     .styled_table {
    #     border: solid 1px #DDEEEE;
    #     border-collapse: collapse;
    #     border-spacing: 0;
    #     font: normal 13px Arial, sans-serif;
    # }
    # .bom_table {
    #     text-align: center;
    #     min-width:10px !important;
    #     max-width:360px !important;
    #     padding: 2px !important;
    #    /*  white-space:nowrap; */
    #     padding-left: 5px !important;
    #     padding-right: 5px !important;
    #
    #
    # }
    # .purchase_table {
    #     min-width:100px !important;
    #     max-width:360px !important;
    #     padding: 2px !important;
    #     white-space:nowrap;
    #     padding-left: 10px !important;
    #     padding-right: 10px !important;
    #
    #
    # }
    #
    # .styled_table thead th {
    #     background-color: #DDEFEF;
    #     border: solid 1px #DDEEEE;
    #     color: #336B6B;
    #     padding: 10px;
    #     text-align: left;
    #     text-shadow: 1px 1px 1px #fff;
    # }
    #
    # notion-embed-block {
    #     max-width: 2000px;
    #     align-self: center;
    #     margin-top: 4px;
    #     margin-bottom: 4px;
    # }
    # .styled_table tbody td {
    #     border: solid 1px #DDEEEE;
    #     color: #333;
    #     /* padding: 10px; */
    #     text-shadow: 1px 1px 1px #fff;
    #     /* min-width:100px */
    # }
    # .table_link {
    #   cursor:pointer;
    #   color:#A4DCF5;
    #   text-decoration:underline;
    #     font-style:normal;
    #   font-weight:bold;
    #   font-size:1.0em;
    #
    # }
    #
    # """
    #     javascript_str = open(self.DIR_GIT+"\JS\header.js", "r")
    #
    #     title = "Last updated: " + str(dt_string)
    #     with tag('style'):
    #         text(style_str)
    #     with tag('script',src="https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js", charset="UTF-8"):
    #         text("")
    #     with tag('script'):
    #         text(javascript_str.read())
    #
    #         # with tag('body'):
    #     with tag('h3'):
    #         text(title)
    #     doc.asis(body)
    #     return doc.getvalue().replace("nan","")
    #
    # def ydump_ORDERS(self,df, **kwargs):
    #     doc, tag, text, line = Doc().ttl()
    #
    #     headings = ["Vendor / MFG","Shopping List","Quotes","Purchase Orders","Invoices"]
    #
    #     vendors = df["Vendor"].dropna().values
    #     mfgs = df["Manufacturer"].dropna().values
    #
    #     unique_mfgs = np.unique(list(mfgs))
    #     unique_vendors =  np.unique(list(vendors))
    #     rows = []
    #     rows_dict = {}
    #     dates = []
    #     for vendor in unique_vendors:
    #
    #         if vendor != "VITROTEM":
    #
    #             vendor_shopping_link = self.GIT_URL+self.SUB_DIR+"/SHOPPING_LISTS/"+vendor.upper()+".xlsx"
    #             vendor_shopping_link = self.GIT_URL+"/JS/DOWNLOAD.html?fileURL="+vendor_shopping_link
    #
    #             rows_dict[vendor] = {}
    #             rows_dict[vendor]["shopping_link"] = [(0, vendor_shopping_link)]
    #             rows_dict[vendor]["quote_links"] = []
    #             rows_dict[vendor]["PO_links"] = []
    #             rows_dict[vendor]["invoice_links"] = []
    #
    #             rows.append([str(vendor),"",vendor_shopping_link,"","","",""])
    #
    #     for mfg in unique_mfgs:
    #
    #
    #         mfg_shopping_link = "https://sirthomasii.github.io/VitroNotion/MVP/SHOPPING_LISTS/"+mfg.upper()+".xlsx"
    #         mfg_shopping_link = "https://sirthomasii.github.io/VitroNotion/JS/DOWNLOAD.html?fileURL="+mfg_shopping_link
    #         rows.append(["VITROTEM",str(mfg),mfg_shopping_link,"","","",""])
    #
    #         rows_dict[mfg] = {}
    #         rows_dict[mfg]["shopping_link"] = [(0, mfg_shopping_link)]
    #         rows_dict[mfg]["quote_links"] = []
    #         rows_dict[mfg]["PO_links"] = []
    #         rows_dict[mfg]["invoice_links"] = []
    #
    #     for file in os.listdir(self.DIR_GIT_ORDERS_INVOICES):
    #         tmp_vendor = file.split("-")[0]
    #
    #         if tmp_vendor in rows_dict:
    #
    #             link = self.GIT_URL+self.SUB_DIR+"/ORDERS/INVOICES/"+file
    #             link = self.GIT_URL+"/JS/DOWNLOAD.html?fileURL="+link
    #             # rows_dict[tmp_vendor]["invoice_links"].append(invoice_link)
    #             rows_dict[tmp_vendor]["invoice_links"].append((self.getDate(file),link))
    #
    #     for file in os.listdir(self.DIR_GIT_ORDERS_PURCHASE_ORDERS):
    #         tmp_vendor = file.split("-")[0]
    #
    #         if tmp_vendor in rows_dict:
    #             link = self.GIT_URL+self.SUB_DIR+"/ORDERS/PURCHASE_ORDERS/"+file
    #             link = self.GIT_URL+"/JS/DOWNLOAD.html?fileURL="+link
    #             rows_dict[tmp_vendor]["PO_links"].append((self.getDate(file),link))
    #
    #     for file in os.listdir(self.DIR_GIT_ORDERS_QUOTES):
    #         tmp_vendor = file.split("-")[0]
    #
    #         if tmp_vendor in rows_dict:
    #             link = self.GIT_URL+self.SUB_DIR+"/ORDERS/QUOTES/"+file
    #             link = self.GIT_URL+"/JS/DOWNLOAD.html?fileURL="+link
    #             rows_dict[tmp_vendor]["quote_links"].append((self.getDate(file),link))
    #
    #     for k,v in rows_dict.items():
    #         v["invoice_links"].sort(reverse=True)
    #         v["PO_links"].sort(reverse=True)
    #         v["quote_links"].sort(reverse=True)
    #
    #     # for k,v in rows_dict.items():
    #     #     for j,w in v.items():
    #     #         for x in w:
    #     #             print(x)
    #
    #     with tag('table', klass="styled_table", **kwargs):
    #         with tag('tr'):
    #             for x in headings:
    #                 line('th', str(x))
    #
    #         for vendor, vendor_items in rows_dict.items():
    #
    #             with tag('tr'):
    #
    #                 with tag('td', klass="purchase_table"):
    #                     text(vendor)
    #
    #                 for item, item_value in vendor_items.items():
    #
    #                     with tag('td', klass="purchase_table"):
    #
    #                         if "link" in item:
    #
    #                             for link in item_value:
    #
    #                                 with tag('a',href=str(link[1]),target="_parent"):
    #                                     text(os.path.basename(link[1]))
    #
    #                         else:
    #                             text(item)
    #
    #     return doc.getvalue()
    #
    # def getDate(self,file):
    #     dt = date(int((file.split("-")[3]).split(".")[0]), int(file.split("-")[2]),int(file.split("-")[1]))
    #     dt = datetime.strftime(dt, "%Y-%m-%d")
    #     return dt
    #
    # def ydump_PDF_STEP(self,df, **kwargs):
    #     doc, tag, text, line = Doc().ttl()
    #
    #     headings = ["Part number","PDF","STEP", "Description"]
    #     rows = []
    #
    #     for i, r in df.iterrows():
    #
    #         if os.path.isfile(os.path.join(self.DIR_GIT_PDF, r["PartNo"]+".pdf")):
    #             PDF_link = "https://sirthomasii.github.io/VitroNotion/MVP/PDF/"+r["PartNo"].upper()+".pdf"
    #             PDF_link = "https://sirthomasii.github.io/VitroNotion/JS/DOWNLOAD.html?fileURL="+PDF_link
    #         else:
    #             PDF_link = 0
    #
    #         if os.path.isfile(os.path.join(self.DIR_GIT_STP, r["PartNo"]+".step")):
    #
    #             STP_link = "https://sirthomasii.github.io/VitroNotion/MVP/STP/"+r["PartNo"].upper()+".step"
    #             STP_link = "https://sirthomasii.github.io/VitroNotion/JS/DOWNLOAD.html?fileURL="+STP_link
    #         else:
    #             STP_link = 0
    #
    #         rows.append([str(r["PartNo"]),PDF_link,STP_link,r["DESCRIPTION"]])
    #
    #
    #     # to_write = df["PartNo"].copy()
    #
    #     with tag('table', klass="styled_table", **kwargs):
    #         with tag('tr'):
    #             for x in headings:
    #                 line('th', str(x))
    #         for row in rows:
    #             with tag('tr'):
    #                 i=1
    #                 for x in row:
    #                     if i==1 or i==4:
    #                         line('td', str(x), klass="bom_table")
    #
    #                     elif x==0:
    #                         line('td', "", klass="bom_table")
    #                     else:
    #                         with tag('td', klass="bom_table"):
    #                             with tag('a',href=str(x),target="_parent"):
    #                                 text(str(row[0]))
    #                     i+=1
    #
    #
    #     return doc.getvalue()
    #
    def dumpBOMimages(self,df, bom_path):
        pxl_doc = openpyxl.load_workbook(bom_path)
        sheet = pxl_doc['Sheet1']
        image_loader = SheetImageLoader(sheet)

        image_partNo = {}
        img_maxwidth = 0

        for i,r in df["PartNo"].items():

            if (image_loader.image_in(('A'+str(i+2)))):
                image = image_loader.get(('A'+str(i+2)))
                # image_partNo[r] = image
                img_path = os.path.join(self.DIR_GIT_BOM,"IMG",r+'.jpg')
                image.convert('RGB').save(img_path)
    #
    # def write_html_files(self):
    #     f = open(self.PATH_GIT_BOM_HTML, "w")
    #     f.write(self.writeHTML("",self.bom_html_str))
    #     f.close()
    #
    #     f = open(self.PATH_GIT_ORDERS_HTML, "w")
    #     f.write(self.writeHTML("",self.orders_html_str))
    #     f.close()
    #
    #     f = open(self.PATH_GIT_PDF_HTML, "w")
    #     f.write(self.writeHTML("",self.pdf_html_str))
    #     f.close()

if __name__ == "__main__":
    df = pd.read_csv("directories.csv",delimiter=";")
    threads = {}
    for i,r in df.iterrows():
        # print(r["LOCAL_DIR"])
        t = threading.Thread(target=pynotion, args=(r["LOCAL_DIR"],r["GIT_DIR"]))
        threads[i] = t
    threads[0].start()
    sleep(10)

    # py = pynotion()
