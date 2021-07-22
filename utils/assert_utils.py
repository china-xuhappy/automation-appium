

def assertEqual(a, b):
    """
    True 成功

    :param a:
    :param b:
    :return:
    """
    try:
        assert a == b
        return True
    except Exception as e:
        print(e)
        return False