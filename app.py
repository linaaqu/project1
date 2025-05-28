from flask import Flask, render_template, request, redirect, url_for, flash
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Конфигурация для загрузки изображений
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# Проверка расширения файла
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Главная страница
@app.route('/')
def index():
    return render_template('main.html')
# Маршруты для категорий
@app.route('/phone')
def phone():
    return render_template('phone.html')

@app.route('/laptops')
def laptops():
    return render_template('laptops.html')

@app.route('/tv')
def tv():
    return render_template('tv.html')

@app.route('/dom')
def dom():
    return render_template('dom.html')

@app.route('/comp')
def comp():
    return render_template('comp.html')

if __name__ == '__main__':
    app.run(debug=True)


# Загрузка изображений
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)

    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        flash('File successfully uploaded')
        return redirect(url_for('index'))

    return redirect(request.url)


# API для товаров (пример)
@app.route('/api/products')
def get_products():
    products = [
        {
            "id": 1,
            "name": "iPhone 16 256GB",
            "price": 99990,
            "old_price": 129990,
            "image": "uploads/iphone16.jpg",
            "rating": 4.5,
            "reviews_count": 42
        },
        # Добавьте другие товары
    ]
    return {"products": products}


if __name__ == '__main__':
    # Создаем папку для загрузок, если её нет
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True)