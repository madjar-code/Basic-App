from django.urls import path

from posts.api.views import *


urlpatterns = [
    path('', PostList.as_view()),
    path('<slug:slug>/', PostDetail.as_view()),
]
