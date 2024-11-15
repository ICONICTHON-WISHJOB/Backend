from django.urls import path
from . import views

urlpatterns = [
    path('api/myPage/<str:userId>/', views.MyPageView.as_view(), name='my_page'),
    path('api/myPage/<str:userId>/interest/', views.MyPageInterestView.as_view(), name='my_page_interest'),
    path('api/myPage/reservationList/<str:userId>/<str:doneType>/', views.ReservationListView.as_view(), name='my_page_interest'),
    path('myPage/api/myPage/interest/new', views.UpdateInterestCategoriesView.as_view(), name='my_page_interest'),
    path('api/myPage/reservationList/remove/<str:userId>/<str:boothID>/', views.RemoveReservationView.as_view(), name='my_page_interest'),
    path('api/myPage/resume/<str:userId>/', views.ResumeView.as_view(), name='my_page_interest'),
]