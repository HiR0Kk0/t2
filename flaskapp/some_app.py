print("Hello world")
from flask import Flask
app = Flask(__name__)
#декоратор для вывода страницы по умолчанию
@app.route("/")
def hello():
    return " <html><head></head> <body> Hello World! </body></html>"
from flask import render_template
#наша новая функция сайта
# модули работы с формами и полями в формах
from flask_wtf import FlaskForm,RecaptchaField
from wtforms import FloatField, SubmitField
# модули валидации полей формы
from wtforms.validators import DataRequired, ValidationError
from wtforms.validators import AnyOf
from flask_wtf.file import FileField, FileAllowed, FileRequired
# используем csrf токен, можете генерировать его сами
SECRET_KEY = 'secret'
app.config['SECRET_KEY'] = SECRET_KEY
# используем капчу и полученные секретные ключи с сайта google
app.config['RECAPTCHA_USE_SSL'] = False
app.config['RECAPTCHA_PUBLIC_KEY'] = '6LcS2P0cAAAAABJgLi8rv8IRyoA3XY64d7z5xvD7'
app.config['RECAPTCHA_PRIVATE_KEY'] = '6LcS2P0cAAAAAIUtQWQdUB39x6D-Dcn7LZaxHFCM'
app.config['RECAPTCHA_OPTIONS'] = {'theme': 'white'}
# обязательно добавить для работы со стандартными шаблонами
from flask_bootstrap import Bootstrap
bootstrap = Bootstrap(app)
# создаем форму для загрузки файла

def my_check(form, field):
    if not (field.data >0 and field.data <= 100):
        raise ValidationError('Failed!!! Write from 1 to 100')

class NetForm(FlaskForm):
# поле для введения строки, валидируется наличием данных
# валидатор проверяет введение данных после нажатия кнопки submit
# и указывает пользователю ввести данные если они не введены
# или неверны
    # поле загрузки файла
    # здесь валидатор укажет ввести правильные файлы
    upload = FileField('Load image', validators=[FileRequired(),FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    # поле формы с capture
    recaptcha = RecaptchaField()
    degree = FloatField('Percentage size', validators=[DataRequired(),my_check])

    #кнопка submit, для пользователя отображена как send
    submit = SubmitField('send')
    # функция обработки запросов на адрес 127.0.0.1:5000/net
    # модуль проверки и преобразование имени файла
    # для устранения в имени символов типа / и т.д.
from werkzeug.utils import secure_filename
import os
import numpy as np
from PIL import Image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import scipy.ndimage.interpolation as interp
import seaborn as sns
import math
## функция для оброботки изображения
def draw(filename,degree):
##открываем изображение
    print(filename)
    img= Image.open(filename)
    height = 224
    width = 224
    img= np.array(img.resize((height,width)))/255.0
    ##делаем график
    from skimage import io
    _ = plt.hist(img.ravel(), bins = 256, color = 'orange', )
    _ = plt.hist(img[:, :, 0].ravel(), bins = 256, color = 'Red', alpha = 0.5)
    _ = plt.hist(img[:, :, 1].ravel(), bins = 256, color = 'Green', alpha = 0.5)
    _ = plt.hist(img[:, :, 2].ravel(), bins = 256, color = 'Blue', alpha = 0.5)
    _ = plt.xlabel('Intensity Value')
    _ = plt.ylabel('Count')
    _ = plt.legend(['Total', 'Red_Channel', 'Green_Channel', 'Blue_Channel'])

    gr_path = "./static/newgr.png"
    plt.savefig(gr_path)
    plt.close()

    ################
    img2 = np.array(img)
    k=0
    dlina=round(math.sqrt(((height*width)/100)*degree))
    for j in range(0,height+dlina,dlina*2):
      for i in range (dlina,width+dlina,dlina*2):
        img2[j:j+dlina,k:i]=[0,0,0]
        k=k+dlina*2
      k=0
    k=dlina
    for j in range(dlina,height+dlina,dlina*2):
      for i in range (dlina*2,width+dlina,dlina*2):
        img2[j:j+dlina,k:i]=[0,0,0]
        k=k+dlina*2
      k=dlina
    ##делаем второй график
    from skimage import io
    _ = plt.hist(img2.ravel(), bins = 256, color = 'orange', )
    _ = plt.hist(img2[:, :, 0].ravel(), bins = 256, color = 'Red', alpha = 0.5)

    _ = plt.hist(img2[:, :, 1].ravel(), bins = 256, color = 'Green', alpha = 0.5)
    _ = plt.hist(img2[:, :, 2].ravel(), bins = 256, color = 'Blue', alpha = 0.5)
    _ = plt.xlabel('Intensity Value')
    _ = plt.ylabel('Count')
    _ = plt.legend(['Total', 'Red_Channel', 'Green_Channel', 'Blue_Channel'])
    img2 = Image.fromarray((img2 * 255).astype(np.uint8))
    new_path = "./static/new.png"
    img = Image.fromarray((img * 255).astype(np.uint8))
    old_path = "./static/old.png"
    img.save(old_path)
    img2.save(new_path)


    gr_path2 = "./static/newgr2.png"
    plt.savefig(gr_path2)
    plt.close()

    return new_path, gr_path, old_path, gr_path2
    # метод обработки запроса GET и POST от клиента
@app.route("/net",methods=['GET', 'POST'])
def net():
    # создаем объект формы
    form = NetForm(meta={'csrf': False})
    # обнуляем переменные передаваемые в форму
    filename=None
    newfilename=None
    grname=None
    grname2=None
    oldimgname=None
    # проверяем нажатие сабмит и валидацию введенных данных
    if form.validate_on_submit():
    # файлы с изображениями читаются из каталога static
        filename = os.path.join('./static', secure_filename(form.upload.data.filename))
      #  sz=form.size.data
        degree=form.degree.data
        form.upload.data.save(filename)
        newfilename, grname, grname2, oldimgname = draw(filename,degree)
    return render_template('net.html',form=form,image_name=newfilename,gr_name=grname,gr_name2= grname2, old_img=oldimgname)
if __name__ == "__main__":
    app.run(host='127.0.0.1',port=5000)
