
import re
def extract_session_id(session_str:str):

    match=re.search(r"/sessions/(.*?)/contexts/",session_str)
    print(match)
    if match:
        extracted_session=match.group(1)
        return extracted_session
    return ""

#Testing
'''if __name__=="__main__":
    test=extract_session_id("projects/agent007-9qpw/agent/sessions/7fc73f07-0cf7-cf79-e7f1-96f01ebfaccd/contexts/47a87ca6-5b25-44e2-98d1-c674979690c0_id_dialog_context")
    print(test)'''

def get_string_from_food_dict(food_dict:dict):
    return ' ,'.join([f"{int(value)} {key}" for key,value in food_dict.items()])

if __name__=="__main__":
    test=get_string_from_food_dict({"pizza":2,"idli":1})
    print(test)