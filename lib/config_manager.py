from fastapi import HTTPException

ENABLE_VAL = True
DISABLE_VAL = False

# these are valid config options
known_error_codes = [400,403,404,418,500]

def disable_func():
    return None

def check_config(value):
    if (value == ENABLE_VAL):
        # do no decoration, send a thin wrapper
        return lambda function: function
    
    if (value in known_error_codes):
        # skip the decoration, send a lambda
        # that just returns the error code
        def wrapper(function):
            raise HTTPException(status_code=int(value))
            # skip invoking the function
        return wrapper
        
    if (value == DISABLE_VAL):
        def wrapper(function):
            pass;
            # skip invoking the funciton
        return wrapper