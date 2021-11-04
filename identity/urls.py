from django.urls import path
from . import views
from rest_framework.routers import DefaultRouter

app_name = 'identity_management'
urlpatterns=[
    path('register/', views.RegistrationView.as_view(), name='user_registration'),
    path('login/', views.CustomAuthToken.as_view(), name='token_auth'),
    path('info/', views.UserInfoView.as_view(), name='user_info')
]
router = DefaultRouter()
router.register(r'organization', views.OrganizationViewSet)
urlpatterns += router.urls
