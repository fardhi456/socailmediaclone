from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/<str:username>/', views.profile_view, name='profile'),
    path('post/delete/<int:post_id>/', views.delete_post, name='delete_post'),
    path('post/<int:post_id>/like/', views.toggle_like, name='toggle_like'),
    path('follow/<str:username>/', views.toggle_follow, name='toggle_follow'),
    path('post/create/', views.create_post_view, name='create_post'),
    path('profile/<str:username>/followers/', views.followers_list, name='followers_list'),
    path('profile/<str:username>/following/', views.following_list, name='following_list'),
    path('search/', views.search, name='search'),
    path('post/<int:post_id>/edit/', views.edit_post, name='edit_post'),
    path('post/<int:post_id>/save/', views.toggle_save_post, name='toggle_save_post'),
    path('saved/', views.saved_posts, name='saved_posts'),

]

