from django.db import models
import uuid
from django.contrib.auth.models import User, AbstractUser, Group, Permission
from django.utils import timezone

# Create your models here.
class User(AbstractUser):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    is_teacher = models.BooleanField(default=False, verbose_name='Is Teacher', help_text='Designates whether the user is a teacher.')
    is_student = models.BooleanField(default=False, verbose_name='Is Student', help_text='Designates whether the user is a student.')
    groups = models.ManyToManyField(Group, blank=True, related_name='custom_user_groups', help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', verbose_name='groups')
    user_permissions = models.ManyToManyField(Permission, blank=True, related_name='custom_user_permissions', help_text='Specific permissions for this user.', verbose_name='user permissions')

    def __str__(self):
        return self.username

class Assignment(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    title = models.CharField(max_length=200)
    description = models.TextField()
    due_date = models.DateField()
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assignments_posted')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title

class Submission(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submission_made')
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    github_repo_url = models.URLField(max_length=200, null=True, blank=True)
    commit_hash = models.CharField(max_length=40, null=True, blank=True, help_text='Option: commit hash to review')
    submitted_at = models.DateTimeField(auto_now_add=True)
    review_feedback = models.TextField(null=True, blank=True, help_text='Feedback from the teacher')
    status = models.CharField(max_length=20)  # e.g., 'completed', 'in-progress'
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('student', 'assignment')
    
    def __str__(self):
        return f"Submission for {self.assignment.title} by {self.student.username}"