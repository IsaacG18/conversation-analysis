from django.urls import path

from . import views
urlpatterns = [
    path("", views.homepage, name="homepage"),
    path("upload", views.upload, name="upload"),
    path("content/<slug:file_slug>", views.content_review, name="content_review"),
    path('filter/', views.filter_view, name='filter_view'),
    path("export_view/<slug:file_slug>", views.export_view, name='export_view'),
] 