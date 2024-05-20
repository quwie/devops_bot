import logging
import re
import paramiko
import psycopg2
import os
from dotenv import load_dotenv

from telegram import Update, ForceReply, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext

load_dotenv()

TOKEN = str(os.getenv('BOT_TOKEN'))

DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')

DB_REPL_USER = os.getenv('DB_REPL_USER')

RM_HOST = os.getenv('RM_HOST')
RM_PORT = os.getenv('RM_PORT')
RM_USER = os.getenv('RM_USER')
RM_PASSWORD = os.getenv('RM_PASSWORD')

logging.basicConfig(filename='logfile.txt',
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def execute_command(command):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=RM_HOST, username=RM_USER,
                password=RM_PASSWORD, port=22)

    stdin, stdout, stderr = ssh.exec_command(command)
    result = stdout.read().decode()

    ssh.close()

    return result


def execute_sql_command(sql_command):
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER,
                            password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)

    cur = conn.cursor()
    cur.execute(sql_command)
    result = cur.fetchall()
    conn.close()

    return result

def insert_into_db(sql_command):
    conn = psycopg2.connect(database=DB_NAME, user=DB_USER,
                            password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)

    cur = conn.cursor()
    cur.execute(sql_command)
    conn.commit()
    conn.close()

def reply_long_sql_messages(update, result):
    message = ''

    if isinstance(result, list):
        for row in result:
            i = 0
            for item in list(row):
                i += 1
                message += str(item)
                if i != len(row):
                    message += ' | '
            message += '\n'

    if len(message) > 4096:
        for x in range(0, len(message), 4096):
            update.message.reply_text(message[x:x+4096])
    else:
        update.message.reply_text(message)


def reply_long_messages(update, result):
    if len(result) > 4096:
        for x in range(0, len(result), 4096):
            update.message.reply_text(result[x:x+4096])
    else:
        update.message.reply_text(result)


def get_release(update, _):
    result = execute_command('lsb_release -a')
    reply_long_messages(update, result)


def get_uname(update, _):
    result = execute_command('uname -a')
    reply_long_messages(update, result)


def get_uptime(update, _):
    result = execute_command('uptime')
    reply_long_messages(update, result)


def get_df(update, _):
    result = execute_command('df -h')
    reply_long_messages(update, result)


def get_free(update, _):
    result = execute_command('free -h')
    reply_long_messages(update, result)


def get_mpstat(update, _):
    result = execute_command('mpstat')
    reply_long_messages(update, result)


def get_w(update, _):
    result = execute_command('w')
    reply_long_messages(update, result)


def get_auths(update, _):
    result = execute_command('last -n 10')
    reply_long_messages(update, result)


def get_critical(update, _):
    result = execute_command('journalctl -p 2 -b -n 5')
    reply_long_messages(update, result)


def get_ps(update, _):
    result = execute_command('ps aux')
    reply_long_messages(update, result)


def get_ss(update, _):
    result = execute_command('ss -tulwn')
    reply_long_messages(update, result)


def get_apt_list(update, _):
    result = execute_command('apt list --installed')
    reply_long_messages(update, result)


def get_services(update, _):
    result = execute_command('systemctl list-units --type=service')
    reply_long_messages(update, result)


def find_email(update: Update, _) -> int:
    update.message.reply_text('Пожалуйста, отправьте мне текст для поиска email-адресов:',
                              reply_markup=ForceReply(selective=True))
    return 'process_email'


def process_email(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    emails = re.findall(
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)

    if emails:
        update.message.reply_text('\n'.join(emails))
        reply_keyboard = [['Да', 'Нет']]
        update.message.reply_text('E-mail адреса найдены. Хотите записать в базу данных?',
                                  reply_markup=ReplyKeyboardMarkup(reply_keyboard,
                                                                   one_time_keyboard=True)
                                  )

        requests = [f"INSERT INTO emails (email) VALUES ('{email}');"
                    for email in emails]
        context.user_data['requests'] = requests

        return 'save_to_db'

    update.message.reply_text('Email-адреса не найдены.')
    return ConversationHandler.END


def find_phone_number(update: Update, _) -> int:
    update.message.reply_text('Пожалуйста, отправьте мне текст для поиска номеров телефона:',
                              reply_markup=ForceReply(selective=True))
    return 'process_phone'


def process_phone_number(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    phone_numbers = re.findall(
        r'\+7[-\s]?\(?\d{3}\)?[-\s]?\d{3}[-\s]?\d{2}[-\s]?\d{2}'
        r'|8[-\s]?\(?\d{3}\)?[-\s]?\d{3}[-\s]?\d{2}[-\s]?\d{2}',
        text)

    if phone_numbers:
        update.message.reply_text('\n'.join(phone_numbers))

        reply_keyboard = [['Да', 'Нет']]
        update.message.reply_text('Номера телефонов найдены. Хотите записать в базу данных?',
                                  reply_markup=ReplyKeyboardMarkup(reply_keyboard,
                                                                   one_time_keyboard=True)
                                  )

        requests = [f"INSERT INTO phones (phone) VALUES ('{number}');"
                    for number in phone_numbers]
        context.user_data['requests'] = requests

        return 'save_to_db'

    update.message.reply_text('Номера телефонов не найдены.')
    return ConversationHandler.END


def save_to_db(update: Update, context: CallbackContext) -> int:
    user_response = update.message.text
    if user_response == 'Да':

        for request in context.user_data['requests']:
            try:
                insert_into_db(request)
            except Exception as e:
                logger.error("Ошибка добавления в БД: %s", e)
                update.message.reply_text('Ошибка добавления в базу данных.',
                                          'Попробуйте чуть позже...', reply_markup=ReplyKeyboardRemove())
                return ConversationHandler.END

        update.message.reply_text('Данные успешно записаны в базу данных.', reply_markup=ReplyKeyboardRemove())
    else:
        update.message.reply_text('Данные не были записаны в базу данных.', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def verify_password_command(update: Update, _) -> str:
    update.message.reply_text('Введите пароль для проверки:')
    return 'process_password'


def process_password(update: Update, _) -> int:
    text = update.message.text
    password_regex = r'^(?=.*[A-Z])(?=.*[!@#$%^&*()])(?=.*[0-9])(?=.*[a-z]).{8,}$'
    if re.match(password_regex, text):
        update.message.reply_text('Пароль сложный.')
    else:
        update.message.reply_text('Пароль простой.')
    return ConversationHandler.END


def get_repl_logs(update: Update, _):
    result = execute_command(
        f'cat /var/lib/postgresql/data/log/postgresql.log | grep replication')
    reply_long_messages(update, result)


def get_emails(update: Update, _):
    result = execute_sql_command('SELECT * FROM emails')
    reply_long_sql_messages(update, result)


def get_phone_numbers(update: Update, _):
    result = execute_sql_command('SELECT * FROM phones')
    reply_long_sql_messages(update, result)


def cancel(update: Update, _) -> int:
    update.message.reply_text(
        'Диалог завершен.', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def main():
    updater = Updater(TOKEN, use_context=True)

    # Получаем диспетчер для регистрации обработчиков
    _ = updater.dispatcher

    # Регистрируем обработчики команд
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('get_repl_logs', get_repl_logs),
                      CommandHandler('find_email', find_email),
                      CommandHandler('get_emails', get_emails),
                      CommandHandler('get_phone_numbers', get_phone_numbers),
                      CommandHandler('find_phone_number', find_phone_number),
                      CommandHandler('verify_password',
                                     verify_password_command),
                      CommandHandler('get_release', get_release),
                      CommandHandler('get_uname', get_uname),
                      CommandHandler('get_uptime', get_uptime),
                      CommandHandler('get_df', get_df),
                      CommandHandler('get_free', get_free),
                      CommandHandler('get_mpstat', get_mpstat),
                      CommandHandler('get_w', get_w),
                      CommandHandler('get_auths', get_auths),
                      CommandHandler('get_critical', get_critical),
                      CommandHandler('get_ps', get_ps),
                      CommandHandler('get_ss', get_ss),
                      CommandHandler('get_apt_list', get_apt_list),
                      CommandHandler('get_services', get_services),
                      ],
        states={
            'process_email': [MessageHandler(Filters.text & ~Filters.command,
                                             process_email)],
            'process_phone': [MessageHandler(Filters.text & ~Filters.command,
                                             process_phone_number)],
            'process_password': [MessageHandler(Filters.text & ~Filters.command,
                                                process_password)],
            'save_to_db': [MessageHandler(Filters.regex('^(Да|Нет)$'),
                                          save_to_db)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    # Регистрируем обработчик текстовых сообщений
    updater.dispatcher.add_handler(conv_handler)

    # Запускаем бота
    updater.start_polling()

    # Останавливаем бота при нажатии Ctrl+C
    updater.idle()


if __name__ == '__main__':
    main()
