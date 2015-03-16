from django.conf.urls import patterns, url
from api.views import default, user, session, testplan, auth, traffic, rule, testplan_rule, recording

urlpatterns = patterns('',
    url(r'^$', default.index),
    url(r'^version/{0,1}$', default.version),
    url(r'^test/{0,1}$', default.test),
    url(r'^user/{0,1}$', user.rest),
    url(r'^user/(\w+?)/{0,1}$', user.rest),
    url(r'^session/{0,1}$', session.rest),
    url(r'^session/(\w+?)/{0,1}$', session.rest),
    url(r'^testplan/{0,1}$', testplan.rest),
    url(r'^testplan/(\w+?)/{0,1}$', testplan.rest),
    url(r'^testplan/(?P<testplan_id>\w+?)/rule/{0,1}$', testplan_rule.rest),
    url(r'^testplan/(?P<testplan_id>\w+?)/rule/(?P<rule_id>\w+?)/{0,1}$', testplan_rule.rest),
    url(r'^auth/login/{0,1}$', auth.login),
    url(r'^traffic/{0,1}$', traffic.rest),
    url(r'^rule/{0,1}$', rule.rest),
    url(r'^rule/(\w+?)/{0,1}$', rule.rest),
    url(r'^recording/{0,1}$', recording.rest),
    url(r'^recording/(?P<recording_id>)/{0,1}$', recording.rest),
    url(r'^recording/(?P<recording_id>)/start/{0,1}$', recording.start),
    url(r'^recording/(?P<recording_id>)/stop/{0,1}$', recording.stop),
)
