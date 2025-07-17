from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("wiki/<str:title>", views.entry, name="entry"),
    path("search/", views.search,name="search"),
    path("create/", views.create,name="create"),
    path("edit/<str:title>", views.edit, name="edit"),
    path("random/", views.random_page, name="random_page"),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
