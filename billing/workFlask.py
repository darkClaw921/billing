import redisWork
from flask import Flask, request, render_template
from flask_restx import Api, Resource, fields
from pprint import pprint  
from datetime import datetime, timedelta
from workBitrix import get_task_work_time, create_item, get_crm_task, prepare_crm_task,get_task_elapseditem_getlist,update_report_for_item, get_billing_items, BillingItem

app = Flask(__name__)
api = Api(app, version='1.0', title='pkGroup API',description='A pkGroup API billing',)

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

        billingItems=get_billing_items(userID=userID,startDate=startDate,endDate=endDate)
        pprint(billingItems)
        allduration=0
        for item in billingItems:
            allduration+=float(item[BillingItem.trydozatrary])
        pprint(allduration)



        # elapseditem=get_task_elapseditem_getlist(str(startDateMonth),userID=userID)# '2024-04-20T18:01:00' 
        # pprint(elapseditem)
        # allduration=0
        # for item in elapseditem:
        #     allduration+=int(item['SECONDS'])
        # pprint(allduration)

        # allduration=allduration/3600
        # allduration=round(allduration, 1)

        update_report_for_item(entinyID=entitiID,itemID=itemID, trydozatraty=allduration, countBillung=len(billingItems))




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



if __name__ == '__main__':
    
    app.run(host='0.0.0.0',port='5007',debug=True)
    
