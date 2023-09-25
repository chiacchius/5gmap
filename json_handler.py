import json


def show_indices(obj, indices):
    for k, v in obj.items() if isinstance(obj, dict) else enumerate(obj):
        if isinstance(v, (dict, list)):
            yield from show_indices(v, indices + [k])
        else:
            yield indices + [k], v

def get_key_value(json_string, key):
    json_value = json.loads(json_string)
    result = []
    for keys, v in show_indices(json_value, []):
        
        if key in keys:
            result.append(str(v))

    if len(result)>1:
        return result
    
    elif len(result) == 1:
        return result[0]

    else: 
        return None 
        
def parse_nas_message(Msg, key):
    
    if is_iterable(Msg):
        for element in Msg:
            try:
                value = parse_nas_message(element, key)
                if (value != None):
                    return value
            except:
                pass
    else:
        if (Msg._name == key):
            return str(Msg._val)
            
        return None

    
def is_iterable(obj):
    try:
        iter(obj)
        return True
    except TypeError:
        return False