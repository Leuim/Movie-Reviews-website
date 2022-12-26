from django.urls import path
from main import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('signup', views.SignupView.as_view(), name='signup'),
    path('login', views.LoginView.as_view(), name='login'),
    path('logout', views.LogoutView.as_view(), name='logout'),
    path('post-review', views.PostReviewView.as_view(), name='post-review'),
    path('review/<str:id>', views.ReviewView.as_view(), name='review'),
    path('review/<str:review_id>/post-comment', views.PostCommentView.as_view(), name='post-comment'),
]
