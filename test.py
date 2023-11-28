from getpass import getpass
from mysql.connector import connect, Error

# try:
#     with connect(
#         host="109.197.48.44",
#         user="tg_bot",
#         password="Psw4TGBOT",
#     ) as connection:
#         show_db_query = "SHOW DATABASES"
#         with connection.cursor() as cursor:
#             cursor.execute(show_db_query)
#             for db in cursor:
#                 print(db)
# except Error as e:
#     print(e)

with connect(
        host="109.197.48.44",
        user="tg_bot",
        password="Psw4TGBOT!",
    ) as connection:
        show_db_query = "SHOW DATABASES"
        with connection.cursor() as cursor:
            cursor.execute(show_db_query)
            for db in cursor:
                print(db)