from django.urls import path
from . import views


urlpatterns = [
    #Acceder al listado con localhost:8000/voting/listadoVotaciones
    path('listadoVotaciones', views.VotacionList.mostrarVotacionesPublicas),
    path('', views.VotingView.as_view(), name='voting'),
    path('<int:voting_id>/', views.VotingUpdate.as_view(), name='voting'),
]
