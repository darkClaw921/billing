

import random
from fast_bitrix24 import Bitrix
import os
from dotenv import load_dotenv
from pprint import pprint
from dataclasses import dataclass
from datetime import datetime, timedelta
# import urllib3
import urllib.request
import time
import asyncio
# from helper import get_last_day_of_month

load_dotenv()
webhook = os.getenv('WEBHOOK')
bit = Bitrix(webhook)



if __name__ == "__main__":
    
    #get task by id
    # taskID=45
    taskID=141
    task = bit.call('tasks.task.get', {'taskId': taskID, 'select':['*','UF_CRM_TASK']}, raw=True)['result']['task']
    pprint(task)

    #update task
    # taskID=45
    firlds={'TITLE': 'test22','UF_CRM_TASK':['T9e_65', 'C_11']}
    
    task = bit.call('tasks.task.update', {'taskId': taskID, 'fields':firlds}, raw=True)['result']

    