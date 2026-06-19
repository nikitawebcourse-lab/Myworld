from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    follows = models.ManyToManyField('self', symmetrical=False, related_name='followers', blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()
    else:
        UserProfile.objects.create(user=instance)


class SavedItem(models.Model):
    PLATFORM_CHOICES = [
        ('Amazon', 'Amazon'),
        ('Flipkart', 'Flipkart'),
        ('Instagram', 'Instagram'),
        ('YouTube', 'YouTube'),
        ('Facebook', 'Facebook'),
        ('Other', 'Other Website'),
    ]

    CATEGORY_CHOICES = [
        ('Shopping', 'Shopping'),
        ('Fashion', 'Fashion'),
        ('Electronics', 'Electronics'),
        ('Education', 'Education'),
        ('Travel', 'Travel'),
        ('Entertainment', 'Entertainment'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_items')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    url = models.URLField(max_length=1000)
    image_url = models.URLField(max_length=1000, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    platform = models.CharField(max_length=50, choices=PLATFORM_CHOICES, default='Other')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Shopping')
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    item = models.ForeignKey(SavedItem, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'item'], name='unique_user_item_like')
        ]

    def __str__(self):
        return f"{self.user.username} liked {self.item.title}"


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    item = models.ForeignKey(SavedItem, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.user.username} on {self.item.title}: {self.content[:30]}"
