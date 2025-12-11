from django.urls import path
from accounts import views

app_name = "account"

urlpatterns = [
    path("kyc-reg/", views.kyc_registration, name="kyc-reg"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("account/", views.account, name="account"),
    path("kyc-review/", views.kyc_under_review, name="kyc_under_review"),
    path("notification/", views.notification, name="notification"),
    path("market/", views.market, name="market"),
    path("profile/", views.profile, name="profile"),


]
