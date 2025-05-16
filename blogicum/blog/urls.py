from django.urls import path

from . import views


app_name = 'blog'

urlpatterns = [
    path('', views.HomePageView.as_view(), name='index'),
    path('category/<slug:category_slug>/', views.CategoryPostsView.as_view(), name='category_posts'),
    path('posts/create/', views.PostCreateView.as_view(), name='create_post'),
    path('posts/<int:pk>/edit/', views.PostUpdateView.as_view(), name='edit_post'),
    path('posts/<int:pk>/delete/',
         views.PostDeleteView.as_view(), name='delete_post'),
    path('posts/<int:id>/comment/', views.add_comment, name='add_comment'),
    path('posts/<int:post_id>/edit_comment/<int:comment_id>/',
         views.edit_comment, name='edit_comment'),
    path('posts/<int:post_id>/delete_comment/<int:comment_id>/',
         views.delete_comment, name='delete_comment'),
    path('posts/<int:id>/', views.PostDetailView.as_view(), name='post_detail'),
    path('profile/edit/', views.ProfileUpdateView.as_view(), name='edit_profile'),
    path('profile/<str:username>/', views.ProfileView.as_view(), name='profile'),
]
