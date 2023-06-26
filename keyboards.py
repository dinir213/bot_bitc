from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import types
from sqlite import maxID_list_tovs, fill_list_tovs, list_tovs



inline_btn_3 = InlineKeyboardButton('Товары', callback_data='tovs')
inline_btn_4 = InlineKeyboardButton('Баланс', callback_data='balance')
inline_btn_5 = InlineKeyboardButton('Пополнение баланса', callback_data='add_balance')
inline_kb_full2 = InlineKeyboardMarkup(row_width=1).add(inline_btn_3,inline_btn_4,inline_btn_5)


inline_btn_6 = InlineKeyboardButton('tov1')
inline_btn_7 = InlineKeyboardButton('tov2')
inline_btn_8 = InlineKeyboardButton('tov3')
inline_btn_9 = InlineKeyboardButton('Назад ↩️',callback_data='Back')
inline_kb_full3 = InlineKeyboardMarkup(row_width=1).add(inline_btn_6,inline_btn_7,inline_btn_8,inline_btn_9)

btn_back_in_menu_after_paym = InlineKeyboardButton(text='Назад', callback_data='back_in_menu_after_paym')
keyboard_back_in_menu_after_paym = InlineKeyboardMarkup().add(btn_back_in_menu_after_paym)

button_pay = InlineKeyboardButton(text="Оплатил", callback_data='successful_payment_button')
button_cancel_buy = InlineKeyboardButton(text="Отменить платеж", callback_data='unsuccessful_payment_button')
keyboard_check_pay = InlineKeyboardMarkup().add(button_pay).add(button_cancel_buy)

btn_back_in_menu = InlineKeyboardButton(text='Назад', callback_data='back_in_menu')
keyboard_back_in_menu = InlineKeyboardMarkup().add(btn_back_in_menu)
btn_buy = InlineKeyboardButton(text='Купить', callback_data='buy_tov')
keyboard_buy = InlineKeyboardMarkup().add(btn_buy).add(btn_back_in_menu)
btn_buy_phase2 = InlineKeyboardButton(text='Купить', callback_data='phase2_buy_tov')
keyboard_buy_phase2 = InlineKeyboardMarkup().add(btn_buy_phase2).add(btn_back_in_menu)