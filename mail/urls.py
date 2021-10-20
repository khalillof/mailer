from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("password_reset", views.password_reset, name="password_reset"),
    path("question", views.security_guestions, name="question"),
    path("reset_confirm", views.password_reset_confirm, name="reset_confirm"),

    # dump db
    path("dbdump", views.dumpdb, name="dbdump"),
    # API Routes
    path("emails", views.compose, name="compose"),
    path("emails/<int:email_id>", views.email, name="email"),
    path("emails/<str:mailbox>", views.mailbox, name="mailbox"),
]
