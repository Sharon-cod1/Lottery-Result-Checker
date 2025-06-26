from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('check/', views.check_result, name='check_result'),
    path('past-results/', views.past_results, name='past_results'),
]