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

cmd_table = {
    'sit down':      'ksit',
    'please sit':    'ksit',
    'stand up':      'kbalance',
    'get up':        'kbalance',
    'walk forward':  'kwkF',
    'run forward':   'ktrF',
    'check status':  'c',
    'rest':          'rest',
    'get down':      'd',
    'stop':          'd',
}


def build_dict():
#     return '["get status down please walk sit forward check rest stand up run stop", "[unk]"]'
#     print("[\"get status down please walk sit forward check rest stand up run stop\", \"[unk]\"]")
    d = []
    keys = cmd_table.keys()
    for k in keys:
        d += k.split(' ')
    d = list(set(d))
    # d.append("hey")
    # d.append("bittle")
    d = [" ".join(d), "[unk]"]
    d = str(d).replace("'", "\"")
    print(d)
    return d


def text2cmd(text):
    return cmd_table.get(text, '')


# def build_dict():
#     d = []
#     keys = list(cmd_table.keys())
#     for k in keys:
#         d += list(k)
#     d = [" ".join(list(set(d)))]
#     # d = [" ".join(list(set(d))), "啊"]
#     d = str(d).replace("'", "\"")
#     print(d)
#     return d

# build_dict()