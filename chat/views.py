from django.contrib.auth.models import User
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Room
from django.contrib.auth.models import User
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import AccessToken

@api_view(['POST'])
def register(request):
    username = request.data.get('username')
    password = request.data.get('password')

    if User.objects.filter(username=username).exists():
        return Response({'error': 'Bu username band'}, status=400)

    user = User.objects.create_user(username=username, password=password)
    token = RefreshToken.for_user(user)
    return Response({
        'access': str(token.access_token),
        'refresh': str(token),
    })

@api_view(['POST'])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')

    from django.contrib.auth import authenticate
    user = authenticate(username=username, password=password)

    if user is None:
        return Response({'error': 'Xato login yoki parol'}, status=400)

    token = RefreshToken.for_user(user)
    return Response({
        'access': str(token.access_token),
        'refresh': str(token),
    })

@api_view(['GET'])
def rooms(request):
    query = request.GET.get('q', '')
    if query:
        room_list = Room.objects.filter(name__icontains=query).values('name')
    else:
        room_list = Room.objects.all().values('name')
    return Response(list(room_list))

@api_view(['POST'])
def create_room(request):
    name = request.data.get('name')
    if not name:
        return Response({'error': 'Nom kiriting'}, status=400)
    room, created = Room.objects.get_or_create(name=name)
    if not created:
        return Response({'error': 'Bu xona mavjud'}, status=400)
    return Response({'name': room.name})


@api_view(['GET'])
def users(request):
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    try:
        access_token = AccessToken(token)
        current_user_id = access_token['user_id']
    except:
        return Response({'error': 'Token xato'}, status=401)
    
    query = request.GET.get('q', '')
    if query:
        user_list = User.objects.filter(username__icontains=query).exclude(id=current_user_id).values('id', 'username')
    else:
        user_list = User.objects.exclude(id=current_user_id).values('id', 'username')
    return Response(list(user_list))