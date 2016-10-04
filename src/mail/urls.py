from django.conf.urls import url, include

from mail import views

urlpatterns = [
    url(r'^$', views.BaseTemplateView.as_view(), name='home'),
    # url(r'^recipients/$', views.RecipientsView.as_view(), name='recipients'),
    url(
        r'^recipients/', include(
            views.RecipientsView.get_urls(namespace='recipients'),
            namespace='recipients'
        )
    ),
    url(r'^emails/$', views.EmailsView.as_view(), name='emails'),
    url(r'^send_emails/$', views.send_emails, name='send_emails'),
    url(
        r'^web_view/(?P<url_token>.+)$',
        views.WebView.as_view(),
        name='web_view'
    ),
    url(
        r'^email/preview/(?P<email_pk>\d+)/$',
        views.email_preview,
        name='email_preview'
    )
]
