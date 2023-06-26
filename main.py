from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup

#Снизу подключение файлов БД
from sqlite import db_start, create_profile, edit_profile, db_create_mails, db_get_ID_mails, db_ready_del_mails, db_fill_mails, db_count_num_mails, db_view_all_mails, db_view_max_id_mails, check_payment_values,check_balance, delete_payment_values, input_payment_values
from sqlite import maxID_list_tovs, fill_list_tovs, list_tovs_str, list_tovs, get_info_tov, get_account_data, update_quantity_lost_accounts, db_view_max_id_mails, db_tov_target, db_tov_lines_target, view_all_bd, edit_tov_menu_id, create_menu_id, get_tov_menu_id, del_tov_menu_id
#Снизу подключение файлов с клавой
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from keyboards import inline_kb_full2, inline_kb_full3, keyboard_back_in_menu_after_paym, keyboard_check_pay, keyboard_back_in_menu, keyboard_buy, keyboard_buy_phase2
from aiogram.dispatcher import filters

from consts import token, YOOTOKEN_live, YUKASSA_API_KEY, YUKASSA_API_URL
storage = MemoryStorage()

from payments import create_payment, check_payment, create_payment_cryptomus, check_payment_cryptomus

class target_delete(StatesGroup):
    target_id = State()
class Form(StatesGroup):
    mail = State()
    password = State()
class deposit(StatesGroup):
    amount_st = State()
class tovars(StatesGroup):
    tov = State()
    price = State()
    description = State()
class delete(StatesGroup):
    config = State()
    keys = State()
class insert(StatesGroup):
    tov = State()
    keys = State()

class buttons(StatesGroup):
    button = State()
    name = State()
    cost = State()
    lost = State()

start_message = 'Выберите: '
global order_id

async def on_startup(_):
    await db_start()
    # await db_create_mails()


bot = Bot(token=token)
dp = Dispatcher(bot, storage=storage)


@dp.message_handler(text=['М'])
async def shop(message: types.Message):

    await message.answer(f"{start_message}", reply_markup=inline_kb_full2)
    await create_profile(user_id=message.from_user.id, username=message.from_user.username)
    await update_quantity_lost_accounts()
    await create_menu_id(message.from_user.id, message.message_id, 0)

    # msg_id = message.message_id
    # last_msg = await edit_msg_menu(msg_id)
    # if last_msg != 0:
    #     await bot.delete_message(message.chat.id, last_msg[0]+1)
async def buttons(message: types.Message):
    maxID = await maxID_list_tovs()
    if maxID != None:
        bd = await list_tovs()
        # print(bd)
        inline_kb_full4 = InlineKeyboardMarkup(row_width=3)
        for i in range(int(maxID)):
            text = bd[i][1]
            inline_kb_full4.add(types.InlineKeyboardButton(text=f'{text}', callback_data=f'but_{text}'))
            # print(f'{i+1}. {text}')
        inline_kb_full4.add(types.InlineKeyboardButton(text='Назад', callback_data=f'back_in_menu'))
    return inline_kb_full4

@dp.callback_query_handler(text_startswith="but_")
async def but_pressed(call: types.CallbackQuery, state: FSMContext):
    call_data = call.data
    but_press = call_data.split("_")[1]
    await edit_tov_menu_id(call.from_user.id, call.message.message_id - 1, but_press)

    async with state.proxy() as data:
        data["name"] = but_press
    info_tov = await get_info_tov(but_press)
    in_stock = info_tov[0][4]
    await call.message.edit_text(f"Ты желаешь купить {but_press}??\nЗдесь данные по этому товару\nЦена: {info_tov[0][2]}$\nОписание товара:\n{info_tov[0][3]}\n\nIn stock: {in_stock} pcs.\n\nЕсли имеются вопросы - @gilmanovdin")
    await call.message.edit_reply_markup(keyboard_buy)

@dp.callback_query_handler(text_startswith="buy_tov")
async def buy_process(call: types.CallbackQuery, state: FSMContext):
    # msg_id = call.message.message_id
    #
    # await edit_msg_menu(msg_id)
    async with state.proxy() as data:
        try:
            tov_name = await get_tov_menu_id(call.message.message_id - 1)
            print("Данное сообщение", tov_name)
        except KeyError:
            await call.message.answer('Произошла ошибка')
            await shop(call.message)
            return 1
        info_tov = await get_info_tov(tov_name)
        # data['button'] = info_tov[0][0]
        # data['cost'] = info_tov[0][2]
        # data['lost'] = info_tov[0][4]

    await call.message.edit_text(f"Ты уверен, что желаешь купить {tov_name}?")
    await call.message.edit_reply_markup(keyboard_buy_phase2)
@dp.callback_query_handler(text_startswith="phase2_buy_tov")
async def buy_process_phase2(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        try:
            tov_name = await get_tov_menu_id(call.message.message_id - 1)
            # tov_ID = data['button']
        except KeyError:
            await call.message.delete()
            await call.message.answer('Произошла ошибка')
            await shop(call.message)
            return 1
        # tov_name = data['name']
    try:
        balance = await check_balance(call.from_user.id)
    except:
        await create_profile(user_id=call.from_user.id, username=call.from_user.username)
        balance = 0
    tov_data = await get_info_tov(tov_name)
    tov_cost = tov_data[0][2]
    tov_lost = tov_data[0][4]
    await del_tov_menu_id(call.message.message_id - 1)
    if tov_lost == 0:
        await call.message.edit_text("Отсутствуют товары на складе")
        await call.message.edit_reply_markup(keyboard_back_in_menu)
    elif balance >= tov_cost: # здесь условие чтобы в базе с товарами кол-во остатка на складе было больше 0
        data = await get_account_data(tov_name)
        print('Данные: ',data)
        await call.message.edit_text(f"Покупка успешно пройдена\nЛогин: {data[0]}\nПароль: {data[1]}")

        await call.message.answer(f"{start_message}", reply_markup=inline_kb_full2)
        await edit_profile(call.from_user.id, call.from_user.username, -tov_cost)
        await db_tov_lines_target(tov_name, data[3])
        await update_quantity_lost_accounts()
    else:
        await call.message.edit_text(f"Недостаточно средств на балансе")
        await call.message.edit_reply_markup(keyboard_back_in_menu)
    await state.finish()


@dp.callback_query_handler(text=["tovs"])
async def tovs(call: types.CallbackQuery):
    maxID = await maxID_list_tovs()
    if maxID != None:
        tovars = await list_tovs_str(maxID)
        await call.message.edit_text(f'{tovars}')
        inline_kb_full4 = await buttons(message=types.Message)
        await call.message.edit_reply_markup(inline_kb_full4)
    else:
        await call.message.edit_text(f'Товары пока отсутствуют')
        await call.message.edit_reply_markup(keyboard_back_in_menu)

@dp.message_handler(filters.IDFilter(user_id=(831031075, 701401228)), commands=['view'])
async def view_bd(message: types.Message):
    bd = await view_all_bd()
    await message.answer(bd)

@dp.message_handler(filters.IDFilter(user_id=(831031075, 701401228)), commands=['del'])
async def delete_data(message: types.Message, state: FSMContext):
    await message.reply("Что желаешь удалить: Товар(/del_tov) или логины+пароли товара(/del_tov_lines)", reply_markup=keyboard_back_in_menu)
    await delete.config.set()

@dp.message_handler(content_types=['text'], state=delete.config)
async def del_tov(message: types.Message, state: FSMContext):
    config = message.text
    async with state.proxy() as data:
        data['config'] = config
    if config == '/del_tov_lines':
        await message.reply('Вводите название товара и удаляемый логин через пробел в одном сообщении', reply_markup=keyboard_back_in_menu)
    elif config == '/del_tov':
        await message.reply('Вводите название товара', reply_markup=keyboard_back_in_menu)
    await delete.keys.set()
@dp.message_handler(content_types=['text'], state=delete.keys)
async def del_tov_phase2(message: types.Message, state: FSMContext):
    key = message.text.split()
    async with state.proxy() as data:
        config = data['config']
    try:
        if config == '/del_tov':
            del_data = await db_tov_target(key[0]) # key в данном случае это название товара в списке товаров = название таблицы с логинами этого товара
            if del_data != None:

                await message.answer(f'Удалены следующие данные: {del_data}', reply_markup=keyboard_back_in_menu)
            else:
                await message.answer('Такого товара не существует, жми сюда /del')
        elif config == '/del_tov_lines':
            print(key)
            del_data = await db_tov_lines_target(key[0], key[1])

            if del_data != None:
                await message.answer(f'Удалены следующие данные: {del_data}', reply_markup=keyboard_back_in_menu)
            else:
                await message.answer('Такого товара не существует, пиши еще раз')
        await state.finish()
        await update_quantity_lost_accounts()
    except IndexError:
        await message.answer("Ошибка, видимо ты сучка, которая ломает бота", reply_markup=keyboard_back_in_menu)
@dp.message_handler(filters.IDFilter(user_id=(831031075, 701401228)), commands=['insert'])
async def insert_data(message: types.Message, state: FSMContext):
    await message.reply("Введи название товара", reply_markup=keyboard_back_in_menu)
    await insert.tov.set()


@dp.message_handler(content_types=['text'], state=insert.tov)
async def get_name_tov(message: types.Message, state: FSMContext):
    name_tov = message.text
    if name_tov == '/fill':
        await state.finish()
        await fill_db(message, state)
        return
    maxID_tov = await db_view_max_id_mails(name_tov)
    if maxID_tov != None:
        await message.reply('Введите 3 ключа данных(через пробелы) следующим образом:\nлогин пароль резерв.данные', reply_markup=keyboard_back_in_menu)
        await insert.keys.set()
        async with state.proxy() as data:
            data['tov'] = name_tov
    else:
        await message.reply('Такого товара не существует. Прежде чем добавлять поля товара, добавьте товар через команду /fill', reply_markup=keyboard_back_in_menu)

@dp.message_handler(content_types=['text'], state=insert.keys)
async def insert_keys(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['keys'] = message.text.split()
    await db_fill_mails(name=data['tov'], key1=data['keys'][0], key2=data['keys'][1], key3=data['keys'][2])
    await message.answer(f"Вы добавили строку с данными по товару {data['tov']}\nkey1: {data['keys'][0]}\nkey2: {data['keys'][1]}\nkey3: {data['keys'][2]}")
    await update_quantity_lost_accounts()
    await state.finish()


@dp.message_handler(filters.IDFilter(user_id=(831031075, 701401228)), commands=['fill'])
async def fill_db(message: types.Message, state: FSMContext):
    await message.reply("Введи название товара", reply_markup=keyboard_back_in_menu)
    await tovars.tov.set()
    # data = message.text.split() # создаем список ['логин', 'пароль']

@dp.message_handler(content_types=['text'], state=tovars.tov)
async def load_name(message: types.Message, state: FSMContext):
    name_tov = message.text
    if not(' ' in name_tov):
        await message.reply("Введи цену товара (пиши только цифры):", reply_markup=keyboard_back_in_menu)
        await tovars.price.set()
    else:
        await message.answer('Вместо пробела используй смайл', reply_markup=keyboard_back_in_menu)
        # await state.finish()
    async with state.proxy() as data:
        data['tov'] = name_tov

@dp.message_handler(content_types=['text'], state=tovars.price)
async def load_name(message: types.Message, state: FSMContext):
    price = message.text
    try:
        price = float(price)
    except ValueError:
        await message.answer("Введите исключительно число", reply_markup=keyboard_back_in_menu)
    if isinstance(price, float) and price >= 0:
        async with state.proxy() as data:
            data['price'] = price
        await message.reply("Введи описание товара (можно текстом):", reply_markup=keyboard_back_in_menu)
        await tovars.description.set()
    else:
        await message.answer("Введите сумму корректно", reply_markup=keyboard_back_in_menu)

@dp.message_handler(content_types=['text'], state=tovars.description)
async def load_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['description'] = message.text
    await fill_list_tovs(tov=data['tov'], price=data['price'], description=data['description'])
    await message.answer(f"Добавлен товар:\nНазвание товара: {data['tov']}\nЦена: {data['price']}\nОписание: {data['description']}")
    await update_quantity_lost_accounts()
    await state.finish()


@dp.callback_query_handler(text=["balance"])
async def balance(call: types.CallbackQuery):
    balance = await check_balance(call.from_user.id)
    await call.message.edit_text(f'На вашем счету сейчас {balance} USDT')
    await call.message.edit_reply_markup(keyboard_back_in_menu)


@dp.callback_query_handler(text=["add_balance"])
async def add_balance(call: types.CallbackQuery):
    # await call.message.answer('Пополнить счет на сумму (Введите сумму):', reply_markup=keyboard_back_in_menu_after_paym)
    await call.message.edit_text('Пополнить счет на сумму (Введите сумму):')
    await call.message.edit_reply_markup(keyboard_back_in_menu_after_paym)
    await deposit.amount_st.set()

@dp.message_handler(state=deposit.amount_st)
async def get_username(message: types.Message, state: FSMContext):
    amount = message.text
    # await bot.delete_message(message.chat.id, message.message_id-1)
    try:
        amount = amount.replace(',', '.')
        amount = float(amount)
    except ValueError:
        amount = 'string'

    if isinstance(amount, float) and amount >= 0.01:
        await state.update_data(amount=amount)
        data = await state.get_data()
        last_receipt_flag = await check_payment_values(message.from_user.id)
        if last_receipt_flag != 1:
            last_receipt = last_receipt_flag[2]
            # Снизу раскомментировать так, как сейчас используется метод общения с клиентом через "одно сообщение"
            # await bot.delete_message(message.chat.id, last_receipt)
            # print(f'Удалены данные: {last_receipt}')
        # print(data["amount"])
        # amount = int(message.text)
        payment_url = await create_payment(data["amount"])
        await message.delete()
        await bot.delete_message(message.chat.id, message.message_id - 1)
        paym_data_crypto = await create_payment_cryptomus(data["amount"])
        await message.answer(f"Перейдите по ссылке для оплаты {amount} USDT: {paym_data_crypto[0]}", reply_markup=keyboard_check_pay)
        await input_payment_values(message.from_user.id, paym_data_crypto[1], data["amount"], message.message_id+1, paym_data_crypto[2], paym_data_crypto[3])
        # await message.answer(f"Перейдите по ссылке для оплаты {amount} руб: {payment_url[0]}", reply_markup=keyboard_check_pay) Это для юкассы

        await state.finish()
    else:
        await message.answer("Введите сумму корректно")

# Снизу возврат в меню в случае отмены при оплате
@dp.callback_query_handler(text=["back_in_menu_after_paym"], state=deposit.amount_st)
async def random_value(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.edit_text(f"{start_message}")
    await call.message.edit_reply_markup(inline_kb_full2)

@dp.callback_query_handler(lambda c: True, text=["successful_payment_button"])
async def random_value(call: types.CallbackQuery):
    # СНИЗУ КОД ДЛЯ ПРОВЕРКИ ПЛАТЕЖА ЮКАССЫ
    '''
    payment_data = await check_payment_values(call.from_user.id)
    payment_id = payment_data[0]
    amount = payment_data[1]
    sostoianie = await check_payment(payment_id)
    sostoianie = 'succeeded'
    if sostoianie == 'waiting_for_capture':
        await call.message.edit_text('Проверка платежа, нажмите на кнопку "Оплатил" еще раз через 10 секунд')
        await call.message.edit_reply_markup(keyboard_check_pay)
    elif sostoianie == 'pending':
        await call.message.edit_text('Платеж не прошёл, создайте новый счет и попробуйте оплатить')
        await call.message.edit_reply_markup(keyboard_check_pay)
    elif sostoianie == 'succeeded':

        await call.message.answer(f"Ваш баланс успешно пополнен\n\n{start_message}", reply_markup=inline_kb_full2)
        # await call.message.edit_reply_markup(inline_kb_full2)
        await edit_profile(user_id=call.from_user.id, username=call.from_user.username, amount=+amount)
        await call.answer('Успешно!')
        last_receipt_flag = await check_payment_values(call.from_user.id)
        print(f'{last_receipt_flag}')
        last_receipt = last_receipt_flag[2]
        await bot.delete_message(call.message.chat.id, int(last_receipt))
        await delete_payment_values(call.from_user.id)
        await update_quantity_lost_accounts()
    elif sostoianie == 'canceled':
        await call.message.answer('Вы отменили платеж', reply_markup=inline_kb_full2)
        await delete_payment_values(call.from_user.id)
    '''
    payment_data = await check_payment_values(call.from_user.id)
    payment_id = payment_data[0]
    amount = payment_data[1]
    payment_sing = payment_data[3]
    order_id = payment_data[4]
    sostoianie = await check_payment_cryptomus(payment_id, order_id)
    # print(f'0{sostoianie}0')
    # sostoianie = 'succeeded'
    if sostoianie == 'check':
        await call.message.edit_text('Проверка платежа, нажмите на кнопку "Оплатил" еще раз через 10 секунд')
        await call.message.edit_reply_markup(keyboard_check_pay)
    elif sostoianie == 'cancel':
        await call.message.edit_text('Платеж не прошёл, создайте новый счет и попробуйте оплатить')
        await call.message.edit_reply_markup(keyboard_check_pay)
    elif sostoianie == 'paid' or sostoianie == 'wrong_amount' or sostoianie == 'paid_over':
        await call.message.answer(f"Ваш баланс успешно пополнен\n\n{start_message}", reply_markup=inline_kb_full2)
        # await call.message.edit_reply_markup(inline_kb_full2)
        await edit_profile(user_id=call.from_user.id, username=call.from_user.username, amount=+amount)
        await call.answer('Успешно!')
        last_receipt_flag = await check_payment_values(call.from_user.id)
        # print(f'{last_receipt_flag}')
        last_receipt = last_receipt_flag[2]
        await bot.delete_message(call.message.chat.id, int(last_receipt))
        await delete_payment_values(call.from_user.id)
        await update_quantity_lost_accounts()
    elif sostoianie == 'canceled':
        await call.message.answer('Вы отменили платеж', reply_markup=inline_kb_full2)
        await delete_payment_values(call.from_user.id)

# Снизу возврат в меню в случае отмены при оплате
@dp.callback_query_handler(text=["unsuccessful_payment_button"])
async def random_value(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text(f"{start_message}")
    await call.message.edit_reply_markup(inline_kb_full2)
    await delete_payment_values(call.from_user.id)

@dp.callback_query_handler(text=["back_in_menu"], state="*")
async def back_func(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.edit_text(f"{start_message}")
    await call.message.edit_reply_markup(inline_kb_full2)

# @dp.callback_query_handler(lambda callback: callback.data in [A, B, C])
# async def next_keybord(callback: types.Callback_query):
#     await callback.edit_message(reply_markup= inline_kb_full3)

@dp.callback_query_handler(lambda call: "A" in call.data)
async def next_keyboard(call):
    await call.message.edit_reply_markup(inline_kb_full3)

if __name__=='__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)