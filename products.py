from flask import Blueprint, jsonify, request
from models import Product, db
from sqlalchemy import or_

products_bp = Blueprint('products', __name__)

@products_bp.route('/', methods=['GET'])
def get_products():
    category = request.args.get('category')
    brand = request.args.get('brand')
    search = request.args.get('search')
    sort = request.args.get('sort', 'default')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    query = Product.query

    # Фильтрация
    if category:
        query = query.filter_by(category=category)
    if brand:
        query = query.filter_by(brand=brand)
    if search:
        query = query.filter(or_(
            Product.name.ilike(f'%{search}%'),
            Product.description.ilike(f'%{search}%')
        ))

    # Сортировка
    if sort == 'price_asc':
        query = query.order_by(Product.price.asc())
    elif sort == 'price_desc':
        query = query.order_by(Product.price.desc())
    elif sort == 'popular':
        query = query.order_by(Product.rating.desc())
    elif sort == 'newest':
        query = query.order_by(Product.created_at.desc())

    # Пагинация
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    products = pagination.items

    return jsonify({
        'products': [product.to_dict() for product in products],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    })

@products_bp.route('/<int:id>', methods=['GET'])
def get_product(id):
    product = Product.query.get_or_404(id)
    return jsonify(product.to_dict())

@products_bp.route('/categories', methods=['GET'])
def get_categories():
    categories = db.session.query(Product.category).distinct().all()
    return jsonify([category[0] for category in categories])

@products_bp.route('/brands', methods=['GET'])
def get_brands():
    brands = db.session.query(Product.brand).distinct().all()
    return jsonify([brand[0] for brand in brands])