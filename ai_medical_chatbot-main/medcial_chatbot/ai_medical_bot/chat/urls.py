from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat_view, name='chat'),
    # path('', view=views.opening_view, name='opening_view'),
]
