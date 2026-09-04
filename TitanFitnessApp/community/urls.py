from django.urls import path

from community import views


urlpatterns = [
    path('', views.community_view, name='community'),
    path(
        'posts/<int:post_id>/comments/',
        views.create_comment_view,
        name='create_comment',
    ),
    path(
        'posts/<int:post_id>/like/',
        views.toggle_like_view,
        name='toggle_like',
    ),
]
