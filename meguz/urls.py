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
    url(r'^premios/(?P<offer_id>.*)/(?P<offer_slug>.*)/$', 'main.views.PrizeView', name='offer_view'),

    # backoffice empresa
    url(r'^boe/$', 'boe.views.Login', name='boe_login'),
    url(r'^boe/salir$', 'boe.views.Logout', name='boe_salir'),
    url(r'^boe/perfil$', 'boe.views.Profile', name='boe_profile'),
    url(r'^boe/premios/lista$', 'boe.views.PrizeList', name='boe_offer_list'),
    url(r'^boe/premios/nuevo$', 'boe.views.PrizeNew', name='boe_offer_new'),
    url(r'^boe/premios/editar/(?P<offer_id>.*)/$', 'boe.views.PrizeEdit', name='boe_offer_edit'),
    url(r'^boe/premios/multimedia/(?P<offer_id>.*)/$', 'boe.views.PrizeMultimedia', name='boe_offer_multimedia'),    

    # youtube
    (r'^boe/youtube/', include('django_youtube.urls')),
)
