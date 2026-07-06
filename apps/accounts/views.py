from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.shortcuts import render
from django.conf import settings
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample
from .serializers import RegisterSerializer, UserSerializer, ChangePasswordSerializer

User = get_user_model()

def _ctx():
    return {'cloudinary_cloud_name': settings.CLOUDINARY_STORAGE.get('CLOUD_NAME', '')}

def landing(request):         return render(request, 'index.html')
def login_page(request):      return render(request, 'login.html')
def register_page(request):   return render(request, 'register.html')
def about_page(request):      return render(request, 'about.html')
def contact_page(request):    return render(request, 'contact.html')
def dashboard_home(request):  return render(request, 'dashboard/index.html', _ctx())
def farms_page(request):      return render(request, 'farms/index.html', _ctx())
def disease_page(request):    return render(request, 'disease/index.html', _ctx())
def weather_page(request):    return render(request, 'weather/index.html', _ctx())
def marketplace_page(request):return render(request, 'marketplace/index.html', _ctx())
def forum_page(request):      return render(request, 'forum/index.html', _ctx())
def finance_page(request):    return render(request, 'dashboard/finance.html', _ctx())
def carbon_page(request):     return render(request, 'dashboard/carbon.html', _ctx())
def account_page(request):    return render(request, 'dashboard/account.html', _ctx())


@extend_schema(
    tags=['auth'],
    summary='Register a new user account',
    description='Creates a new user and returns JWT access and refresh tokens.',
    request=RegisterSerializer,
    responses={201: UserSerializer},
    examples=[
        OpenApiExample('Example Request', value={
            'first_name': 'John', 'last_name': 'Doe',
            'email': 'john@farm.com', 'password': 'Testpass123!',
            'password2': 'Testpass123!', 'role': 'farmer',
            'phone': '+254712345678', 'country': 'Kenya'
        }, request_only=True),
        OpenApiExample('Example Response', value={
            'user': {'id': 1, 'email': 'john@farm.com', 'role': 'farmer'},
            'access': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...',
            'refresh': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'
        }, response_only=True),
    ]
)
class RegisterView(generics.CreateAPIView):
    queryset           = User.objects.all()
    serializer_class   = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user    = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'user':    UserSerializer(user).data,
            'refresh': str(refresh),
            'access':  str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)


@extend_schema(tags=['auth'], summary='Retrieve and update the authenticated user profile')
class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class   = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_object(self): return self.request.user


@extend_schema(tags=['auth'], summary='Change the authenticated user password')
class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        if not user.check_password(serializer.validated_data['old_password']):
            return Response({'error': 'old password is incorrect'}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({'message': 'password updated successfully'})


@extend_schema(tags=['auth'], summary='Logout and blacklist the refresh token')
class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            token = RefreshToken(request.data['refresh'])
            token.blacklist()
            return Response({'message': 'logged out successfully'})
        except Exception:
            return Response({'error': 'invalid token'}, status=status.HTTP_400_BAD_REQUEST)
