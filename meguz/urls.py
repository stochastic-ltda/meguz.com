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

    url(r'^premios/participar/form/(?P<prize_id>.*)/(?P<user_token>.*)/$', 'main.views.PrizeParticipateForm', name='offer_participate_form'),    
    url(r'^premios/(?P<offer_id>.*)/(?P<offer_slug>.*)/$', 'main.views.PrizeView', name='offer_view'), 

    url(r'^meguz/update/multimedia/(?P<prize_id>.*)/(?P<user_token>.*)/$', 'main.views.MeguzUpdateMultimedia', name='meguz_update_multimedia'),        
    url(r'^meguz/(?P<meguz_id>.*)/editar/$', 'main.views.MeguzEdit', name='meguz_edit'),
    url(r'^meguz/(?P<meguz_id>.*)/eliminar/$', 'main.views.MeguzDelete', name='meguz_delete'),
    url(r'^meguz/(?P<meguz_id>.*)/eliminar-video/$', 'main.views.MeguzDeleteVideo', name='meguz_delete_video'),
    url(r'^meguz/edit/form/(?P<meguz_id>.*)/(?P<user_token>.*)/$', 'main.views.MeguzEditForm', name='meguz_edit_form'),
    url(r'^meguz/(?P<meguz_id>.*)/(?P<meguz_slug>.*)/$', 'main.views.MeguzView', name='meguz_view'),

    url(r'^usuario/login$', 'main.views.UserLogin', name="user_login"),
    url(r'^usuario/mis-meguz$', 'main.views.UserMisMeguz', name="user_mismeguz"),
    url(r'^usuario/mis-datos$', 'main.views.UserMisDatos', name="user_misdatos"),
    url(r'^usuario/premios/(?P<offer_id>.*)/participar/$', 'main.views.PrizeParticipate', name='user_participate'),

    # backoffice empresa
    url(r'^epanel/$', 'boe.views.Login', name='boe_login'),
    url(r'^epanel/salir$', 'boe.views.Logout', name='boe_salir'),
    url(r'^epanel/perfil$', 'boe.views.Profile', name='boe_profile'),
    url(r'^epanel/premios/lista$', 'boe.views.PrizeList', name='boe_offer_list'),
    url(r'^epanel/premios/nuevo$', 'boe.views.PrizeNew', name='boe_offer_new'),
    url(r'^epanel/premios/editar/(?P<offer_id>.*)/$', 'boe.views.PrizeEdit', name='boe_offer_edit'),
    url(r'^epanel/premios/multimedia/(?P<offer_id>.*)/$', 'boe.views.PrizeMultimedia', name='boe_offer_multimedia'),    

    # boss zone
    url(r'^boss/$', 'boss.views.Home', name='boss_home'),
    url(r'^boss/premios/pendientes$', 'boss.views.PrizePendingApproval', name='boss_prize_pending'),
    url(r'^boss/premios/aprobar/(?P<prize_id>.*)/$', 'boss.views.PrizeApprove', name='boss_prize_approve'),
    url(r'^boss/premios/rechazar/(?P<prize_id>.*)/$', 'boss.views.PrizeReject', name='boss_prize_reject'),
    url(r'^boss/meguz/pendientes$', 'boss.views.MeguzPendingApproval', name='boss_prize_pending'),
    url(r'^boss/meguz/aprobar/(?P<meguz_id>.*)/$', 'boss.views.MeguzApprove', name='boss_meguz_approve'),
    url(r'^boss/meguz/rechazar/(?P<meguz_id>.*)/$', 'boss.views.MeguzReject', name='boss_meguz_reject'),


    # youtube
    (r'^epanel/youtube/', include('django_youtube.urls')),
)
