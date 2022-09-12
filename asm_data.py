import pandas as pd
import numpy as np
import os
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
import sys

try:
   if sys.frozen or sys.importers:
      current_DIR = os.path.dirname(sys.executable)

except AttributeError:
   current_DIR = os.path.dirname(os.path.realpath(__file__))

def git_push(repo):
    ran = ''.join(random.choices(string.ascii_uppercase + string.digits, k = 10))
    repo = Repo(repo)
    repo.git.add(all=True)
    repo.index.commit(ran)
    origin = repo.remote(name='origin')
    origin.push()

class asm_data:

    def __init__(self,DIR_ASM=None,SUB_DIR=None):

        self.pp = pprint.PrettyPrinter(indent=4)

        doc, tag, text = Doc().tagtext()
        self.GIT_URL = "https://vitrotem.github.io/vitronotion/"
        self.SUB_DIR = SUB_DIR
        # self.SUB_DIR = "MVP_02"

        # self.DIR_ASM = r"C:\Users\tomgr\OneDrive\13 R&D\1. Device\MVP 02"
        self.DIR_ASM = DIR_ASM
        self.DIR_BOM = os.path.join(self.DIR_ASM, 'BOM')
        self.DIR_SHOPPING_LIST = os.path.join(self.DIR_ASM, 'SHOPPING_LISTS')

        self.DIR_GIT = os.path.join(current_DIR)
        self.SUB_DIR_GIT = os.path.join(self.DIR_GIT,self.SUB_DIR)
        self.DIR_GIT_BOM = os.path.join(self.SUB_DIR_GIT, 'BOM')
        self.DIR_GIT_BOM_IMG = os.path.join(self.DIR_GIT_BOM, 'IMG')
        self.DIR_GIT_SHOPPING_LIST = os.path.join(self.SUB_DIR_GIT, 'SHOPPING_LISTS')

        for x in [self.SUB_DIR_GIT,
                  self.DIR_GIT_BOM,
                  self.DIR_GIT_BOM_IMG,
                  self.DIR_GIT_SHOPPING_LIST
                  ]:

            self.genPath(x)

        self.main()

    def main(self):
        self.copy_directories()
        git_push(os.path.join(self.DIR_GIT,".git"))

    def genPath(self,path):
        isExist = os.path.exists(path)
        if not isExist:
          os.mkdir(path)

    def copy_directories(self):
        shutil.copytree(self.DIR_SHOPPING_LIST, self.DIR_GIT_SHOPPING_LIST, dirs_exist_ok=True)

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

if __name__ == "__main__":
    df = pd.read_csv("directories.csv",delimiter=";")
    threads = {}
    for i,r in df.iterrows():
        # print(r["LOCAL_DIR"])
        t = threading.Thread(target=asm_data, args=(r["LOCAL_DIR"],r["GIT_DIR"]))
        threads[i] = t
    threads[0].start()
