from django.conf.urls import url
from django.contrib.auth import views as auth_views
import asterfront.views as view
import views

urlpatterns = [
    url(r'^login$', view.LoginForm.as_view()),
    url(r'^logout$', auth_views.logout, {'next_page': '/'}),
    url(r'^$', views.Main.as_view()),
    url(r'^status$', views.QueueStats.as_view()),
    url(r'^abandon$', views.AbandonedCallsView.as_view()),
    url(r'^outcalls', views.OutCalls.as_view()),
    url(r'^addtoblack', views.BlackNumber.as_view(), name='addtoblack')
    ]