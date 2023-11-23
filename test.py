# import config
import configparser


config = configparser.ConfigParser()

config.sections()

config['DB'] = {'db_name': "DataBaseName",
                'Host': "LocalHost",
                'db_port:': "3306",
                'Charset': "utf-8"}

# config['DB']['USER'] = {'Name': "name",
#                         'Password': "password"}

config['BOT'] = {'token': "TOKEN",
                 'group_id': {"-123213123","31231231","231213"}}

with open('example.ini', 'w') as configfile:
    config.write(configfile)
# config['BOT']