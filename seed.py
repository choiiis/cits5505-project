from app import app, db
from app.models import (
    User,
    Restaurant,
    MenuItem,
    OpeningHour,
    Review,
    ReviewPhoto,
    BookmarkCollection,
    Bookmark,
    CollectionSubscription,
)
from werkzeug.security import generate_password_hash

import random
from datetime import datetime, timedelta

random.seed(42)

DEFAULT_PASSWORD_HASH = generate_password_hash("password")

USER_STATUS_PATTERN = [
    "active",
    "active",
    "active",
    "active",
    "suspended",
]

RESTAURANT_STATUS_PATTERN = [
    "approved",
    "approved",
    "approved",
    "approved",
    "approved",
    "pending",
    "reported",
]

REVIEW_STATUS_PATTERN = [
    "active",
    "active",
    "active",
    "active",
    "reported",
    "hidden",
]

PROFILE_IMAGES = [
    "https://randomuser.me/api/portraits/women/44.jpg",
    "https://randomuser.me/api/portraits/men/32.jpg",
    "https://randomuser.me/api/portraits/women/68.jpg",
    "https://randomuser.me/api/portraits/men/45.jpg",
    "https://randomuser.me/api/portraits/women/12.jpg",
    "https://randomuser.me/api/portraits/men/11.jpg",
    "https://randomuser.me/api/portraits/women/22.jpg",
    "https://randomuser.me/api/portraits/men/23.jpg",
]

CATEGORY_IMAGES = {
    "Italian": "https://images.unsplash.com/photo-1513104890138-7c749659a591?auto=format&fit=crop&w=1200&q=80",
    "Cafe": "https://images.unsplash.com/photo-1554118811-1e0d58224f24?auto=format&fit=crop&w=1200&q=80",
    "Korean": "https://images.unsplash.com/photo-1498654896293-37aacf113fd9?auto=format&fit=crop&w=1200&q=80",
    "Japanese": "https://images.unsplash.com/photo-1579871494447-9811cf80d66c?auto=format&fit=crop&w=1200&q=80",
    "Thai": "https://images.unsplash.com/photo-1559847844-5315695dadae?auto=format&fit=crop&w=1200&q=80",
    "Mexican": "https://images.unsplash.com/photo-1565299585323-38174c4a67df?auto=format&fit=crop&w=1200&q=80",
    "Healthy": "https://images.unsplash.com/photo-1540420773420-3366772f4999?auto=format&fit=crop&w=1200&q=80",
    "Fast Food": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?auto=format&fit=crop&w=1200&q=80",
    "Dessert": "https://images.unsplash.com/photo-1551024506-0bccd828d307?auto=format&fit=crop&w=1200&q=80",
    "Indian": "https://images.unsplash.com/photo-1585937421612-70a008356fbe?auto=format&fit=crop&w=1200&q=80",
    "Seafood": "https://images.unsplash.com/photo-1559737558-2f5a35f4523b?auto=format&fit=crop&w=1200&q=80",
    "Modern Australian": "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?auto=format&fit=crop&w=1200&q=80",
}

# Only these 20 restaurants have uploaded restaurant images.
# The other 20 restaurants intentionally keep thumbnail_image/hero_image as None
# so the UI fallback/default image can be tested.
RESTAURANT_IMAGE_OVERRIDES = {
    "Laneway Pizza Co.": "https://images.unsplash.com/photo-1513104890138-7c749659a591?auto=format&fit=crop&w=1200&q=80",
    "Northbridge Coffee Lab": "https://images.unsplash.com/photo-1554118811-1e0d58224f24?auto=format&fit=crop&w=1200&q=80",
    "Seoul Table": "https://images.unsplash.com/photo-1498654896293-37aacf113fd9?auto=format&fit=crop&w=1200&q=80",
    "Burger Corner": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?auto=format&fit=crop&w=1200&q=80",
    "Green Bowl Kitchen": "https://images.unsplash.com/photo-1540420773420-3366772f4999?auto=format&fit=crop&w=1200&q=80",
    "Sakura Sushi House": "https://images.unsplash.com/photo-1579871494447-9811cf80d66c?auto=format&fit=crop&w=1200&q=80",
    "Bangkok Street Eats": "https://images.unsplash.com/photo-1559847844-5315695dadae?auto=format&fit=crop&w=1200&q=80",
    "Taco Verde": "https://images.unsplash.com/photo-1565299585323-38174c4a67df?auto=format&fit=crop&w=1200&q=80",
    "Sweet Crumb Dessert Bar": "https://images.unsplash.com/photo-1551024506-0bccd828d307?auto=format&fit=crop&w=1200&q=80",
    "Curry Leaf Kitchen": "https://images.unsplash.com/photo-1585937421612-70a008356fbe?auto=format&fit=crop&w=1200&q=80",
    "Harbour Fish Grill": "https://images.unsplash.com/photo-1559737558-2f5a35f4523b?auto=format&fit=crop&w=1200&q=80",
    "Banksia Bistro": "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?auto=format&fit=crop&w=1200&q=80",
    "Pasta Piazza": "https://images.unsplash.com/photo-1528137871618-79d2761e3fd5?auto=format&fit=crop&w=1200&q=80",
    "Campus Brew": "https://images.unsplash.com/photo-1509042239860-f550ce710b93?auto=format&fit=crop&w=1200&q=80",
    "Kimchi Garden": "https://images.unsplash.com/photo-1580651315530-69c8e0026377?auto=format&fit=crop&w=1200&q=80",
    "Tokyo Bento Bar": "https://images.unsplash.com/photo-1617196034796-73dfa7b1fd56?auto=format&fit=crop&w=1200&q=80",
    "Siam Corner": "https://images.unsplash.com/photo-1569562211093-4ed0d0758f12?auto=format&fit=crop&w=1200&q=80",
    "El Camino Cantina": "https://images.unsplash.com/photo-1615870216519-2f9fa575fa5c?auto=format&fit=crop&w=1200&q=80",
    "Fit Plate Co.": "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?auto=format&fit=crop&w=1200&q=80",
    "Crispy Burger Works": "https://images.unsplash.com/photo-1550547660-d9450f859349?auto=format&fit=crop&w=1200&q=80",
}

MENU_LIBRARY = {
    "Italian": [
        ("Margherita Pizza", "Tomato, mozzarella, basil", 22.0),
        ("Pepperoni Pizza", "Pepperoni, tomato, mozzarella", 24.0),
        ("Truffle Mushroom Pizza", "Mushroom, truffle oil, mozzarella", 27.0),
        ("Carbonara", "Pasta, egg, pancetta, parmesan", 25.0),
        ("Seafood Linguine", "Linguine, prawns, mussels, tomato", 31.0),
        ("Lasagne", "Beef ragu, pasta sheets, bechamel", 26.0),
        ("Caprese Salad", "Tomato, mozzarella, basil", 16.0),
        ("Garlic Bread", "Toasted bread with garlic butter", 9.0),
        ("Tiramisu", "Coffee, mascarpone, cocoa", 14.0),
        ("Panna Cotta", "Vanilla cream dessert with berry compote", 13.0),
    ],
    "Cafe": [
        ("Flat White", "Espresso with steamed milk", 5.5),
        ("Iced Latte", "Espresso, milk, ice", 6.5),
        ("Cold Brew", "Slow brewed coffee over ice", 6.0),
        ("Avocado Toast", "Sourdough, avocado, feta, chilli", 18.0),
        ("Eggs Benedict", "Poached eggs, hollandaise, sourdough", 22.0),
        ("Granola Bowl", "Yoghurt, fruit, granola, honey", 17.0),
        ("Chicken Panini", "Chicken, pesto, cheese, toasted bread", 19.0),
        ("Mushroom Toast", "Mushrooms, ricotta, herbs", 20.0),
        ("Banana Bread", "Toasted banana bread with butter", 8.0),
        ("Almond Croissant", "Flaky pastry with almond filling", 7.5),
    ],
    "Korean": [
        ("Bibimbap", "Rice bowl with vegetables, beef, egg, gochujang", 21.0),
        ("Kimchi Stew", "Kimchi stew with pork and tofu", 19.0),
        ("Bulgogi", "Marinated beef with rice and sides", 24.0),
        ("Korean Fried Chicken", "Crispy chicken with sweet spicy sauce", 25.0),
        ("Tteokbokki", "Rice cakes in spicy sauce", 17.0),
        ("Japchae", "Glass noodles with vegetables", 18.0),
        ("Soft Tofu Stew", "Spicy tofu soup with egg", 19.0),
        ("Seafood Pancake", "Crispy pancake with seafood and spring onion", 22.0),
        ("Kimchi Fried Rice", "Fried rice with kimchi and egg", 18.0),
        ("Banchan Set", "Assorted Korean side dishes", 10.0),
    ],
    "Japanese": [
        ("Salmon Sushi Set", "Assorted salmon nigiri and rolls", 24.0),
        ("Chicken Katsu Curry", "Crispy chicken with Japanese curry", 21.0),
        ("Tonkotsu Ramen", "Pork broth ramen with chashu", 23.0),
        ("Teriyaki Chicken Don", "Chicken teriyaki rice bowl", 19.0),
        ("Tempura Udon", "Udon noodles with prawn tempura", 22.0),
        ("Gyoza", "Pan-fried pork dumplings", 12.0),
        ("Sashimi Plate", "Fresh assorted sashimi", 32.0),
        ("Miso Soup", "Soybean soup with tofu and seaweed", 5.0),
        ("Edamame", "Steamed soybeans with salt", 7.0),
        ("Matcha Cheesecake", "Creamy matcha dessert", 13.0),
    ],
    "Thai": [
        ("Pad Thai", "Rice noodles, egg, tofu, prawns, peanuts", 21.0),
        ("Green Curry", "Green curry with chicken and vegetables", 22.0),
        ("Massaman Beef Curry", "Slow cooked beef curry with potato", 24.0),
        ("Tom Yum Soup", "Hot and sour soup with prawns", 19.0),
        ("Papaya Salad", "Green papaya, lime, chilli, peanuts", 16.0),
        ("Basil Chicken", "Stir-fried chicken with basil and chilli", 20.0),
        ("Satay Skewers", "Chicken skewers with peanut sauce", 14.0),
        ("Coconut Rice", "Jasmine rice cooked with coconut milk", 6.0),
        ("Thai Fish Cakes", "Spiced fish cakes with dipping sauce", 13.0),
        ("Mango Sticky Rice", "Sweet coconut rice with mango", 12.0),
    ],
    "Mexican": [
        ("Beef Tacos", "Soft tacos with beef, salsa, coriander", 18.0),
        ("Fish Tacos", "Battered fish, slaw, chipotle mayo", 19.0),
        ("Chicken Quesadilla", "Tortilla, cheese, chicken, salsa", 17.0),
        ("Nachos", "Corn chips, cheese, beans, guacamole", 20.0),
        ("Burrito Bowl", "Rice, beans, meat, salsa, avocado", 21.0),
        ("Pork Carnitas", "Slow-cooked pork with tortillas", 24.0),
        ("Street Corn", "Corn with chilli, cheese, lime", 9.0),
        ("Guacamole", "Avocado dip with corn chips", 12.0),
        ("Churros", "Cinnamon sugar churros with chocolate", 11.0),
        ("Horchata", "Sweet cinnamon rice drink", 6.5),
    ],
    "Healthy": [
        ("Salmon Poke Bowl", "Rice, salmon, edamame, cucumber, avocado", 23.0),
        ("Vegan Buddha Bowl", "Quinoa, chickpeas, greens, tahini", 20.0),
        ("Chicken Protein Bowl", "Chicken, brown rice, greens, yoghurt sauce", 22.0),
        ("Green Smoothie", "Spinach, banana, apple, almond milk", 10.0),
        ("Acai Bowl", "Acai, berries, banana, granola", 17.0),
        ("Falafel Wrap", "Falafel, salad, hummus, pita", 16.0),
        ("Lentil Soup", "Lentils, vegetables, herbs", 14.0),
        ("Tofu Salad", "Tofu, greens, sesame dressing", 18.0),
        ("Overnight Oats", "Oats, yoghurt, berries", 12.0),
        ("Fresh Juice", "Seasonal cold-pressed juice", 8.0),
    ],
    "Fast Food": [
        ("Classic Cheeseburger", "Beef patty, cheddar, pickles, house sauce", 16.0),
        ("Double Smash Burger", "Two beef patties, cheese, onions", 21.0),
        ("Chicken Burger", "Crispy chicken, slaw, mayo", 18.0),
        ("Loaded Fries", "Fries, cheese, bacon, sauce", 14.0),
        ("Onion Rings", "Crispy onion rings", 9.0),
        ("Nuggets", "Chicken nuggets with dipping sauce", 11.0),
        ("Milkshake", "Vanilla, chocolate, or strawberry", 8.0),
        ("Veggie Burger", "Plant-based patty, lettuce, tomato", 17.0),
        ("Hot Wings", "Spicy chicken wings", 15.0),
        ("Soft Drink", "Chilled canned drink", 4.0),
    ],
    "Dessert": [
        ("Chocolate Waffle", "Waffle, chocolate sauce, ice cream", 16.0),
        ("Strawberry Crepe", "Crepe with strawberries and cream", 15.0),
        ("Basque Cheesecake", "Burnt cheesecake slice", 13.0),
        ("Gelato Cup", "Two scoops of gelato", 8.5),
        ("Brownie Sundae", "Warm brownie, ice cream, fudge", 14.0),
        ("Matcha Roll Cake", "Soft roll cake with matcha cream", 12.0),
        ("Mango Pancake", "Pancake filled with mango and cream", 11.0),
        ("Taro Milk Tea", "Milk tea with taro flavour", 7.5),
        ("Macaron Box", "Assorted macarons", 18.0),
        ("Fruit Tart", "Custard tart with fresh fruit", 12.0),
    ],
    "Indian": [
        ("Butter Chicken", "Creamy tomato curry with chicken", 23.0),
        ("Lamb Rogan Josh", "Slow-cooked lamb curry", 25.0),
        ("Palak Paneer", "Spinach curry with paneer", 21.0),
        ("Chana Masala", "Chickpea curry with spices", 18.0),
        ("Garlic Naan", "Naan bread with garlic butter", 5.5),
        ("Biryani", "Spiced rice with meat or vegetables", 22.0),
        ("Tandoori Chicken", "Chargrilled spiced chicken", 24.0),
        ("Samosa", "Crispy pastry with potato filling", 9.0),
        ("Raita", "Yoghurt with cucumber and herbs", 5.0),
        ("Gulab Jamun", "Sweet milk dumplings in syrup", 8.0),
    ],
    "Seafood": [
        ("Fish and Chips", "Battered fish with chips and tartare", 24.0),
        ("Grilled Barramundi", "Barramundi with lemon butter", 31.0),
        ("Garlic Prawns", "Prawns cooked with garlic and herbs", 28.0),
        ("Seafood Platter", "Mixed seafood with chips and salad", 42.0),
        ("Calamari", "Crispy calamari with aioli", 18.0),
        ("Oysters", "Fresh oysters with mignonette", 30.0),
        ("Crab Linguine", "Pasta with crab, chilli, garlic", 33.0),
        ("Mussel Pot", "Mussels in white wine sauce", 27.0),
        ("Prawn Tacos", "Prawns, slaw, lime crema", 20.0),
        ("Lemon Sorbet", "Refreshing citrus sorbet", 9.0),
    ],
    "Modern Australian": [
        ("Grilled Chicken", "Chicken breast, seasonal vegetables", 27.0),
        ("Steak Sandwich", "Beef steak, onion jam, chips", 25.0),
        ("Barramundi Plate", "Barramundi, greens, lemon butter", 31.0),
        ("Pumpkin Risotto", "Creamy risotto with pumpkin and sage", 23.0),
        ("Lamb Shoulder", "Slow-cooked lamb with mash", 34.0),
        ("Caesar Salad", "Cos lettuce, parmesan, croutons", 18.0),
        ("Pork Belly", "Crispy pork belly with apple slaw", 32.0),
        ("Roast Vegetable Plate", "Seasonal roasted vegetables", 20.0),
        ("Sticky Date Pudding", "Warm pudding with caramel sauce", 14.0),
        ("Lemon Lime Bitters", "Classic Australian soft drink", 6.0),
    ],
}

MENU_IMAGE_OVERRIDES = {
    "Margherita Pizza": "https://images.unsplash.com/photo-1574071318508-1cdbab80d002?auto=format&fit=crop&w=800&q=80",
    "Pepperoni Pizza": "https://images.unsplash.com/photo-1628840042765-356cda07504e?auto=format&fit=crop&w=800&q=80",
    "Carbonara": "https://images.unsplash.com/photo-1612874742237-6526221588e3?auto=format&fit=crop&w=800&q=80",
    "Tiramisu": "https://images.unsplash.com/photo-1571877227200-a0d98ea607e9?auto=format&fit=crop&w=800&q=80",
    "Flat White": "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?auto=format&fit=crop&w=800&q=80",
    "Iced Latte": "https://images.unsplash.com/photo-1517701550927-30cf4ba1dba5?auto=format&fit=crop&w=800&q=80",
    "Avocado Toast": "https://images.unsplash.com/photo-1525351484163-7529414344d8?auto=format&fit=crop&w=800&q=80",
    "Eggs Benedict": "https://images.unsplash.com/photo-1608039829572-78524f79c4c7?auto=format&fit=crop&w=800&q=80",
    "Bibimbap": "https://images.unsplash.com/photo-1590301157890-4810ed352733?auto=format&fit=crop&w=800&q=80",
    "Kimchi Stew": "https://images.unsplash.com/photo-1583224964978-2257b960c3d3?auto=format&fit=crop&w=800&q=80",
    "Bulgogi": "https://images.unsplash.com/photo-1580651315530-69c8e0026377?auto=format&fit=crop&w=800&q=80",
    "Korean Fried Chicken": "https://images.unsplash.com/photo-1626082927389-6cd097cdc6ec?auto=format&fit=crop&w=800&q=80",
    "Salmon Sushi Set": "https://images.unsplash.com/photo-1579871494447-9811cf80d66c?auto=format&fit=crop&w=800&q=80",
    "Chicken Katsu Curry": "https://images.unsplash.com/photo-1591814468924-caf88d1232e1?auto=format&fit=crop&w=800&q=80",
    "Tonkotsu Ramen": "https://images.unsplash.com/photo-1569718212165-3a8278d5f624?auto=format&fit=crop&w=800&q=80",
    "Gyoza": "https://images.unsplash.com/photo-1496116218417-1a781b1c416c?auto=format&fit=crop&w=800&q=80",
    "Pad Thai": "https://images.unsplash.com/photo-1559314809-0d155014e29e?auto=format&fit=crop&w=800&q=80",
    "Green Curry": "https://images.unsplash.com/photo-1455619452474-d2be8b1e70cd?auto=format&fit=crop&w=800&q=80",
    "Tom Yum Soup": "https://images.unsplash.com/photo-1569562211093-4ed0d0758f12?auto=format&fit=crop&w=800&q=80",
    "Beef Tacos": "https://images.unsplash.com/photo-1565299585323-38174c4a67df?auto=format&fit=crop&w=800&q=80",
    "Fish Tacos": "https://images.unsplash.com/photo-1512838243191-e81e8f66f1fd?auto=format&fit=crop&w=800&q=80",
    "Nachos": "https://images.unsplash.com/photo-1513456852971-30c0b8199d4d?auto=format&fit=crop&w=800&q=80",
    "Churros": "https://images.unsplash.com/photo-1624371414361-e670edf4898d?auto=format&fit=crop&w=800&q=80",
    "Salmon Poke Bowl": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=800&q=80",
    "Vegan Buddha Bowl": "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?auto=format&fit=crop&w=800&q=80",
    "Acai Bowl": "https://images.unsplash.com/photo-1590301157890-4810ed352733?auto=format&fit=crop&w=800&q=80",
    "Classic Cheeseburger": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?auto=format&fit=crop&w=800&q=80",
    "Double Smash Burger": "https://images.unsplash.com/photo-1550547660-d9450f859349?auto=format&fit=crop&w=800&q=80",
    "Loaded Fries": "https://images.unsplash.com/photo-1573080496219-bb080dd4f877?auto=format&fit=crop&w=800&q=80",
    "Chocolate Waffle": "https://images.unsplash.com/photo-1562376552-0d160a2f238d?auto=format&fit=crop&w=800&q=80",
    "Basque Cheesecake": "https://images.unsplash.com/photo-1533134242443-d4fd215305ad?auto=format&fit=crop&w=800&q=80",
    "Gelato Cup": "https://images.unsplash.com/photo-1567206563064-6f60f40a2b57?auto=format&fit=crop&w=800&q=80",
    "Butter Chicken": "https://images.unsplash.com/photo-1603894584373-5ac82b2ae398?auto=format&fit=crop&w=800&q=80",
    "Garlic Naan": "https://images.unsplash.com/photo-1626132647523-66f5bf380027?auto=format&fit=crop&w=800&q=80",
    "Biryani": "https://images.unsplash.com/photo-1631515242808-497c3fbd3972?auto=format&fit=crop&w=800&q=80",
    "Fish and Chips": "https://images.unsplash.com/photo-1579208030886-b937da0925dc?auto=format&fit=crop&w=800&q=80",
    "Garlic Prawns": "https://images.unsplash.com/photo-1565680018434-b513d5e5fd47?auto=format&fit=crop&w=800&q=80",
    "Steak Sandwich": "https://images.unsplash.com/photo-1550547660-d9450f859349?auto=format&fit=crop&w=800&q=80",
    "Caesar Salad": "https://images.unsplash.com/photo-1550304943-4f24f54ddde9?auto=format&fit=crop&w=800&q=80",
}

REVIEW_TEXTS = [
    "Really enjoyable meal and the staff were friendly.",
    "Good value for the price and the food came out quickly.",
    "The atmosphere was relaxed and the dishes tasted fresh.",
    "Would come back again with friends.",
    "The main dish was excellent, although the service was a little slow.",
    "Nice spot for a casual meal after class.",
    "The flavours were balanced and the portion size was generous.",
    "A reliable place when I want something simple and tasty.",
    "The menu had enough variety and everything felt well prepared.",
    "Loved the vibe and the location was convenient.",
    "The food was good, but the place was a bit noisy.",
    "Great option for dinner around Perth.",
    "The dessert was the highlight of the visit.",
    "Friendly team and a comfortable dining space.",
    "Solid restaurant overall, especially for a quick catch-up.",
]


RESTAURANT_DATA = [
    (
        "Laneway Pizza Co.",
        "Italian",
        "A casual pizza spot with wood-fired favourites and a relaxed laneway feel.",
        "Barrack St, Perth, WA 6000",
        "Perth CBD",
        "+61 8 1000 0001",
    ),
    (
        "Northbridge Coffee Lab",
        "Cafe",
        "Specialty coffee, brunch plates, and a calm morning atmosphere.",
        "William St, Northbridge, WA 6003",
        "Northbridge",
        "+61 8 1000 0002",
    ),
    (
        "Seoul Table",
        "Korean",
        "Korean comfort food, BBQ dishes, stews, and generous shared plates.",
        "Albany Hwy, Victoria Park, WA 6100",
        "Victoria Park",
        "+61 8 1000 0003",
    ),
    (
        "Burger Corner",
        "Fast Food",
        "Quick burgers, loaded fries, and late-night comfort food.",
        "Murray St, Perth, WA 6000",
        "Perth CBD",
        "+61 8 1000 0004",
    ),
    (
        "Green Bowl Kitchen",
        "Healthy",
        "Fresh bowls, salads, smoothies, and vegan-friendly meals.",
        "Hay St, Subiaco, WA 6008",
        "Subiaco",
        "+61 8 1000 0005",
    ),
    (
        "Sakura Sushi House",
        "Japanese",
        "Fresh sushi, ramen, rice bowls, and simple Japanese lunch sets.",
        "Rokeby Rd, Subiaco, WA 6008",
        "Subiaco",
        "+61 8 1000 0006",
    ),
    (
        "Bangkok Street Eats",
        "Thai",
        "Thai curries, noodles, and street-food favourites with bold flavours.",
        "Beaufort St, Mount Lawley, WA 6050",
        "Mount Lawley",
        "+61 8 1000 0007",
    ),
    (
        "Taco Verde",
        "Mexican",
        "Colourful tacos, burrito bowls, nachos, and fresh salsa.",
        "South Tce, Fremantle, WA 6160",
        "Fremantle",
        "+61 8 1000 0008",
    ),
    (
        "Sweet Crumb Dessert Bar",
        "Dessert",
        "Waffles, cakes, gelato, and colourful desserts for late afternoons.",
        "James St, Northbridge, WA 6003",
        "Northbridge",
        "+61 8 1000 0009",
    ),
    (
        "Curry Leaf Kitchen",
        "Indian",
        "Classic curries, naan, biryani, and rich spiced dishes.",
        "Albany Hwy, Cannington, WA 6107",
        "Cannington",
        "+61 8 1000 0010",
    ),
    (
        "Harbour Fish Grill",
        "Seafood",
        "Grilled seafood, fish and chips, and casual harbour-side plates.",
        "Mews Rd, Fremantle, WA 6160",
        "Fremantle",
        "+61 8 1000 0011",
    ),
    (
        "Banksia Bistro",
        "Modern Australian",
        "Modern Australian meals using local produce and seasonal sides.",
        "St Georges Tce, Perth, WA 6000",
        "Perth CBD",
        "+61 8 1000 0012",
    ),
    (
        "Pasta Piazza",
        "Italian",
        "Handmade pasta, sauces, salads, and classic Italian desserts.",
        "Oxford St, Leederville, WA 6007",
        "Leederville",
        "+61 8 1000 0013",
    ),
    (
        "Campus Brew",
        "Cafe",
        "Student-friendly cafe with coffee, toasties, and study tables.",
        "Hackett Dr, Crawley, WA 6009",
        "Crawley",
        "+61 8 1000 0014",
    ),
    (
        "Kimchi Garden",
        "Korean",
        "A cosy Korean diner with stews, fried chicken, and rice dishes.",
        "Francis St, Northbridge, WA 6003",
        "Northbridge",
        "+61 8 1000 0015",
    ),
    (
        "Tokyo Bento Bar",
        "Japanese",
        "Fast Japanese bento boxes, curry, sushi, and udon.",
        "Hay St, Perth, WA 6000",
        "Perth CBD",
        "+61 8 1000 0016",
    ),
    (
        "Siam Corner",
        "Thai",
        "Thai restaurant serving curries, stir-fries, and noodle dishes.",
        "Cambridge St, Wembley, WA 6014",
        "Wembley",
        "+61 8 1000 0017",
    ),
    (
        "El Camino Cantina",
        "Mexican",
        "Casual Mexican food with tacos, nachos, and shared plates.",
        "Scarborough Beach Rd, Scarborough, WA 6019",
        "Scarborough",
        "+61 8 1000 0018",
    ),
    (
        "Fit Plate Co.",
        "Healthy",
        "Protein bowls, salads, smoothies, and healthy takeaway meals.",
        "Angelo St, South Perth, WA 6151",
        "South Perth",
        "+61 8 1000 0019",
    ),
    (
        "Crispy Burger Works",
        "Fast Food",
        "Burgers, wings, fries, and easy takeaway meals.",
        "Great Eastern Hwy, Belmont, WA 6104",
        "Belmont",
        "+61 8 1000 0020",
    ),
    (
        "Milky Moon Desserts",
        "Dessert",
        "Milk tea, crepes, cakes, and soft desserts.",
        "Murray St, Perth, WA 6000",
        "Perth CBD",
        "+61 8 1000 0021",
    ),
    (
        "Tandoori Nights",
        "Indian",
        "Tandoori dishes, curries, naan, and rice plates.",
        "High Rd, Willetton, WA 6155",
        "Willetton",
        "+61 8 1000 0022",
    ),
    (
        "Ocean Basket Perth",
        "Seafood",
        "Seafood platters, grilled fish, prawns, and fresh sides.",
        "Riverside Dr, Perth, WA 6000",
        "Perth CBD",
        "+61 8 1000 0023",
    ),
    (
        "Jarrah House",
        "Modern Australian",
        "Local plates, steaks, seafood, and seasonal vegetables.",
        "Rokeby Rd, Subiaco, WA 6008",
        "Subiaco",
        "+61 8 1000 0024",
    ),
    (
        "Little Napoli",
        "Italian",
        "Neighbourhood Italian spot with pizza, pasta, and desserts.",
        "Albany Hwy, East Victoria Park, WA 6101",
        "East Victoria Park",
        "+61 8 1000 0025",
    ),
    (
        "Morning Fox Cafe",
        "Cafe",
        "Bright cafe serving brunch, pastries, and smooth coffee.",
        "Napoleon St, Cottesloe, WA 6011",
        "Cottesloe",
        "+61 8 1000 0026",
    ),
    (
        "Busan BBQ House",
        "Korean",
        "Korean BBQ, stews, rice dishes, and group-friendly tables.",
        "Beaufort St, Inglewood, WA 6052",
        "Inglewood",
        "+61 8 1000 0027",
    ),
    (
        "Kyoto Ramen Lane",
        "Japanese",
        "Ramen, gyoza, rice bowls, and Japanese desserts.",
        "Albany Hwy, Victoria Park, WA 6100",
        "Victoria Park",
        "+61 8 1000 0028",
    ),
    (
        "Thai Orchid Room",
        "Thai",
        "Traditional Thai flavours with curries, salads, and soups.",
        "Canning Hwy, Applecross, WA 6153",
        "Applecross",
        "+61 8 1000 0029",
    ),
    (
        "Casa Burrito",
        "Mexican",
        "Burritos, tacos, quesadillas, and quick Mexican takeaway.",
        "Leach Hwy, Booragoon, WA 6154",
        "Booragoon",
        "+61 8 1000 0030",
    ),
    (
        "Nourish Lane",
        "Healthy",
        "Light meals, plant-based options, juices, and grain bowls.",
        "Hampden Rd, Nedlands, WA 6009",
        "Nedlands",
        "+61 8 1000 0031",
    ),
    (
        "Fry Yard",
        "Fast Food",
        "Crispy fried chicken, burgers, fries, and shakes.",
        "Oats St, Carlisle, WA 6101",
        "Carlisle",
        "+61 8 1000 0032",
    ),
    (
        "Sugar Finch",
        "Dessert",
        "Small dessert cafe with cakes, waffles, and drinks.",
        "Queen Victoria St, Fremantle, WA 6160",
        "Fremantle",
        "+61 8 1000 0033",
    ),
    (
        "Masala Street",
        "Indian",
        "Indian street snacks, curries, and warm breads.",
        "Walter Rd, Morley, WA 6062",
        "Morley",
        "+61 8 1000 0034",
    ),
    (
        "Coral Coast Seafood",
        "Seafood",
        "Fresh seafood dishes with simple sides and casual service.",
        "West Coast Dr, Hillarys, WA 6025",
        "Hillarys",
        "+61 8 1000 0035",
    ),
    (
        "Rivergum Kitchen",
        "Modern Australian",
        "Relaxed Australian dining with local ingredients.",
        "Canning Hwy, South Perth, WA 6151",
        "South Perth",
        "+61 8 1000 0036",
    ),
    (
        "Roman Hearth",
        "Italian",
        "Italian dishes, roasted vegetables, and handmade pasta.",
        "Cambridge St, West Leederville, WA 6007",
        "West Leederville",
        "+61 8 1000 0037",
    ),
    (
        "Foam & Flour",
        "Cafe",
        "Bakery cafe with coffee, sourdough, and pastries.",
        "Stirling Hwy, Claremont, WA 6010",
        "Claremont",
        "+61 8 1000 0038",
    ),
    (
        "Han River Kitchen",
        "Korean",
        "Korean rice bowls, noodles, stew, and fried snacks.",
        "Korean St, Perth, WA 6000",
        "Perth CBD",
        "+61 8 1000 0039",
    ),
    (
        "Nori Market",
        "Japanese",
        "Sushi rolls, donburi, ramen, and light Japanese meals.",
        "Fremantle Markets, Fremantle, WA 6160",
        "Fremantle",
        "+61 8 1000 0040",
    ),
]


def clear_data():
    ReviewPhoto.query.delete()
    Review.query.delete()
    CollectionSubscription.query.delete()
    Bookmark.query.delete()
    BookmarkCollection.query.delete()
    OpeningHour.query.delete()
    MenuItem.query.delete()
    Restaurant.query.delete()
    User.query.delete()
    db.session.commit()


def create_opening_hours(
    restaurant_id,
    weekday_hours,
    friday_hours=None,
    weekend_hours=None,
    closed_days=None,
):
    friday_hours = friday_hours or weekday_hours
    weekend_hours = weekend_hours or weekday_hours
    closed_days = closed_days or []

    days = [
        (0, "Mon", weekday_hours[0], weekday_hours[1]),
        (1, "Tue", weekday_hours[0], weekday_hours[1]),
        (2, "Wed", weekday_hours[0], weekday_hours[1]),
        (3, "Thu", weekday_hours[0], weekday_hours[1]),
        (4, "Fri", friday_hours[0], friday_hours[1]),
        (5, "Sat", weekend_hours[0], weekend_hours[1]),
        (6, "Sun", weekend_hours[0], weekend_hours[1]),
    ]

    return [
        OpeningHour(
            restaurant_id=restaurant_id,
            day_of_week=day_of_week,
            day_label=day_label,
            open_time=None if day_of_week in closed_days else open_time,
            close_time=None if day_of_week in closed_days else close_time,
            is_closed=day_of_week in closed_days,
        )
        for day_of_week, day_label, open_time, close_time in days
    ]


def create_users():
    admin_user = User(
        email="admin@example.com",
        username="Admin User",
        password_hash=DEFAULT_PASSWORD_HASH,
        profile_image=None,
        role="admin",
        status="active",
        email_verified_at=datetime.utcnow() - timedelta(days=70),
        created_at=datetime.utcnow() - timedelta(days=70),
        updated_at=datetime.utcnow() - timedelta(days=1),
    )

    owner_specs = [
        ("owner1@example.com", "Mia Owner", "51824753556", "+61 8 2000 0001"),
        ("owner2@example.com", "Daniel Owner", "23684597120", "+61 8 2000 0002"),
        ("owner3@example.com", "Sophie Owner", "74920138645", "+61 8 2000 0003"),
        ("owner4@example.com", "Noah Owner", "90361278451", "+61 8 2000 0004"),
        ("owner5@example.com", "Grace Owner", "61273948015", "+61 8 2000 0005"),
    ]

    users = [admin_user]

    for index, (email, username, abn_number, contact_number) in enumerate(owner_specs):
        users.append(
            User(
                email=email,
                username=username,
                password_hash=DEFAULT_PASSWORD_HASH,
                profile_image=(
                    PROFILE_IMAGES[index] if index < len(PROFILE_IMAGES) else None
                ),
                role="owner",
                status=USER_STATUS_PATTERN[index % len(USER_STATUS_PATTERN)],
                email_verified_at=datetime.utcnow() - timedelta(days=65 - index),
                abn_number=abn_number,
                contact_number=contact_number,
                created_at=datetime.utcnow() - timedelta(days=65 - index),
                updated_at=datetime.utcnow() - timedelta(days=index + 1),
            )
        )

    customer_names = [
        "Alex",
        "Mia",
        "Daniel",
        "Sophie",
        "Noah",
        "Grace",
        "Ethan",
        "Olivia",
        "Liam",
        "Emma",
        "Lucas",
        "Ava",
        "Henry",
        "Chloe",
        "Jack",
        "Ruby",
        "Leo",
        "Isla",
        "Mason",
        "Zoe",
        "Charlie",
        "Lily",
        "Oscar",
        "Ella",
        "Max",
        "Amelia",
        "Hugo",
        "Maya",
        "Arlo",
        "Ivy",
        "Finn",
        "Sienna",
        "Kai",
        "Harper",
        "Jasper",
        "Evie",
        "Theo",
        "Poppy",
        "Louis",
        "Freya",
        "Ben",
        "Nora",
        "Adam",
        "Clara",
        "Ryan",
    ]

    for index, name in enumerate(customer_names, start=1):
        users.append(
            User(
                email=f"customer{index:02d}@example.com",
                username=name,
                password_hash=DEFAULT_PASSWORD_HASH,
                profile_image=(
                    PROFILE_IMAGES[len(owner_specs) + index - 1]
                    if len(owner_specs) + index - 1 < len(PROFILE_IMAGES)
                    else None
                ),
                role="customer",
                status=USER_STATUS_PATTERN[index % len(USER_STATUS_PATTERN)],
                email_verified_at=datetime.utcnow() - timedelta(days=60 - (index % 40)),
                created_at=datetime.utcnow() - timedelta(days=60 - (index % 40)),
                updated_at=datetime.utcnow() - timedelta(days=index % 12),
            )
        )

    db.session.add_all(users)
    db.session.commit()

    owners = [user for user in users if user.role == "owner"]
    customers = [user for user in users if user.role == "customer"]

    return owners, customers


def create_restaurants(owners):
    restaurants = []

    for index, (name, category, description, address, suburb, phone) in enumerate(
        RESTAURANT_DATA
    ):
        image_url = RESTAURANT_IMAGE_OVERRIDES.get(name)
        status = RESTAURANT_STATUS_PATTERN[index % len(RESTAURANT_STATUS_PATTERN)]

        restaurant = Restaurant(
            name=name,
            category=category,
            description=description,
            address=address,
            suburb=suburb,
            phone=phone,
            website=f"https://example.com/restaurants/{index + 1}",
            thumbnail_image=image_url,
            hero_image=image_url,
            average_rating=0.0,
            review_count=0,
            status=status,
            owner_id=owners[index % len(owners)].id,
            created_at=datetime.utcnow() - timedelta(days=40 - index),
            updated_at=datetime.utcnow() - timedelta(days=index % 10),
        )

        restaurants.append(restaurant)

    db.session.add_all(restaurants)
    db.session.commit()

    return restaurants


def create_menu_items(restaurants):
    menu_items = []

    for restaurant in restaurants:
        items = MENU_LIBRARY[restaurant.category]

        for item_index, (name, description, price) in enumerate(items):
            menu_items.append(
                MenuItem(
                    restaurant_id=restaurant.id,
                    name=name,
                    description=description,
                    price=price,
                    image_url=MENU_IMAGE_OVERRIDES.get(name),
                )
            )

    db.session.add_all(menu_items)
    db.session.commit()


def create_all_opening_hours(restaurants):
    opening_patterns = [
        (("7:00 AM", "3:00 PM"), ("7:00 AM", "4:00 PM"), ("8:00 AM", "2:00 PM"), [6]),
        (
            ("11:00 AM", "9:00 PM"),
            ("11:00 AM", "10:30 PM"),
            ("11:30 AM", "10:30 PM"),
            [0],
        ),
        (
            ("10:00 AM", "10:00 PM"),
            ("10:00 AM", "12:00 AM"),
            ("11:00 AM", "12:00 AM"),
            [],
        ),
        (("8:00 AM", "8:00 PM"), ("8:00 AM", "9:00 PM"), ("9:00 AM", "8:00 PM"), []),
        (
            ("12:00 PM", "9:30 PM"),
            ("12:00 PM", "11:00 PM"),
            ("12:00 PM", "11:00 PM"),
            [2],
        ),
        (("6:30 AM", "2:30 PM"), ("6:30 AM", "3:00 PM"), ("7:30 AM", "2:00 PM"), [6]),
        (
            ("5:00 PM", "10:00 PM"),
            ("5:00 PM", "11:30 PM"),
            ("4:30 PM", "11:30 PM"),
            [1],
        ),
        (("9:00 AM", "5:00 PM"), ("9:00 AM", "6:00 PM"), ("10:00 AM", "4:00 PM"), []),
    ]

    # Intentionally leave two restaurants without opening hours to test fallback UI.
    restaurants_without_hours = {restaurants[4].id, restaurants[32].id}

    all_hours = []

    for index, restaurant in enumerate(restaurants):
        if restaurant.id in restaurants_without_hours:
            continue

        weekday_hours, friday_hours, weekend_hours, closed_days = opening_patterns[
            index % len(opening_patterns)
        ]

        all_hours.extend(
            create_opening_hours(
                restaurant.id,
                weekday_hours=weekday_hours,
                friday_hours=friday_hours,
                weekend_hours=weekend_hours,
                closed_days=closed_days,
            )
        )

    db.session.add_all(all_hours)
    db.session.commit()


def create_reviews(restaurants, customers):
    reviews = []

    # Max review count is 15. Most restaurants have fewer.
    review_counts = [
        15,
        14,
        13,
        12,
        11,
        10,
        9,
        8,
        7,
        6,
        5,
        5,
        4,
        4,
        3,
        3,
        2,
        2,
        1,
        1,
        8,
        7,
        6,
        5,
        4,
        3,
        2,
        1,
        9,
        6,
        5,
        4,
        3,
        2,
        1,
        7,
        6,
        5,
        4,
        0,
    ]

    rating_patterns = [
        [5, 5, 4, 5, 4, 5, 5, 4, 5, 4, 5, 5, 4, 5, 5],
        [5, 4, 4, 5, 4, 4, 5, 4, 3, 5, 4, 4, 5, 4],
        [4, 4, 5, 4, 3, 4, 5, 4, 4, 3, 5, 4, 4],
        [4, 3, 4, 4, 5, 3, 4, 4, 3, 4, 5, 4],
        [3, 4, 4, 3, 5, 4, 3, 4, 4, 3, 4],
    ]

    for restaurant_index, restaurant in enumerate(restaurants):
        count = review_counts[restaurant_index]
        ratings = rating_patterns[restaurant_index % len(rating_patterns)]

        selected_customers = random.sample(customers, count) if count else []

        for review_index, customer in enumerate(selected_customers):
            rating = ratings[review_index % len(ratings)]
            content = REVIEW_TEXTS[
                (restaurant_index + review_index) % len(REVIEW_TEXTS)
            ]
            review_status = REVIEW_STATUS_PATTERN[
                (restaurant_index + review_index) % len(REVIEW_STATUS_PATTERN)
            ]

            reviews.append(
                Review(
                    restaurant_id=restaurant.id,
                    user_id=customer.id,
                    rating=rating,
                    content=content,
                    status=review_status,
                    created_at=datetime.utcnow()
                    - timedelta(days=(restaurant_index * 2 + review_index)),
                    updated_at=datetime.utcnow()
                    - timedelta(days=(restaurant_index * 2 + review_index)),
                )
            )

    db.session.add_all(reviews)
    db.session.commit()

    return reviews


def update_restaurant_review_stats(restaurants):
    for restaurant in restaurants:
        reviews = Review.query.filter_by(restaurant_id=restaurant.id).all()
        total_reviews = len(reviews)

        restaurant.review_count = total_reviews
        restaurant.average_rating = (
            round(sum(review.rating for review in reviews) / total_reviews, 1)
            if total_reviews
            else 0.0
        )

    db.session.commit()


def create_review_photos(reviews):
    # Add photos to some reviews only.
    photo_urls = [
        "https://images.unsplash.com/photo-1513104890138-7c749659a591?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1552566626-52f8b828add9?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1498654896293-37aacf113fd9?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1540420773420-3366772f4999?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?auto=format&fit=crop&w=800&q=80",
    ]

    review_photos = []

    for index, review in enumerate(reviews[:20]):
        if index % 3 == 0:
            review_photos.append(
                ReviewPhoto(
                    review_id=review.id,
                    image_url=photo_urls[index % len(photo_urls)],
                )
            )

    db.session.add_all(review_photos)
    db.session.commit()


def create_bookmarks(customers, restaurants):
    collection_specs = [
        (
            customers[0],
            "Favorite",
            "My default saved restaurant collection.",
            False,
            [0, 2, 5, 10],
        ),
        (
            customers[0],
            "Perth best",
            "My favourite restaurants around Perth.",
            True,
            [0, 2, 5, 10],
        ),
        (
            customers[0],
            "Study cafes",
            "Places with coffee and a good study atmosphere.",
            False,
            [1, 13, 25, 37],
        ),
        (
            customers[1],
            "Dinner shortlist",
            "Restaurants to try for dinner.",
            True,
            [0, 3, 6, 14],
        ),
        (customers[2], "Healthy picks", "Fresh and lighter meals.", False, [4, 18, 30]),
        (
            customers[3],
            "Date night",
            "Places with a nicer dinner atmosphere.",
            True,
            [11, 23, 35],
        ),
    ]

    collections = []

    for user, name, description, is_public, _restaurant_indexes in collection_specs:
        collections.append(
            BookmarkCollection(
                user_id=user.id,
                name=name,
                description=description,
                is_public=is_public,
            )
        )

    db.session.add_all(collections)
    db.session.commit()

    bookmarks = []

    for collection, spec in zip(collections, collection_specs):
        restaurant_indexes = spec[4]

        for restaurant_index in restaurant_indexes:
            bookmarks.append(
                Bookmark(
                    collection_id=collection.id,
                    restaurant_id=restaurants[restaurant_index].id,
                )
            )

    db.session.add_all(bookmarks)
    db.session.commit()

    public_collections = [
        collection for collection in collections if collection.is_public
    ]
    subscriptions = []
    seen_subscription_pairs = set()

    for index in range(50):
        user = customers[index % len(customers)]
        collection = public_collections[index % len(public_collections)]

        if user.id == collection.user_id:
            collection = public_collections[(index + 1) % len(public_collections)]

        pair = (collection.id, user.id)

        if pair in seen_subscription_pairs:
            continue

        seen_subscription_pairs.add(pair)

        subscriptions.append(
            CollectionSubscription(
                collection_id=collection.id,
                user_id=user.id,
            )
        )

    db.session.add_all(subscriptions)
    db.session.commit()


def seed_data():
    owners, customers = create_users()
    restaurants = create_restaurants(owners)

    create_menu_items(restaurants)
    create_all_opening_hours(restaurants)

    reviews = create_reviews(restaurants, customers)
    update_restaurant_review_stats(restaurants)
    create_review_photos(reviews)

    create_bookmarks(customers, restaurants)


if __name__ == "__main__":
    with app.app_context():
        clear_data()
        seed_data()

        print("Database seeded successfully.")
        print("Created 50 users: 5 owners and 45 customers.")
        print("Created 40 restaurants.")
        print("Added custom restaurant images for 20 restaurants.")
        print("Left 20 restaurant images empty to test fallback UI.")
        print("Created 400 menu items.")
        print("Created opening hours for 38 restaurants.")
        print("Created reviews and synced restaurant average_rating/review_count.")
