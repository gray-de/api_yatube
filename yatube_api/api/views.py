from posts.models import Group, Post, Comment
from rest_framework import viewsets
from .serializers import PostSerializer, GroupSerializer, CommentSerializer
# from .permissions import IsOwnerOrReadOnly
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import MethodNotAllowed


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    # permission_classes = [IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        if serializer.instance.author != self.request.user:
            raise PermissionDenied('Изменение чужого контента запрещено!')
        super().perform_update(serializer)

    def perform_destroy(self, comment):
        if comment.author != self.request.user:
            raise PermissionDenied('Удаление чужого контента запрещено!')
        super().perform_destroy(comment)


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

    def create(self, request, *args, **kwargs):
        # Запрещаем создание через API – только через админку
        raise MethodNotAllowed(request.method)

    def update(self, request, *args, **kwargs):
        if request.user.is_superuser:
            return Response(
                {"detail": "Администратору запрещено изменять группы."},
                status=status.HTTP_405_METHOD_NOT_ALLOWED
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if request.user.is_superuser:
            return Response(
                {"detail": "Администратору запрещено удалять группы."},
                status=status.HTTP_405_METHOD_NOT_ALLOWED
            )
        return super().destroy(request, *args, **kwargs)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    queryset = Comment.objects.none()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, post=get_object_or_404(
            Post, pk=self.kwargs.get('post_id')))

    def perform_update(self, serializer):
        if serializer.instance.author != self.request.user:
            raise PermissionDenied('Изменение чужого контента запрещено!')
        super().perform_update(serializer)

    def perform_destroy(self, comment):
        if comment.author != self.request.user:
            raise PermissionDenied('Удаление чужого контента запрещено!')
        super().perform_destroy(comment)

    def get_queryset(self):
        post_obj = get_object_or_404(Post, pk=self.kwargs.get('post_id'))
        return Comment.objects.filter(post=post_obj)