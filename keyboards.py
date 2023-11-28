from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


kb_menu = InlineKeyboardMarkup(inline_keyboard=
                               [[InlineKeyboardButton(text="Показать аварии", callback_data="Show_Trables")],
                                [InlineKeyboardButton(text="Итог по авариям", callback_data="Count_Troubles")]
                                ])

def trouble_menu(trouble_id):
    kb_builder = InlineKeyboardBuilder()
    buttons = [InlineKeyboardButton(text="Проверить аварию", callback_data=f"Update_Trouble:{trouble_id}"),
               InlineKeyboardButton(text="Удалить сообщение", callback_data=f"Delete_Message")]
    
    kb_builder.row(*buttons, width=2)
    
    buttons = [InlineKeyboardButton(text="Показать все аварии", callback_data="Show_Trables"),
               InlineKeyboardButton(text="Удалить сообщение", callback_data=f"Delete_Message")]
    kb_builder.row(*buttons, width=1)

    
    # kb_builder.row(InlineKeyboardButton(text="Устранить аварию", callback_data=f"comlite_trouble:{trouble_id}"))
    
    return kb_builder.as_markup()
    
count_trables_menu = InlineKeyboardMarkup(inline_keyboard=
                                          [[InlineKeyboardButton(text="Обновить", callback_data=f"Update_Count_Trouble"),],])