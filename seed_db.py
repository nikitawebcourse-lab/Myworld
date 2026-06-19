import os
import django

# Set settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myworld_project.settings')
django.setup()

from django.contrib.auth.models import User
from myworld.models import UserProfile, SavedItem, Like, Comment

def seed():
    print("Seeding database...")
    
    # 1. Create superuser if it doesn't exist
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@myworld.com', 'admin123')
        print("Superuser 'admin' created (password: admin123)")
    
    # 2. Create sample users
    users_data = [
        {'username': 'alex_wish', 'password': 'password123', 'bio': 'Tech enthusiast, gadget collector, and book lover.'},
        {'username': 'sarah_styles', 'password': 'password123', 'bio': 'Fashion curator and design blogger. Sharing my favorite finds.'},
        {'username': 'mike_travels', 'password': 'password123', 'bio': 'Adventure photographer and remote worker. Saving travel gear.'}
    ]
    
    users = {}
    for ud in users_data:
        user, created = User.objects.get_or_create(username=ud['username'])
        if created:
            user.set_password(ud['password'])
            user.save()
        
        # update bio
        profile = user.profile
        profile.bio = ud['bio']
        profile.save()
        users[ud['username']] = user
        print(f"User '{ud['username']}' created/updated.")
        
    # 3. Create items for each user
    items_data = [
        # Alex (Tech)
        {
            'user': users['alex_wish'],
            'title': 'Sony WH-1000XM5 Noise Cancelling Headphones',
            'description': 'Amazing sound and active noise cancellation. Planning to buy this next month!',
            'url': 'https://www.amazon.in/Sony-WH-1000XM5-Wireless-Cancelling-Headphones/dp/B0B3C572D1',
            'image_url': 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?q=80&w=600&auto=format&fit=crop',
            'price': 29990.00,
            'platform': 'Amazon',
            'category': 'Electronics',
            'is_public': True
        },
        {
            'user': users['alex_wish'],
            'title': 'Learn Python Programming - Full Course for Beginners',
            'description': 'Very comprehensive python training. Good for reference.',
            'url': 'https://www.youtube.com/watch?v=rfscVS0vtbw',
            'image_url': 'https://images.unsplash.com/photo-1515879218367-8466d910aaa4?q=80&w=600&auto=format&fit=crop',
            'price': None,
            'platform': 'YouTube',
            'category': 'Education',
            'is_public': True
        },
        {
            'user': users['alex_wish'],
            'title': 'Keychron K2 Mechanical Keyboard',
            'description': 'Wireless mechanical keyboard. Love the tactile response.',
            'url': 'https://www.amazon.in/Keychron-Mechanical-Keyboard-Backlight-Bluetooth/dp/B07QBPDWNV',
            'image_url': 'https://images.unsplash.com/photo-1618384887929-16ec33fab9ef?q=80&w=600&auto=format&fit=crop',
            'price': 7499.00,
            'platform': 'Amazon',
            'category': 'Electronics',
            'is_public': False
        },
        
        # Sarah (Fashion)
        {
            'user': users['sarah_styles'],
            'title': 'Minimalist Trench Coat - Beige Classic',
            'description': 'Classic style trench coat. Perfect layering piece for autumn styling.',
            'url': 'https://www.flipkart.com/minimalist-trench-coat-beige/p/itm1234567890',
            'image_url': 'https://images.unsplash.com/photo-1591047139829-d91aecb6caea?q=80&w=600&auto=format&fit=crop',
            'price': 3499.00,
            'platform': 'Flipkart',
            'category': 'Fashion',
            'is_public': True
        },
        {
            'user': users['sarah_styles'],
            'title': 'Minimalist Home Office Aesthetics Tour',
            'description': 'Stunning layout ideas. Taking inspiration from the color scheme here.',
            'url': 'https://www.instagram.com/p/CoHomeOfficeTour/',
            'image_url': 'https://images.unsplash.com/photo-1499951360447-b19be8fe80f5?q=80&w=600&auto=format&fit=crop',
            'price': None,
            'platform': 'Instagram',
            'category': 'Fashion',
            'is_public': True
        },
        {
            'user': users['sarah_styles'],
            'title': 'Leather Crossbody Bag - Coffee Brown',
            'description': 'Beautiful structured bag. Ideal for everyday use.',
            'url': 'https://www.amazon.in/Leather-Crossbody-Bag-Coffee-Brown/dp/B0CSarahBag',
            'image_url': 'https://images.unsplash.com/photo-1548036328-c9fa89d128fa?q=80&w=600&auto=format&fit=crop',
            'price': 1899.00,
            'platform': 'Amazon',
            'category': 'Shopping',
            'is_public': False
        },
        
        # Mike (Travel)
        {
            'user': users['mike_travels'],
            'title': 'Osprey Farpoint 40 Travel Backpack',
            'description': 'Highly recommended carry-on backpack. Fits standard flight cabins perfectly.',
            'url': 'https://www.amazon.in/Osprey-Farpoint-Travel-Pack-Volcano/dp/B014EBLM8K',
            'image_url': 'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?q=80&w=600&auto=format&fit=crop',
            'price': 12500.00,
            'platform': 'Amazon',
            'category': 'Travel',
            'is_public': True
        },
        {
            'user': users['mike_travels'],
            'title': 'Beautiful Iceland Road Trip Itinerary',
            'description': 'Complete video guide showing stops, camping spots, and budget details.',
            'url': 'https://www.youtube.com/watch?v=IcelandTrip',
            'image_url': 'https://images.unsplash.com/photo-1504893524553-ac55fce69cbf?q=80&w=600&auto=format&fit=crop',
            'price': None,
            'platform': 'YouTube',
            'category': 'Travel',
            'is_public': True
        },
        {
            'user': users['mike_travels'],
            'title': 'Travel Hacks for Packing Light',
            'description': 'Good tips for folding clothes and organizing electronics in small bags.',
            'url': 'https://www.facebook.com/watch/travelhacks',
            'image_url': 'https://images.unsplash.com/photo-1527853787696-f7be74f2e39a?q=80&w=600&auto=format&fit=crop',
            'price': None,
            'platform': 'Facebook',
            'category': 'Entertainment',
            'is_public': False
        }
    ]
    
    for idata in items_data:
        SavedItem.objects.get_or_create(
            user=idata['user'],
            title=idata['title'],
            defaults={
                'description': idata['description'],
                'url': idata['url'],
                'image_url': idata['image_url'],
                'price': idata['price'],
                'platform': idata['platform'],
                'category': idata['category'],
                'is_public': idata['is_public']
            }
        )
        print(f"Item '{idata['title']}' created/updated.")
        
    # 4. Create Follows
    # Clear follows first to prevent double seeding conflicts
    for u in users.values():
        u.profile.follows.clear()
        
    # Alex follows Sarah
    users['alex_wish'].profile.follows.add(users['sarah_styles'].profile)
    # Sarah follows Mike
    users['sarah_styles'].profile.follows.add(users['mike_travels'].profile)
    # Mike follows Alex
    users['mike_travels'].profile.follows.add(users['alex_wish'].profile)
    print("Follow links configured between users.")
    
    # 5. Create Likes
    coat = SavedItem.objects.get(title='Minimalist Trench Coat - Beige Classic')
    Like.objects.get_or_create(user=users['alex_wish'], item=coat)
    
    headphones = SavedItem.objects.get(title='Sony WH-1000XM5 Noise Cancelling Headphones')
    Like.objects.get_or_create(user=users['sarah_styles'], item=headphones)
    
    python_vid = SavedItem.objects.get(title='Learn Python Programming - Full Course for Beginners')
    Like.objects.get_or_create(user=users['mike_travels'], item=python_vid)
    print("Likes populated.")
    
    # 6. Create Comments
    Comment.objects.get_or_create(
        user=users['sarah_styles'],
        item=headphones,
        content="I have these and they are absolutely worth every penny! Best NC ever."
    )
    Comment.objects.get_or_create(
        user=users['mike_travels'],
        item=headphones,
        content="Great for long flights. Love the sound signature too."
    )
    Comment.objects.get_or_create(
        user=users['alex_wish'],
        item=coat,
        content="This looks super clean, thinking of gifting it to my sister!"
    )
    print("Comments populated.")
    print("Seeding finished successfully!")

if __name__ == '__main__':
    seed()
