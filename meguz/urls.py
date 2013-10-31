from django.conf.urls.defaults import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'meguz.views.home', name='home'),
    # url(r'^meguz/', include('meguz.foo.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', 'main.views.Home', name='home'),
    url(r'^oferta/(?P<company_slug>.*)/(?P<offer_slug>.*)/$', 'main.views.SpecificOffer', name='offer'),
    url(r'^empresa/contacto/$', 'main.views.CompanyContact', name='company_contact'),
    url(r'^empresa/registro/ok$', 'main.views.CompanyThanks', name='company_thanks'),
)
