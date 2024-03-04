from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model, authenticate
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

@api_view(['POST'])
def register(request):
    if request.method == 'POST':
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email')
        phone = request.data.get('phone')

        print(username, password, email, phone)
        if not all([username, password, email,phone]):
            return Response({'message': 'All fields are required'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({'message': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email).exists():
            return Response({'message': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create(username=username, email=email)
        user.set_password(password)
        user.save()

        if user:
            return Response({'message': 'Registration successful', 'username': username, 'email': email}, status=status.HTTP_201_CREATED)
        else:
            return Response({'message': 'User creation failed'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return Response({'message': 'Invalid request'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['POST'])
def login(request):
    if request.method == 'POST':
        username = request.data.get('username')
        password = request.data.get('password')
        if not all([username, password]):
            return Response({'message': 'All fields are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            print(f'User {username} logged in successfully')
            print(f'User details: {user.__dict__}')
            refresh = RefreshToken.for_user(user)
            user.refreshToken = str(refresh)
            user.save()
            return Response({
                'message': 'Login successful',
                'username': username,
                'refresh_token': str(refresh),
                'access_token': str(refresh.access_token)
            })
        else:
            return Response({'message': 'Invalid username or password'}, status=status.HTTP_401_UNAUTHORIZED)
    else:
        return Response({'message': 'Invalid request'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)



@api_view(['POST'])
def logout(request):
    if request.method == 'POST':
        username = request.data.get('username')
        
        try:
            user = User.objects.get(username=username)
            user.refreshToken = None  # Set refreshToken to null
            user.save()
            return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    else:
        return Response({'message': 'Invalid request'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
