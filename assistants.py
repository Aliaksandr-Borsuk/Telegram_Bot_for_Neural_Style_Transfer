# модель для переноса стиля

import torch
import torch.nn as nn
import torch.nn.functional as F


# класс потерь по контенту
class ContentMSELoss(nn.Module):
    def __init__(self):
        super(ContentMSELoss, self).__init__()
        self.target= None

    # делаем detach ибо обучать будем не их а входное изображение
    def set_target(self, target):
        self.target = target.detach()
    # перевод на device
    def to_device(self, device):
        if self.target is not None:
            self.target.to(device)
#        self.to(device)

    def forward(self, input):
        loss = F.mse_loss(input, self.target)
        return loss
    
# потери по стилю
# Далее объявляются классы матрицы Грама и функции потерь для матрицы Грама
class GramMatrix(nn.Module):
    def forward(self, x):
        a, b, c, d = x.size()
        # получаем вектора в количестве feature map в батче
        features = x.view(a * b, c * d)  # resise F_XL into \hat F_XL
        G = torch.mm(features, features.t())  # compute the gram product,
        return G.div(a*b*c*d)
    
class StyleMSELoss(nn.Module):
    def __init__(self):
        super(StyleMSELoss, self).__init__()
        self.target= None
    def set_target(self, target):
        self.target = (GramMatrix()(target)).detach()
    # перевод на device
    def to_device(self, device):
        if self.target is not None :
            self.target.to(device)
#        self.to(device)
    def forward(self, x):
        loss = F.mse_loss(GramMatrix()(x), self.target)
        return loss

# создаём класс нормализации входного изображения
class Normalization_for_VGG(nn.Module):
    def __init__(self):
        super(Normalization_for_VGG, self).__init__()
        self.mean = torch.tensor([0.485, 0.456, 0.406]).view(-1, 1, 1)
        self.std = torch.tensor([0.229, 0.224, 0.225]).view(-1, 1, 1)
        
    def forward(self, img):
        # normalize img
        return (img - self.mean) / self.std 
    # это чтобы перносить экземпляр класса с устройства на устройство
    def to_device(self, device):
        self.mean = self.mean.to(device)
        self.std = self.std.to(device)
#        self.to(device)

# класс самой модели для переноса стиля
class Style_Transfer_01(nn.Module):
    '''
    модель основана на первых слоях VGG19
    перед переносом стиля требует инициализации
    картинкаами style и content
    '''
    def __init__(self, pool='max'):
        super(Style_Transfer_01, self).__init__()
        
        # модуль который нормализует входную картинку
        self.norm = Normalization_for_VGG()
        # считает style_loss по матрице грамма 
        # и хранит в себе  матрицу Грамма по стилю
        self.style_loss_1 = StyleMSELoss()
        self.style_loss_2 = StyleMSELoss()
        self.style_loss_3 = StyleMSELoss()
        self.style_loss_4 = StyleMSELoss()
        self.style_loss_5 = StyleMSELoss()
        
        
        # считает contentloss
        self.content_loss = ContentMSELoss()
        
        self.conv_1 = nn.Conv2d(3, 64, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1))
        self.conv_2 = nn.Conv2d(64, 64, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1))
        self.conv_3 = nn.Conv2d(64, 128, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1))
        self.conv_4 = nn.Conv2d(128, 128,  kernel_size=(3, 3), stride=(1, 1), padding=(1, 1))
        self.conv_5 = nn.Conv2d(128, 256,  kernel_size=(3, 3), stride=(1, 1), padding=(1, 1))
       
        self.pool1 = nn.MaxPool2d(kernel_size=2, stride=2, padding=0, dilation=1, ceil_mode=False)
        self.pool2 = nn.MaxPool2d(kernel_size=2, stride=2, padding=0, dilation=1, ceil_mode=False)
    
    # функция перемещения модели на нужный device
    def to_device(self, device):
        self.norm.to_device(device)
        self.style_loss_1.to_device(device)
        self.style_loss_2.to_device(device)
        self.style_loss_3.to_device(device)
        self.style_loss_4.to_device(device)
        self.style_loss_5.to_device(device)
        self.content_loss.to_device(device)     
        self.to(device)

            
    def forward(self, x, fit_style = False, fit_content = False):
        # выходной словарик лоссов
        out = {'style_loss':[], 'content_loss':[]}
        x = self.norm(x)
        x = self.conv_1(x)
        if fit_style:
            self.style_loss_1.set_target(x)
            x = self.conv_2(F.relu(x))
            self.style_loss_2.set_target(x)
            x = self.conv_3(self.pool1(F.relu(x)))
            self.style_loss_3.set_target(x)
            x = self.conv_4(F.relu(x))
            self.style_loss_4.set_target(x)
            x = self.conv_5(self.pool2(F.relu(x)))
            self.style_loss_5.set_target(x)
        elif fit_content:
            x = self.conv_2(F.relu(x))
            x = self.conv_3(self.pool1(F.relu(x)))
            x = self.conv_4(F.relu(x))
            self.content_loss.set_target(x)
        else:
            out['style_loss'].append (self.style_loss_1(x))
            x = self.conv_2(F.relu(x))
            out['style_loss'].append (self.style_loss_2(x))
            x = self.conv_3(self.pool1(F.relu(x)))
            out['style_loss'].append (self.style_loss_3(x))
            x = self.conv_4(F.relu(x))
            out['style_loss'].append (self.style_loss_4(x))
            out['content_loss'].append(self.content_loss(x))
            x = self.conv_5(self.pool2(F.relu(x)))
            out['style_loss'].append ( self.style_loss_5(x))
            
            return out
