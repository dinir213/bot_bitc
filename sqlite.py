import sqlite3 as sq
import datetime

async def db_start():
    global db, cur

    db = sq.connect('new.db')
    cur = db.cursor()

    cur.execute("CREATE TABLE IF NOT EXISTS profile(user_id TEXT PRIMARY KEY, money REAL, username TEXT, buys_минус_1 INTEGER, balance REAL)")
    cur.execute("CREATE TABLE IF NOT EXISTS payment_values(user_id TEXT PRIMARY KEY, payment_id_or_uuid TEXT, amount REAL, message_id TEXT, sign TEXT, order_id TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS list_tovs(ID INTEGER PRIMARY KEY, tov TEXT, price REAL, description TEXT, lost INTEGER)")
    cur.execute("CREATE TABLE IF NOT EXISTS menu(msg_id INTEGER PRIMARY KEY, user_id TEXT, tov TEXT)")


    db.commit()
async def create_profile(user_id, username):
    user = cur.execute("SELECT 1 FROM profile WHERE user_id == '{key}'".format(key=user_id)).fetchone()
    if not user:
        cur.execute("INSERT INTO profile VALUES(?, ?, ?, ?, ?)", (user_id, 0, username, 1, 0))
        db.commit()
async def edit_profile(user_id, username, amount):
    # Чтобы пополнить баланс при передаче значения "amount" нужно передавать, как положительное значение, а при списании с баланса денег - как отрицательное
    cons = cur.execute("SELECT buys_минус_1 FROM profile WHERE user_id == '{key}'".format(key=user_id))
    before_balance = float(cur.execute("SELECT balance FROM profile WHERE user_id == '{key}'".format(key=user_id)).fetchone()[0])
    new_balance = before_balance + amount
    # a = cons.fetchone()[0] + 1
    a = 1
    new_balance = before_balance + amount
    money_bd = amount
    cur.execute("INSERT OR REPLACE INTO profile VALUES(?, ?, ?, ?, ?)", (user_id, money_bd, username, a, new_balance))
    # cur.execute("UPDATE profile SET money = '{}' WHERE user_id == '{}'")
    db.commit()

async def create_menu_id(user_id, msg_id, tov):
    cur.execute(f"INSERT INTO menu VALUES(?, ?, ?)", (msg_id, user_id, tov))
    db.commit()

async def edit_tov_menu_id(user_id, msg_id, tov_name):
    # msg_ID = cur.execute(f"SELECT msg_id FROM menu WHERE msg_id={msg_id}")
    # print(msg_id, ' ', tov)
    # cur.execute(f"UPDATE menu SET tov={tov} WHERE msg_id={msg_id}")
    print(msg_id)
    cur.execute("UPDATE menu SET tov='{tov_name}' WHERE msg_id='{msg_id}'".format(tov_name=tov_name, msg_id=msg_id))
    # print('msg_ID = ', msg_ID)
    res = cur.execute(f"SELECT * FROM menu WHERE msg_id={msg_id}").fetchall()
    print(res)
    db.commit()
async def get_tov_menu_id(msg_id):
    tov = cur.execute(f"SELECT tov FROM menu WHERE msg_id={msg_id}").fetchall()[0][0]
    return tov
async def del_tov_menu_id(msg_id):
    cur.execute(f"DELETE FROM menu WHERE msg_id={msg_id}")
    db.commit()
# async def edit_msg_menu(msg_id):
#     msg = cur.execute(f"SELECT msg FROM profile").fetchall()[0]
#     cur.execute(f"UPDATE profile SET msg={msg_id}")
#     db.commit()
#     return msg
async def db_create_mails():
    db = sq.connect('new.db')
    cur = db.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS chatgpt_mails (email TEXT, password TEXT, ID INTEGER)")
    cur.execute("CREATE TABLE IF NOT EXISTS chatgpt_deleted_mails (email_del TEXT, password_del TEXT, username_buy TEXT, now_time TEXT)")

    db.commit()

async def view_all_bd():
    tovs = cur.execute("SELECT tov FROM list_tovs").fetchall()
    print(tovs)
    result = ''
    for i in tovs:
        print('Сейчас очередь для этого товара: ', i[0])
        tov = i[0]
        bd = cur.execute(f"SELECT * FROM {tov}").fetchall()
        result = result + f"Товар: {i[0]}\n{bd}\n"
        print(bd)
    return result
async def db_fill_mails(name, key1, key2, key3):
    try:
        if isinstance(((cur.execute(f"SELECT MAX(ID) FROM {name}")).fetchall()[0][0]), int):
            FILL_ID = ((cur.execute(f"SELECT MAX(ID) FROM {name}")).fetchall()[0][0]) + 1
        else:
            FILL_ID = 1
        cur.execute(f"INSERT INTO {name} VALUES(?, ?, ?, ?)", (key1, key2, key3, FILL_ID))
        db.commit()
    except IndexError:
        pass
async def db_get_ID_mails():
    if isinstance(((cur.execute("SELECT MIN(ID) FROM chatgpt_mails")).fetchall()[0][0]), float):
        mov1 = cur.execute("SELECT * FROM chatgpt_mails WHERE ID=(SELECT MIN(ID) FROM chatgpt_mails)")
        db.commit()
        return mov1
    else:
        mov1 = None
        db.commit()
        return mov1
async def db_view_all_mails():
    bd = cur.execute("SELECT * FROM chatgpt_mails").fetchall()
    # print(bd)
    return bd
async def db_view_max_id_mails(name_tov):

    try:
        maxID = cur.execute(f"SELECT MAX(ID) FROM {name_tov}").fetchall()[0][0]
        if maxID == None:
            maxID = 1
        # print(f'Индекс равен= {maxID}')
    except:
        maxID = None
    print('максИД: ', maxID)
    # print(maxID)
    return maxID
async def maxID_list_tovs():
    maxID = cur.execute("SELECT MAX(ID) FROM list_tovs").fetchall()[0][0]
    return maxID


async def fill_list_tovs(tov, price, description):
    maxID = await maxID_list_tovs()
    if maxID == None:
        maxID = 0
    nowID = maxID + 1
    cur.execute("INSERT INTO list_tovs VALUES(?, ?, ?, ?, ?)", (nowID, tov, price, description, 0))
    cur.execute(f"CREATE TABLE IF NOT EXISTS {tov} (key1 TEXT, key2 TEXT, key3 TEXT, ID INTEGER)")
    db.commit()

async def get_info_tov(name):
    info_tov = cur.execute("SELECT * FROM list_tovs WHERE tov='{key}'".format(key=name)).fetchall()
    # print(info_tov)
    db.commit()
    return info_tov

async def list_tovs():
    list_with_tovs = cur.execute("SELECT * FROM list_tovs").fetchall()
    # print(list_with_tovs)
    return list_with_tovs
async def list_tovs_str(maxID):
    list_with_tovs = ''
    maxID = int(maxID)
    for i in range(maxID):
        now_tov = cur.execute("SELECT tov FROM list_tovs WHERE ID='{key}'".format(key=i+1)).fetchone()[0]
        try:
            maxID_now_tov = int(cur.execute(f"SELECT MAX(ID) FROM {now_tov}").fetchone()[0])
            minID_now_tov = int(cur.execute(f"SELECT MIN(ID) FROM {now_tov}").fetchone()[0])
            print(f'расчет: {maxID_now_tov} - {minID_now_tov}')
            lost = maxID_now_tov - minID_now_tov + 1
        except:
            lost = 0

        # print(now_tov)
        now_tov = str(now_tov)
        # list_with_tovs = l
        list_with_tovs = f'{list_with_tovs}{i+1}. {now_tov}, остаток на складе: {lost}\n'
    return list_with_tovs

async def update_quantity_lost_accounts():
    maxID = cur.execute("SELECT MAX(ID) FROM list_tovs").fetchall()[0][0]
    minID = cur.execute("SELECT MIN(ID) FROM list_tovs").fetchall()[0][0]
    print('Макс ИД',maxID)
    print(type(maxID))
    if maxID != None or minID != None:
        quantityID = maxID - minID + 1
        print(f'Количество товаров: {quantityID}')
        for i in range(quantityID):
            print(f'Итерация №{i}:')
            now_tov = cur.execute("SELECT tov FROM list_tovs WHERE ID='{key}'".format(key=i + 1)).fetchone()[0]
            quantityID_this_tov = 0

            maxID_this_tov = cur.execute(f"SELECT MAX(ID) FROM {now_tov}").fetchall()[0][0]
            minID_this_tov = cur.execute(f"SELECT MIN(ID) FROM {now_tov}").fetchall()[0][0]
            print(f'Кал-во {quantityID_this_tov} = {maxID_this_tov} - {minID_this_tov} + 1')
            if maxID_this_tov == None or minID_this_tov == None:
                quantityID_this_tov = 0
            else:
                quantityID_this_tov = maxID_this_tov - minID_this_tov + 1

            cur.execute("UPDATE list_tovs SET lost='{quantityID_this_tov}' WHERE tov='{now_tov}'".format(
                quantityID_this_tov=quantityID_this_tov, now_tov=now_tov))
            db.commit()
    else:
        return 0
    # try:
    #     for i in range(quantityID):
    #         print(f'Итерация №{i}:')
    #         now_tov = cur.execute("SELECT tov FROM list_tovs WHERE ID='{key}'".format(key=i+1)).fetchone()[0]
    #         quantityID_this_tov = 0
    #
    #         maxID_this_tov = cur.execute(f"SELECT MAX(ID) FROM {now_tov}").fetchall()[0]
    #         minID_this_tov = cur.execute(f"SELECT MIN(ID) FROM {now_tov}").fetchall()[0]
    #         quantityID_this_tov = maxID_this_tov - minID_this_tov + 1
    #         print(f'Калво {quantityID_this_tov}')
    #         if maxID_this_tov == None or minID_this_tov == None:
    #             quantityID_this_tov = 0
    #         cur.execute("UPDATE list_tovs SET lost='{quantityID_this_tov}' WHERE tov='{now_tov}'".format(quantityID_this_tov=quantityID_this_tov, now_tov=now_tov))
    #     db.commit()
    # except:
    #     return 1


    # try:
    #     if isinstance(((cur.execute("SELECT MAX(ID) FROM chatgpt_mails")).fetchall()[0][0]), int):
    #         FILL_ID = ((cur.execute("SELECT MAX(ID) FROM chatgpt_mails")).fetchall()[0][0]) + 1
    #     else:
    #         FILL_ID = 1
    #     cur.execute("INSERT INTO chatgpt_mails VALUES(?, ?, ?)", (login, password, FILL_ID))
    #     db.commit()
    # except IndexError:
    #     pass
# async def get_lost_accounts(name_bd):

async def get_account_data(name_bd):
    minID = cur.execute(f"SELECT MIN(ID) FROM {name_bd}").fetchall()[0][0]
    data = cur.execute(f"SELECT * FROM {name_bd} WHERE ID={minID}").fetchall()[0]
    print(data)
    db.commit()
    return data


async def db_tov_target(target):
    # deleted = cur.execute(f"SELECT * FROM {name_bd} WHERE ID=={target_id}").fetchall()
    try:
        del_id = cur.execute("SELECT ID FROM list_tovs WHERE tov='{key}'".format(key=target)).fetchall()[0][0]
    except IndexError:
        return None
    # print(type(del_id))
    maxID = await maxID_list_tovs()
    if del_id != maxID:
        del_data = cur.execute("SELECT * FROM list_tovs WHERE tov='{key}'".format(key=target)).fetchall()[0]
        cur.execute("DELETE FROM list_tovs WHERE tov='{key}'".format(key=target))
        cur.execute(f"UPDATE list_tovs SET ID={del_id} WHERE ID={maxID}")
    else:
        del_data = cur.execute("SELECT * FROM list_tovs WHERE tov='{key}'".format(key=target)).fetchall()[0]
        cur.execute("DELETE FROM list_tovs WHERE tov='{key}'".format(key=target))
    cur.execute(f"DROP TABLE IF EXISTS {target}")
    db.commit()
    return del_data


async def db_tov_lines_target(name_bd, target_key1):
    # del_data = cur.execute("SELECT * FROM {name_bd} WHERE key1='{target_key1}'".format(name_bd=name_bd, target_key1=target_key1)).fetchall()[0]
    try:
        cur.execute(f"DELETE FROM {name_bd} WHERE ID={target_key1}")
    except:
        return None
    db.commit()
    # return del_data

async def db_ready_del_mails(email, username_buy):
    del_data = cur.execute("SELECT * FROM chatgpt_mails WHERE email=='{key}'".format(key=email)).fetchall()
    login_del = str(del_data[0][0])
    password_del = str(del_data[0][1])
    now_time = datetime.datetime.now()
    cur.execute("INSERT INTO chatgpt_deleted_mails VALUES(?, ?, ?, ?)", (login_del, password_del, username_buy, now_time))
    cur.execute("DELETE FROM chatgpt_mails WHERE email== '{key}'".format(key=email))

    db.commit()
    return [login_del, password_del]
async def db_count_num_mails():
    # print((cur.execute("SELECT MAX(ID) FROM chatgpt_mails")).fetchall()[0][0])
    if isinstance(((cur.execute("SELECT MAX(ID) FROM chatgpt_mails")).fetchall()[0][0]), float):
        count_num_mails = (cur.execute("SELECT MAX(ID) FROM chatgpt_mails")).fetchall()[0][0] - (cur.execute("SELECT MIN(ID) FROM chatgpt_mails")).fetchall()[0][0] + 1
        return count_num_mails
    else:
        return 0


# Работа с платежкой снизу
async def input_payment_values(user_id, payment_id, amount, message_id, sign, order_id):
    # try:
    cur.execute("INSERT OR REPLACE INTO payment_values VALUES(?, ?, ?, ?, ?, ?)", (user_id, payment_id, amount, message_id, sign, order_id))
    # except sq.IntegrityError:

    db.commit()
async def check_payment_values(user_id):
    try:
        # print(user_id)
        payment_data = cur.execute("SELECT * FROM payment_values WHERE user_id == '{key}'".format(key=user_id)).fetchone()
        # print(payment_data)
        payment_id = payment_data[1]
        amount = payment_data[2]
        message_id = payment_data[3]
        sign = payment_data[4]
        order_id = payment_data[5]
        # print(f'payment_id = {payment_id}, amount= {amount}, message_id= {message_id}')
        return [payment_id, amount, message_id, sign, order_id]
    except TypeError:
        return 1

    # payment_id = cur.execute("SELECT payment_id FROM payment_values WHERE user_id == '{key}'".format(key=user_id)).fetchone()[0]
    # amount = cur.execute("SELECT amount FROM payment_values WHERE user_id == '{key}'".format(key=user_id)).fetchone()[0]
    # message_id = cur.execute("SELECT message_id FROM payment_values WHERE user_id == '{key}'".format(key=user_id)).fetchone()[0]
    # print(payment_id)

async def delete_payment_values(user_id):
    cur.execute("DELETE FROM payment_values WHERE user_id == '{key}'".format(key=user_id))
    db.commit()

async def check_balance(user_id):
    balance = cur.execute("SELECT balance FROM profile WHERE user_id == '{key}'".format(key=user_id)).fetchone()[0]
    # print(balance)
    return balance


