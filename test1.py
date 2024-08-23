from httpx import AsyncClient, HTTPStatusError

from CRest.call.call_parameters_encoder.сall_parameters_encoder import call_parameters_encoder

import asyncio

import base64
async def run():
    async with AsyncClient(timeout=10.0) as clinet:
        
        response = await clinet.post("https://b24-65bvoq.bitrix24.ru/rest/1/5w7yb124a318kdxn/crm.documentgenerator.numerator.add.json?"+call_parameters_encoder(
            {
                "fields":{
                    "name": "Test numerator",
                    "template": "{NUMBER}",
                    "settings":{
                        "Bitrix_Main_Numerator_Generator_SequentNumberGenerator":{
                            "start": "0",
                            "step": "1"
                        }
                    }
                }
            }
        ))
        res = response.json()
        print(res)

        with open("C:\\Users\\vl\\Desktop\\1.docx", "rb") as file:
            response1 = await clinet.post("https://b24-65bvoq.bitrix24.ru/rest/1/5w7yb124a318kdxn/crm.documentgenerator.template.add.json?"+call_parameters_encoder(
                {
                    "fields":{
                        "name": "Test template",
                        "numeratorId": res["result"]["numerator"]["id"],
                        "region":"ru",
                        "providers":["Bitrix\\DocumentGenerator\\DataProvider\\Rest"],
                        "entityTypeId":"2",
                        # "file": file.read
                    }
                }
            ),
            files= {"file": file},
            # headers={
            #     "Content-Type":"multipart/form-data",
            #     }
            )
            res1 = response1.json() 
            # print(res1)


        response2 = await clinet.post("https://b24-65bvoq.bitrix24.ru/rest/1/5w7yb124a318kdxn/crm.documentgenerator.document.add.json?"+call_parameters_encoder(
            {
                "templateId":"84",
                "entityTypeId": 2,
                "entityId": 2,
                "providerClassName":"\\Bitrix\\DocumentGenerator\\DataProvider\\Rest",
                "values":{
                    "NUMBER":1,
                    "Table":[
                        {
                            "Test1":"123"
                        },
                        {
                            "Test1":"qwe"
                        },
                        {
                            "Test1":"qwwe"
                        }
                    ],
                    "Test":"Table.Item.Test1",
                    # "TableIndex":"Table.INDEX",

                    "Table1":[
                        {
                            "Test12":"12we3"
                        },
                        {
                            "Test12":"qweeee"
                        }
                    ],
                    "Test123":"Table1.Item1.Test12",
                    # "Table1Index":"Table1.INDEX"
                },
                "fields":{
                    "Table":{
                        "PROVIDER":"Bitrix\\DocumentGenerator\\DataProvider\\ArrayDataProvider",
                        "OPTIONS":{
                            "ITEM_NAME":"Item",
                            "ITEM_PROVIDER": "Bitrix\\DocumentGenerator\\DataProvider\\HashDataProvider"
                        }
                    },
                    "Table1":{
                        "PROVIDER":"Bitrix\\DocumentGenerator\\DataProvider\\ArrayDataProvider",
                        "OPTIONS":{
                            "ITEM_NAME":"Item1",
                            "ITEM_PROVIDER": "Bitrix\\DocumentGenerator\\DataProvider\\HashDataProvider"
                        }
                    }
                }
            }
        ))
        res2 = response2.json() 
        print(res2)




asyncio.run(run())