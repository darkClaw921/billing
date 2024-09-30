import time
import redisWork
from flask import Flask, request, render_template
from flask_restx import Api, Resource, fields
from pprint import pprint  
from datetime import datetime, timedelta
from workBitrix import get_task_work_time, create_item, get_crm_task, \
    create_billing_for_task,get_task_elapseditem_getlist, \
    update_report_for_item, get_billing_items, BillingItem, \
    create_billing_for_event,get_calendar_event, \
    update_project_for_sotrudnik,update_billing_for_event
import asyncio

app = Flask(__name__)
api = Api(app, version='1.0', title='pkGroup API',description='A pkGroup API billing',)
from queue import Queue
# Создание экземпляра очереди
request_queue = Queue()
REPORT_ITEM_ID=159
@api.route('/task')
class task_entity(Resource):
    def post(self,):
        """Обновление сущности"""
        data = request.get_json() 
        pprint(data)
        taskID = data['a'][2].split('=')[1]
        workList=get_task_work_time(taskID)
        lenWork=len(workList)
        
        oldLenWork=redisWork.get_lenWork_for_task(taskID)
        if oldLenWork == lenWork:
            return 'OK'
        elif oldLenWork < lenWork:
            redisWork.update_lenWork_for_task(taskID, lenWork)

        workList=workList[oldLenWork:]
        for work in workList:
            create_item(work['SECONDS'], taskID, work['COMMENT_TEXT'], work['CREATED_DATE'])

        # pprint(a)

        return 'OK'
    
    def get(self,):
        """Обновление сущности"""
        pprint(request)
        data = request.get_json() 
        pprint(data)
        return 'OK'


@api.route('/event-old')
class task_entity(Resource):
    def post(self):
        """Обновление сущности"""
        data = request.form
        pprint(data)

        # Добавление задачи в очередь
        request_queue.put(data)

        # Обработка задачи
        self.process_queue()

        return 'OK'

    def process_queue(self):
        """Обработка элементов из очереди"""
        while not request_queue.empty():
            # Получение задачи из очереди
            data = request_queue.get()
            event= data['event']
            
            if event == 'ONCALENDARENTRYADD':
                eventID = data['data[id]']
                 
                print(f"{eventID=}")
                event = get_calendar_event(eventID)
                pprint(event)
                create_billing_for_event(event=event)

            # Сигнализация о том, что задача обработана
                request_queue.task_done()
            
            if event == 'ONCALENDARENTRYUPDATE':
                eventID = data['data[id]']
                print(f"{eventID=}")
                event = get_calendar_event(eventID)
                pprint(event)

                update_billing_for_event(event=event)
                # create_billing_for_event(event=event)
                request_queue.task_done()

            if event == 'ONTASKUPDATE':
                taskID=data['data[FIELDS_BEFORE][ID]']
                #если задача не закрыта то биллинг не создатся 
                create_billing_for_task(taskID=taskID)
@api.route('/event')
class task_entity(Resource):
    async def post(self):
        """Обновление сущности"""
        data = request.form
        pprint(data)

        # Добавление задачи в очередь
        # request_queue.put(data)

        # Получение задачи из очереди
        # data = request_queue.get()
        event= data.get('event')
        
        if event == 'ONCALENDARENTRYADD':
            eventID = data['data[id]']
                
            print(f"{eventID=}")
            event = await get_calendar_event(eventID)
            pprint(event)
            create_billing_for_event(event=event)

        # Сигнализация о том, что задача обработана
            # request_queue.task_done()
        
        if event == 'ONCALENDARENTRYUPDATE':
            eventID = data['data[id]']
            print(f"{eventID=}")
            event = await get_calendar_event(eventID)
            pprint(event)

            update_billing_for_event(event=event)
            # create_billing_for_event(event=event)
            # request_queue.task_done()

        if event == 'ONTASKUPDATE':
            taskID=data['data[FIELDS_BEFORE][ID]']
            #если задача не закрыта то биллинг не создатся 
            create_billing_for_task(taskID=taskID)

    def get(self,):
        """Обновление сущности"""
        pprint(request)
        # data = request.get_json() 
        # pprint(data)
        return 'OK'

@api.route('/project/<string:userID>/<string:projectID>')
class Project_entity(Resource):
    def post(self,userID:str,projectID:str):
        """Обновление сущности"""
        # data = request.get_json() 
        # pprint(data)
        print(f"{userID=}")
        print(f"{projectID=}")
        # try:
        projectID=projectID.split('_')
        if projectID[0] != 'T9e':
            return 'No'
        projectID=projectID[1]
        # except:
            # 1+0
        update_project_for_sotrudnik(userID, projectID)
        # tasks=get_crm_task(13)
        # p=prepare_crm_task(tasks)
        
        return 'OK'
@api.route('/report/<string:entitiID>/<int:itemID>/<string:userID>/<string:startDate>/<string:endDate>')
class report_entity(Resource):
    def post(self,entitiID:int,itemID:int,userID:str,startDate:str,endDate:str):
        """Обновление сущности"""
        # pprint(request)
        userID=userID.split('_')[1] 
        entitiID=entitiID.split('_')[0]
        if entitiID != 'T9f': return 'Not report'
        
        entitiID=REPORT_ITEM_ID
            
        print(f"{entitiID=}")
        print(f"{itemID=}")
        print(f"{userID=}")

        # timeNOW=datetime.now().isoformat(timespec='seconds')
        startDateMonth=datetime.now().replace(day=1, hour=0,minute=0,second=0).isoformat(timespec='seconds')
        print(startDateMonth)
        # print(timeNOW)
        # timeBack=datetime.now()-timedelta(minutes=1)
        # timeBack=datetime.now()-timedelta(days=10)
        # timeBack=timeBack.isoformat(timespec='seconds')
        # print(timeBack)
        # 1/0
        #formated date 1.1.2024 to 2024-01-01T00:00:00
        
        
        startDate=startDate.split('.')
        startDate=f"{startDate[2]}-{startDate[1]}-{startDate[0]}T00:00:00"
        endDate=endDate.split('.')
        endDate=f"{endDate[2]}-{endDate[1]}-{endDate[0]}T23:59:59"




        billingItems=get_billing_items(userID=userID,startDate=startDate,endDate=endDate)
        pprint(billingItems)
        allduration=0
        countBilling=0
        allDurationToBuy=0
        for item in billingItems:
            if item['stageId'].find(':FAIL') != -1:
                continue
            allduration+=float(item[BillingItem.trydozatrary])
            allDurationToBuy+=float(item[BillingItem.trydozatratyKoplate])
            countBilling+=1

        pprint(allduration)
        pprint(allDurationToBuy)
        



        # elapseditem=get_task_elapseditem_getlist(str(startDateMonth),userID=userID)# '2024-04-20T18:01:00' 
        # pprint(elapseditem)
        # allduration=0
        # for item in elapseditem:
        #     allduration+=int(item['SECONDS'])
        # pprint(allduration)

        # allduration=allduration/3600
        # allduration=round(allduration, 1)

        update_report_for_item(entinyID=entitiID,itemID=itemID, trydozatraty=allduration, countBillung=countBilling,trydozatratyKoplate=allDurationToBuy)




        # data = request.data
        # entityID = data['entityID'] #Tb8_2
        # itemID = data['itemID']
        # userID = data['userID'].split('_')[1]

        # pprint(data)
        return 'OK'
    
    # def post(self,):
    #     """Обновление сущности"""
    #     data = request.get_json() 
    #     pprint(data)
    #     # tasks=get_crm_task(13)
    #     # p=prepare_crm_task(tasks)
        
    #     return 'OK'

async def a():
    eventID='1122'    
    print(f"{eventID=}")
    event = await get_calendar_event(eventID)
    pprint(event)

if __name__ == '__main__':
    # asyncio.run(a())
    app.run(host='0.0.0.0',port='5006',debug=False)
    

    # update_billing_for_event(event=event)
    
