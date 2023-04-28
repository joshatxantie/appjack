from django.urls import path
from . import views, consumers
app_name = "game"

urlpatterns = [
    path('<str:join_code>/hit/', views.hit, name='hit'),
    path('<str:join_code>/stand/', views.stand, name='stand'),
    path('play/<str:join_code>/', views.play, name='play'),
    path('new/', views.new, name='new'),
    path('join/', views.join, name='join'),
    path('start/<str:join_code>/', views.start_game, name="start"),
    # other app urls
]