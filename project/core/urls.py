from django.urls import path
from .views import *

urlpatterns = [
    path('', HomeView.as_view(), name = 'home'),
    path('search/', BookSearchView.as_view(), name = 'search'),
    path('login/', CustomLoginView.as_view(), name = 'login'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('add-book/', AddBookToListView.as_view(), name='add_book'),
    path('remove-book/<int:userbook_id>/', RemoveBookFromListView.as_view(), name='remove_book'),
    path('update-status/<int:userbook_id>/', UpdateBookStatusView.as_view(), name='update_status'),
]