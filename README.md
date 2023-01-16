# Telegram_Bot_for_Neural_Style_Transfer 
    
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
### Запуск
Этот бот готов для запуска на локальной машине.
- Скопируйте файлы в любую папку.
-  Запустите скрипт badger_style_transfering_bot_01.py  
При запуске Вы можете выбрать 
-  размер меньшей стороны выходного изображения --size (default=256)
-  - в файле class_for_style_trasfering.py , в классе Style_Transfering, в функции transfering прописано ограничение на размер выходного изображени (128) в случае отсутствия cuda.
-  кол-во шагов оптимайзера --num_steps  (default=15)
-  вес функции потерь стиля --style_weight (default=70000)
-  - при уменьшении веса влияние стиля тоже уменьшается.   
  
Во время работы бот создаёт папку badger_style_transfering_bot куда складывает временные файлы изображений и losses. После получения выходного изображения файлы удаляются. За это отвечает последняя строка в методе /draw файла badger_style_transfering_bot_01.py . Если её закоментить , то losses и выходные изображения будут сохраняться.
### Работа бота.
Бот воспринимает две команды:  
**/start** -  выдаёт краткие инструкции   
**/draw** - обрабатывает входные картинки    
Если пользователь присылает незнакомые команды , или картинки с неправильными метками бот сообщает об этом пользователю и просит сделать всё как нужно.
Так же бот ждёт картинки с метками style и content.
Пример отсыдки картинок для бота.
![](https://github.com/Alexandr-Borsuk/Telegram_Bot_for_Neural_Style_Transfer/blob/main/images/sample.jpg = 100x50)



(При использовании этого алгоритма необходимо учитывать , что при больших различиях в содержании картинок результат переноса может быть неудовлетворительным)
