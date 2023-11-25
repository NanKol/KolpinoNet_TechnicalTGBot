from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


kb_menu = InlineKeyboardMarkup(inline_keyboard=
                               [[InlineKeyboardButton(text="Показать аварии", callback_data="Show_Trables")],
                                [InlineKeyboardButton(text="Итог по авариям", callback_data="Result_Trables")],
                                [InlineKeyboardButton(text="*Проверить аварию", callback_data="Check_Trable")]
                                ])

def trouble_menu(trouble_id):
    kb_builder = InlineKeyboardBuilder()
    buttons = [InlineKeyboardButton(text="Проверить аварию", callback_data=f"Update_Trouble:{trouble_id}"),
               InlineKeyboardButton(text="Удалить сообщение", callback_data=f"Delete_Message")]
    
    kb_builder.row(*buttons, width=2)
    
    return kb_builder.as_markup()
    
