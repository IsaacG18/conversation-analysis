from django.urls import path

from . import views
urlpatterns = [
    path("", views.homepage, name="homepage"),
    path("upload", views.upload, name="upload"),
    path("content/<slug:file_slug>", views.content_review, name="content_review"),
    path('json_content/<slug:file_slug>/', views.json_content_review, name='json_content_review'), 
] 