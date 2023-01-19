# Telegram_Bot_for_Neural_Style_Transfer 
    
ссылка на бота https://t.me/badger_style_transfering_bot  

Автор бота: @badger_by (stepik id:  327028887)  
  
При создании бота и модели для обработки изображений были использованы материалы:   
https://stepik.org/course/122947/syllabus   
https://docs-python.ru/packages/biblioteka-python-telegram-bot-python/   
https://pytorch.org/tutorials/advanced/neural_style_tutorial.html   
https://habr.com/ru/post/453512/   
  
## Что умеет этот бот ?
Этот Telegram бот перносит стиль одной картинки на другую, с помощью алгоритма NST (Neural Style Transfer).  
  
Примеры работы бота.
  
![](https://github.com/Alexandr-Borsuk/Telegram_Bot_for_Neural_Style_Transfer/blob/main/images/scr.jpg)


## Как работает этот этот бот.
### Запуск.
#### Запуск на локальной машине.
Этот бот готов для запуска на локальной машине.
- Скопируйте файлы в любую папку.
-  Запустите скрипт badger_style_transfering_bot_01.py  
При запуске Вы можете выбрать 
-  размер меньшей стороны выходного изображения --size (default=256)
-  - в файле class_for_style_trasfering.py , в классе Style_Transfering, в функции transfering прописано ограничение на размер выходного изображени (128) в случае отсутствия cuda.
-  кол-во шагов оптимайзера --num_steps  (default=15)
-  вес функции потерь стиля --style_weight (default=70000)
-  - при уменьшении веса влияние стиля тоже уменьшается.  
#### Запуск в Colab 
Выполните следующие команды :   

! git clone https://github.com/Aliaksandr-Borsuk/Telegram_Bot_for_Neural_Style_Transfer.git        

!  pip install python-telegram-bot==13.14    

Тут необходжимо вставить свой токен в token.txt    

! python /content/Telegram_Bot_for_Neural_Style_Transfer/badger_style_transfering_bot_01.py --size=512
  
Если всё хорошо , то бот уже ждёт Ваши картинки.)
  
### Работа.
Бот воспринимает две команды:  
**/start** -  выдаёт краткие инструкции   
**/draw** - обрабатывает входные картинки      
Если пользователь присылает незнакомые команды , или картинки с неправильными метками бот сообщает об этом пользователю и просит сделать всё как нужно.   
Так же бот ждёт картинки с метками style и content.    
Пример отсылки картинок для бота.       

<img src="https://github.com/Alexandr-Borsuk/Telegram_Bot_for_Neural_Style_Transfer/blob/main/images/sample.jpg" width="400"  />

После получения каждой картинки бот присылает пользователю подтверждение получения.  
После команды /draw бот создаёт новое изображение и отсылает пользователю.   
(При использовании этого алгоритма необходимо учитывать , что при больших различиях в содержании входных картинок результат переноса может быть не совсем ожидаемым)   

### Что внутри.

  Телеграмм-бот находится в файле badger_style_transfering_bot_01.py.Написан при помощи библиотеки python-telegram-bot.
Во время работы бот создаёт папку badger_style_transfering_bot, а так же отдельные папки для каждого чата  куда складывает временные файлы изображений и losses. После получения выходного изображения файлы удаляются. За это отвечает последняя строка в методе /draw файла badger_style_transfering_bot_01.py . Если её закоментить , то losses и выходные изображения будут сохраняться.
  Обработка изображений происходит с помощью модели Style_Transfer_01 из файла assistants.py. Основа модели взята из 
  - https://pytorch.org/tutorials/advanced/neural_style_tutorial.html   
  В файле token.txt должен быть Ваш токен для бота.
  В файле reading_of_losses.ipynb находится функция для отрисовки losses.(если Вы конечно настроите бот на их сохранение )
    
Мной внесено следующее изменение:  
- вместо того чтобы каждый раз скачивать  VGG и собирать модель  для каждой пары картинок, модель была создана заранее, веса слоёв заранее были инициализированы весами слоёв VGG, и состояние модели записано в файл st_01_state_dict.pth. Т.е. модель инициализируется единожды при запуске бота а не при каждой загрузке новых картинок. 
### P.S.
Т.к. я - "чайник" и только учусь,  код  далёк от совершенства и перегружен комментариями.)
 
  



