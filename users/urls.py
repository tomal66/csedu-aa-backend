from django.urls import path
from users.views import obtain_auth_token, logout
from . import views

urlpatterns = [
    path('login/', obtain_auth_token, name='token_obtain_pair'),
    path('logout/',logout, name = 'logout'),
    path('user/',views.SelfUserDetail.as_view(), name = 'user_self'),
    path('users/create/', views.UserCreate.as_view(), name = 'user_create'),
    path('users/', views.UserList.as_view(), name='user_list'),
    path('users/<str:username>/', views.UserDetail.as_view(), name='user_detail'),
    path('basic-profile/',views.SelfProfileDetail.as_view(), name = 'basic_profile_self'),
    path('basic-profiles/', views.ProfileList.as_view(), name='basic_profile_list'),
    path('basic-profiles/<str:username>/', views.ProfileDetail.as_view(), name='basic_profile_detail'),
    path('referrals/create/', views.ReferralCreate.as_view(), name='referral_create'),
    path('profile/social-media-links/', views.SocialMediaLinkListView.as_view(), name='social-media-links'),
    path('profile/create/social-media-links/', views.SocialMediaLinkCreateView.as_view(), name='create-social-media-link'),
    path('profile/present-address/', views.PresentAddressDetailView.as_view(), name='present-address'),
    path('profile/create/present-address/', views.PresentAddressCreateView.as_view(), name='create-present-address'),
    path('profile/skills/', views.SkillListView.as_view(), name='skills'),
    path('profile/create/skills/', views.SkillCreateView.as_view(), name='create-skill'),
    path('profile/work-experiences/', views.WorkExperienceListView.as_view(), name='work-experiences'),
    path('profile/create/work-experiences/', views.WorkExperienceCreateView.as_view(), name='create-work-experience'),
    path('profile/academic-histories/', views.AcademicHistoryListView.as_view(), name='academic-histories'),
    path('profile/create/academic-histories/', views.AcademicHistoryCreateView.as_view(), name='create-academic-history'),
    path('profile/social-media-links/<int:pk>/', views.SocialMediaLinkDetailView.as_view(), name='social-media-link-detail'),
    path('profile/skills/<int:pk>/', views.SkillDetailView.as_view(), name='skill-detail'),
    path('profile/work-experiences/<int:pk>/', views.WorkExperienceDetailView.as_view(), name='work-experience-detail'),
    path('profile/academic-histories/<int:pk>/', views.AcademicHistoryDetailView.as_view(), name='academic-history-detail'),
    path('profiles/<str:username>/social-media-links/', views.SocialMediaLinkUserListView.as_view(), name='user-social-media-links'),
    path('profiles/<str:username>/skills/', views.SkillUserListView.as_view(), name='user-skills'),
    path('profiles/<str:username>/work-experiences/', views.WorkExperienceUserListView.as_view(), name='user-work-experiences'),
    path('profiles/<str:username>/academic-histories/', views.AcademicHistoryUserListView.as_view(), name='user-academic-histories'),
    path('profiles/<str:username>/present-address/', views.PresentAddressUserDetailView.as_view(), name='user-present-address'),
    path('profile/', views.OwnFullProfileView.as_view(), name = 'own_full_profile'),
    path('profiles/<str:username>/', views.FullProfileDetail.as_view(), name='full_profile_detail')
]
