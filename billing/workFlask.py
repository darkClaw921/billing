import redisWork
from flask import Flask, request, render_template
from flask_restx import Api, Resource, fields
from pprint import pprint  
from datetime import datetime
from workBitrix import get_task_work_time, create_item, get_crm_task, prepare_crm_task

app = Flask(__name__)
api = Api(app, version='1.0', title='pkGroup API',description='A pkGroup API billing',)


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
    
@api.route('/report/<int:entytyID>/<int:itemID>/<string:userID>')
class report_entity(Resource):
    def post(self,entytyID:int,itemID:int,userID:str):
        """Обновление сущности"""
        # pprint(request)
        userID=userID.split('_')[1] 
        print(f"{entytyID=}")
        print(f"{itemID=}")
        print(f"{userID=}")

        data = request.data
        entityID = data['entityID'] #Tb8_2
        itemID = data['itemID']
        userID = data['userID'].split('_')[1]

        pprint(data)
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
    
