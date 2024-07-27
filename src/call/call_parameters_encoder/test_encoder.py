from сall_parameters_encoder import call_parameters_encoder, call_parameters_encoder_recursion

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