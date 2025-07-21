from django.urls import path
from .views import TeacherApiView, TeacherUpdateDeleteView

urlpatterns = [
    path('teachers/', TeacherApiView.as_view(), name='teacher-list'),
    path('teachers/<uuid:pk>/', TeacherUpdateDeleteView.as_view(), name='teacher-detail'),
]
