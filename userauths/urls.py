from django.urls import path
from userauths import views

app_name = "userauths"

urlpatterns = [
    path("register/", views.register_view, name="register"),    
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    # # path("activate/<uidb64>/<token>/", views.activate, name="activate"),
    path("forget_password/", views.forget_password, name="forget_password"),
    path("reset_validate/<uidb64>/<token>/", views.reset_validate, name="reset_validate"),
    path("reset_password/", views.reset_password, name="reset_password"),

    path("created/", views.account_created, name="account_created"),

    
    

]