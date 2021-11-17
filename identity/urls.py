from django.urls import path
from . import views
from rest_framework.routers import DefaultRouter

app_name = 'identity_management'
urlpatterns=[
    path('register/', views.RegistrationView.as_view(), name='user_registration'),
    path('login/', views.CustomAuthToken.as_view(), name='token_auth'),
    path('info/', views.UserInfoView.as_view(), name='user_info'),
    path('org/members/', views.OrgMembersView.as_view(), name='org_members'),
]
router = DefaultRouter()
router.register(r'organization', views.OrganizationViewSet)
router.register(r'application', views.OrgApplicationViewSet)
router.register(r'joinrequests', views.JoinRequestViewSet)
urlpatterns += router.urls
