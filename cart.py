from flask import Blueprint, jsonify, request
from models import CartItem, Product, db
from flask_login import login_required, current_user

cart_bp = Blueprint('cart', __name__)

@cart_bp.route('/', methods=['GET'])
@login_required
def get_cart():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    total = 0
    items = []
    
    for item in cart_items:
        product = Product.query.get(item.product_id)
        items.append({
            'id': item.id,
            'product': product.to_dict(),
            'quantity': item.quantity,
            'subtotal': product.price * item.quantity
        })
        total += product.price * item.quantity
    
    return jsonify({
        'items': items,
        'total': total,
        'count': len(items)
    })

@cart_bp.route('/add', methods=['POST'])
@login_required
def add_to_cart():
    product_id = request.json.get('product_id')
    quantity = request.json.get('quantity', 1)
    
    product = Product.query.get_or_404(product_id)
    
    # Проверяем, есть ли уже такой товар в корзине
    cart_item = CartItem.query.filter_by(
        user_id=current_user.id,
        product_id=product_id
    ).first()
    
    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = CartItem(
            user_id=current_user.id,
            product_id=product_id,
            quantity=quantity
        )
        db.session.add(cart_item)
    
    db.session.commit()
    
    return jsonify({'message': 'Product added to cart'}), 201

@cart_bp.route('/update/<int:item_id>', methods=['PUT'])
@login_required
def update_cart_item(item_id):
    cart_item = CartItem.query.filter_by(
        id=item_id,
        user_id=current_user.id
    ).first_or_404()
    
    quantity = request.json.get('quantity')
    if quantity < 1:
        return jsonify({'error': 'Quantity must be at least 1'}), 400
    
    cart_item.quantity = quantity
    db.session.commit()
    
    return jsonify({'message': 'Cart item updated'})

@cart_bp.route('/remove/<int:item_id>', methods=['DELETE'])
@login_required
def remove_cart_item(item_id):
    cart_item = CartItem.query.filter_by(
        id=item_id,
        user_id=current_user.id
    ).first_or_404()
    
    db.session.delete(cart_item)
    db.session.commit()
    
    return jsonify({'message': 'Item removed from cart'})