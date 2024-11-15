from django.urls import path
from . import views

urlpatterns = [
    path('waitCnt/<int:id>', views.WaitCountView.as_view(), name='wait_count'),
    path('waitList/<int:id>', views.WaitListView.as_view(), name='wait_list'),
    path('consultDone/<str:id>/', views.ConsultationDoneView.as_view(), name='consult_done'),
    path('consultDelete/<str:id>/', views.ConsultDeleteView.as_view(), name='consult_delete'),
    path('consultDoneList/', views.CompletedConsultationsListView.as_view(), name='consult_list'),
]
