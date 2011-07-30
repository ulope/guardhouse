
def skip_has_account_middleware(func):
    """
    Decorator to exempt certain views from the HasAccountMiddleware check
    """
    func.skip_has_account_middleware = True
    return func
