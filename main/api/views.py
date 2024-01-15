from rest_framework.decorators import api_view
from rest_framework.response import Response
from main.models import Post
from .serializers import PostSerializer


@api_view(['GET'])
def getRoutes(request):
    routes = [
        'GET /api',
        'GET /api/posts',
        'GET /api/posts/:id'
    ]
    return Response(routes)

@api_view(['GET'])
def getPosts(request):
    posts = Post.objects.all()
    serializer = PostSerializer(posts, many=True)
    return Response(serializer.data)
