"""
cmd_table : dict{ str:str }
    key represents the result of speech recognition(voice command).
    value represents the corresponding Petoi command.
"""

# ===================================== Chinese ====================================
# cmd_table = {
#     '坐下':   'ksit',
#     '坐':     'ksit',
#     '请坐':   'ksit',
#     '站起来': 'kbalance',
#     '起立':   'kbalance',
#     '向前走': 'kwkF',
#     '向前跑': 'ktrF',
#     '检查':   'c',
#     '睡觉':   'rest',
#     '趴下':   'd',
#     '停':     'd',
#     '停下':   'd',
# }


# def build_dict():
#     """This is for Chinese.
#
#     Build a custom list of words from cmd_table for vosk model to choose from when recognizing.
#
#     Returns
#     -------
#     d : str
#         The str form of a custom list of words.
#     """
#     d = []
#     keys = list(cmd_table.keys())
#     for k in keys:
#         d += list(k)
#     d = [" ".join(list(set(d)))]
#     d = str(d).replace("'", "\"")
#     print(d)
#     return d
# ===================================== Chinese ====================================


# ===================================== English ====================================
cmd_table = {
    'sit down': 'ksit',
    'please sit': 'ksit',
    'stand up': 'kbalance',
    'get up': 'kbalance',
    'walk forward': 'kwkF',
    'run forward': 'ktrF',
    'check status': 'c',
    'rest': 'rest',
    'get down': 'd',
    'stop': 'd',
}


def build_dict():
    """This is for English.

    Build a custom list of words from cmd_table for vosk model to choose from when recognizing.

    Returns
    -------
    d : str
        The str form of a custom list of words.
    """

    # return '["get status down please walk sit forward check rest stand up run stop", "[unk]"]'
    # print("[\"get status down please walk sit forward check rest stand up run stop\", \"[unk]\"]")
    d = []
    keys = cmd_table.keys()
    for k in keys:
        d += k.split(' ')
    d = list(set(d))
    d = [" ".join(d), "[unk]"]
    d = str(d).replace("'", "\"")
    print(d)
    return d
# ===================================== English ====================================


def text2cmd(text):
    """Convert the result of speech recognition into Petoi command.

    Parameters
    ----------
    text : str
        The result from vosk model after speech recognition.

    Returns
    -------
    An str. The corresponding Petoi command.
    """

    return cmd_table.get(text, '')
