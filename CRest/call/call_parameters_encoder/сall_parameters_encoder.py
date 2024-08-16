from urllib.parse import quote
from CRest.settings import settings

def call_parameters_encoder(params: dict) -> str:
    """
    Пиринимает словарь параметров params и 
    возвращяет эти параметры представленные в виде строки.
    Пример:
    Создать новый контакт.
    https://dev.1c-bitrix.ru/rest_help/crm/contacts/crm_contact_add.php
    Вход:
    {
        "fields":{
            "NAME": "Глеб",
            "SECOND_NAME": "Егорович", 
			"LAST_NAME": "Титов", 
			"OPENED": "Y", 
			"ASSIGNED_BY_ID": 1, 
			"TYPE_ID": "CLIENT",
			"SOURCE_ID": "SELF",
			"PHOTO": { "fileData": <str> }, (В примере указано document.getElementById('photo') в место <str>, возможно нужно будет пересмотреть.)
			"PHONE": [ 
                { 
                    "VALUE": "555888", 
                    "VALUE_TYPE": "WORK" 
                } 
            ],
            "EMAIL":[
                {
                    "VALUE":"mail@example.com",
                    "VALUE_TYPE":"WORK"
                }
            ]
        }
    }
    Выход:
    FIELDS[NAME]=Глеб&
    FIELDS[SECOND_NAME]=Егорович&
    FIELDS[LAST_NAME]=Титов&
    FIELDS[OPENED]=Y&
    FIELDS[ASSIGNED_BY_ID]=1&
    FIELDS[TYPE_ID]=CLIENT&
    FIELDS[PHOTO][FILEDATA]=<str>&
    FIELDS[PHONE][0][VALUE]=555888&
    FIELDS[PHONE][0][VALUE_TYPE]=WORK&
    FIELDS[EMAIL][0][VALUE]=mail@example.com&
    FIELDS[PHONE][0][VALUE_TYPE]=WORK
    """
    list_params = []
    for key, value in params.items():
        if (type(value)==list or type(value)==dict):
            list_params.extend([ str(key)+for_value for for_value in call_parameters_encoder_recursion(value)])
        else:
            list_params.append(f"{key}={quote(str(value))}")

    return "&".join(list_params)

def call_parameters_encoder_recursion(params: dict | list) -> list:
    """
    Вспомогателный метод для call_parameters_encoder.
    Отличается тем что в место строки:
    FIELDS[TYPE_ID]=CLIENT
    Сформерует строку:
    [FIELDS][TYPE_ID]=CLIENT
    И вернёт список не соеденённых параметров.
    """
    list_params = []
    if (type(params)==dict):
        for key, value in params.items():
            if (type(value)==list or type(value)==dict):
                list_params.extend([f"[{str(key)}]{for_value}" for for_value in call_parameters_encoder_recursion(value)])
            else:
                list_params.append(f"[{key}]={quote(str(value))}")
    else:
        for key, value in enumerate(params):
            if (type(value)==list or type(value)==dict):
                list_params.extend([f"[{str(key)}]{for_value}" for for_value in call_parameters_encoder_recursion(value)])
            else:
                list_params.append(f"[{key}]={quote(str(value))}")
    return list_params


def call_parameters_encoder_batсh(calls: list, start: int, end: int) -> str:
    """
    !!! Примечание кодирование массива начинается с 1 т.к. в таком случае в ответе содержатся индексы.
    !!! Также если, происходит ошибка в первом методе, то он не нумеруется.
    !!! По этому нумерация с 1.

    Принемает пакет запросов и приобразовывает его в строки параметров.
    Calls:
    [
        {
            "method": "crm.contact.add",
            "params": {
                "FIELDS":{
                    "NAME":"Иван",
                    "LAST_NAME":"Петров"
                }
            }
        },
        ...
    ]
    res = "cmd[1]crm.contact.add%3FFIELDS%5BNAME%5D%3D%25D0%2598%25D0%25B2%25D0%25B0%25D0%25BD1%26FIELDS%5BLAST_NAME%5D%3D%25D0%259F%25D0%25B5%25D1%2582%25D1%2580%25D0%25BE%25D0%25B21&cmd[2]crm.contact.add%3FFIELDS%5BNAME%5D%3D%25D0%2598%25D0%25B2%25D0%25B0%25D0%25BD2%26FIELDS%5BLAST_NAME%5D%3D%25D0%259F%25D0%25B5%25D1%2582%25D1%2580%25D0%25BE%25D0%25B22"
    """
    call = []
    for i in range(end-start):
        index = i + start
        call.append(f"cmd[{str(index+1)}]="+quote(calls[index]["method"]+"?"+call_parameters_encoder(calls[index]["params"])))

    return "&".join(call)


def call_parameters_encoder_batсh_by_index(calls: list, index:list[int]) -> str:
    """
    !!! Примечание кодирование массива начинается с 1 т.к. в таком случае в ответе содержатся индексы.
    !!! Также если, происходит ошибка в первом методе, то он не нумеруется.
    !!! По этому нумерация с 1.

    Принемает пакет запросов и приобразовывает его в строки параметров.
    Calls:
    [
        {
            "method": "crm.contact.add",
            "params": {
                "FIELDS":{
                    "NAME":"Иван",
                    "LAST_NAME":"Петров"
                }
            }
        },
        ...
    ]
    res = "cmd[1]crm.contact.add%3FFIELDS%5BNAME%5D%3D%25D0%2598%25D0%25B2%25D0%25B0%25D0%25BD1%26FIELDS%5BLAST_NAME%5D%3D%25D0%259F%25D0%25B5%25D1%2582%25D1%2580%25D0%25BE%25D0%25B21&cmd[2]crm.contact.add%3FFIELDS%5BNAME%5D%3D%25D0%2598%25D0%25B2%25D0%25B0%25D0%25BD2%26FIELDS%5BLAST_NAME%5D%3D%25D0%259F%25D0%25B5%25D1%2582%25D1%2580%25D0%25BE%25D0%25B22"
    """
    call = []
    for i in index:
        call.append(f"cmd[{str(i+1)}]="+quote(calls[i]["method"]+"?"+call_parameters_encoder(calls[i]["params"])))

    return "&".join(call)
    
    