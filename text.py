from aiogram.utils.formatting import as_marked_section, as_key_value
#Сообщения на команды /<команда>
start = """Бот запущен!\n
Используйте /help для просмотра команд бота"""

help = """Список команд бота:
        /start - Запускает бота
        /help - выводит информацию о доступных командах
        /menu - выводит меню
        /check - позоляет проверить исправна ли авария
        """
        
menu = """Меню:\n\n* - в разработке"""

#Осталные сообщения
about_trable = """{emoji} Авария TID:{trouble_id}
Объект: {adress}
Время начала: {time_start}
Длительность: {time}
Узел: {uzel}
Примечание: {comment}
Оборудование: {brand} {model} [{ipaddr}]
Коммент: {ecomment}
Кол-во ФЛ: {count_fl}
Кол-во ЮЛ: {count_ul}"""

result_trables = """Всего существующих аварий: {count_trable}"""

no_trables = """Аварии не найдены."""

