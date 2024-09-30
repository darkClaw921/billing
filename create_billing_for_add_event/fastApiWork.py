import time
import redisWork
from fastapi import FastAPI, Request, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi import BackgroundTasks
from pydantic import BaseModel
from pprint import pprint  
from datetime import datetime
from workBitrix import (
    get_task_work_time, create_item, get_crm_task,
    create_billing_for_task, get_task_elapseditem_getlist,
    update_report_for_item, get_billing_items, BillingItem,
    create_billing_for_event, get_calendar_event,
    update_project_for_sotrudnik, update_billing_for_event
)
import asyncio
from dotenv import load_dotenv
import os
from loguru import logger

# log = logger()
from loguru import logger
logger.add("logs/fastApi_{time}.log",format="{time} - {level} - {message}", rotation="100 MB", retention="10 days", level="DEBUG")

load_dotenv()

PORT = os.getenv('PORT')
app = FastAPI(title='pkGroup API', description='A pkGroup API billing')

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

REPORT_ITEM_ID = 159

@app.post('/task')
async def update_task(data: dict):
    """Обновление сущности"""
    pprint(data)
    taskID = data['a'][2].split('=')[1]
    workList = get_task_work_time(taskID)
    lenWork = len(workList)
    
    oldLenWork = redisWork.get_lenWork_for_task(taskID)
    if oldLenWork == lenWork:
        return JSONResponse(content={'message': 'OK'})
    elif oldLenWork < lenWork:
        redisWork.update_lenWork_for_task(taskID, lenWork)

    workList = workList[oldLenWork:]
    for work in workList:
        create_item(work['SECONDS'], taskID, work['COMMENT_TEXT'], work['CREATED_DATE'])

    return JSONResponse(content={'message': 'OK'})

@app.post('/event')
async def update_event(request: Request):
    """Обновление сущности"""
    form_data = await request.form()
    data = {key: form_data[key] for key in form_data.keys()}
    pprint(data)

    event = data.get('event')
    print(f"{event=}")
    
    if event == 'ONCALENDARENTRYADD':
        eventID = data['data[id]']
        print(f"{eventID=}")
        event = await get_calendar_event(eventID)
        # pprint(event)
        await create_billing_for_event(event=event)

    elif event == 'ONCALENDARENTRYUPDATE':
        eventID = data['data[id]']
        print(f"{eventID=}")
        event = await get_calendar_event(eventID)
        # pprint(event)
        await update_billing_for_event(event=event)
        

    elif event == 'ONTASKUPDATE':
        taskID = data['data[FIELDS_BEFORE][ID]']
        create_billing_for_task(taskID=taskID)

    return JSONResponse(content={'message': 'OK'})

@app.post('/project/{userID}/{projectID}')
async def update_project(userID: str, projectID: str):
    """Обновление сущности"""
    print(f"{userID=}")
    print(f"{projectID=}")
    projectID = projectID.split('_')
    if projectID[0] != 'T9e':
        return JSONResponse(content={'message': 'No'})
    projectID = projectID[1]
    update_project_for_sotrudnik(userID, projectID)
    return JSONResponse(content={'message': 'OK'})

@app.post('/report/{entitiID}/{itemID}/{userID}/{startDate}/{endDate}')
async def update_report(entitiID: str, itemID: int, userID: str, startDate: str, endDate: str):
    """Обновление сущности"""
    userID = userID.split('_')[1] 
    entitiID = entitiID.split('_')[0]
    if entitiID != 'T9f':
        return JSONResponse(content={'message': 'Not report'})
    
    entitiID = REPORT_ITEM_ID
    print(f"{entitiID=}")
    print(f"{itemID=}")
    print(f"{userID=}")

    startDate = startDate.split('.')
    startDate = f"{startDate[2]}-{startDate[1]}-{startDate[0]}T00:00:00"
    endDate = endDate.split('.')
    endDate = f"{endDate[2]}-{endDate[1]}-{endDate[0]}T23:59:59"

    billingItems = get_billing_items(userID=userID, startDate=startDate, endDate=endDate)
    pprint(billingItems)
    allduration = 0
    countBilling = 0
    allDurationToBuy = 0
    for item in billingItems:
        if item['stageId'].find(':FAIL') != -1:
            continue
        allduration += float(item[BillingItem.trydozatrary])
        allDurationToBuy += float(item[BillingItem.trydozatratyKoplate])
        countBilling += 1

    pprint(allduration)
    pprint(allDurationToBuy)

    update_report_for_item(entinyID=entitiID, itemID=itemID, trydozatraty=allduration, countBillung=countBilling, trydozatratyKoplate=allDurationToBuy)

    return JSONResponse(content={'message': 'OK'})

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=int(PORT), log_level="info")