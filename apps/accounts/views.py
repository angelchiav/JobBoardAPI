from contextvars import Token
from rest_framework.response import Response
from apps.users.models import User, EmployerProfile, EmployeeProfile
from apps.users.serializers import UserSerializer, EmployerProfileSerializer, EmployeeProfileSerializer
from django.contrib.auth import authenticate
from rest_framework import viewsets, status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_serializer_class(self):
        if self.action == "create":
            return UserSerializer

        return super().get_serializer_class()

    # el decorador hace que el metodo login sea un nuevo endpoint
    @action(detail=False, methods=["POST"])
    def login(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response(
                {"Error the email or password are incorrect or empty"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(request, email=email, password=password)

        if not user:
            return Response(
                {"error, credentials invalid"},
                status=status.HTTP_400_BAD_REQUEST

            )

        # si no hay errores genera tokens refresh y access JWT
        refresh = RefreshToken.for_user(user)

        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": UserSerializer(user).data
        })

    @action(detail=False, methods=["POST"])
    def register(self, request):
        serializer = UserSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()  # El serializer ya maneja el set_password

            refresh = RefreshToken.for_user(user)  # genera un token nuevo

            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)

        return Response(
            {"error": "register failed", "details": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )


class userLogOut(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        print(request.headers)
        token_key = request.auth.key
        token = Token.objects.get(key=token_key)
        token.delete()

        return Response({'detail': 'Successfully logged out.'})

class EmployerViewSet(viewsets.ModelViewSet):
    queryset = EmployerProfile.objects.all()
    serializer_class = EmployerProfileSerializer

    def get_serializer_class(self):
        if self.action == "create":
            return EmployerProfileSerializer

        return super().get_serializer_class()

    @action(detail=False, methods=["POST"])
    def register(self, request):
        serializer = EmployerProfileSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()  # El serializer ya maneja el set_password

            refresh = RefreshToken.for_user(user)  # genera un token nuevo

            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)

        return Response(
            {"error": "register failed", "details": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = EmployeeProfile.objects.all()
    serializer_class = EmployeeProfileSerializer

    def get_serializer_class(self):
        if self.action == "create":
            return EmployeeProfileSerializer

        return super().get_serializer_class()

    @action(detail=False, methods=["POST"])
    def register(self, request):
        serializer = EmployeeProfileSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()  # El serializer ya maneja el set_password

            refresh = RefreshToken.for_user(user)  # genera un token nuevo

            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)

        return Response(
            {"error": "register failed", "details": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )