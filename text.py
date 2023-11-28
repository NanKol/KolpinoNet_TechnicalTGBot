import random
import string

from aiogram.utils.formatting import Text, Bold

#Сообщения на команды /<команда>
start = """Бот запущен!\n
Используйте /help для просмотра команд бота"""

help = """Список команд бота:
        /start - Запускает бота
        /help - выводит информацию о доступных командах
        /menu - выводит меню
        /check - позоляет проверить исправна ли авария
Проверка аварии: \n/check <ip или TID> <XXX.XXX.XXX.XXX или XXX>
        """
        
menu = """Меню:"""# \n\n* - в разработке

#Осталные сообщения
about_trable = """{emoji} Авария TID:{trouble_id}
Объект: {adress}
Время начала: {time_start}
Длительность: {time}"""+ """{time_end}""" + """\nУзел: {uzel}
Примечание: {ecomment}
Оборудование: {brand} {model} [{ipaddr}]
Коммент: {comment}
Кол-во ФЛ: {count_fl}
Кол-во ЮЛ: {count_yl}"""

count_trables = """На данный момент аварий: {count_trable}"""

no_trables = """Аварии не найдены."""

# def about_trouble(emoji, trouble_id, adress, time_start, 
#                   time, time_end,uzel, comment, brand,model, 
#                   ipaddr,ecomment,count_fl,count_yl,*args):
        
#         text = Text(f"{emoji} Авария TID:{trouble_id}",
#              f"Объект: {adress}",
#              f"Время начала: {time_start}",
#              f"Длительность: {time}",
#              f"{time_end}",
#              f"Узел: {uzel}",
#              f"Примечание: {comment}",
#              f"Оборудование: {brand} {model} [{ipaddr}]",
#              f"Коммент: {ecomment}",
#              f"Кол-во ФЛ: {count_fl}",
#              f"Кол-во ЮЛ: {count_yl}")
        
#         return text



# def generate_random_string(length) -> str:
#     letters = string.ascii_lowercase
#     rand_string = ''.join(random.choice(letters) for i in range(length))
#     print("Random string of length", length, "is:", rand_string)
