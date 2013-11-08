from django.conf.urls.defaults import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'meguz.views.home', name='home'),
    # url(r'^meguz/', include('meguz.foo.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', 'main.views.Home', name='home'),
    # url(r'^oferta/(?P<company_slug>.*)/(?P<offer_slug>.*)/$', 'main.views.SpecificOffer', name='offer'),
    url(r'^empresa/lista/$', 'main.views.CompanyList', name='company_list'),
    url(r'^empresa/registro/$', 'main.views.CompanyContact', name='company_contact'),
    url(r'^empresa/registro/ok$', 'main.views.CompanyThanks', name='company_thanks'),

    # backoffice empresa
    url(r'^boe/$', 'boe.views.Login', name='boe_login'),
    url(r'^boe/salir$', 'boe.views.Logout', name='boe_salir'),
    url(r'^boe/ofertas/lista$', 'boe.views.OfferList', name='boe_offer_list'),
    url(r'^boe/ofertas/nueva$', 'boe.views.OfferNew', name='boe_offer_new'),
    url(r'^boe/ofertas/multimedia/(?P<offer_id>.*)/$', 'boe.views.OfferMultimedia', name='boe_offer_multimedia'),

    # youtube
    (r'^boe/youtube/', include('django_youtube.urls')),
)
