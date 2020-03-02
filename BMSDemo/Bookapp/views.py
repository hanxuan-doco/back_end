from django.shortcuts import render, redirect, HttpResponse
from Bookapp.models import *


# Create your views here.
def add_book(request):
    """
    添加书籍信息的视图函数
    :param request:
    :return:
    """
    if request.method == 'POST':
        title = request.POST.get("title")
        price = request.POST.get("price")
        date = request.POST.get("date")
        publish = request.POST.get("publish")
        authors = request.POST.getlist('authors')
        book_obj = Book.objects.create(title=title, price=price, pub_date=date, publish_id=publish)
        book_obj.authors.add(*authors)
        return redirect('Bookapp:books')

    pub_list = Publish.objects.all()
    aut_list = Author.objects.all()

    return render(request, 'add_book.html', {'pub_list': pub_list, 'aut_list': aut_list})


def mod_book(request, id):
    '''
    主页的视图函数
    :param request:
    :param id:
    :return:
    '''
    mod_obj = Book.objects.filter(nid=id).first()
    if request.method == 'POST':
        title = request.POST.get("title")
        price = request.POST.get("price")
        date = request.POST.get("date")
        publish = request.POST.get("publish")
        authors = request.POST.getlist('authors')
        Book.objects.filter(pk=id).update(title=title, price=price, pub_date=date, publish_id=publish)
        mod_obj.authors.set(authors)
        return redirect('Bookapp:books')

    pub_list = Publish.objects.all()
    aut_list = Author.objects.all()
    return render(request, 'modbook.html', {'mod_obj': mod_obj, 'pub_list': pub_list, 'aut_list': aut_list})


def books(request):
    '''
    返回书籍信息的视图函数
    :param request:
    :return:
    '''
    book_list = Book.objects.all()

    return render(request, 'books.html', {'book_list': book_list})


def del_book(request, id):
    Book.objects.filter(nid=id).delete()
    return redirect('Bookapp:books')


def aut_detail(request, id, tag):
    if tag == "2":
        print(id)
        book_list = Book.objects.filter(authors__nid=id).all()
    else:
        book_list = Book.objects.filter(publish_id=id).all()
    return render(request, 'book_detail.html', locals())
