from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


kb_menu = InlineKeyboardMarkup(inline_keyboard=
                               [[InlineKeyboardButton(text="Показать аварии", callback_data="Show_Trables")],
                                [InlineKeyboardButton(text="Итог по авариям", callback_data="Result_Trables")],
                                [InlineKeyboardButton(text="*Проверить аварию", callback_data="Check_Trable")]
                                ])

def check_trouble(trouble_id):
    kb_builder = InlineKeyboardBuilder()
    
    InlineKeyboardBuilder.button(text="Проверить аварию", callback_data=f"trouble_id:{trouble_id}")
    
    return kb_builder.as_markup()
    
