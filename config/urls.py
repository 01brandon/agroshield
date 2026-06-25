from django.contrib import admin
from apps.accounts.views import landing
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from apps.accounts.views import landing

urlpatterns = [
    path('',                      landing,                                                    name='home'),
    path('admin/',                admin.site.urls),
    path('api/schema/',           SpectacularAPIView.as_view(),                               name='schema'),
    path('api/schema/swagger-ui/',SpectacularSwaggerView.as_view(url_name='schema'),         name='swagger-ui'),
    path('api/schema/redoc/',     SpectacularRedocView.as_view(url_name='schema'),           name='redoc'),
    path('api/auth/',             include('apps.accounts.urls')),
    path('api/farms/',            include('apps.farms.urls')),
    path('api/disease/',          include('apps.disease.urls')),
    path('api/weather/',          include('apps.weather.urls')),
    path('api/marketplace/',      include('apps.marketplace.urls')),
    path('api/seeds/',            include('apps.seeds.urls')),
    path('api/cooperatives/',     include('apps.cooperatives.urls')),
    path('api/livestock/',        include('apps.livestock.urls')),
    path('api/insurance/',        include('apps.insurance.urls')),
    path('api/soil/',             include('apps.soil.urls')),
    path('api/satellite/',        include('apps.satellite.urls')),
    path('api/forum/',            include('apps.forum.urls')),
    path('api/academy/',          include('apps.academy.urls')),
    path('api/traceability/',     include('apps.traceability.urls')),
    path('api/carbon/',           include('apps.carbon.urls')),
    path('api/drones/',           include('apps.drones.urls')),
    path('api/finance/',          include('apps.finance.urls')),
    path('api/ivr/',              include('apps.ivr.urls')),
    path('api/alerts/',           include('apps.alerts.urls')),
    path('api/equipment/',        include('apps.equipment.urls')),
    path('api/campaigns/',        include('apps.campaigns.urls')),
]
