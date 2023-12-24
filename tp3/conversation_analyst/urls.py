from django.urls import path

from . import views
urlpatterns = [
    path("", views.homepage, name="homepage"),
    path("upload", views.upload, name="upload"),
    path("content/<slug:file_slug>", views.content_review, name="content_review"),
    path('filter/', views.filter_view, name='filter_view'),
    path('settings', views.settings_page, name='settings'),
    path('create_suite', views.create_suite, name='create_suite'),
] 