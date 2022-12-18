from django.urls import path
from .views import VisualizerView
from . import views

urlpatterns = [
    path('<int:voting_id>/', VisualizerView.as_view()),
    path('graphics/<int:voting_id>', views.graphics),
]
