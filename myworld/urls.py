from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing, name='landing'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    path('my-world/', views.my_world, name='my_world'),
    path('global-world/', views.global_world, name='global_world'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    path('add-item/', views.add_item, name='add_item'),
    path('edit-item/<int:pk>/', views.edit_item, name='edit_item'),
    path('delete-item/<int:pk>/', views.delete_item, name='delete_item'),
    
    path('like/<int:pk>/', views.toggle_like, name='toggle_like'),
    path('comment/<int:pk>/', views.add_comment, name='add_comment'),
    
    path('profile/<str:username>/', views.profile_view, name='profile_view'),
    path('follow/<str:username>/', views.toggle_follow, name='toggle_follow'),
    path('update-profile/', views.update_profile, name='update_profile'),
]
