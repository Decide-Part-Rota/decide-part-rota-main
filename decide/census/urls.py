from django.urls import path, include
from . import views


urlpatterns = [
    path('', views.CensusCreate.as_view(), name='census_create'),
    path('<int:voting_id>/', views.CensusDetail.as_view(), name='census_detail'),
    path('add/', views.census_add, name='census_add'),
    path('add/add_to_census', views.add_to_census),
    path('remove/', views.census_remove, name='census_remove'),
    path('remove/remove_from_census', views.remove_from_census),
    path('export/', views.export_census),
    path('export/exporting_census/', views.exporting_census),
    path('import/', views.import_census),
    path('import/importing_census/', views.importing_census)
]
