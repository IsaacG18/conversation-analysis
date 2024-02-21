from django.urls import path
from django.conf import settings
from django.conf.urls.static import static


from . import views
urlpatterns = [
    path("", views.homepage, name="homepage"),
    path("upload", views.upload, name="upload"),
    path("content/<slug:file_slug>", views.content_review, name="content_review"),
    path("content/chatgpt_page/search_chats", views.search_chats, name="search_chats"),
    path("content/chatgpt_page/<slug:chatgpt_slug>", views.chatgpt_page, name='chatgpt_page'),
    path("content/chatgpt_page/", views.chatgpt_page_without_slug, name='chatgpt_page_without_slug'),
    path("message/", views.message, name='message'),
    path('filter/', views.filter_view, name='filter_view'),
    path('quick_chat_message/', views.quick_chat_message, name='quick_chat_message'),
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
    path('create_delim', views.create_delimiter, name='create_delim'),
    path('delete_delim', views.delete_delimiter, name='delete_delim'),
    path('order_update', views.order_update, name='order_update'),
    path('value_update', views.value_update, name='value_update'),
    path('settings_delim', views.settings_delim, name='settings_delim'),
    path('suite_selection/<slug:file_slug>', views.suite_selection, name='suite_selection'),
    path('clear_duplicate_submission', views.clear_duplicate_submission, name='clear_duplicate_submission'),
    path('settings/strictness', views.strictness_update, name='strictness_update'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
