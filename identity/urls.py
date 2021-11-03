from django.urls import path
from . import views
from rest_framework.authtoken.views import obtain_auth_token

app_name = 'identity_management'
urlpatterns=[
    path('register/', views.RegistrationView.as_view(), name='user_registration'),
    path('login/', views.CustomAuthToken.as_view(), name='token_auth'),
    path('info/', views.UserInfoView.as_view(), name='user_info'),
]
