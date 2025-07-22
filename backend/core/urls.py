from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token # Default DRF token view
from core.views import (
    CustomAuthToken,
    RegisterStudentView,
    RegisterTeacherView,
    AssignmentListCreateView,
    AssignmentDetailView,
    SubmissionListCreateView,
    SubmissionDetailView,
    CodeReviewView,
)

urlpatterns = [
    path('login/', CustomAuthToken.as_view(), name='api_login'),
    path('register/student/', RegisterStudentView.as_view(), name='register_student'),
    path('register/teacher/', RegisterTeacherView.as_view(), name='register_teacher'),

    path('assignments/', AssignmentListCreateView.as_view(), name='assignment_list_create'),
    path('assignments/<uuid:pk>/', AssignmentDetailView.as_view(), name='assignment_detail'),

    path('submissions/', SubmissionListCreateView.as_view(), name='submission_list_create'),
    path('submissions/<uuid:pk>/', SubmissionDetailView.as_view(), name='submission_detail'),
    path('submissions/<uuid:submission_id>/review/', CodeReviewView.as_view(), name='code_review'),
]