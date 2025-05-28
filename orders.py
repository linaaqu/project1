from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from models import Order, OrderItem, CartItem, db
from datetime import datetime

orders_bp = Blueprint('orders', __name__)

@orders_bp.route('/', methods=['GET'])
@login_required
def get_orders():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return jsonify([order.to_dict() for order in orders])

@orders_bp.route('/<int:order_id>', methods=['GET'])
@login_required
def get_order(order_id):
    order = Order.query.filter_by(
        id=order_id,
        user_id=current_user.id
    ).first_or_404()
    
    return jsonify(order.to_dict(with_items=True))

@orders_bp.route('/create', methods=['POST'])
@login_required
def create_order():
    # Получаем товары из корзины пользователя
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    
    if not cart_items:
        return jsonify({'error': 'Cart is empty'}), 400
    
    # Создаем заказ
    order = Order(user_id=current_user.id, total=0, status='processing')
    db.session.add(order)
    db.session.flush()  # Получаем ID заказа
    
    total = 0
    items = []
    
    for cart_item in cart_items:
        product = cart_item.product
        quantity = cart_item.quantity
        subtotal = product.price * quantity
        
        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=quantity,
            price=product.price
        )
        db.session.add(order_item)
        
        items.append({
            'product_id': product.id,
            'name': product.name,
            'quantity': quantity,
            'price': product.price,
            'subtotal': subtotal
        })
        
        total += subtotal
    
    # Обновляем общую сумму заказа
    order.total = total
    db.session.commit()
    
    # Очищаем корзину
    CartItem.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()
    
    return jsonify({
        'message': 'Order created successfully',
        'order_id': order.id,
        'total': total,
        'items': items
    }), 201