from django.urls import path
from django.conf import settings
from django.conf.urls.static import static


from . import views
urlpatterns = [
    path("", views.homepage, name="homepage"),
    path("upload", views.upload, name="upload"),
    path("content/<slug:file_slug>", views.content_review, name="content_review"),
    path("content/chatgpt_page/<slug:chatgpt_slug>", views.chatgpt_page, name='chatgpt_page'),
    path("content/chatgpt_page/", views.chatgpt_page_without_slug, name='chatgpt_page_without_slug'),
    path("message/", views.message, name='message'),
    path('filter/', views.filter_view, name='filter_view'),
    path("chatgpt_new_message/", views.chatgpt_new_message, name="chatgpt_new_message"),
    path('/<str:query>/', views.homepage, name='homepage'),
    path('settings', views.settings_page, name='settings'),
    path("export_view/<slug:file_slug>", views.export_view, name='export_view'),
    path('create_suite', views.create_suite, name='create_suite'),
    path('select_suite', views.select_suite, name='select_suite'),
    path('create_keyword', views.create_keyword, name='create_keyword'),
    path('delete_suite', views.delete_suite, name='delete_suite'),
    path('delete_keyword', views.delete_keyword, name='delete_keyword'),
    path('check_suite', views.check_suite, name='check_suite'),
    path('risk_update', views.risk_update, name='risk_update'),
    path('rename_file', views.rename_file, name='rename_file'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)