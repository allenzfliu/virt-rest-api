# from fastapi import HTTPException
# from fastapi.types import DecoratedCallable

# ENABLE_VAL = True
# DISABLE_VAL = False

# these are valid config options
# known_error_codes = [400,403,404,418,500]

# def disable_func():
    # return None

# def check_config(value):
    # if (value == ENABLE_VAL):
        # do no decoration, just send a thin wrapper
        # return lambda function: function
    
    # if (value in known_error_codes):
    #     # skip the decoration, send a lambda
    #     # that just returns the error code
    #     def wrapper(function):
    #         raise HTTPException(status_code=int(value))
    #         # skip invoking the function
    #     return wrapper
        
    # if (value == DISABLE_VAL):
    #     def outer_wrapper(function):
    #         def dummy_function(*args, **kwargs):
    #             return None
    #         outer_wrapper.__name__ = function.__name__
    #         outer_wrapper.__doc__ = function.__doc__
            
    #     return outer_wrapper
    
    # return lambda function: function