import configparser

config = configparser.ConfigParser()
config.read_dict("example.ini")

print(config['BOT']['group_id'])
print(type(config['BOT']['group_id']))

# for id in config['BOT']['group_id']:
#     print(id)