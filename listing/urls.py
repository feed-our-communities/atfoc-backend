from django.urls import path
from . import views

app_name = 'listing'
urlpatterns=[
    path('donations/', views.DonationView.as_view(), name='donations'),
    path('requests/', views.RequestView.as_view(), name='requests'),
]
