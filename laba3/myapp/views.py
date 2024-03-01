import json
import pymysql
import requests
from myapp.credentials import TELEGRAM_API_URL, URL, HOSTDB, DBNAME, PORTDB, USERDB, PASSDB, TIMEOUT
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt

timeout = TIMEOUT

connection = pymysql.connect(
    charset="utf8mb4",
    connect_timeout=timeout,
    cursorclass=pymysql.cursors.DictCursor,
    db=DBNAME,
    host=HOSTDB,
    password=PASSDB,
    read_timeout=timeout,
    port=PORTDB,
    user=USERDB,
    write_timeout=timeout,
)
table = "customers"


def setwebhook(request):
    response = requests.post(TELEGRAM_API_URL + "setWebhook?url=" + URL).json()
    return HttpResponse(f"{response}")


@csrf_exempt
def telegram_bot(request):
    if request.method == 'POST':
        update = json.loads(request.body.decode('utf-8'))
        handle_update(update)
        return HttpResponse('ok')
    else:
        return HttpResponseBadRequest('Bad Request')


def handle_update(update):
    try:
        chat_id = update['message']['chat']['id']
        text = update['message'].get('text', '')
        contact = update['message'].get('contact')

        if text == '/register':
            send_message("sendMessage", {
                'chat_id': chat_id,
                'text': 'Please enter your phone number:',
                'reply_markup': {
                    'keyboard': [
                        [
                            {
                                'text': 'My phone',
                                'request_contact': True
                            }
                        ]
                    ],
                    'resize_keyboard': True,
                    'one_time_keyboard': True
                }
            })
        elif contact:

            phone_number = contact['phone_number']
            first_name = contact.get('first_name', '')
            last_name = contact.get('last_name', '')

            user_id = check_user(phone_number)

            if user_id:
                send_message("sendMessage", {
                    'chat_id': chat_id,
                    'text': f'Welcome back, {first_name} {last_name}! Your user ID is {user_id}'
                })
            else:
                user_id = save_user(
                    phone_number, first_name, last_name, chat_id)
                send_message("sendMessage", {
                    'chat_id': chat_id,
                    'text': f'Congratulations, {first_name} {last_name}! You have been successfully registered. Your user ID is {user_id}'
                })
        elif text == 'My phone':
            send_message("sendMessage", {
                'chat_id': chat_id,
                'text': 'Please use the "My phone" button to share your contact.'
            })

    except Exception as e:
        send_message("sendMessage", {
            'chat_id': chat_id,
            'text': f'Error: {str(e)}'
        })


def send_message(method, data):
    return requests.post(TELEGRAM_API_URL + method, json=data)


def check_user(phone_number):
    with connection.cursor() as cursor:
        sql = f"SELECT id FROM {table} WHERE phone_number = %s"
        cursor.execute(sql, (phone_number,))
        result = cursor.fetchone()
        return result['id'] if result else None


def save_user(phone_number, first_name, last_name, chat_id):
    with connection.cursor() as cursor:
        sql = f"INSERT INTO {
            table} (first_name, last_name, phone_number, telegram_id) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql, (first_name, last_name, phone_number, chat_id))
        connection.commit()
        return cursor.lastrowid
