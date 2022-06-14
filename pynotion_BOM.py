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
from pathlib import Path
import asm_data

class pynotion:

    def __init__(self,DIR_ASM=None,SUB_DIR=None):

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

        self.main()

    def main(self):

        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")

        df = self.GET_BOM()
        response_BOM = self.create_BOM_db(df)
        self.add_BOM_pages(df, response_BOM["id"])

        response_SHOPPING = self.create_SHOPPING_db(df)
        self.add_SHOPPING_pages(df, response_SHOPPING["id"])

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

        bom_path = os.path.join(self.DIR_BOM, highest_v_file)
        BOM = pd.read_excel(bom_path,dtype=str).replace(r'\n','', regex=True)
        # print(highest_v_file)
        self.dumpBOMimages(BOM, bom_path)

        return BOM

    def create_SHOPPING_db(self,df, **kwargs):
        # df = df.drop('column_name', 1)
        headings = ["Purchased","Vendor/MFG","Shopping List","Purchase Order","Delivered","Cost"]
        Shopping_list_properties = {}
        for i,h in enumerate(headings):
            if h == "Vendor/MFG": Shopping_list_properties[h] = {"title": {}}
            elif h in ["Shopping List","Purchase Order"]: Shopping_list_properties[h] = {"files": {}}
            elif  h in ["Purchased","Delivered"]: Shopping_list_properties[h] = {"checkbox": {}}
            else: Shopping_list_properties[h] = {"rich_text": {}}

        response = pyn_c.curl_db(Shopping_list_properties,"Shopping list","📁")
        print(response)
        return response

    def create_BOM_db(self,df, **kwargs):
        # df = df.drop('column_name', 1)
        headings = df.columns.values
        BOM_properties = {}
        for i,h in enumerate(headings):
            if h == "PartNo": BOM_properties[h] = {"title": {}}
            elif h == "DOCUMENT PREVIEW": BOM_properties[h] = {"files": {}}
            else: BOM_properties[h] = {"rich_text": {}}

        response = pyn_c.curl_db(BOM_properties,"BOM","🗃️")
        print(response)
        return response

    def add_BOM_pages(self,df, db_id=None):
        # df = df.drop('column_name', 1)
        headings = df.columns.values
        df = df.fillna("")
        for i,r in df.iterrows():
            page_data = {}
            img_url = self.GIT_URL+"/MVP_02/BOM/IMG/"+r["PartNo"]+".jpg"
            for j,h in enumerate(headings):
                # img_url = ''
                if h == "PartNo":
                    page_data[h] = {"title": [{"text":{"content":str(df.iloc[i][h])}}]}
                elif h == "DOCUMENT PREVIEW": page_data[h] =  {"files": [{"name":img_url, "type":"external","external":{"url": str(img_url)}}]}
                else: page_data[h] = {"rich_text": [{"text":{"content":str(df.iloc[i][h])}}]}
            # page_data.replace("\'","\"").replace("\n","")
            # self.pp.pprint(page_data)
            print(pyn_c.curl_db_page(db_id, page_data))
            sleep(.3)

    def add_SHOPPING_pages(self,df, db_id=None):
        headings = ["Purchased","Vendor/MFG","Shopping List","Purchase Order","Delivered"]

        mfgs = [ f.name for f in os.scandir(self.DIR_SHOPPING_LIST) if f.is_dir() ]

        shopping_lists = list(Path(self.DIR_SHOPPING_LIST).rglob("*.xlsx" ))

        for i,item in enumerate(shopping_lists):
            page_data = {}
        #     img_url = self.GIT_URL+"/MVP_02/BOM/IMG/"+r["PartNo"]+".jpg"
            xlsx = Path(item).name
            stem = Path(item).stem
            vendor = stem
            if vendor != "VITROTEM":
                if stem in mfgs:
                    shopping_URL = self.GIT_URL+self.SUB_DIR+"/SHOPPING_LISTS/"+stem.upper()+"/"+stem.upper()+".xlsx"
                    # mfg = stem
                else:
                    # mfg = ''
                    shopping_URL = self.GIT_URL+self.SUB_DIR+"/SHOPPING_LISTS/"+stem.upper()+".xlsx"

                for j,h in enumerate(headings):
            #         # img_url = ''
                    if h == "Vendor/MFG":
                        page_data[h] = {"title": [{"text":{"content":vendor}}]}
                    # if h == "Manufacturer":
                    #     page_data[h] = {"rich_text": [{"text":{"content":mfg}}]}
                    elif h == "Shopping List": page_data[h] =  {"files": [{"name":shopping_URL, "type":"external","external":{"url": shopping_URL}}]}
                    elif h == "Purchase Order": page_data[h] =  {"files": []}
                    elif h in ["Purchased","Delivered"]:
                        page_data[h] = {"checkbox": False}
                    else: page_data[h] = {"rich_text": [{"text":{"content":""}}]}
            #     # page_data.replace("\'","\"").replace("\n","")
            #     # self.pp.pprint(page_data)
                print(pyn_c.curl_db_page(db_id, page_data))
            sleep(.3)

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
