from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListAPIView
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Post, Profile, Comment, Like
from django.core.cache import cache
from rest_framework_simplejwt.tokens import RefreshToken
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from dj_rest_auth.registration.views import SocialLoginView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from .serializers import UserSerializer, PostSerializer, CommentSerializer, LikeSerializer
from .models import User



class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        user = self.request.user
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        }, status=status.HTTP_200_OK)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer


    def retrieve(self, request, *args, **kwargs):
        post_id = kwargs.get('pk')
        cache_key = f'post_{post_id}'
        post = cache.get(cache_key)

        if not post:
            post = self.get_object()
            cache.set(cache_key, post)
        
        serializer = self.get_serializer(post)
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        cache_key = 'post_list'
        post_list = cache.get(cache_key)
        
        if not post_list:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            post_list = serializer.data
            cache.set(cache_key, post_list)
        
        return Response(post_list)



    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        post_id = kwargs.get('pk')
        cache_key = f'post_{post_id}'
        cache.delete(cache_key)
        cache.delete('post_list')
        return response

    def destroy(self, request, *args, **kwargs):
        post_id = kwargs.get('pk')
        cache_key = f'post_{post_id}'
        cache.delete(cache_key)
        cache.delete('post_list')
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['post'], url_name='add_comment', url_path='add_comment')
    def add_comment(self, request, pk=None):
        try:
            post  = self.get_object()
            user = request.user
            body = request.data.get('body')
            if not post:
                return Response({'error': 'post is missing'}, status=status.HTTP_400_BAD_REQUEST)
            if not body:
                return Response({'error': 'body is missing'}, status=status.HTTP_400_BAD_REQUEST)
            comment = Comment.objects.create(post=post, user=user,  body=body)
            return Response({'status': 'comment created', 'comment': comment.id})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

    @action(detail=True, methods=['post'], url_name='like_post', url_path='like_post')
    def like_post(self, request, pk=None):
        try:
            post  = self.get_object()
            user = request.user
            kind = request.data.get('kind')
            if not post :
                return Response({'error': 'post is missing'}, status=status.HTTP_400_BAD_REQUEST)
            like = Like.objects.create(post=post, user=user, kind=kind)
            return Response({'status': 'like created', 'like': like.id})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    @action(detail=True, methods=['get'], url_name='comment', url_path='comment')
    def comment(self, request, pk=None):
        try:
            post = self.get_object()
            if post is None:
                return Response({'error': 'post is missing'}, status=status.HTTP_400_BAD_REQUEST)
            comments = Comment.objects.filter(post=post).prefetch_related('post')
            if not comments:
                comments = []
            serializer = CommentSerializer(comments, many=True)
            return Response(serializer.data)
        except Comment.DoesNotExist:
            return Response({'error': 'post not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

    @action(detail=True, methods=['get'], url_name='like', url_path='like')
    def like(self, request, pk=None):
        try:
            post  = self.get_object()
            if not post :
                return Response({'error': 'post is missing'}, status=status.HTTP_400_BAD_REQUEST)
            likes = Like.objects.filter(post=post).prefetch_related('post')
            serializer = LikeSerializer(likes, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
