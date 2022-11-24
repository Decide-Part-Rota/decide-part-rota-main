from django.urls import path, include
from . import views


urlpatterns = [
    path('', views.CensusCreate.as_view(), name='census_create'),
    path('<int:voting_id>/', views.CensusDetail.as_view(), name='census_detail'),
    path('add/', views.census_add, name='census_add'),
    path('add/add_to_census', views.add_to_census),
    path('remove/', views.census_remove, name='census_remove'),
    path('remove/remove_from_census', views.remove_from_census),
    path('add/by_group/age', views.census_age),
    path('add/by_group/age/create', views.add_by_age_to_census),
    path('add/by_group/gender', views.census_gender),
    path('add/by_group/gender/create', views.add_by_gender_to_census),
]
