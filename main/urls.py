from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.loginPage, name='login'),
    path('logout/', views.logoutUser, name='logout'),
    path('register/', views.registerPage, name='register'),
    
    path('', views.home, name="home"),
    path('post/<str:pk>/', views.post, name="post"),
    path('profile/<str:pk>/', views.userProfile, name="user-profile"),

    path('create-post/', views.createPost, name="create-post"),
    path('update-post/<str:pk>/', views.updatePost, name="update-post"),
    path('delete-post/<str:pk>/', views.deletePost, name="delete-post"),
    path('delete-comment/<str:pk>/', views.deleteComment, name="delete-comment"),

    path('update-profile/', views.updateProfile, name="update-profile"),

    path('verify-email/', views.verify_email, name='verify-email'),
    path('verify-email/done/', views.verify_email_done, name='verify-email-done'),
    path('verify-email-confirm/<uidb64>/<token>/', views.verify_email_confirm, name='verify-email-confirm'),
    path('verify-email/complete/', views.verify_email_complete, name='verify-email-complete'),

    path('password-reset', views.password_reset_request, name="password-reset"),
    path('reset/<uidb64>/<token>', views.passwordResetConfirm, name='password-reset-confirm')
    
]