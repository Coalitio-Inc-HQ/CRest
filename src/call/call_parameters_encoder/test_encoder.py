from сall_parameters_encoder import call_parameters_encoder, call_parameters_encoder_recursion, call_parameters_encoder_bath

def test_call_parameters_encoder_recursion_dict():
    res = call_parameters_encoder_recursion(
        {
            "a":1,
            "b":"2"
        }
    )

    assert res == ["[a]=1","[b]=2"]

def test_call_parameters_encoder_recursion_list():
    res = call_parameters_encoder_recursion(
        ["a", "b"]
    )

    assert res == ["[0]=a","[1]=b"]

def test_call_parameters_encoder_recursion_dict_list():
    res = call_parameters_encoder_recursion(
        {
            "a":1,
            "b":"2",
            "c":[
                {"a":"a",
                 "b":"b"
                },
                {"a":"c",
                 "b":"d"
                }
            ]
        }
    )
    
    assert res == ["[a]=1","[b]=2","[c][0][a]=a","[c][0][b]=b","[c][1][a]=c","[c][1][b]=d"]


def test_call_parameters_encoder_dict():
    res = call_parameters_encoder(
        {
            "a":1,
            "b":"2"
        }
    )

    assert res == "a=1&b=2"


def test_call_parameters_encoder_dict_list():
    res = call_parameters_encoder(
        {
            "a":1,
            "b":"2",
            "c":[
                {"a":"a",
                 "b":"b"
                },
                {"a":"c",
                 "b":"d"
                }
            ]
        }
    )
    
    assert res == "a=1&b=2&c[0][a]=a&c[0][b]=b&c[1][a]=c&c[1][b]=d"

def test_call_parameters_encoder_bath():
    res = call_parameters_encoder_bath(
        [
            {
                "method": "crm.contact.add",
                "params":{
                    "FIELDS":{
                        "NAME":"Иван1",
                        "LAST_NAME":"Петров1"
                    }
                }
            },
            {
                "method": "crm.contact.add",
                "params":{
                    "FIELDS":{
                        "NAME":"Иван2",
                        "LAST_NAME":"Петров2"
                    }
                }
            }
        ]
    )
    assert res == "cmd[0]=crm.contact.add%3FFIELDS%5BNAME%5D%3D%25D0%2598%25D0%25B2%25D0%25B0%25D0%25BD1%26FIELDS%5BLAST_NAME%5D%3D%25D0%259F%25D0%25B5%25D1%2582%25D1%2580%25D0%25BE%25D0%25B21&cmd[1]=crm.contact.add%3FFIELDS%5BNAME%5D%3D%25D0%2598%25D0%25B2%25D0%25B0%25D0%25BD2%26FIELDS%5BLAST_NAME%5D%3D%25D0%259F%25D0%25B5%25D1%2582%25D1%2580%25D0%25BE%25D0%25B22"