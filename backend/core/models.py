from django.db import models
import uuid
from django.contrib.auth.models import User

# Create your models here.
ROLE_CHOICES = [
    ('student', 'STUDENT'),
    ('teacher', 'TEACHER'),
]
class Semester(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    
    def __str__(self):
        return self.name

class Teacher(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='teacher')
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.user.username

class Student(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.user.username

class StudentEnrollment(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    enrollment_date = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.student.user.username} - {self.semester.name}"

class Assignment(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    title = models.CharField(max_length=200)
    description = models.TextField()
    due_date = models.DateField()
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.title

class Progress(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    status = models.CharField(max_length=20)  # e.g., 'completed', 'in-progress'
    submission_date = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.student.user.username} - {self.assignment.title} ({self.status})"