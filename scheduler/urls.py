from django.conf.urls import include, url
from django.conf import settings

from scheduler.views import index, schedule_year, presentations, presentation_detail, schedules, meeting, groups, \
    group_detail, presenters, presenter_detail, schedule_ics, raw_mails, send_request, send_announce, generate, \
    send_alert

# Enable the admin
from django.contrib import admin
from django.contrib.auth.views import login, logout

admin.autodiscover()

urlpatterns = [
    # index
    url(r'^$', index),

    # Presentations
    url(r'^presentation/$', presentations),
    url(r'^presentation/(?P<presentation_id>\d+)/$', presentation_detail),

    # Agenda
    url(r'^schedule/$', schedules),
    url(r'^schedule/(?P<year>\d+)/$', schedule_year),
    url(r'^schedule/(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)/$', meeting),

    # Groups
    url(r'^group/$', groups),
    url(r'^group/(?P<group_id>\d+)/$', group_detail),

    # Presenters
    url(r'^presenter/$', presenters),
    url(r'^presenter/(?P<presenter_id>\d+)/$', presenter_detail),

    # ICAL export
    url(r'^ical/schedule.ics$', schedule_ics),

    # Mails export
    url(r'^mails.txt$', raw_mails),

    # Mailing export
    url(r'^mailing/send_request/$', send_request),
    url(r'^mailing/send_announce/$', send_announce),

    # Account
    url(r'^accounts/login/$', admin.site.urls),
    url(r'^accounts/logout/$', logout, {'template_name': 'logout.html'}),


    # Generate
    url(r'^generate/$', generate),

    # Send Alert
    url(r'^mailing/send_alert/$', send_alert),

    # (r'^browse/(.*)', databrowse.site.root),
    # url(r'^admin/(.*)', admin.site.root),
    # url(r'^accounts/login/$', login, {'template_name': 'wai/login.html'}),
    # url(r'^accounts/logout/$', logout, {'template_name': 'wai/logout.html'}),
    # url(r'^media/(?P<path>.*)$', 'django.views.info.serve', {'document_root': settings.MEDIA_ROOT})
]
