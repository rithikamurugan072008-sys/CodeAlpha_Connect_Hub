from django.urls import path
from . import views

urlpatterns = [
    # Main Views
    path('', views.feed_view, name='feed'),
    path('explore/', views.explore_view, name='explore'),
    path('bookmarks/', views.bookmarks_view, name='bookmarks'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('profile/<str:username>/', views.profile_view, name='profile'),
    path('edit-profile/', views.edit_profile_view, name='edit_profile'),
    path('post/<int:post_id>/', views.post_detail_view, name='post_detail'),

    # Auth Views
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('quick-login/<str:username>/', views.quick_login_api, name='quick_login'),

    # Interactive APIs
    path('api/post/create/', views.create_post_api, name='api_create_post'),
    path('api/post/<int:post_id>/delete/', views.delete_post_api, name='api_delete_post'),
    path('api/post/<int:post_id>/like/', views.toggle_like_api, name='api_toggle_like'),
    path('api/post/<int:post_id>/bookmark/', views.toggle_bookmark_api, name='api_toggle_bookmark'),
    path('api/post/<int:post_id>/comment/', views.add_comment_api, name='api_add_comment'),
    path('api/comment/<int:comment_id>/delete/', views.delete_comment_api, name='api_delete_comment'),
    path('api/user/<str:username>/follow/', views.toggle_follow_api, name='api_toggle_follow'),
    path('api/user/<str:username>/followers/', views.followers_list_api, name='api_followers_list'),
    path('api/user/<str:username>/following/', views.following_list_api, name='api_following_list'),
    path('api/search/', views.search_api, name='api_search'),
    path('api/notifications/read-all/', views.mark_notifications_read_api, name='api_notifications_read'),
]
