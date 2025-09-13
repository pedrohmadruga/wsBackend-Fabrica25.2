from django.urls import path
from .views import HomeView, BookSearchView

urlpatterns = [
    path('', HomeView.as_view(), name = 'home'),
    path('search/', BookSearchView.as_view(), name = 'search')
]