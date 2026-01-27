

# This function will define only what kind of response the API is showing 


def classify_status(status_codes : int | None) -> str:

    '''
    returns one of:
    - 'success'
    - 'client_error'
    - 'system_error'

    '''

    if status_codes is None:
        return "system_error"
    
    if status_codes < 400 :
        return "success"
    
    if 400 <= status_codes < 500:
        return "client_error"
    
    return "system_error"