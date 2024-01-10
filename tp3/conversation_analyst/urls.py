from django.urls import path

from . import views
urlpatterns = [
    path("", views.homepage, name="homepage"),
    path("upload", views.upload, name="upload"),
    path('delimiter-settings/', views.delimiter_settings, name='delimiter_settings'),
    path("content/<slug:file_slug>", views.content_review, name="content_review"),
    path('filter/', views.filter_view, name='filter_view'),
    path('settings', views.settings_page, name='settings'),
    path('create_suite', views.create_suite, name='create_suite'),
    path('select_suite', views.select_suite, name='select_suite'),
    path('create_keyword', views.create_keyword, name='create_keyword'),
    path('delete_suite', views.delete_suite, name='delete_suite'),
    path('delete_keyword', views.delete_keyword, name='delete_keyword'),
    path('check_suite', views.check_suite, name='check_suite'),
    path('risk_update', views.risk_update, name='risk_update'),
] 