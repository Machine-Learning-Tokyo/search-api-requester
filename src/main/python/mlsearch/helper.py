import json

def is_valid_parameters(event, param_names):
    """
    Check whether the item in param_names exist in event dictionary.
    
    :param  event:          Lambda event object.
    :param  param_names:    The list of the param names to be checked.
    
    :retrun:                True if exist else False
    """
    for param in param_names:
        if not param in event:
            return False
    return True

def response(message, status_code, headers=dict(), optional_attributes=dict()):
    """
    Response message for the request.
    
    :param message:         The response message.
    :param status_code:     The response status.
    :headers:               The header of the response.
    :optional_attributes:   The dict key value used by backend to communicate
                            with front end.
    
    :return:                The dic('statusCode', 'body', 'optional_attributes')
    """
    return {
        'statusCode': status_code,
        'body': json.dumps({'content': message, 'optional_attributes': optional_attributes}),
        'headers': headers
    }

def parse_parameters(event):
    """
    Parse the parameters from event dictionary.
    
    :param  event:      The event dictionary.
    :return:            dict(
                            'query', 'init_idx',
                            'count', 'source',
                            'cookies', 'timestamp',
                            'y_next_page_token')
    """
    try:
        param = dict()
        param['query'] = event['query']
        param['init_idx'] = int(event['init_idx'])
        param['count'] = int(event['count'])
        param['source'] = event['source']
        param['cookies'] = event['cookies']
        param['timestamp'] = event['timestamp']
        param['y_next_page_token'] = event['y_next_page_token']
        
        if param['init_idx'] >= 0 and param['count'] > 0:
            return param
        else:
            return dict()
            
    except:
        return dict()
