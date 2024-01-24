from django.urls import path
from django.conf import settings
from django.conf.urls.static import static


from . import views
urlpatterns = [
    path("", views.homepage, name="homepage"),
    path("upload", views.upload, name="upload"),
    path("content/<slug:file_slug>", views.content_review, name="content_review"),
    path('filter/', views.filter_view, name='filter_view'),
    path('/<str:query>/', views.homepage, name='homepage'),
    path('settings', views.settings_page, name='settings'),
    path('create_suite', views.create_suite, name='create_suite'),
    path('select_suite', views.select_suite, name='select_suite'),
    path('create_keyword', views.create_keyword, name='create_keyword'),
    path('delete_suite', views.delete_suite, name='delete_suite'),
    path('delete_keyword', views.delete_keyword, name='delete_keyword'),
    path('check_suite', views.check_suite, name='check_suite'),
    path('risk_update', views.risk_update, name='risk_update'),
    path('rename_file', views.rename_file, name='rename_file'),
    path('create_delim', views.create_delimiter, name='create_delim'),
    # path('delete_delim', views.delete_delimiter, name='delete_delim'),
    path('order_update', views.order_update, name='order_update'),
    path('settings_delim', views.settings_delim, name='settings_delim'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)