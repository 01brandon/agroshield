from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from apps.accounts.views import (
    landing, login_page, register_page, dashboard_home,
    farms_page, disease_page, weather_page, marketplace_page,
    forum_page, academy_page, finance_page, insurance_page, carbon_page,
)

urlpatterns = [
    # landing
    path('',                        landing,           name='home'),

    # auth pages
    path('auth/login',              login_page,        name='login-page'),
    path('register',                register_page,     name='register-page'),

    # dashboard pages
    path('dashboard/',              dashboard_home,    name='dashboard-home'),
    path('dashboard/farms/',        farms_page,        name='farms-page'),
    path('dashboard/disease/',      disease_page,      name='disease-page'),
    path('dashboard/weather/',      weather_page,      name='weather-page'),
    path('dashboard/marketplace/',  marketplace_page,  name='marketplace-page'),
    path('dashboard/forum/',        forum_page,        name='forum-page'),
    path('dashboard/academy/',      academy_page,      name='academy-page'),
    path('dashboard/finance/',      finance_page,      name='finance-page'),
    path('dashboard/insurance/',    insurance_page,    name='insurance-page'),
    path('dashboard/carbon/',       carbon_page,       name='carbon-page'),

    # admin
    path('admin/',                  admin.site.urls),

    # api docs
    path('api/schema/',             SpectacularAPIView.as_view(),                        name='schema'),
    path('api/schema/swagger-ui/',  SpectacularSwaggerView.as_view(url_name='schema'),  name='swagger-ui'),
    path('api/schema/redoc/',       SpectacularRedocView.as_view(url_name='schema'),    name='redoc'),

    # api endpoints
    path('api/auth/',               include('apps.accounts.urls')),
    path('api/farms/',              include('apps.farms.urls')),
    path('api/disease/',            include('apps.disease.urls')),
    path('api/weather/',            include('apps.weather.urls')),
    path('api/marketplace/',        include('apps.marketplace.urls')),
    path('api/seeds/',              include('apps.seeds.urls')),
    path('api/cooperatives/',       include('apps.cooperatives.urls')),
    path('api/livestock/',          include('apps.livestock.urls')),
    path('api/insurance/',          include('apps.insurance.urls')),
    path('api/soil/',               include('apps.soil.urls')),
    path('api/satellite/',          include('apps.satellite.urls')),
    path('api/forum/',              include('apps.forum.urls')),
    path('api/academy/',            include('apps.academy.urls')),
    path('api/traceability/',       include('apps.traceability.urls')),
    path('api/carbon/',             include('apps.carbon.urls')),
    path('api/drones/',             include('apps.drones.urls')),
    path('api/finance/',            include('apps.finance.urls')),
    path('api/ivr/',                include('apps.ivr.urls')),
    path('api/alerts/',             include('apps.alerts.urls')),
    path('api/equipment/',          include('apps.equipment.urls')),
    path('api/campaigns/',          include('apps.campaigns.urls')),
]
