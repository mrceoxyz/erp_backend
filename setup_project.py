import os
# pyrefly: ignore [missing-import]
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'solar_erp_backend.settings')
django.setup()

# pyrefly: ignore [missing-import]
from django.contrib.auth import get_user_model
from products.models import Category, Product
from customers.models import Customer
from suppliers.models import Supplier
from datetime import datetime, timedelta

User = get_user_model()

def setup_users():
    print("Creating users...")
    
    # Create admin user
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            username='admin',
            email='admin@solarerp.com',
            password='admin123',
            first_name='Admin',
            last_name='User',
            role='admin'
        )
        print("✓ Admin user created (username: admin, password: admin123)")
    
    # Create manager
    if not User.objects.filter(username='manager').exists():
        User.objects.create_user(
            username='manager',
            email='manager@solarerp.com',
            password='manager123',
            first_name='Manager',
            last_name='User',
            role='manager'
        )
        print("✓ Manager user created")
    
    # Create sales person
    if not User.objects.filter(username='sales').exists():
        User.objects.create_user(
            username='sales',
            email='sales@solarerp.com',
            password='sales123',
            first_name='Sales',
            last_name='Person',
            role='sales'
        )
        print("✓ Sales user created")

def setup_categories_and_products():
    print("\nCreating categories and products...")
    
    # Categories
    categories_data = [
        {'name': 'Inverters', 'description': 'Power inverters for solar systems'},
        {'name': 'Batteries', 'description': 'Deep cycle batteries for energy storage'},
        {'name': 'Solar Panels', 'description': 'Photovoltaic solar panels'},
        {'name': 'Charge Controllers', 'description': 'Solar charge controllers'},
        {'name': 'Accessories', 'description': 'Cables, connectors, and accessories'},
    ]
    
    categories = {}
    for cat_data in categories_data:
        cat, created = Category.objects.get_or_create(
            name=cat_data['name'],
            defaults={'description': cat_data['description']}
        )
        categories[cat.name] = cat
        if created:
            print(f"✓ Category created: {cat.name}")
    
    # Products
    products_data = [
        # Inverters
        {'name': '1.5KVA Inverter', 'category': 'Inverters', 'price': 85000, 'stock': 30, 'sku': 'INV-1.5KVA-001'},
        {'name': '3.5KVA Inverter', 'category': 'Inverters', 'price': 125000, 'stock': 20, 'sku': 'INV-3.5KVA-001'},
        {'name': '5KVA Inverter', 'category': 'Inverters', 'price': 185000, 'stock': 15, 'sku': 'INV-5KVA-001'},
        {'name': '7.5KVA Inverter', 'category': 'Inverters', 'price': 275000, 'stock': 10, 'sku': 'INV-7.5KVA-001'},
        {'name': '10KVA Inverter', 'category': 'Inverters', 'price': 385000, 'stock': 8, 'sku': 'INV-10KVA-001'},
        
        # Batteries
        {'name': '100Ah Battery', 'category': 'Batteries', 'price': 75000, 'stock': 35, 'sku': 'BAT-100AH-001'},
        {'name': '150Ah Battery', 'category': 'Batteries', 'price': 95000, 'stock': 28, 'sku': 'BAT-150AH-001'},
        {'name': '200Ah Battery', 'category': 'Batteries', 'price': 135000, 'stock': 25, 'sku': 'BAT-200AH-001'},
        {'name': '220Ah Battery', 'category': 'Batteries', 'price': 155000, 'stock': 20, 'sku': 'BAT-220AH-001'},
        
        # Solar Panels
        {'name': '150W Solar Panel', 'category': 'Solar Panels', 'price': 45000, 'stock': 50, 'sku': 'SOL-150W-001'},
        {'name': '250W Solar Panel', 'category': 'Solar Panels', 'price': 65000, 'stock': 45, 'sku': 'SOL-250W-001'},
        {'name': '350W Solar Panel', 'category': 'Solar Panels', 'price': 85000, 'stock': 40, 'sku': 'SOL-350W-001'},
        {'name': '450W Solar Panel', 'category': 'Solar Panels', 'price': 105000, 'stock': 30, 'sku': 'SOL-450W-001'},
        
        # Charge Controllers
        {'name': '30A MPPT Controller', 'category': 'Charge Controllers', 'price': 35000, 'stock': 25, 'sku': 'CHG-30A-001'},
        {'name': '50A MPPT Controller', 'category': 'Charge Controllers', 'price': 55000, 'stock': 20, 'sku': 'CHG-50A-001'},
        {'name': '60A MPPT Controller', 'category': 'Charge Controllers', 'price': 75000, 'stock': 15, 'sku': 'CHG-60A-001'},
        
        # Accessories
        {'name': 'MC4 Connectors (Pair)', 'category': 'Accessories', 'price': 2500, 'stock': 100, 'sku': 'ACC-MC4-001'},
        {'name': '10mm Solar Cable (Per Meter)', 'category': 'Accessories', 'price': 850, 'stock': 500, 'sku': 'ACC-CBL-001'},
        {'name': 'Battery Terminal', 'category': 'Accessories', 'price': 1500, 'stock': 80, 'sku': 'ACC-TERM-001'},
        {'name': 'Panel Mounting Kit', 'category': 'Accessories', 'price': 15000, 'stock': 30, 'sku': 'ACC-MNT-001'},
    ]
    
    for prod_data in products_data:
        Product.objects.get_or_create(
            sku=prod_data['sku'],
            defaults={
                'name': prod_data['name'],
                'category': categories[prod_data['category']],
                'description': f"{prod_data['name']} - High quality product",
                'price': prod_data['price'],
                'stock_quantity': prod_data['stock'],
                'reorder_level': 10
            }
        )
    print(f"✓ {len(products_data)} products created")

def setup_customers():
    print("\nCreating sample customers...")
    
    customers_data = [
        {
            'first_name': 'John', 'last_name': 'Doe',
            'email': 'john.doe@example.com', 'phone': '+234 803 123 4567',
            'address': '123 Lagos Street', 'city': 'Lagos', 'state': 'Lagos'
        },
        {
            'first_name': 'Jane', 'last_name': 'Smith',
            'email': 'jane.smith@example.com', 'phone': '+234 805 234 5678',
            'address': '456 Abuja Avenue', 'city': 'Abuja', 'state': 'FCT'
        },
        {
            'first_name': 'Mike', 'last_name': 'Johnson',
            'email': 'mike.j@example.com', 'phone': '+234 807 345 6789',
            'address': '789 Port Harcourt Road', 'city': 'Port Harcourt', 'state': 'Rivers'
        },
        {
            'first_name': 'Sarah', 'last_name': 'Williams',
            'email': 'sarah.w@example.com', 'phone': '+234 809 456 7890',
            'address': '321 Kano Close', 'city': 'Kano', 'state': 'Kano'
        },
        {
            'first_name': 'David', 'last_name': 'Brown',
            'email': 'david.b@example.com', 'phone': '+234 810 567 8901',
            'address': '654 Ibadan Street', 'city': 'Ibadan', 'state': 'Oyo'
        },
    ]
    
    for cust_data in customers_data:
        Customer.objects.get_or_create(
            email=cust_data['email'],
            defaults=cust_data
        )
    print(f"✓ {len(customers_data)} customers created")

def setup_suppliers():
    print("\nCreating sample suppliers...")
    
    suppliers_data = [
        {
            'name': 'Ahmed Ibrahim',
            'company_name': 'Solar Tech Nigeria Ltd',
            'email': 'info@solartech.ng',
            'phone': '+234 803 111 2222',
            'address': '15 Industrial Estate',
            'city': 'Lagos',
            'state': 'Lagos',
            'tax_id': 'STN-12345'
        },
        {
            'name': 'Chen Wei',
            'company_name': 'PowerMax Solutions',
            'email': 'sales@powermax.com',
            'phone': '+234 805 333 4444',
            'address': '27 Business District',
            'city': 'Abuja',
            'state': 'FCT',
            'tax_id': 'PMS-67890'
        },
        {
            'name': 'Emeka Okafor',
            'company_name': 'Green Energy Suppliers',
            'email': 'contact@greenenergy.ng',
            'phone': '+234 807 555 6666',
            'address': '42 Trade Center',
            'city': 'Port Harcourt',
            'state': 'Rivers',
            'tax_id': 'GES-24680'
        },
    ]
    
    for supp_data in suppliers_data:
        Supplier.objects.get_or_create(
            email=supp_data['email'],
            defaults=supp_data
        )
    print(f"✓ {len(suppliers_data)} suppliers created")

def main():
    print("=" * 60)
    print("Solar Shop ERP - Initial Setup")
    print("=" * 60)
    
    setup_users()
    setup_categories_and_products()
    setup_customers()
    setup_suppliers()
    
    print("\n" + "=" * 60)
    print("Setup completed successfully! 🎉")
    print("=" * 60)
    print("\nYou can now login with:")
    print("  Username: admin")
    print("  Password: admin123")
    print("\nOr access the admin panel at: http://localhost:8000/admin/")
    print("API Documentation: http://localhost:8000/api/")
    print("=" * 60)

if __name__ == '__main__':
    main()