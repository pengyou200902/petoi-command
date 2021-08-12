"""
cmd_table_[xx] : dict{ str:str }
    Key represents the result of speech recognition(voice command).
    Value represents the corresponding Petoi command.
"""

# ===================================== Chinese(zh) ====================================
cmd_table_cn = {
    '坐 下':   'ksit',
    '坐':     'ksit',
    '请 坐':   'ksit',
    '站 起 来': 'kbalance',
    '起 立':   'kbalance',
    '向 前 走': 'kwkF',
    '向 前 跑': 'ktrF',
    '检 查':   'c',
    '睡 觉':   'rest',
    '趴 下':   'd',
    '停':     'd',
    '停 下':   'd',
}


def build_dict_cn(cmd_table):
    """This is for Chinese.

    Build a custom list of words from cmd_table for vosk model to choose from when recognizing.

    Parameters
    ----------
    cmd_table : dict{ str:str }
        Description as above.

    Returns
    -------
    d : str
        The str form of a custom list of words.
    """
    d = []
    keys = list(cmd_table.keys())
    for k in keys:
        d += list(k)
    d = [" ".join(list(set(d)))]
    d = str(d).replace("'", "\"")
    print(d)
    return d
# ===================================== Chinese(zh) ====================================


# ===================================== English(en-us) ====================================
cmd_table_en = {
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


def build_dict_en(cmd_table):
    """This is for English.

    Build a custom list of words from cmd_table for vosk model to choose from when recognizing.

    Parameters
    ----------
    cmd_table : dict{ str:str }
        Description as above.

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
# ===================================== English(en-us) ====================================


def text2cmd(text, cmd_table):
    """Convert the result of speech recognition into Petoi command.

    Parameters
    ----------
    text : str
        The result from vosk model after speech recognition.

    cmd_table : dict{ str:str }
        Description as above.

    Returns
    -------
    An str. The corresponding Petoi command.
    """

    return cmd_table.get(text, '')
