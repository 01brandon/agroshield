from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.shortcuts import render
from django.conf import settings
from .serializers import RegisterSerializer, UserSerializer, ChangePasswordSerializer

User = get_user_model()

def _cloudinary_context():
    return {'cloudinary_cloud_name': settings.CLOUDINARY_STORAGE.get('CLOUD_NAME', '')}

def landing(request):
    return render(request, 'index.html')

def login_page(request):
    return render(request, 'login.html')

def register_page(request):
    return render(request, 'register.html')

def dashboard_home(request):
    return render(request, 'dashboard/index.html', _cloudinary_context())

def farms_page(request):
    return render(request, 'farms/index.html', _cloudinary_context())

def disease_page(request):
    return render(request, 'disease/index.html', _cloudinary_context())

def weather_page(request):
    return render(request, 'weather/index.html', _cloudinary_context())

def marketplace_page(request):
    return render(request, 'marketplace/index.html', _cloudinary_context())

def forum_page(request):
    return render(request, 'forum/index.html', _cloudinary_context())

def academy_page(request):
    return render(request, 'academy/index.html', _cloudinary_context())

def finance_page(request):
    return render(request, 'dashboard/finance.html', _cloudinary_context())

def insurance_page(request):
    return render(request, 'dashboard/insurance.html', _cloudinary_context())

def carbon_page(request):
    return render(request, 'dashboard/carbon.html', _cloudinary_context())

def about_page(request):
    return render(request, 'about.html')

def contact_page(request):
    return render(request, 'contact.html')


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

class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class   = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

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

class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            token = RefreshToken(request.data['refresh'])
            token.blacklist()
            return Response({'message': 'logged out successfully'})
        except Exception:
            return Response({'error': 'invalid token'}, status=status.HTTP_400_BAD_REQUEST)
