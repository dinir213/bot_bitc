from yookassa import Payment
import uuid

import cryptomus
# from cryptomus import CryptomusAPI, PaymentType
import requests
import json
import hashlib
import base64
from datetime import datetime

async def create_payment(amount):
    idempotence_key = str(uuid.uuid4())
    payment = Payment.create({
        "amount": {
            "value": f'{amount}',
            "currency": "RUB"
        },
        "payment_method_data": {
            "type": "bank_card"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": "https://www.example.com/return_url"
        },
        "capture": True,
        "description": "Заказ №114"
    }, idempotence_key)
    # get confirmation url
    confirmation_url = payment.confirmation.confirmation_url
    confirmation_id = payment.id
    print(payment.json())
    print(confirmation_id)
    return [confirmation_url, confirmation_id]
async def check_payment(payment_id):
    payment = Payment.find_one(payment_id)
    sostoinie = payment.status
    return sostoinie


MERCHANT_KEY = 'b76f1b63-1990-4e5a-b52a-b12960494a12'
API_KEY = 'LyU8wM0axQGKZR5U5BSsuHYS8hLnF49x11U4SOSMZ2L1DFyg5UfJocc4hEyj8c32MNYBBtKr1bzNNLU3Sew5ibdsiClqdkjOtDOZJ2ao2nBtu2ysgtGEF9bwXHRpM0ck'
async def create_payment_cryptomus(amount):
    now = datetime.now().time()
    order_id = f"{now}"
    delete_symbols = ":."
    for char in delete_symbols:
        order_id = order_id.replace(char, "")
    data = {
        'amount': f'{amount}',
        'currency': 'USDT',
        'order_id': f'{order_id}',
        'url_return': 'https://your.site/return',
        'url_callback': 'https://your.site/callback'
    }
    data = json.dumps(data)
    data_base64 = base64.b64encode(data.encode('utf-8'))
    sign = hashlib.md5(data_base64 + API_KEY.encode('utf-8')).hexdigest()
    print(f'Sign = {sign}')
    headers = {
        'merchant': f'{MERCHANT_KEY}',
        'sign': f'{sign}',
        'Content-Type': 'application/json'
    }
    response = requests.post('https://api.cryptomus.com/v1/payment', headers=headers, data=data)

    if response.status_code == 200:
        payment_url = response.json()["result"]["url"]
        uuid = response.json()["result"]["uuid"]
        print(f'payment_id = {uuid}')
        return [payment_url, uuid, sign, order_id]
    else:
        payment_id = response.json()
        return payment_id
async def check_payment_cryptomus(uuid, order_id):
    data = {
        'uuid': f'{uuid}',
        'order_id': f'{order_id}'
    }
    data = json.dumps(data)
    data_base64 = base64.b64encode(data.encode('utf-8'))
    sign = hashlib.md5(data_base64 + API_KEY.encode('utf-8')).hexdigest()
    headers = {
        'merchant': f'{MERCHANT_KEY}',
        'sign': f'{sign}',
        'Content-Type': 'application/json'
    }

    response = requests.post('https://api.cryptomus.com/v1/payment/info', headers=headers, data=data)
    if response.status_code == 200:
        payment_status = response.json()['result']['status']
        print(f'СТАТУС ПЛАТЕЖА:\n {payment_status}')
        return payment_status

    else:
        payment_status = response.json()
        print(f'ОШИБКА:\n {payment_status}')
        return payment_status
