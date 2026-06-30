from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from apps.accounts.views import (
    landing, login_page, register_page, dashboard_home,
    farms_page, disease_page, weather_page, marketplace_page,
    about_page, contact_page,
)

urlpatterns = [
    path('',                        landing,           name='home'),
    path('about/',                  about_page,        name='about'),
    path('contact/',                contact_page,      name='contact'),

    path('auth/login',              login_page,        name='login-page'),
    path('auth/login/',             login_page,        name='login-page-slash'),
    path('register',                register_page,     name='register-page'),
    path('register/',               register_page,     name='register-page-slash'),

    path('dashboard/',              dashboard_home,    name='dashboard-home'),
    path('dashboard/farms/',        farms_page,        name='farms-page'),
    path('dashboard/disease/',      disease_page,      name='disease-page'),
    path('dashboard/weather/',      weather_page,      name='weather-page'),
    path('dashboard/marketplace/',  marketplace_page,  name='marketplace-page'),
    path('dashboard/forum/',        forum_page,        name='forum-page'),
    path('dashboard/finance/',      finance_page,      name='finance-page'),
    path('dashboard/carbon/',       carbon_page,       name='carbon-page'),

    # allauth handles google oauth flow
    path('accounts/',               include('allauth.urls')),

    path('admin/',                  admin.site.urls),

    path('api/schema/',             SpectacularAPIView.as_view(),                       name='schema'),
    path('api/schema/swagger-ui/',  SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/',       SpectacularRedocView.as_view(url_name='schema'),   name='redoc'),

    path('api/auth/',               include('apps.accounts.urls')),
    path('api/farms/',              include('apps.farms.urls')),
    path('api/disease/',            include('apps.disease.urls')),
    path('api/weather/',            include('apps.weather.urls')),
    path('api/marketplace/',        include('apps.marketplace.urls')),
    path('api/seeds/',              include('apps.seeds.urls')),
    path('api/cooperatives/',       include('apps.cooperatives.urls')),
    path('api/livestock/',          include('apps.livestock.urls')),
    path('api/soil/',               include('apps.soil.urls')),
    path('api/satellite/',          include('apps.satellite.urls')),
    path('api/forum/',              include('apps.forum.urls')),
    path('api/traceability/',       include('apps.traceability.urls')),
    path('api/carbon/',             include('apps.carbon.urls')),
    path('api/drones/',             include('apps.drones.urls')),
    path('api/finance/',            include('apps.finance.urls')),
    path('api/ivr/',                include('apps.ivr.urls')),
    path('api/alerts/',             include('apps.alerts.urls')),
    path('api/equipment/',          include('apps.equipment.urls')),
    path('api/campaigns/',          include('apps.campaigns.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
