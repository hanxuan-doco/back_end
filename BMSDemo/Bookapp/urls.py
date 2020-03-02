from django.contrib import admin
from django.urls import path, re_path, include
from Bookapp import views

app_name = 'app01'
urlpatterns = [
    re_path(r'^addbook/', views.add_book, name='addbook'),
    re_path(r'^books/', views.books, name='books'),
    re_path(r'^bookapp/books/(\d+)/delete',views.del_book,name='delete'),
    re_path(r'^bookapp/books/(\d+)/modify',views.mod_book,name='modify'),
    re_path(r'^bookapp/books/(\d+)/(\d+)/aut_detail/',views.aut_detail,name='aut_detail'),
]