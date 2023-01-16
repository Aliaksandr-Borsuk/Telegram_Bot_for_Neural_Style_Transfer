# этот бот расписан по шагам ибо я - чайник 

# используем библиотеку python-telegram-bot в Python
# Подключим многопоточный модуль расширения telegram.ext (версия 13.x(13.13))
from telegram.ext import Updater
# импортируем обработчик CommandHandler, 
# который фильтрует сообщения с командами
from telegram.ext import CommandHandler
# импортируем обработчик `MessageHandler` и класс с фильтрами
from telegram.ext import MessageHandler, Filters
# '''
# Модуль argparse
# Благодаря этому модулю в скриптах становится возможным работа с тем, что, без его использования,
# было бы скрыто от кода этих скриптов.
# '''
import argparse

# Чтобы знать, когда и почему что-то не работает должным образом, настроим модуль ведения журнала логов:
# https://docs-python.ru/standart-library/paket-logging-python/
# 1.02
import logging
import requests
# import os
from pathlib import Path
import shutil
import json
# мои костыли
import preparation
import class_for_style_trasfering

from PIL import Image
from io import BytesIO

# создаётся объект parser с указанием его описания.
parser = argparse.ArgumentParser(description='badger_style_transfering_bot_01')
# Далее, с помощью метода parser.add_argument(), описываются переменнst work_dir, ....
# в которые планируется записывать входные параметры , и устанавливаем их дефолтные значения
# При этом указывается их тип, а также задаётся справочная информация о них.
# символы -- указывают на то, что ввод аргументов необязателен
# пример команды вызова скрипта:   python badger_style_transfering_bot_01.py  --sizer=500
parser.add_argument("--size", type=int, default=256,
                    help="размер меньшей стороны обработанного изображения")
parser.add_argument("--num_steps", type=int, default=15,
                    help="число шагов оптимайзера")
# меняя параметр --style_weight можно получить разные выходные картинки
parser.add_argument("--style_weight", type=int, default=70000,
                    help="вес функции потерь стиля")
parser.add_argument("--content_weight", type=int, default=1,
                    help="вес функции потерь контента")

opt = parser.parse_args()
print(opt)

# оптределяем текущую дирректорию
CURRENT_DIR = Path(__file__).parent.resolve()


# задаём TOKEN 
# если  токен содержится в файле token.txt в текущей дирректории берем его оттуда
with open(CURRENT_DIR/'token.txt') as file:
    TOKEN = file.readline()
# или раскоментируем эту строку и забиваем токен здесь
##########################################
#TOKEN = < ваш токен  >
################################

# создадим временную рабочую  папку где храним фотки стиля и контента,
# и куда по желанию будем сбрасывать loss и готовое фото
work_dir_name = 'badger_style_transfering_bot'
WORK_DIR = CURRENT_DIR / work_dir_name
Path.mkdir ( WORK_DIR, parents=True, exist_ok=True)

# определим экземпляр класса для трансферинга
ST = class_for_style_trasfering.Style_Transfering()


# '''1.03.
# Теперь определим функцию, которая должна обрабатывать определенный тип сообщения, отправленных боту:
# '''
def start(update, context):
    # `bot.send_message` это метод Telegram API
    # `update.effective_chat.id` - определяем `id` чата, 
    # откуда прилетело сообщение 
    context.bot.send_message(chat_id=update.effective_chat.id, 
                             text="I'm a bot artist. Let's draw!\n \
                             Send two images with labels content and style.\n \
                             Then send the '/draw' command . ")
#     '''Примечание. Обратите внимание, аргументы update и context функции обратного вызова start():
#         - аргументы update и context передаются автоматически;
#         - update - это объект связанный с экземпляром Update который
#     присылает и отправляет все сообщения. Через него можно получить
#     доступ к экземпляру telegram.Bot() как update.bot;
#         - context - это объект связанный с контекстом обработанного сообщения.
#     Через него также можно получить доступ к экземпляру telegram.Bot()
#     как context.bot.'''


# '''1.07
# Пользователи могут попытаться отправить боту команды,
# которые он не понимает, поэтому можно использовать обработчик MessageHandler
# с фильтром Filters.command, чтобы отвечать на все команды, которые
# не были распознаны предыдущими обработчиками.'''
def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, 
                             text="Sorry, I didn't understand that command." )
    
def draw(update, context):
    chat_id = update.effective_chat.id
    path_for_save_images = WORK_DIR /str(chat_id) 
    # проверяем загрузил ли пользователь картинки
    if not Path(path_for_save_images /'content.jpg').exists():
        text = 'Please send a picture marked "content".'
        context.bot.send_message(chat_id=update.effective_chat.id, text= text )
    elif not Path(path_for_save_images /'style.jpg').exists():
        text = 'Please send a picture marked "style".'
        context.bot.send_message(chat_id=update.effective_chat.id, text= text )
    else :
        # если все картинки на месте начинаем рисовать
        # выводим в чат исходные картинки маленького размера
        for category in ['style', 'content']:
            img = preparation.open_and_repair_image(
                size = 150,
                chat_id = chat_id, category = category,
                work_dir = WORK_DIR
            )
            context.bot.send_photo(chat_id=chat_id, photo=img)
            context.bot.send_message(chat_id=update.effective_chat.id, text= f'I have the picture {category}.' )

        text = "I'll draw it.\n I create... and I do a little magic...\n Please wait a bit..."
        context.bot.send_message(chat_id=update.effective_chat.id, text= text )
        # само рисование
        result = ST.transfering(
            path = WORK_DIR,
            chat_id = update.effective_chat.id,
            size = opt.size,
            num_steps=opt.num_steps,
            style_weight= opt.style_weight, #70000,
            content_weight = opt.content_weight  #1
        )
        context.bot.send_message(chat_id=update.effective_chat.id, text= "I did it!" )
        ### превращаем картинку в формат который бот сможет заслать в телегу
        bio = BytesIO()
        bio.name = 'image.jpeg'
        result.save(bio, 'JPEG')
        bio.seek(0)
        context.bot.send_photo(chat_id=chat_id, photo=bio)
        context.bot.send_message(chat_id=update.effective_chat.id, text= 'And here is the result...' )
        # Если закоментировать строку удаления то в папке под номером чата будут сохраняться последние входные изображения,
        # а также все выходные изображения и losses
        # удаление рабочей папки пользователя если оно надо
        # shutil.rmtree(WORK_DIR/str(update.effective_chat.id))



        

    
def image(update, context):
    print('image')
#     text = json.dumps(update.to_dict(), indent=2)
#     context.bot.send_message(chat_id=update.effective_chat.id, text=text) 
    
    chat_id = update.effective_chat.id
    category = update.message.caption
    
    if category in ['content', 'style']:
        # получаем id картинки
        file_id = update.message.document.file_id
        # её url
        file_path = context.bot.get_file(file_id).file_path
        # сохраняем локально
        # если какой-нить сбой возвращается сообщение об ошибке
        result = preparation.change_and_save_image(
            file_path=file_path, size = opt.size+10,
            chat_id = chat_id, category = category,
            work_dir = WORK_DIR
        )
        
        if result:
            text = f'Something is wrong with this file...'
            print( f'image exception  {result}' )
        else:
            text =f'{category} picture created successfully.'
    else: 
        text = "The picture must be signed 'content' or 'style' "
        

    # text = json.dumps(update.to_dict(), indent=2) + text
    context.bot.send_message(chat_id = chat_id, text=text )

    
def photo(update, context):
    print('photo')
    chat_id = update.effective_chat.id
    category = update.message.caption
    
    if category in ['content', 'style']:
        # получаем id картинки
        file_id = update.message.photo[-1].file_id
        # её url
        file_path = context.bot.get_file(file_id).file_path
        # сохраняем локально
        result = preparation.change_and_save_image(
            file_path=file_path, size = opt.size+10,
            chat_id = chat_id, category = category,
            work_dir = WORK_DIR
        )
        
        if result:
            text = f'Something is wrong with this file...'
            print(print( f'photo exception  {result}' ))
        else:
            text =f'{category} picture created successfully.'
    else: 
        text = "The photo must be signed 'content' or 'style' "
        

    # text = json.dumps(update.to_dict(), indent=2) + text
    context.bot.send_message(chat_id = chat_id, text=text )
    
     



# '''0.01.
# Объявляем функцию main и в ней создаём экземпляр класса  Updater, в конструктор передаём токен бота, 
# который получили у BotFather. Задача класса Updater получать сообщения Telegram'а через 
# long-polling — напомню, это значит, что бот делает запросы в Bot API, чтобы их получить.'''
def main() -> None:
    # ''' 1.01.
    # - https://docs-python.ru/packages/biblioteka-python-telegram-bot-python/
    # Во-первых, нужно создать объект Updater.
    # Для более быстрого доступа к Dispatcher, в который Updater посылает сообщение,
    # можно создать его отдельно:'''
    # получаем экземпляр `Updater`
    updater = Updater(token=TOKEN)    
    # получаем экземпляр `Dispatcher`
    dispatcher = updater.dispatcher
    
#     '''1.02.
#     Чтобы знать, когда и почему что-то не работает должным образом, настроим модуль ведения журнала логов:
#     https://docs-python.ru/standart-library/paket-logging-python/
#         import logging сделоно выше
#     '''
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
#     '''Примечание. если хотите узнать больше об обработке исключений с python-telegram-bot,
#     прочтите подраздел об "Обработка исключений".
#     https://docs-python.ru/packages/biblioteka-python-telegram-bot-python/obrabotka-oshibok/
#     '''
    
#     '''1.04.
#     Цель состоит в том, чтобы функция start вызывалась каждый раз,
#     когда бот получает сообщение с серверов Telegram, содержащее команду /start.
#     Для этого можно использовать класс CommandHandler (один из предоставленных подклассов Handler)
#     и зарегистрировать его в Dispatcher:
#         # импортируем обработчик CommandHandler, 
#         # который фильтрует сообщения с командами
#         from telegram.ext import CommandHandler 
#         сделано выше
#     '''

    # 1.03 говорим обработчику, если увидишь команду `/start`,
    # то вызови функцию `start()`
    start_handler = CommandHandler('start', start)
    # добавляем этот обработчик в `dispatcher`
    dispatcher.add_handler(start_handler)
    
    #Если увидишь комaнду /draw то вызови функцию `draw()`
    draw_handler = CommandHandler('draw', draw)
    # добавляем этот обработчик в `dispatcher`
    dispatcher.add_handler(draw_handler)
    
    # 2.00 создадим обработчик получения картинки сжатой
    photo_handler =  MessageHandler( Filters.photo, photo)
    # добавляем этот обработчик в `dispatcher`
    dispatcher.add_handler(photo_handler)
    
    # 2.01 создадим обработчик получения картинки сжатой
    image_handler =  MessageHandler( Filters.document.image, image)
    # добавляем этот обработчик в `dispatcher`
    dispatcher.add_handler(image_handler)    
    
    
    
    
    # 1.99 говорим обработчику, если увидишь неизвестную команду ,
    # то вызови функцию `unknown()`
    unknown_handler = MessageHandler(Filters.text | Filters.document, unknown)
    dispatcher.add_handler(unknown_handler)
#     '''Примечание. Этот обработчик должен быть добавлен последним.
#     Если его поставить первым, то он будет срабатывать до того, как обработчик
#     CommandHandlers для команды /start увидит обновление.
#     После обработки обновления функцией unknown() все дальнейшие обработчики будут игнорироваться.
#     Чтобы обойти такое поведение, можно передать в метод dispatcher.add_handler(handler, group),
#     помимо самой функции обработчика аргумент group со значением, отличным от 0.
#     Аргумент group можно воспринимать как число, которое указывает приоритет обновления обработчика.
#     Более низкая группа означает более высокий приоритет.
#     Обновление может обрабатываться (максимум) одним обработчиком в каждой группе.'''
    
    # '''1.05.
    # Для запуска бота дописываем команду:'''
    # говорим экземпляру `Updater`, 
    # слушай сервера Telegram.
    updater.start_polling()
    # Печатает при запуске Started в терминале из которого запустили бота
    print('Started') 
    
    # '''1.06.
    # Далее делаем так, чтобы бот работал, пока не получит сигнал о прекращении. Например, 
    # сигнал о нажатии Ctrl+C в Терминале в котором запустили бота.'''
    updater.idle()

    



# '''0.00
# Вызываем функцию main.'''
if __name__ == "__main__":
    main()
