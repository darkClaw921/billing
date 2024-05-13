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
from helper import get_last_day_of_month
load_dotenv()
webhook = os.getenv('WEBHOOK')
bit = Bitrix(webhook)
BILLING_ITEM_ID=168
PROJECT_ITEM_ID=153
# TODO: нужно как-то получить id проекта автоматически а так можно посомтреть через get
# case ['T99', itemID]:

@dataclass
class Lead:
    userName:str
    title:str='TITLE'
    userID:str='UF_CRM_1709220784686'
    photos:str='UF_CRM_1709223951925'
    urlUser:str='UF_CRM_1709224894080'
    messageURL:str='UF_CRM_1709293438392'

    description:str='COMMENTS'

@dataclass
class Deal:
    id:str='ID'
    title:str='TITLE'
    categoryID:str='CATEGORY_ID'
    statusID:str='STATUS_ID'
    comments:str='COMMENTS'
    responsibleID:str='ASSIGNED_BY_ID'

@dataclass
class BillingItem:
    id:str='id'
    title:str='title'
    # duration:str='UF_CRM9_1713363122'

    dateClose:str='ufCrm10_1715010793674'
    # dateClose:str='ufCrm_17Date'
    # entityTypeId:str='ENTITY_TYPE_ID 
    # fields:str='FIELDS'
    trydozatrary:str='ufCrm10_1715009361575'
    stavka:str='ufCrm10_1715009373186'
    project:str='ufCrm10_1715009699'
    assigned:str='assignedById'
    
    

@dataclass
class ProjectItem:
    id:str='id'
    title:str='title'
    # duration:str='UF_CRM9_1713363122'
    # dateClose:str='UF_CRM9_1713363093'
    trydozatrary:str='ufCrm10_1715009361575'
    stavka:str='ufCrm10_1715009373186'

@dataclass
class ReportItem:
    month:str='ufCrm12_1715167326269'
    trydozatrary:str='ufCrm12_1715167372937'

# async def te
def find_deal(dealID:str):
    deal = bit.call('crm.deal.get', params={'id': dealID})
    return deal

def find_lead(leadID:str):
    lead = bit.call('crm.lead.get', params={'id': leadID})
    return lead


def get_deals():
    prepareDeal=[]
    deals = bit.call('crm.deal.list', items={'filter': 
                                             {'STAGE_SEMANTIC_ID':'S'}}, raw=True)['result']
    for deal in deals:
        
        product=bit.call('crm.deal.productrows.get', items={'id': int(deal['ID'])}, raw=True)['result']
        
        a={'deal':deal,
            'product':product}
        
        prepareDeal.append(a)
    pprint(prepareDeal)
    return prepareDeal

def get_products():
    products = bit.call('crm.product.list', raw=True)['result']
    pprint(products)
    return products

def get_users():
    prepareUser = []
    # users = bit.call('user.get', items={'filter' :{'ACTIVE':False}})
    users = bit.call('user.get', raw=True)['result']
    # for user in users:
        # prepareUser.append(f'[{user["ID"]}] {user["NAME"]} {user["LAST_NAME"]}')
    # pprint(users)
    # print(prepareUser)
    return users

def get_departments():
    departments = bit.call('department.get', raw=True)['result']
    pprint(departments)
    return departments

def get_task_work_time(id)->list:
    # task=bit.call('tasks.task.get', items={'taskId': id}, raw=True)['result']
    task=bit.call('task.elapseditem.getlist', items={'ID': id}, raw=True)['result']
    # pprint(task)
    return task

def create_item(duretion,taskID, comment, dateClose):
    bit.call('crm.item.add', items={
                            'entityTypeId':179, #биллинг
                            'fields': {'title': comment,
                                'ufCrm9_1713363122': duretion,
                                'ufCrm9_1713363093': dateClose.split('+')[0],}})

def add_new_post_timeline(itemID, entityID, entityType):
    bit.call('crm.timeline.comment.add', items={
                            'fields': {'ENTITY_ID': entityID,
                                'ENTITY_TYPE': entityType,
                                'COMMENT': """Создан новый пост
                                Test comment [URL=/crm/deal/details/26/]test123[/URL]""",}}) #для ссылки в нутри битрикса


def get_task(taskID):
    task = bit.call('tasks.task.get', items={'taskId': taskID, 'select':['UF_CRM_TASK','TITLE']}, raw=True)['result']
    # pprint(task)
    return task

# def get_item(entinyID, itemID):
def get_item(entinyID):
    enID=0
    itID=0
    match entinyID.split('_'):
        
        case ['T99', itemID]: #процесс проект
            # print(itemID)
            # pprint(PROJECT_ITEM_ID)

            enID=PROJECT_ITEM_ID
            itID=itemID
        case _: 
            pprint(1)
    
    # 1/0
    item=bit.call('crm.item.get', items={'entityTypeId':enID,'id': itID}, raw=True)['result']['item']
    # pprint(item)
    return item

def prepare_crm_task(tasks:list)->str:
    prepareTask=[]
    for task in tasks:
        taskID=task['id']
        taskName=task['title']
        taskDescription=task['description']
        taskDurationFackt=task['durationFact']
        taskDurationPlan=task['durationPlan']
        taskDurationType=task['durationType']
        # taskAssignedBy=task['responsibleId']
        taskAssignedBy=task['responsible']['name']
        # taskCRM=task['UF_CRM_TASK']
        prepareTask.append({'taskID':taskID, 'taskName':taskName, 
                            'taskDurationFackt':taskDurationFackt,
                            'taskDurationPlan':taskDurationPlan, 'taskDurationType':taskDurationType,
                            'taskAssignedBy':taskAssignedBy, 'description':taskDescription})
    allTasks=''
    for task in prepareTask:
        allTasks+=f"""ID:{task["taskID"]} 
Title: {task["taskName"]} 
Description: {task["description"]} 
Факт(min): {task["taskDurationFackt"]}
План: {task["taskDurationPlan"]} 
Длительность: {task["taskDurationType"]} 
Испольнитель: {task["taskAssignedBy"]}\n\n"""
    
    print(allTasks)
    return allTasks

def get_crm_task(taskID:str)->list:
    """T89_9 если нужно по проектам"""
    task = bit.call('tasks.task.list', items={ 
                                            #  'select':['UF_CRM_TASK','TITLE'],
                                             'filter':{'UF_CRM_TASK':taskID},}, raw=True)['result']['tasks']
    pprint(task)
    return task


def update_tasks_for_item(entinyID, itemID, tasks:str):
    # enID=0
    # itID=0

    fields={'ufCrm7_1713540841714':tasks}
    # 1/0
    bit.call('crm.item.update', items={'entityTypeId':entinyID,'id': itemID, 'fields':fields})

def update_report_for_item(entinyID, itemID, trydozatraty :str, month:str):

    fields={
            ReportItem.trydozatrary: trydozatraty
            }


    bit.call('crm.item.update', items={'entityTypeId':entinyID,'id': itemID, 'fields':fields})

def get_activity(activityID:str):
    activity = bit.call('crm.activity.get', items={'id': activityID})
    return activity

def get_task_elapseditem_getlist(date:str, userID=None):
    """Вернет все потраченное время на задачи после указанной даты >=date

    Args:
        date (str): '2024-04-20T18:01:00'

    Returns:
        _type_: _description_
    """
    # task = bit.call('task.elapseditem.getlist', items={'>=CREATED_DATE': '2021-09-01T00:00:00'}, raw=True)['result']
    # task = bit.call('task.elapseditem.getlist', items=[1,{'ID': 'desc'},{'>=CREATED_DATE': '2021-09-01T00:00:00','iNumPage':1}])
    # task = bit.call('task.elapseditem.getlist', items=[{'ID': 'desc'},{'ID': 15}], raw=True)['result']
 
    #NOTE
    # если на станице данных больге нет то вернет []
    #очень важно соблюдать порядок вложенности
    # https://dev.1c-bitrix.ru/rest_help/tasks/task/elapseditem/getlist.php
    tasks=[]
    numPage=1
    while True:
        if userID is None:
            task = bit.call('task.elapseditem.getlist', items=[{'ID': 'desc'}, #сортировка по ID
                                                    {'>=CREATED_DATE': date}, #FILTER
                                                    ['ID', 'TASK_ID', 'USER_ID','CREATED_DATE','SECONDS','COMMENT_TEXT'], #SELECT
                                                    {'NAV_PARAMS':{'nPageSize':2,#MAX 50
                                                                   'iNumPage':numPage}}], #СТРАНИЦЫ 
                                                    raw=True)['result']
        
        else:
            task = bit.call('task.elapseditem.getlist', items=[{'ID': 'desc'}, #сортировка по ID
                                                    {'>=CREATED_DATE': date,
                                                     'USER_ID':userID}, #FILTER
                                                    ['ID', 'TASK_ID', 'USER_ID','CREATED_DATE','SECONDS','COMMENT_TEXT'], #SELECT
                                                    {'NAV_PARAMS':{'nPageSize':2,#MAX 50
                                                                   'iNumPage':numPage}}], #СТРАНИЦЫ 
                                                    raw=True)['result']
        if task==[] or numPage>=50:
            break

        tasks.extend(task)
        numPage+=1
        print(f'{numPage=}')

    t={'COMMENT_TEXT': '23222ываываыв',
  'CREATED_DATE': '2024-04-30T17:39:00+03:00',
  'DATE_START': '2024-04-30T17:39:14+03:00',
  'DATE_STOP': '2024-04-30T17:39:14+03:00',
  'ID': '21',
  'MINUTES': '60',
  'SECONDS': '3600',
  'SOURCE': '2',
  'TASK_ID': '13',
  'USER_ID': '11'},

    # pprint(task)
    return tasks


def create_billing_item(fields:dict):
    bit.call('crm.item.add', items={'entityTypeId':BILLING_ITEM_ID, 'fields':fields})

def get_billing_items(userID:str):
    """Возвращает все записи по биллингу за месяц по пользователю

    Args:
        userID (str): _description_

    Returns:
        _type_: _description_
    """

    startDateMonth=datetime.now().replace(day=1, hour=0,minute=0,second=0).isoformat(timespec='seconds')
    endDateMonth=get_last_day_of_month()
    print(f'{startDateMonth=}')
    print(f'{endDateMonth=}')

    items = bit.get_all('crm.item.list', params={'entityTypeId':BILLING_ITEM_ID,
                                             'filter':
                                                {
                                                f'>={BillingItem.dateClose}': startDateMonth,
                                                f'<={BillingItem.dateClose}': endDateMonth,
                                                'assignedById': userID}
                                            }, )
                                            #
                                            #   }, raw=True)['result']
                                             
    
    return items

def main():

    # pass
    # asyncio.run(get_deals())
    # get_deals()\
    # get_products()
    # get_users()
    # # get_departments()
    # add_new_post_timeline(1, 179, 'item')
    # add_new_post_timeline(1, 7, 'deal')
    timeNOW=datetime.now().isoformat(timespec='seconds')
    # print(timeNOW)
    timeBack=datetime.now()-timedelta(days=6)
    # timeBack=datetime.now()-timedelta(days=2)
    timeBack=timeBack.isoformat(timespec='seconds')
    print(timeBack)
    # 1/0
    elapseditem=get_task_elapseditem_getlist(str(timeBack))# '2024-04-20T18:01:00') 
    pprint(elapseditem)

    for item in elapseditem:
        taskID=item['TASK_ID']
        duration=int(item['SECONDS'])
        title=item['COMMENT_TEXT']
        dateClose=item['CREATED_DATE']
        userID=item['USER_ID']
        if duration<360:
            continue
        # create_item(duration, taskID, title, dateClose)
        
        # taskID=item['ID']
        task=get_task(taskID=taskID) 
        pprint(task)
        projectIDtask=task['task']['ufCrmTask'][0] # T89_13
        project=get_item(projectIDtask)  
        pprint(project)
        duration=duration/3600
        duration=round(duration, 1)
        
        fields={
            BillingItem.assigned: userID,
            BillingItem.title: title,
            BillingItem.trydozatrary: duration,
            BillingItem.dateClose: dateClose.split('+')[0],
            BillingItem.project: projectIDtask.split('_')[1],
        }
        create_billing_item(fields)



if __name__ == '__main__':
    main()
    # billingItems=get_billing_items(userID=1)
    # pprint(billingItems)
    # allduration=0
    # for item in billingItems:
    #     allduration+=int(item[BillingItem.trydozatrary])
    # allduration=allduration/3600
    # allduration=round(allduration, 1)
    # pprint(allduration)
    # print(get_last_day_of_month())
    # endDateMonth=datetime.now().replace(day=1, hour=0,minute=0,second=0)-timedelta(days=1)
    # pprint(endDateMonth.isoformat(timespec='seconds'))
    # tasks=get_crm_task('T89_13')
    # p=prepare_crm_task(tasks)
    # update_tasks_for_item(137, 13, p)


    # taskID=5
    # works=get_task_work_time(taskID)
    # for work in works:
    #     # print(work['COMMENT_TEXT'])
    #     duration=work['SECONDS']
    #     title=work['COMMENT_TEXT']
    #     create_item(duration, taskID, title)
    
    





