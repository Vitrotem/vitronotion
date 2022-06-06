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


def create_db(db_properties):
    pp = pprint.PrettyPrinter(indent=4)
    url = "https://api.notion.com/v1/databases"

    headers = {
        "Accept": "application/json",
        "Notion-Version": "2022-02-22",
        "Content-Type": "application/json",
        "Authorization": "Bearer secret_jPLqKNJD68cdmhlSRKKDTDt7Yr0wzaqZUiDd4pbT650"
    }

    data = """
    {
        "parent": {
            "type": "page_id",
            "page_id": "05e0f0969ab4403d8ce5ff361eb27b8b"
        },
        "icon": {
        	"type": "emoji",
    			"emoji": "🎉"
      	},
      	"cover": {
      		"type": "external",
        	"external": {
        		"url": "https://website.domain/images/image.png"
        	}
      	},
        "title": [
            {
                "type": "text",
                "text": {
                    "content": "MVP1",
                    "link": null
                }
            }
        ],
        "properties": {}
    }
    """
    data = data.replace("\'","\"").replace("\n","")

    # payload["properties"] = json.loads(data)
    payload = json.loads(data)
    payload["properties"] = db_properties
    response = requests.post(url, json=payload, headers=headers)
    return json.loads(response.text)

def add_db_page(db_id, page_data):
    pp = pprint.PrettyPrinter(indent=4)

    url = "https://api.notion.com/v1/pages"
    headers = {
        "Accept": "application/json",
        "Notion-Version": "2022-02-22",
        "Content-Type": "application/json",
        "Authorization": "Bearer secret_jPLqKNJD68cdmhlSRKKDTDt7Yr0wzaqZUiDd4pbT650"
    }

    data = """
    {
    "parent": { "database_id": \""""+db_id+"""\" },
    "properties": {}
    }
    """
    # pp.pprint(json.loads(page_data))
    payload = json.loads(data)
    payload["properties"] = page_data

    response = requests.post(url, json=payload, headers=headers)
    return json.loads(response.text)       # self.pp.pprint(response['results'][0]['properties'])


# if __name__ == "__main__":
    # df = pd.read_csv("directories.csv",delimiter=";")
    # threads = {}
    # for i,r in df.iterrows():
    #     # print(r["LOCAL_DIR"])
    #     t = threading.Thread(target=pynotion, args=(r["LOCAL_DIR"],r["GIT_DIR"]))
    #     threads[i] = t
    #     threads[i].start()
    #     sleep(10)
    # pyn = pynotion_curl()
    # py = pynotion()
