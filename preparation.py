import requests
import os
from PIL import Image
from io import BytesIO

# этот модуль будет уменьшать принятое изображение до нужных размеров
# и записывать куда следует
# функция изменения размера картинки
# size отвечает за выходной размер картинки
# нам нужна квадратная
def change_and_save_image(file_path, size , chat_id , category, work_dir):
    try :
        response  = requests.get(file_path)
        img = Image.open(BytesIO(response.content))
        proportion = img.size[0]/img.size[1] # пропорции сторон тож сохраним для последующего восстановления 
        img=img.resize((size, size))
        # мастерим папку для сохранения фоток если её пока нет
        save_images = work_dir/str(chat_id)
        if not os.path.exists(save_images ):
                os.makedirs(save_images)

        img.save(save_images/(category +'.jpg'))
        with open (save_images/(category + '_proportion.txt'), 'w') as file:
            file.write(str(proportion))
        return 0
    except Exception as e :
        return str(e)
    
def open_and_repair_image( size, chat_id , category, work_dir ):
    save_images = work_dir /str(chat_id)
    img = Image.open(save_images /( category + '.jpg'))
    with open(save_images/(category + '_proportion.txt'), 'r') as file:
        proportion = float(file.readlines()[0])
    img = img.resize( (int(size*proportion),size))
    ### превращаем картинку в формат который бот сможет заслать в телегу
    bio = BytesIO()
    bio.name = 'image.jpeg'
    img.save(bio, 'JPEG')
    bio.seek(0)
    return bio
    