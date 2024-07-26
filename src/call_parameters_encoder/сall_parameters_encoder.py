from urllib.parse import quote

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
            # list_params.append(f"{key}={quote(str(value))}")
            list_params.append(f"{str(key)}={str(value)}") # Почему-то на сайте не используется процентное кодирование.

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
                # list_params.append(f"{key}={quote(str(value))}")
                list_params.append(f"[{str(key)}]={str(value)}") # Почему-то на сайте не используется процентное кодирование.
    else:
        for key, value in enumerate(params):
            if (type(value)==list or type(value)==dict):
                list_params.extend([f"[{str(key)}]{for_value}" for for_value in call_parameters_encoder_recursion(value)])
            else:
                # list_params.append(f"{key}={quote(str(value))}")
                list_params.append(f"[{str(key)}]={str(value)}") # Почему-то на сайте не используется процентное кодирование.
    return list_params