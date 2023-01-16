# модель для переноса стиля
# import os
import time
import pickle

import torch
# import torch.nn as nn
# import torch.nn.functional as F
import torch.optim as optim

from pathlib import Path
from PIL import Image

import torchvision.transforms as transforms
# import torchvision.models as models

import copy
# подпорки
from assistants import Style_Transfer_01



# ну а теперь напишем CLASS который по адресу папки с изображениями 
# делает трансфер стиля 
class Style_Transfering():
    def __init__(self):
        self.DEVICE = None
        self.model = None
        # размер картинок для обработки (можно изменять при получении картинок)
        self.size = None

    
    # функция  получения начальных изображений    
    def getting_images(self, path, chat_id ): 
###############################################################
        print('getting_images  self.size ',self.size)
#############################################################        
        # transformer преобразует 'JpegImageFile' object к тензору 
        transformer = transforms.Compose([
            transforms.Resize(self.size),  # меняем размер
            transforms.CenterCrop(self.size),
            transforms.ToTensor()])  # переводим в torch tensor
        # читаем картинки
        style_image = Image.open(path/str(chat_id)/"style.jpg")
        content_image = Image.open(path/str(chat_id)/"content.jpg")
        # добавляем ось для соответствия входному размеру сети
        style_image = transformer(style_image).unsqueeze(0)\
                            .to(torch.float)
        content_image = transformer(content_image).unsqueeze(0)\
                            .to(torch.float) 
        return style_image, content_image
    
    
    # сам перенос
    def style_transfer (self, style_image, content_image, num_steps= 15,
                       style_weight=100000, content_weight=1):
        
        ################################################
        print('Set the style transfer model..')
        ################################################


        # отправляем модель , надеюсь, на cuda )
        self.model.to_device(self.DEVICE)
        # переводим в режим инференса
        self.model.eval()
        # настраиваем её
        self.model(style_image.to(self.DEVICE), fit_style = True)
        self.model(content_image.to(self.DEVICE), fit_content = True)
        # отключаем изменение параметров модели
        self.model.requires_grad_(False)
        # создаём картинку которую будем обучать
        input_image = content_image.to(self.DEVICE)
        input_image.requires_grad_(True)
        # будем добывать лучший результат
        best_image = input_image.to('cpu')
        best_score = float('inf')       

        # для сбора лоссов заведём словарик
        losses = {'style': [], 'content' : []}
        # определяем optimizer
        optimizer = optim.LBFGS([input_image])

        ########################################################
        print('Optimizing..')
        #######################################################
        def closure():
            # correct the values of updated input image
            with torch.no_grad():
                input_image.clamp_(0, 1)

            optimizer.zero_grad()
            loss_dict = self.model(input_image)
            style_score = sum(loss_dict['style_loss']) 
            content_score = sum(loss_dict['content_loss'])
            style_score *= style_weight
            content_score *= content_weight            
            
            loss = style_score + content_score
            loss.backward()
            
            # собираем лоссы
            losses['style'].append(style_score.item())
            losses['content'].append(content_score.item())

            return style_score + content_score
        for i in range (num_steps):
            optimizer.step(closure)
            # запоминаем лучший результат
            if losses['style'][-1] < best_score:
                best_image =  input_image.to('cpu')
                best_score = losses['style'][-1]
            ###########################################################
            # печать losses
            if i % 3 == 0:
                print (f"ns {i}, Style Loss : {losses['style'][-1]}, Content Loss: {losses['content'][-1]}")
            #####################################################  
        # best_image = input_image.to('cpu')
        # a last correction...
        with torch.no_grad():
            best_image.clamp_(0, 1)
        # освобождение cuda
        self.model.to_device('cpu')
        optimizer = None
        loss = None
        loss_dict =None
        style_score = None
        content_score = None
        input_image = None

        torch.cuda.empty_cache()

        return best_image, losses    
    
    # функция переноса
    def transfering(self, path , chat_id ,
                    size = 512, num_steps=15,
                    style_weight=70000, content_weight=1):
        
        # определение DEVICE
        self.DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # размер изображений с которыми работаем
        if torch.cuda.is_available():
            self.size = size
        else:
            self.size = 128
        # определяем сами изображение и перекидываем в тензоры
        style_image, content_image = self.getting_images(path, chat_id)
        # получаем модель если её ещё нет
        if self.model is None:
            self.model = Style_Transfer_01()
            # импортим веса обученой мордели
            
            self.model.load_state_dict(torch.load(Path(__file__).parent.resolve()/'st_01_state_dict.pth'))
        # запускаем процесс переноса стиля
        best_image, losses = self.style_transfer(style_image, content_image, num_steps = num_steps,
                       style_weight=style_weight, content_weight=content_weight)
        # вытаскиваем пропорции картинки для восстановления
        with open (path/str(chat_id)/'content_proportion.txt', 'r') as file:
            proportion = float(file.readlines()[0])
        # устанавливаем ширину, и высоту выходной картинки
        width, height = size, size
        if proportion >1:
            width = int(size*proportion)
            print(f'w {width}, p {proportion}')
        else:
            height = int(size / proportion)
            print(f'h {height}, p {proportion}')
        print( width, height)
        # восстанавливаем картинку из тензора
        topiller = transforms.ToPILImage()    #)
        output_img = topiller(best_image.squeeze(0))\
                    .resize((width, height))
        # сохраняем результат для потомков
        time_marker = str(int(time.time()))
        output_img.save(path /str(chat_id)/
                        ('out_'
                        + time_marker
                        + '.jpg'))
        # сохраним историю лоссов
        path_to_losses =(path /str(chat_id)/
                         ('losses_'
                        + time_marker
                        + '.pkl'))
        with open(path_to_losses, 'wb') as file:
            pickle.dump(losses, file)
            
        # Очистим cuda после работы
        self.content = None
        self.style = None
        
        
        # очистка памяти GPU
        torch.cuda.empty_cache()
        # возвращаем картинку в формате PIL
        return output_img
     