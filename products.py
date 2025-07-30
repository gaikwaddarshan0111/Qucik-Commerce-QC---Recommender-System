# products.py (or directly paste into your main script)
import pandas as pd

products_data = {
    'product_id': [101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115],
    'name': [
        'Fresh Milk (1L)', 'Whole Wheat Bread', 'Organic Eggs (6-pack)', 'Butter (250g)',
        'Chicken Breast (500g)', 'Basmati Rice (1kg)', 'Tomato Ketchup (500g)',
        'Diet Cola (2L)', 'Potato Chips (Large)', 'Dish Soap (Lemon)',
        'Fresh Paneer (200g)', 'Ghee (500ml)', 'Curd (400g)', 'Mineral Water (1L)',
        'Instant Noodles (Pack)'
    ],
    'category': [
        'Dairy & Eggs', 'Bakery', 'Dairy & Eggs', 'Dairy & Eggs',
        'Meat & Seafood', 'Staples', 'Sauces & Spreads',
        'Beverages', 'Snacks', 'Home Essentials',
        'Dairy & Eggs', 'Dairy & Eggs', 'Dairy & Eggs', 'Beverages',
        'Ready Meals'
    ],
    'description': [
        'Pure, pasteurized cow milk, sourced locally from trusted farms.',
        'Soft and nutritious bread, perfect for sandwiches and toast.',
        'Farm-fresh, large organic eggs, rich in protein.',
        'Creamy, unsalted butter for cooking and spreading.',
        'Boneless, skinless chicken breast, ideal for grilling and curries.',
        'Premium quality long-grain basmati rice for biryani and pulao.',
        'Classic tomato ketchup, great with snacks and meals.',
        'Refreshing, sugar-free cola, perfect for a guilt-free drink.',
        'Crispy, salted potato chips, the ultimate snack.',
        'Powerful dishwashing liquid with a refreshing lemon scent.',
        'Soft, fresh cottage cheese, perfect for Indian dishes.',
        'Traditional Indian clarified butter, aromatic and healthy.',
        'Thick and creamy yogurt, great for raita or as a side.',
        'Pure, filtered mineral water for daily hydration.',
        'Quick and easy to prepare noodles, a popular snack.'
    ]
}

products_df = pd.DataFrame(products_data)
products_df.to_csv('products.csv', index=False)
print("Product.csv file sucessfully created .......!")


# Create user_interactions.csv:

import numpy as np 

#simulate more realistic user interactions
np.random.seed(42)
num_users = 50
num_interactions = 1000

user_ids = np.random.randint(1, num_users + 1, num_interactions)
products_ids = np.random.choice(products_data['product_id'], size=num_interactions,p=np.random.dirichlet(np.ones(len(products_df)), size=1)[0]) # Simulate some products being more popular


# Simulate different interaction types (view, add_to_cart, purchase)
interaction_types = np.random.choice(['view', 'add_to_cart', 'purchase'], size=num_interactions, p=[0.6, 0.2, 0.2])


# Simulate timestamps (last 30 days)
end_time = pd.Timestamp.now()
start_time = end_time - pd.Timedelta(days=30)
timestamps = pd.to_datetime(np.random.uniform(start_time.timestamp(), end_time.timestamp(), num_interactions), unit='s')

user_interactions_data = {
    'user_id': user_ids,
    'product_id': products_ids,
    'interaction_type': interaction_types,
    'timestamp': timestamps
}
user_interactions_df = pd.DataFrame(user_interactions_data)
user_interactions_df.to_csv('user_interactions.csv', index=False)
print("user_interactions.csv created.")