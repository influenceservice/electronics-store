from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///products.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'  # Для сессий
db = SQLAlchemy(app)

# Категории товаров
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    products = db.relationship('Product', backref='category', lazy=True)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200))
    image_url = db.Column(db.String(300))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)

@app.route('/')
def index():
    categories = Category.query.all()
    selected_cat = request.args.get('category', type=int)
    if selected_cat:
        products = Product.query.filter_by(category_id=selected_cat).all()
    else:
        products = Product.query.all()
    return render_template('index.html', products=products, categories=categories, selected_cat=selected_cat)

@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    cart = session.get('cart', {})
    cart[str(product_id)] = cart.get(str(product_id), 0) + 1
    session['cart'] = cart
    flash('Товар добавлен в корзину')
    return redirect(request.referrer or url_for('index'))

@app.route('/cart')
def cart():
    cart = session.get('cart', {})
    products = []
    total = 0
    for product_id, quantity in cart.items():
        product = Product.query.get(int(product_id))
        if product:
            products.append({'product': product, 'quantity': quantity})
            total += product.price * quantity
    return render_template('cart.html', products=products, total=total)

@app.route('/remove_from_cart/<int:product_id>')
def remove_from_cart(product_id):
    cart = session.get('cart', {})
    cart.pop(str(product_id), None)
    session['cart'] = cart
    flash('Товар удалён из корзины')
    return redirect(url_for('cart'))

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    cart = session.get('cart', {})
    if not cart:
        flash('Ваша корзина пуста')
        return redirect(url_for('index'))
    if request.method == 'POST':
        # Просто выводим данные из формы — можно расширить сохранение заказа в базу и т.п.
        name = request.form['name']
        email = request.form['email']
        address = request.form['address']
        flash(f'Спасибо за заказ, {name}! Мы свяжемся с вами по {email}.')
        session.pop('cart')  # Очищаем корзину после заказа
        return redirect(url_for('index'))
    return render_template('checkout.html')
    

@app.route('/search')
def search():
    query = request.args.get('q', '')
    results = []
    if query:
        results = Product.query.filter(Product.name.ilike(f'%{query}%')).all()
    return render_template('search_results.html', query=query, results=results)

if __name__ == '__main__':
    with app.app_context():
        db.drop_all()
        db.create_all()

        # Создаём категории
        cat_gpu = Category(name="Видеокарты")
        cat_cpu = Category(name="Процессоры")
        cat_motherboard = Category(name="Материнские платы")
        db.session.add_all([cat_gpu, cat_cpu, cat_motherboard])
        db.session.commit()

        # Добавляем товары
        products = [
            Product(name="NVIDIA GeForce RTX 4090", price=100000,
                    description="Флагманская видеокарта с 24 ГБ памяти",
                    image_url="images/rtx4090.jpg",
                    category_id=cat_gpu.id),
            Product(name="AMD Radeon RX 7900 XTX", price=1099.99,
                        description="Высокопроизводительная видеокарта от AMD",
                        image_url="images/radeon.jpg",
                        category_id=cat_gpu.id),
                Product(name="Intel Core i9-13900K", price=599.99,
                        description="24-поточный процессор 13-го поколения",
                        image_url="images/intel_i9.jpg",
                        category_id=cat_cpu.id),
                Product(name="AMD Ryzen 9 7950X", price=699.99,
                        description="Процессор с 16 ядрами на архитектуре Zen 4",
                        image_url="images/amd_ryzen_9.jpg",
                        category_id=cat_cpu.id),
                Product(name="MSI MAG B650 Tomahawk", price=229.99,
                        description="Материнская плата для AMD AM5",
                        image_url="images/msi_mag.jpg",
                        category_id=cat_motherboard.id),
                Product(name="ASUS ROG Maximus Z790 Hero", price=599.99,
                        description="Материнская плата для Intel LGA1700",
                        image_url="images/asus_rog.jpg",
                        category_id=cat_motherboard.id),
        ]
        db.session.add_all(products)
        db.session.commit()

    app.run(debug=True)
