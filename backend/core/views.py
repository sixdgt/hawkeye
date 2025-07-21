from django.shortcuts import render
from rest_framework import viewsets
from .models import Teacher, Student, Semester, Assignment, Progress, StudentEnrollment
from .serializers import TeacherSerializer, StudentSerializer, SemesterSerializer, AssignmentSerializer, ProgressSerializer

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# Create your views here.
class TeacherApiView(APIView):
    def get(self, request):
        teachers = Teacher.objects.all()
        serializer = TeacherSerializer(teachers, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = TeacherSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TeacherUpdateDeleteView(APIView):
    def get_object(self, pk):
        try:
            return Teacher.objects.get(pk=pk)
        except Teacher.DoesNotExist:
            return None

    def get(self, request, pk):
        teacher = self.get_object(pk)
        if teacher is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = TeacherSerializer(teacher)
        return Response(serializer.data)

    def put(self, request, pk):
        teacher = self.get_object(pk)
        if teacher is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = TeacherSerializer(teacher, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        teacher = self.get_object(pk)
        if teacher is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        teacher.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)