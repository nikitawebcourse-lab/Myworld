import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Count, Q

from .models import UserProfile, SavedItem, Like, Comment

# Helper: Scrape URL metadata
def scrape_url_metadata(url):
    data = {
        'title': '',
        'description': '',
        'image_url': '',
        'platform': 'Other',
        'price': None
    }
    
    # 1. Detect platform
    parsed_url = urlparse(url)
    domain = parsed_url.netloc.lower()
    if 'amazon' in domain:
        data['platform'] = 'Amazon'
    elif 'flipkart' in domain:
        data['platform'] = 'Flipkart'
    elif 'instagram' in domain:
        data['platform'] = 'Instagram'
    elif 'youtube' in domain or 'youtu.be' in domain:
        data['platform'] = 'YouTube'
    elif 'facebook' in domain:
        data['platform'] = 'Facebook'
    else:
        data['platform'] = 'Other'
        
    # 2. Scrape metadata
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Title
            og_title = soup.find('meta', property='og:title') or soup.find('meta', name='twitter:title')
            if og_title and og_title.get('content'):
                data['title'] = og_title.get('content').strip()
            elif soup.title:
                data['title'] = soup.title.string.strip()
            else:
                data['title'] = parsed_url.path.split('/')[-1] or "Saved Link"
                
            # Image URL
            og_image = soup.find('meta', property='og:image') or soup.find('meta', name='twitter:image')
            if og_image and og_image.get('content'):
                data['image_url'] = og_image.get('content')
            else:
                # Try finding some image tags
                first_img = soup.find('img')
                if first_img and first_img.get('src'):
                    src = first_img.get('src')
                    if src.startswith('http'):
                        data['image_url'] = src
                    else:
                        data['image_url'] = f"{parsed_url.scheme}://{parsed_url.netloc}{src}"
                        
            # Description
            og_desc = soup.find('meta', property='og:description') or soup.find('meta', name='description') or soup.find('meta', name='twitter:description')
            if og_desc and og_desc.get('content'):
                data['description'] = og_desc.get('content').strip()
                
            # Price detection for Amazon/Flipkart
            og_price = soup.find('meta', property='product:price:amount') or soup.find('meta', property='og:price:amount')
            if og_price and og_price.get('content'):
                try:
                    data['price'] = float(re.sub(r'[^\d.]', '', og_price.get('content')))
                except ValueError:
                    pass
            else:
                price_text = None
                if data['platform'] == 'Amazon':
                    price_element = soup.find('span', class_='a-price-whole')
                    if price_element:
                        price_text = price_element.text.strip()
                elif data['platform'] == 'Flipkart':
                    price_element = soup.find('div', class_='_30jeq3')
                    if price_element:
                        price_text = price_element.text.strip()
                
                if price_text:
                    try:
                        clean_price = re.sub(r'[^\d.]', '', price_text)
                        data['price'] = float(clean_price)
                    except ValueError:
                        pass
    except Exception:
        # Fallback to domain name if failed
        data['title'] = parsed_url.netloc or "Saved Link"
        
    if not data['title']:
        data['title'] = parsed_url.netloc or "Saved Link"
        
    return data

# Landing page
def landing(request):
    if request.user.is_authenticated:
        return redirect('my_world')
    return render(request, 'myworld/landing.html')

# Signup View
def signup_view(request):
    if request.user.is_authenticated:
        return redirect('my_world')
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to MyWorld, {user.username}!")
            return redirect('my_world')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")
    else:
        form = UserCreationForm()
    return render(request, 'myworld/signup.html', {'form': form})

# Login View
def login_view(request):
    if request.user.is_authenticated:
        return redirect('my_world')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {username}!")
                return redirect('my_world')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'myworld/login.html', {'form': form})

# Logout View
def logout_view(request):
    logout(request)
    messages.info(request, "You have logged out successfully.")
    return redirect('landing')

# "My World" - Private Saved Items Dashboard
@login_required
def my_world(request):
    query = request.GET.get('q', '').strip()
    category = request.GET.get('category', '')
    platform = request.GET.get('platform', '')
    
    items = SavedItem.objects.filter(user=request.user)
    
    if query:
        items = items.filter(Q(title__icontains=query) | Q(description__icontains=query) | Q(url__icontains=query))
    if category:
        items = items.filter(category=category)
    if platform:
        items = items.filter(platform=platform)
        
    categories = [choice[0] for choice in SavedItem.CATEGORY_CHOICES]
    platforms = [choice[0] for choice in SavedItem.PLATFORM_CHOICES]
    
    return render(request, 'myworld/my_world.html', {
        'items': items,
        'query': query,
        'selected_category': category,
        'selected_platform': platform,
        'categories': categories,
        'platforms': platforms
    })

# "Global World" - Public saved items feed
@login_required
def global_world(request):
    query = request.GET.get('q', '').strip()
    category = request.GET.get('category', '')
    platform = request.GET.get('platform', '')
    
    # Public items of other users, or user's own public items
    items = SavedItem.objects.filter(is_public=True).annotate(
        like_count=Count('likes'),
        comment_count=Count('comments')
    )
    
    if query:
        items = items.filter(
            Q(title__icontains=query) | 
            Q(description__icontains=query) | 
            Q(user__username__icontains=query)
        )
    if category:
        items = items.filter(category=category)
    if platform:
        items = items.filter(platform=platform)
        
    categories = [choice[0] for choice in SavedItem.CATEGORY_CHOICES]
    platforms = [choice[0] for choice in SavedItem.PLATFORM_CHOICES]
    
    # Check which items the current user has liked
    user_liked_item_ids = Like.objects.filter(user=request.user).values_list('item_id', flat=True)
    
    # Check which users the current user follows
    followed_user_ids = request.user.profile.follows.values_list('user_id', flat=True)
    
    return render(request, 'myworld/global_world.html', {
        'items': items,
        'query': query,
        'selected_category': category,
        'selected_platform': platform,
        'categories': categories,
        'platforms': platforms,
        'user_liked_item_ids': user_liked_item_ids,
        'followed_user_ids': followed_user_ids
    })

# Add Saved Item
@login_required
def add_item(request):
    if request.method == 'POST':
        url = request.POST.get('url', '').strip()
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        category = request.POST.get('category', 'Shopping')
        price = request.POST.get('price', None)
        is_public = request.POST.get('is_public') == 'on'
        
        if not url:
            messages.error(request, "URL is required.")
            return redirect('my_world')
            
        # Scrape metadata if title or image_url is missing
        scraped = scrape_url_metadata(url)
        
        final_title = title if title else (scraped['title'] or "Saved Item")
        final_desc = description if description else scraped['description']
        final_image = scraped['image_url'] or 'https://images.unsplash.com/photo-1598128558393-70ff21433be0?q=80&w=600&auto=format&fit=crop'
        final_platform = scraped['platform']
        
        final_price = None
        if price:
            try:
                final_price = float(price)
            except ValueError:
                pass
        else:
            final_price = scraped['price']
            
        SavedItem.objects.create(
            user=request.user,
            title=final_title,
            description=final_desc,
            url=url,
            image_url=final_image,
            price=final_price,
            platform=final_platform,
            category=category,
            is_public=is_public
        )
        messages.success(request, f"Saved item from {final_platform} successfully!")
        return redirect('my_world')
        
    return redirect('my_world')

# Edit Saved Item
@login_required
def edit_item(request, pk):
    item = get_object_or_404(SavedItem, pk=pk, user=request.user)
    if request.method == 'POST':
        item.title = request.POST.get('title', '').strip() or item.title
        item.description = request.POST.get('description', '').strip()
        item.category = request.POST.get('category', item.category)
        item.is_public = request.POST.get('is_public') == 'on'
        
        price = request.POST.get('price', '')
        if price:
            try:
                item.price = float(price)
            except ValueError:
                item.price = None
        else:
            item.price = None
            
        item.save()
        messages.success(request, "Saved item updated successfully!")
        return redirect('my_world')
        
    return redirect('my_world')

# Delete Saved Item
@login_required
def delete_item(request, pk):
    item = get_object_or_404(SavedItem, pk=pk, user=request.user)
    if request.method == 'POST':
        item.delete()
        messages.success(request, "Item deleted successfully.")
    return redirect('my_world')

# Toggle AJAX Like
@login_required
@require_POST
def toggle_like(request, pk):
    item = get_object_or_404(SavedItem, pk=pk)
    like_qs = Like.objects.filter(user=request.user, item=item)
    
    if like_qs.exists():
        like_qs.delete()
        liked = False
    else:
        Like.objects.create(user=request.user, item=item)
        liked = True
        
    like_count = item.likes.count()
    return JsonResponse({
        'success': True,
        'liked': liked,
        'like_count': like_count
    })

# Add AJAX Comment
@login_required
@require_POST
def add_comment(request, pk):
    item = get_object_or_404(SavedItem, pk=pk)
    content = request.POST.get('content', '').strip()
    
    if not content:
        return JsonResponse({'success': False, 'error': 'Comment content cannot be empty.'}, status=400)
        
    comment = Comment.objects.create(
        user=request.user,
        item=item,
        content=content
    )
    
    return JsonResponse({
        'success': True,
        'comment': {
            'username': comment.user.username,
            'avatar_url': comment.user.profile.profile_picture.url if comment.user.profile.profile_picture else 'https://cdn-icons-png.flaticon.com/512/149/149071.png',
            'content': comment.content,
            'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M')
        },
        'comment_count': item.comments.count()
    })

# User Profile page (public/private profiles)
@login_required
def profile_view(request, username):
    profile_user = get_object_or_404(User, username=username)
    profile = profile_user.profile
    
    # If viewing self, show all items. Otherwise show only public items.
    if profile_user == request.user:
        items = SavedItem.objects.filter(user=profile_user)
    else:
        items = SavedItem.objects.filter(user=profile_user, is_public=True)
        
    is_following = request.user.profile.follows.filter(pk=profile.pk).exists()
    
    return render(request, 'myworld/profile.html', {
        'profile_user': profile_user,
        'profile': profile,
        'items': items,
        'is_following': is_following,
        'followers_count': profile.followers.count(),
        'following_count': profile.follows.count()
    })

# Follow / Unfollow toggle
@login_required
@require_POST
def toggle_follow(request, username):
    user_to_follow = get_object_or_404(User, username=username)
    if user_to_follow == request.user:
        return JsonResponse({'success': False, 'error': 'You cannot follow yourself.'}, status=400)
        
    profile = request.user.profile
    target_profile = user_to_follow.profile
    
    if profile.follows.filter(pk=target_profile.pk).exists():
        profile.follows.remove(target_profile)
        following = False
    else:
        profile.follows.add(target_profile)
        following = True
        
    return JsonResponse({
        'success': True,
        'following': following,
        'followers_count': target_profile.followers.count(),
        'following_count': target_profile.follows.count()
    })

# Update User Profile (Bio & Profile picture)
@login_required
@require_POST
def update_profile(request):
    profile = request.user.profile
    bio = request.POST.get('bio', '').strip()
    profile_picture = request.FILES.get('profile_picture')
    
    profile.bio = bio
    if profile_picture:
        profile.profile_picture = profile_picture
    profile.save()
    
    messages.success(request, "Profile updated successfully!")
    return redirect('profile_view', username=request.user.username)

# Dashboard & Analytics
@login_required
def dashboard_view(request):
    total_saved = SavedItem.objects.filter(user=request.user).count()
    public_items = SavedItem.objects.filter(user=request.user, is_public=True).count()
    private_items = SavedItem.objects.filter(user=request.user, is_public=False).count()
    
    # Recent activity
    recent_saves = SavedItem.objects.filter(user=request.user)[:5]
    
    # Analytics data (Group by Category and Platform)
    category_data = SavedItem.objects.filter(user=request.user).values('category').annotate(count=Count('id'))
    platform_data = SavedItem.objects.filter(user=request.user).values('platform').annotate(count=Count('id'))
    
    # Likes received on public items
    likes_received = Like.objects.filter(item__user=request.user).count()
    
    return render(request, 'myworld/dashboard.html', {
        'total_saved': total_saved,
        'public_items': public_items,
        'private_items': private_items,
        'recent_saves': recent_saves,
        'category_data': category_data,
        'platform_data': platform_data,
        'likes_received': likes_received
    })
