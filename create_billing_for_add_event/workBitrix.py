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
from helper import get_last_day_of_month
load_dotenv()
webhook = os.getenv('WEBHOOK')
bit = Bitrix(webhook)
import traceback
from loguru import logger
logger.add("logs/workBitrix_{time}.log",format="{time} - {level} - {message}", rotation="100 MB", retention="10 days", level="DEBUG")


BILLING_ITEM_ID=os.getenv('BILLING_ITEM_ID')
PROJECT_ITEM_ID=os.getenv('PROJECT_ITEM_ID')
CHECK_HAVE_UPDATE_UP_TASK=os.getenv('CHECK_HAVE_UPDATE_UP_TASK')
CHECK_HAVE_UPDATE_LOWER_TASK=os.getenv('CHECK_HAVE_UPDATE_LOWER_TASK')
SOTRYDNIK_ITEM_ID=0 #тут нету

# TODO: нужно как-то получить id проекта автоматически а так можно посомтреть через get
# case ['T99', itemID]:
#ПРОЕКТЫ
# 'T9e_158'
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

    # dateClose:str='ufCrm10_1715010793674'
    dateClose:str='ufCrm17Date'
    # entityTypeId:str='ENTITY_TYPE_ID 
    # fields:str='FIELDS'
    trydozatrary:str='ufCrm17Duration'
    trydozatratyKoplate:str='ufCrm17Durationbillable'
    stavka:str='None'
    project:str=f'parentId{PROJECT_ITEM_ID}'#umbrella
    assigned:str='assignedById'
    
@dataclass
class Task:
    id:str='id'
    title:str='title'
    check_have_update_up:str=CHECK_HAVE_UPDATE_UP_TASK.__str__()
    check_have_update_lower:str=CHECK_HAVE_UPDATE_LOWER_TASK.__str__()
    

@dataclass
class ProjectItem:
    id:str='id'
    title:str='title'
    # duration:str='UF_CRM9_1713363122'
    # dateClose:str='UF_CRM9_1713363093'
    trydozatrary:str='ufCrm10_1715009361575'
    stavka:str='ufCrm15Rates'
    UF_CRM_15_RATES:str='ufCrm15Rates'
@dataclass
class ReportItem:
    # month:str='ufCrm12_1715167326269'
    # month:str='ufCrm12_1715167326269'
    # trydozatrary:str='ufCrm12_1715167372937'
    trydozatrary:str='ufCrm27Durationfact' 
    trydozatratyKoplate:str='ufCrm27Durationfactbillable'
    # UF_CRM_27_DURATIONFACTBILLABLE:str='ufCrm27Durationfactbillable'
    countBilling:str='ufCrm27Billingsamount'
    startDate:str='begindate',
    closeDate:str='closedate',

@dataclass
class Calendar:
    id:str='ID'
    title:str='NAME'
    duration:str='DT_LENGTH'
    project:str='UF_CRM_CAL_EVENT'

@dataclass
class User:
    id:str='ID'
    name:str='NAME'
    lastName:str='LAST_NAME'
    secondName:str='SECOND_NAME'
    active:str='ACTIVE'
    email:str='EMAIL'
    department:str='UF_DEPARTMENT'
    lastProject:str='UF_USR_1716303188461'

@dataclass
class Sotrudnik:
    lastProject:str='ufCrm41_1716819274'
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
    task = bit.call('tasks.task.get', items={'taskId': taskID, 'select':['*','UF_CRM_TASK','TITLE']}, raw=True)['result']['task']
    # pprint(task)
    return task

# def get_item(entinyID, itemID):
def get_item(entinyID):
    enID=0
    itID=0
    match entinyID.split('_'):
        
        case ['T99', itemID]: #процесс проект test
        # case ['T9e', itemID]: #процесс проект
            print(itemID)
            # pprint(PROJECT_ITEM_ID)

            enID=PROJECT_ITEM_ID
            itID=itemID

        case _: 
            print('неизвестный тип должен быть в формате T9e')
    
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

def update_report_for_item(entinyID, itemID, trydozatraty :str, countBillung:int, trydozatratyKoplate,month:str='Aprill'):

    fields={
            ReportItem.trydozatrary: trydozatraty,
            ReportItem.countBilling: countBillung,
            ReportItem.trydozatratyKoplate: trydozatratyKoplate
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
                                                    ['ID', 'TASK_ID', 'USER_ID','CREATED_DATE','SECONDS','COMMENT_TEXT','DATE_STOP'], #SELECT
                                                    {'NAV_PARAMS':{'nPageSize':50,#MAX 50
                                                                   'iNumPage':numPage}}], #СТРАНИЦЫ 
                                                    raw=True)['result']
        
        else:
            task = bit.call('task.elapseditem.getlist', items=[{'ID': 'desc'}, #сортировка по ID
                                                    {'>=CREATED_DATE': date,
                                                     'USER_ID':userID}, #FILTER
                                                    ['ID', 'TASK_ID', 'USER_ID','CREATED_DATE','SECONDS','COMMENT_TEXT','DATE_STOP'], #SELECT
                                                    {'NAV_PARAMS':{'nPageSize':50,#MAX 50
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


async def create_billing_item(fields:dict):
    logger.debug(f'Создаем биллинг на основании {fields=}')
    id1= await bit.call('crm.item.add', items={'entityTypeId':BILLING_ITEM_ID, 'fields':fields})
    print(f'{id1=}')
    id1=id1['item']['id']

    return id1

def get_billing_items(userID:str, startDate:str, endDate:str):
    """Возвращает все записи по биллингу за месяц по пользователю

    Args:
        userID (str): _description_
        startDate:str (str): '2024-04-20T18:01:00'
    Returns:
        _type_: _description_
    """

    # startDate=datetime.now().replace(day=1, hour=0,minute=0,second=0).isoformat(timespec='seconds')
    # endDate=get_last_day_of_month()
    # print(f'{startDateMonth=}')
    # print(f'{endDateMonth=}')


    items = bit.get_all('crm.item.list', params={'entityTypeId':BILLING_ITEM_ID,
                                             'filter':
                                                {
                                                f'>={BillingItem.dateClose}': startDate,
                                                f'<={BillingItem.dateClose}': endDate,
                                                'assignedById': userID},
                                                # f'!={BillingItem.stage}'
                                            }, )
                                            #
                                            #   }, raw=True)['result']
                                             
    
    return items

def update_event(eventID:str, fields:dict):
    bit.call('calendar.event.update', items={'id': eventID, 'fields': fields})

async def create_billing_for_event(event:dict):


    # project=get_item(projectIDtask)  
    # pprint(project)
    # try:
    try:
        event=event['order0000000000']
    except:
        1+0
    projectIDtask=event.get('UF_CRM_CAL_EVENT') # T89_13

    # projectIDtask=event.get('UF_CRM_CAL_EVENT') # T89_13
    print(f'{projectIDtask=}')
    if projectIDtask is False: return 0
        # projectLastID=get_last_project_for_sotrudnik(event['CREATED_BY'])
        # projectIDtask=f'T9e_{projectLastID}' # T89 просто для целосности данных
        # update_event(event['ID'], {'UF_CRM_CAL_EVENT': [projectIDtask]})
    else:
        projectIDtask=projectIDtask[0]

    duration=event['DT_LENGTH']
    duration=duration/3600
    duration=round(duration, 2)

    title=event['NAME']
    dateClose=event['DATE_FROM']

    
    dateClose=dateClose.split(' ')[0].split('.')
    dateClose=f"{dateClose[2]}-{dateClose[1]}-{dateClose[0]}T00:00:00"

    ATTENDEES_CODES=event['ATTENDEES_CODES']
    for code in ATTENDEES_CODES:
        try:
            code.startswith('U')
        except:
            code='U'+event['CREATED_BY']

        if code.startswith('U'):
            userID=code.replace('U','')
            
            fields={
                # BillingItem.assigned: event['CREATED_BY'],
                BillingItem.assigned: userID,
                BillingItem.title: title,
                BillingItem.trydozatrary: duration,
                BillingItem.trydozatratyKoplate: duration,
                BillingItem.dateClose: dateClose,
                BillingItem.project: projectIDtask.split('_')[1],
            }
            # pprint(fields)
            logger.info(f'{fields=}')
            await create_billing_item(fields)


async def find_billing(assignedID:int, title:str, dateClose:str)->list:
    # dateClose=dateClose.split(' ')[0].split('.')
    # dateClose=f"{dateClose[2]}-{dateClose[1]}-{dateClose[0]}T00:00:00"
    param={'entityTypeId':BILLING_ITEM_ID, \
                                               'filter': {
                                              'assignedById': assignedID,
                                              'title':title,
                                              BillingItem.dateClose:dateClose}}
    pprint(param)

    billing = await bit.get_all('crm.item.list', params=param)
    # pprint(billing)
    return billing




async def update_billing_for_event(event:dict):
    try:
        event=event['order0000000000']
    except:
        1+0
    projectIDtask=event.get('UF_CRM_CAL_EVENT') # T89_13

    print(f'{projectIDtask=}')
    if projectIDtask is False: return 0
 
    else:
        projectIDtask=projectIDtask[0]

    duration=event['DT_LENGTH']
    duration=duration/3600
    duration=round(duration, 2)

    title=event['NAME']
    dateClose=event['DATE_FROM']
    # pprint(event)
    print(f'{dateClose=}')

    
    dateClose=dateClose.split(' ')[0].split('.')
    dateClose=f"{dateClose[2]}-{dateClose[1]}-{dateClose[0]}"

    ATTENDEES_CODES=event['ATTENDEES_CODES']
    for code in ATTENDEES_CODES:
        try:
            code.startswith('U')
        except:
            code='U'+event['CREATED_BY']

        if code.startswith('U'):
            userID=code.replace('U','')
            logger.info(f'Ищем биллинг assignedID={userID}, {title=}, {dateClose=}')
            billing = await find_billing(assignedID=userID, title=title, dateClose=dateClose)
            # logger.info(f'Нашли {billing=}')
            if billing==[]:
                
                fields={
                    # BillingItem.assigned: event['CREATED_BY'],
                    BillingItem.assigned: userID,
                    BillingItem.title: title,
                    BillingItem.trydozatrary: duration,
                    BillingItem.trydozatratyKoplate: duration,
                    BillingItem.dateClose: dateClose,
                    BillingItem.project: projectIDtask.split('_')[1],
                }
                # pprint(fields)
                logger.info(f'Нет такого биллига создаем биллинг "{title}" на {dateClose}')
                try:

                    await create_billing_item(fields=fields)
                except Exception as e:
                    logger.error(f'не удалось создать биллинг "{title}" {e}')
                    logger.error(traceback.format_exc())
                    logger.error(traceback.print_exc())
                    
                    
            else:
                fields={
                    # BillingItem.assigned: event['CREATED_BY'],
                    # BillingItem.assigned: userID,
                    # BillingItem.title: title,
                    BillingItem.trydozatrary: duration,
                    BillingItem.trydozatratyKoplate: duration,
                    BillingItem.dateClose: dateClose,
                    BillingItem.project: projectIDtask.split('_')[1],
                }
                # print('Есть такой человек обновляем биллинг')
                logger.info(f'Есть такой биллинг обновляем "{title}" на {dateClose}')
                try:
                    # logger.warning(billing)
                    await update_billing(billing[0]['id'], fields=fields)
                    
                except Exception as e:
                    logger.error(f'не удалось обновить биллинг "{title}" {e}')
                

   
    pass


async def update_billing(billingID:str, fields:dict):
    await bit.call('crm.item.update', items={'entityTypeId':BILLING_ITEM_ID, 
                                       'id': billingID, 
                                       'fields':fields})
    return 0

def create_billing_for_trydozatrary():

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
    timeBack=datetime.now()-timedelta(minutes=1)
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

        stopDate=item['DATE_STOP']
        # format stopDate to datetime
        stopDate1=stopDate.split('+')[0]
        startDate1=dateClose.split('+')[0]
        print(f'{stopDate1=}')
        stopDate=datetime.strptime(stopDate1, '%Y-%m-%dT%H:%M:%S')
        startDate=datetime.strptime(startDate1, '%Y-%m-%dT%H:%M:%S')

        if duration<360 or stopDate-startDate<=timedelta(minutes=1):
            continue
        # create_item(duration, taskID, title, dateClose)
        
        # taskID=item['ID']
        task=get_task(taskID=taskID) 
        pprint(task)
        projectIDtask=task['task']['ufCrmTask'][0] # T89_13
        project=get_item(projectIDtask)  
        pprint(project)
        duration=duration/3600
        duration=round(duration, 2)
        
        fields={
            BillingItem.assigned: userID,
            BillingItem.title: title,
            BillingItem.trydozatrary: duration,
            BillingItem.dateClose: dateClose.split('+')[0],
            BillingItem.project: projectIDtask.split('_')[1],
        }
        # create_billing_item(fields)


async def get_calendar_event(eventID:str):
    # randomSecond=random.randint(2, 4)
    # time.sleep(randomSecond)
    try:
        event = await bit.call('calendar.event.getbyid', items={'id': eventID})
        return event
    except Exception as e:
        print(e)
        print(f"не удалось получить эвент для {eventID}")
        return -1 
    # return event

def get_all_calendar_events():
    events = bit.call('calendar.event.get', items={
        'type': 'user',
		'ownerId': '1',
		'from': '2024-05-10',
		'to': '2023-05-20',
		# 'section': [21, 44]
        })
    return events


def get_last_project_for_sotrudnik(userID:str):
    items = bit.get_all('crm.item.list', params={'entityTypeId':SOTRYDNIK_ITEM_ID,
                                             'filter':
                                                {
                                                'assignedById': userID},
                                            }, )
                                            #
                                      
           
    
    return items[0][Sotrudnik.lastProject], items[0]['id']

def update_project_for_sotrudnik(userID:str, projectID:str):
    projectIDlast,itemSotrudnikID=get_last_project_for_sotrudnik(userID)
    fields={Sotrudnik.lastProject: projectID}
    bit.call('crm.item.update', items={'entityTypeId':SOTRYDNIK_ITEM_ID,'id': itemSotrudnikID, 'fields':fields})


def prepare_date(date:str):
    new_format = "%Y-%m-%d %H:%M"

    old_date = datetime.strptime(date, "%d.%m.%Y %H:%M:%S")
    new_date_str = old_date.strftime(new_format)
    return new_date_str

def create_event(event:dict):
    #event['TO'] 28.05.2024 13:40:00 to '%Y-%m-%d %H:%M:%S'
    
    
    
    
    
    # items={
    #     'from':prepare_date(event['DATE_FROM']),
    #     'to':prepare_date(event['DATE_TO']),
    #     'ownerId':event['CREATED_BY'],
    #     'section':event['SECTION_ID'],
    #     'name':event['NAME'],
    #     'description':event['DESCRIPTION'],
    #     'location':event['LOCATION'],
    #     'is_meeting':'Y',
    #     # 'type':event['CAL_TYPE'],
    #     'type':'user',
    #     # 'type':'company_calendar',
    #     'UF_CRM_CAL_EVENT':['D_2'],

        
    # }
    # to = prepare_date(event['DATE_TO']),
    # print(to)
    # a = bit2./
    # eventID=bit.call('calendar.event.add', items=items, raw=True)['result']x
    # pprint(a)
    # return a
    pass

def add_billings_to_task(taskID:int, taskCrm:list, billings:list):
    #переводим биллинг в 16 ричную систему
    hexBilling = hex(int(BILLING_ITEM_ID))[2:]
    # billings=[f'Tad_{i}' for i in billings]
    billings=[f'T{hexBilling}_{i}' for i in billings]
    

    # task=get_task(taskID) 
    # crm=task['ufCrmTask']
    taskCrm.extend(billings)
    firlds={'UF_CRM_TASK':taskCrm}
    pprint(firlds)
    task = bit.call('tasks.task.update', {'taskId': taskID, 'fields':firlds}, raw=True)['result']

def create_billing_for_task(taskID:int):
    hexProject = hex(int(PROJECT_ITEM_ID))[2:]
    task=get_task(taskID)
    pprint(task)
    if task['closedDate'] is None :
        return 0
    if task[Task.check_have_update_lower] == '1':
        return 0
    
    durationFact=float(task['durationFact'])
    if  task['durationType'] == 'days':
        durationFact=durationFact/60
    else:
        durationFact=durationFact/3600
    
    durationFact=round(durationFact, 2)

    users=task['accomplices']
    users.append(task['responsibleId'])

    title=task['title']
    
    dateClose=task['closedDate'].split('T')[0]+'T00:00:00'
    # dateClose=task['closedDate']
    if not str(task['ufCrmTask'][0].split('_')[0]).startswith(f'T{hexProject}'):
        return 0
    projectID=task['ufCrmTask'][0].split('_')[1]
    
    billings=[]
    for user in users:
        fields={
            BillingItem.title: title,
            BillingItem.trydozatrary: durationFact,
            BillingItem.trydozatratyKoplate: durationFact,
            BillingItem.assigned: user,
            BillingItem.dateClose: dateClose,
            BillingItem.project: projectID,
        }
        pprint(fields)
        billingID=create_billing_item(fields)
        print(f'{billingID=}')
        billings.append(billingID)
    
    fields={Task.check_have_update_up:'1'}
    pprint(fields)
    bit.call('tasks.task.update', {'taskId': taskID, 'fields':fields}, raw=True)
    task=get_task(taskID)
    pprint(task)
    add_billings_to_task(taskID=taskID, taskCrm=task['ufCrmTask'], billings=billings)
    
    


import asyncio
async def main():
    # a= await bit2.callMethod('crm.product.list')
    # pprint(a)
    event=await get_calendar_event('62')
    pprint(event)

    eventID=await create_event(event)
    print(f'{eventID=}')
    event1=await get_calendar_event(eventID=eventID)
    pprint(event1)
    print('done')
# https://test-6-may.bitrix24.ru/rest/1/q62k8mchz97yjwap/calendar.event.add.json?type=user&to=2024-05-28+12:00&ownerId=1&FROM=2024-05-28+11:00&section=4&name=wee&is_meeting=Y&UF_CRM_CAL_EVENT%5B0%5D=1&start=0


if __name__ == '__main__':
    # create_billing_for_task(153)
    # a=bit.call('tasks.task.getFields', raw=True)
    # pprint(a)
    asyncio.run(find_billing(assignedID='23',
                             title='тест2',
                             dateClose='2024-05-23'))
    pass
    # eventt=get_calendar_event('231')
    # pprint(eventt)
    # billing= find_billing(11, 'Пример Ratio', '2024-07-26')
    # pprint(billing)
    
    # get_item(23)

    # item=bit.call('crm.item.get', items={'entityTypeId':BILLING_ITEM_ID,'id':'437' }, raw=True)
    # pprint(item)


