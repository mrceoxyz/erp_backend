from products.models import Product, StockAuditLog
from orders.models import OrderHistory

def adjust_stock_for_order(order, action='create', user=None):
    '''
    Adjust product stock when order is created, updated, or cancelled
    action: 'create', 'update', 'cancel'
    '''
    for item in order.items.all():
        product = item.product
        previous_stock = product.stock_quantity
        
        if action == 'create':
            # Decrease stock when order is created
            product.stock_quantity -= item.quantity
            change = -item.quantity
            audit_action = 'order_created'
            
        elif action == 'cancel':
            # Increase stock when order is cancelled (restock)
            product.stock_quantity += item.quantity
            change = item.quantity
            audit_action = 'order_cancelled'
            
        product.save()
        
        # Create audit log
        StockAuditLog.objects.create(
            product=product,
            action_type=audit_action,
            quantity_change=change,
            previous_stock=previous_stock,
            new_stock=product.stock_quantity,
            reference_order=order,
            reference_number=order.order_number,
            notes=f"Order {order.order_number} {action}d",
            created_by=user
        )

def update_order_items_with_diff(order, new_items_data, user=None):
    '''
    Update order items with diff-based approach
    Only changes what's different
    '''
    current_items = {item.product.id: item for item in order.items.all()}
    new_items = {item['product']: item for item in new_items_data}
    changes = []
    
    # Check for removed items (restock)
    for product_id, item in current_items.items():
        if product_id not in new_items:
            # Item removed, restock
            product = item.product
            previous_stock = product.stock_quantity
            product.stock_quantity += item.quantity
            product.save()
            
            StockAuditLog.objects.create(
                product=product,
                action_type='order_updated',
                quantity_change=item.quantity,
                previous_stock=previous_stock,
                new_stock=product.stock_quantity,
                reference_order=order,
                reference_number=order.order_number,
                notes=f"Item removed from order {order.order_number}",
                created_by=user
            )
            
            changes.append(f"Removed {item.product.name} (x{item.quantity})")
            item.delete()
    
    # Check for new or updated items
    for product_id, new_item_data in new_items.items():
        product = Product.objects.get(id=product_id)
        new_quantity = new_item_data['quantity']
        
        if product_id in current_items:
            # Item exists, check for quantity change
            item = current_items[product_id]
            old_quantity = item.quantity
            
            if old_quantity != new_quantity:
                quantity_diff = new_quantity - old_quantity
                previous_stock = product.stock_quantity
                product.stock_quantity -= quantity_diff
                product.save()
                
                StockAuditLog.objects.create(
                    product=product,
                    action_type='order_updated',
                    quantity_change=-quantity_diff,
                    previous_stock=previous_stock,
                    new_stock=product.stock_quantity,
                    reference_order=order,
                    reference_number=order.order_number,
                    notes=f"Quantity changed from {old_quantity} to {new_quantity}",
                    created_by=user
                )
                
                item.quantity = new_quantity
                item.subtotal = item.unit_price * new_quantity
                item.save()
                changes.append(f"Updated {product.name}: {old_quantity} → {new_quantity}")
        else:
            # New item, decrease stock
            previous_stock = product.stock_quantity
            product.stock_quantity -= new_quantity
            product.save()
            
            StockAuditLog.objects.create(
                product=product,
                action_type='order_updated',
                quantity_change=-new_quantity,
                previous_stock=previous_stock,
                new_stock=product.stock_quantity,
                reference_order=order,
                reference_number=order.order_number,
                notes=f"Item added to order {order.order_number}",
                created_by=user
            )
            
            order.items.create(
                product=product,
                quantity=new_quantity,
                unit_price=new_item_data['unit_price'],
                subtotal=new_item_data['subtotal']
            )
            changes.append(f"Added {product.name} (x{new_quantity})")
    
    # Record order history
    if changes:
        OrderHistory.objects.create(
            order=order,
            action='items_updated',
            changes={'modifications': changes},
            performed_by=user,
            notes=f"Order items modified: {', '.join(changes)}"
        )
    
    return changes