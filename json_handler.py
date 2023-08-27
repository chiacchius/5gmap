import json


# def json_parser(json_msg, file):
#     parsed_data = json.loads(json_msg)
#     #print(parsed_data)
#     json_explorer(parsed_data, file)

# def json_explorer(data, file, keys='', indent=0):
    
#     if isinstance(data, dict):
#         for key, value in data.items():
#             new_keys = f"{keys}{key}:"
#             json_explorer(value, file, new_keys, indent + 1)
#     elif isinstance(data, list):
#         for index, element in enumerate(data):
#             new_keys = f"{keys}[{index}] : "
#             json_explorer(element, file, new_keys, indent)
#     else:
#         #print('  ' * indent + str(keys) + str(data))
#         file.write(str(keys) + str(data) + "\n")
#         file.flush()
#         #return parameter
        
def show_indices(obj, indices):
    for k, v in obj.items() if isinstance(obj, dict) else enumerate(obj):
        if isinstance(v, (dict, list)):
            yield from show_indices(v, indices + [k])
        else:
            yield indices + [k], v



def parse_json_msg(json_string, key):
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
        
		

def parse_nas_message(Msg, name):
    
    
    name = name + "_" + Msg._name
    
    if is_iterable(Msg):
        for element in Msg:
            #print(element)
            try:
                parse_nas_message(element, name)
            except:
                pass
            
    else:
        #print(name)
        print(Msg)
        
        
        
    


def is_iterable(obj):
    try:
        iter(obj)
        return True
    except TypeError:
        return False