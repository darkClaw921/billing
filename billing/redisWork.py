import redis
import json
from pprint import pprint
r = redis.Redis(host='localhost', port=6379, decode_responses=False)


def add_new_task(taskID:str, lenWork:int):
    task={'taskID':taskID, 'lenWork':lenWork}    
    r.lpush(taskID, json.dumps(task))
    
def get_lenWork_for_task(taskID:str)->int:
    items = r.lrange(taskID, 0, -1)
    try:
        lenWork = [json.loads(m.decode("utf-8")) for m in items][0]['lenWork']
    except:
        lenWork = 0
    # pprint(lenWork)
    return lenWork

def update_lenWork_for_task(taskID:str, lenWork:int):
    task={'taskID':taskID, 'lenWork':lenWork}    
    r.lpush(taskID, json.dumps(task))




# def add_message_to_history(userID:str, role:str, message:str):
#     mess = {'role': role, 'content': message}
#     r.lpush(userID, json.dumps(mess))

# def add_old_history(userID:str, history:list):
#     his = history.copy()
#     clear_history(userID)
#     for i in his:
#         mess = i
#         r.lpush(userID, json.dumps(mess))

# def get_history(userID:str):
#     items = r.lrange(userID, 0, -1)
#     history = [json.loads(m.decode("utf-8")) for m in items[::-1]]
#     return history

# def clear_history(userID:str):
#     r.delete(userID)
# add_new_task('t1', 10)
if __name__ =='__main__':

    # a=get_lenWork_for_task('t1')
    # print(a)
    # update_lenWork_for_task('t1', 20)
    a=get_lenWork_for_task('t2')
    print(a)
