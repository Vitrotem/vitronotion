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
import requests
import json

def git_push(repo):
    ran = ''.join(random.choices(string.ascii_uppercase + string.digits, k = 10))
    repo = Repo(repo)
    repo.git.add(all=True)
    repo.index.commit(ran)
    origin = repo.remote(name='origin')
    origin.push()

class pynotion:

    def __init__(self):
        self.pp = pprint.PrettyPrinter(indent=4)

        url = "https://api.notion.com/v1/databases/2d719565bce14d26b7209d3bb1f8f2c7/query"

        payload = {"page_size": 100}
        headers = {
            "Accept": "application/json",
            "Notion-Version": "2022-02-22",
            "Content-Type": "application/json",
            "Authorization": "Bearer secret_jPLqKNJD68cdmhlSRKKDTDt7Yr0wzaqZUiDd4pbT650"
        }

        response = requests.post(url, json=payload, headers=headers)
        response = json.loads(response.text)

        # print()
        properties_list = []
        properties_dict = {}
        for k,v in response['results'][0]['properties'].items():
            properties_list.append(k)
            properties_dict[k]=''
        df = pd.DataFrame(columns=properties_list)

        for i, v in enumerate(response['results']):
            for k1,v1 in v["properties"].items():
                # property = k1
                # print(v1['type'])
                value = ''
                if v1['type'] in ["rich_text","title"] and len(v1[v1['type']])!=0:
                    value=v1[v1['type']][0]['plain_text']
                    properties_dict[k1] = value

                elif v1['type'] in ["select"] and v1[v1['type']]!=None:
                    value=v1[v1['type']]['name']
                    properties_dict[k1] = value

                else :
                    if(len(v1["files"])!=0):
                        print(v1)

            df = df.append(properties_dict, ignore_index=True)


        print(df)
        # self.pp.pprint(response['results'][0]['properties'])


if __name__ == "__main__":
    # df = pd.read_csv("directories.csv",delimiter=";")
    # threads = {}
    # for i,r in df.iterrows():
    #     # print(r["LOCAL_DIR"])
    #     t = threading.Thread(target=pynotion, args=(r["LOCAL_DIR"],r["GIT_DIR"]))
    #     threads[i] = t
    #     threads[i].start()
    #     sleep(10)
    pyn = pynotion()
    # py = pynotion()
