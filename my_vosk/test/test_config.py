
import importlib

def t():
    import yaml
    return yaml

yaml = t()
with open('../config/config.yml', 'r', encoding='utf-8') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)
    print(config['cmd_table'])

# a = importlib.import_module('cmd_table_en', config['cmd_table'])
# print(a)
# print(a.cmd_table_en)