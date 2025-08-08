from rest_framework.decorators import api_view
from rest_framework.response import Response
from apps.users.models import User
from apps.users.serializers import UserSerializer
from django.contrib.auth import authenticate
from rest_framework import viewsets, status
from rest_framework_simplejwt.tokens import RefreshToken


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serialzier_class = UserSerializer
    
    def get_serializer_class(self):
        if self.action == "create":
            return UserSerializer
        
        return super().get_serializer_class()
    
    def login(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        
        if email or not password:
            return Response(
                {"Error the email or password are incorrect or empty"},
                status= status.HTTP_400_BAD_REQUEST
            )
            
        user = authenticate(request, email=email, password=password)
        
        if not user:
            return Response(
                {"error, credentials invalid"},
                status= status.HTTP_400_BAD_REQUEST
            )
            
        #si no hay errores genera tokens refresh y access JWT
        refresh = RefreshToken.for_user(user)
        
        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": UserSerializer(user).data     
        })  