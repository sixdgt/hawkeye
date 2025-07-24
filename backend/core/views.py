from rest_framework import generics, permissions, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils import timezone
from github import Github, Auth
import requests
import base64
import re
from core.models import User, Assignment, Submission
from core.serializers import UserSerializer, RegisterTeacherSerializer, RegisterStudentSerializer, AssignmentSerializer, SubmissionSerializer
from social_django.utils import load_strategy, load_backend
from social_core.exceptions import AuthException
from rest_framework_simpljejwt.token import RefreshToken

User = get_user_model()

# Create your views here.
class GithubLogin(APIView):
    def post(self, request):
        access_token = request.data.get('access_token')
        if not access_token:
            return Response({'error': 'Access token is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            strategy = load_strategy(request)
            backend = load_backend(strategy=strategy, name='github', redirect_uri=None)
            user = backend.do_auth(access_token)
        except MissingBackend:
            return Response({'error': 'Invalid backend'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        if user and user.is_active:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        else:
            return Response({'error': 'Authentication failed'}, status=status.HTTP_400_BAD_REQUEST)

class IsTeacher(permissions.BasePermission):
    """
    Custom permission to only allow teachers to access certain views.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_teacher

class IsStudent(permissions.BasePermission):
    """
    Custom permission to only allow students to access certain views.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_student

class CustomAuthToken(ObtainAuthToken):
    """
    Custom authentication view to return the user and token.
    """
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'username': user.username,
            'is_teacher': user.is_teacher
        })

class RegisterStudentView(generics.CreateAPIView):
    """
    View to register a new student.
    """
    queryset = User.objects.all()
    serializer_class = RegisterStudentSerializer
    permission_classes = [permissions.AllowAny]

class RegisterTeacherView(generics.CreateAPIView):
    """
    View to register a new teacher.
    """
    queryset = User.objects.all()
    serializer_class = RegisterTeacherSerializer
    permission_classes = [permissions.AllowAny]

class AssignmentListCreateView(generics.ListCreateAPIView):
    """
    View to create a new assignment.
    """
    queryset = Assignment.objects.all().order_by('-created_at')
    serializer_class = AssignmentSerializer
    permission_classes = [IsTeacher] # Only teachers can create assignments

    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user)

class AssignmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    View to retrieve, update or delete an assignment.
    """
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer
    permission_classes = [IsTeacher]

    def get_queryset(self):
        # Teachers can only manage their own assignments
        return self.queryset.filter(teacher=self.request.user)

class SubmissionListCreateView(generics.ListCreateAPIView):
    queryset = Submission.objects.all().order_by('-submitted_at')
    serializer_class = SubmissionSerializer
    permission_classes = [IsAuthenticated] # Both students and teachers can list/create (with filters)

    def get_queryset(self):
        if self.request.user.is_teacher:
            # Teachers see all submissions for assignments they own
            return Submission.objects.filter(assignment__teacher=self.request.user).order_by('-submitted_at')
        else:
            # Students see only their own submissions
            return Submission.objects.filter(student=self.request.user).order_by('-submitted_at')

    def perform_create(self, serializer):
        # Ensure only students can create submissions
        if self.request.user.is_teacher:
            raise permissions.PermissionDenied("Teachers cannot create submissions.")
        # Ensure student hasn't already submitted for this assignment
        assignment = serializer.validated_data['assignment']
        if Submission.objects.filter(assignment=assignment, student=self.request.user).exists():
            raise serializers.ValidationError("You have already submitted for this assignment.")
        serializer.save(student=self.request.user)

class SubmissionDetailView(generics.RetrieveAPIView):
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_teacher:
            # Teachers can view any submission for their assignments
            return self.queryset.filter(assignment__teacher=self.request.user)
        else:
            # Students can only view their own submissions
            return self.queryset.filter(student=self.request.user)


class CodeReviewView(APIView):
    permission_classes = [IsTeacher] # Only teachers can trigger code review

    def post(self, request, submission_id):
        try:
            submission = Submission.objects.get(id=submission_id)
        except Submission.DoesNotExist:
            return Response({"error": "Submission not found."}, status=status.HTTP_404_NOT_FOUND)

        # Ensure the teacher owns the assignment for this submission
        if submission.assignment.teacher != request.user:
            return Response({"error": "You do not have permission to review this submission."},
                            status=status.HTTP_403_FORBIDDEN)

        github_url = submission.github_repo_url
        commit_hash = submission.commit_hash

        # --- PyGithub Integration to fetch code ---
        try:
            auth = Auth.Token(settings.GITHUB_PAT) # Use the teacher's PAT from settings
            g = Github(auth=auth)

            # Extract owner and repo name from GitHub URL
            # Assumes format like https://github.com/owner/repo_name
            match = re.match(r'https://github.com/([^/]+)/([^/]+)(?:.git)?', github_url)
            if not match:
                return Response({"error": "Invalid GitHub repository URL format."}, status=status.HTTP_400_BAD_REQUEST)
            owner, repo_name = match.groups()

            repo = g.get_repo(f"{owner}/{repo_name}")

            # Fetch relevant files (e.g., Python files, specific assignment files)
            # This is a simplified example; you might want to fetch specific files
            # or filter by file type based on assignment requirements.
            code_content = {}
            contents = repo.get_contents("") # Get root contents

            while contents:
                file_content = contents.pop(0)
                if file_content.type == "dir":
                    contents.extend(repo.get_contents(file_content.path))
                elif file_content.type == "file" and (file_content.name.endswith(".py") or file_content.name.endswith(".js") or file_content.name.endswith(".ts")):
                    try:
                        # For larger files, consider using file_content.download_url with requests
                        file_decoded_content = base64.b64decode(file_content.content).decode('utf-8')
                        code_content[file_content.path] = file_decoded_content
                    except Exception as e:
                        print(f"Error decoding file {file_content.path}: {e}")
                        code_content[file_content.path] = f"Error reading file: {e}"

            if not code_content:
                return Response({"message": "No relevant code files found in the repository."},
                                status=status.HTTP_400_BAD_REQUEST)

            # Combine code content for LLM
            combined_code = "\n\n".join([f"--- File: {path} ---\n{content}" for path, content in code_content.items()])

        except Exception as e:
            return Response({"error": f"Error fetching code from GitHub: {str(e)}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # --- LLM Integration (Placeholder) ---
        review_feedback = "No review generated yet." # Default feedback

        try:
            # Prepare the prompt for the LLM
            prompt = (
                f"Review the following code submission for the assignment '{submission.assignment.title}'. "
                f"Provide constructive feedback, identify potential bugs, suggest improvements, and evaluate code style. "
                f"Focus on the overall quality and adherence to best practices. "
                f"The code is from GitHub repository: {github_url}\n\n"
                f"Code:\n\n{combined_code}"
            )

            # Call the LLM (Gemini API)
            # This part will be executed on the server side (Django)
            # The API key is managed by the Canvas environment for Gemini models.
            # No need to expose it in the frontend.
            chat_history = []
            chat_history.push({ "role": "user", "parts": [{ "text": prompt }] })
            payload = { "contents": chat_history }
            api_key = "" # Canvas will inject the key
            api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"

            # Using requests library for server-side HTTP call
            llm_response = requests.post(api_url, json=payload, headers={'Content-Type': 'application/json'})
            llm_result = llm_response.json()

            if llm_result.get('candidates') and llm_result['candidates'][0].get('content') and \
               llm_result['candidates'][0]['content'].get('parts'):
                review_feedback = llm_result['candidates'][0]['content']['parts'][0]['text']
            else:
                review_feedback = "LLM did not return a valid response."
                print(f"LLM Response Error: {llm_result}") # Log for debugging

        except requests.exceptions.RequestException as e:
            review_feedback = f"Error communicating with LLM API: {e}"
            print(f"LLM API Request Error: {e}")
        except Exception as e:
            review_feedback = f"An unexpected error occurred during LLM review: {e}"
            print(f"LLM Review Error: {e}")

        # Save feedback to submission
        submission.review_feedback = review_feedback
        submission.reviewed_at = timezone.now()
        submission.save()

        return Response({"message": "Code review completed.", "feedback": review_feedback}, status=status.HTTP_200_OK)