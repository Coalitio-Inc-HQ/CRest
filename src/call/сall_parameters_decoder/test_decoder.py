from сall_parameters_decoder import call_parameters_decoder

def test_call_parameters_decoder_dict():
    assert call_parameters_decoder("[a]=1&[b]=2") == {
            "a":"1",
            "b":"2"
        }
    
def test_call_parameters_encoder_list():
    assert call_parameters_decoder("[0]=a&[1]=b") == {
        "0":"a",
        "1":"b"
    }


def test_call_parameters_decoder_dict_list():
    print(call_parameters_decoder("[a]=1&[b]=2&[c][0][a]=a&[c][0][b]=b&[c][1][a]=c&[c][1][b]=d"))
    assert call_parameters_decoder("[a]=1&[b]=2&[c][0][a]=a&[c][0][b]=b&[c][1][a]=c&[c][1][b]=d") == {
            "a":"1",
            "b":"2",
            "c":{
                "0":{"a":"a",
                 "b":"b"
                },
                "1":{"a":"c",
                 "b":"d"
                }
            }
        }
