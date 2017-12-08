def merge_conflict(src_template, returns):
    return src_template % tuple(returns[:src_template.count("%s")])


def retry_wrapper(retry_times, error_handler=None):
    """
    重试装饰器
    :param retry_times: 重试次数
    :param error_handler: 重试异常处理函数
    :return:
    """
    def out_wrapper(func):
        def wrapper(*args, **kwargs):
            count = 0

            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    count += 1

                    if error_handler:
                        result = error_handler(func.__name__, count, e, *args, **kwargs)
                        if result:
                            count -= 1

                    if count >= retry_times:
                        raise
        return wrapper
    return out_wrapper