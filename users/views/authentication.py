from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.hashers import check_password
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from users.models import Referral, User
from users.serializers import ReferralSerializer, ChangePasswordSerializer, UserSerializer
from users.managers import UserManager
from mailing.models import SystemMailManager
from django.template.loader import render_to_string
import logging

logger = logging.getLogger(__name__)


@csrf_exempt
@api_view(["POST"])
@permission_classes([AllowAny])
def obtain_auth_token(request):
    """
    Obtain a token for a user.
    """
    username = request.data.get("username")
    email = request.data.get("email")
    password = request.data.get("password")

    if username:
        user = authenticate(username=username, password=password)
    elif email:
        try:
            user = User.objects.get(email_address=email)
        except User.DoesNotExist:
            user = None
        if user and not user.check_password(password):
            user = None
    else:
        user = None

    if not user:
        return Response({
            'error': 'Invalid credentials'
        }, status=status.HTTP_401_UNAUTHORIZED)
    if user.is_pending:
        return Response({
            'error': 'Registration pending'
        }, status=status.HTTP_403_FORBIDDEN)

    token, created = Token.objects.get_or_create(user=user)
    return Response({'token': token.key})


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def logout(request):
    """
    Logout the user by deleting their token.
    """
    request.auth.delete()
    return Response({'detail': 'Successfully logged out.'})


class ReferralCreate(APIView):
    queryset = Referral.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, format=None):
        serializer = ReferralSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        referral = serializer.save(referrer=self.request.user)
        referred_email = referral.referred_email
        referral_code = referral.referral_code
        referrer_first_name = referral.referrer.profile.first_name
        referrer_last_name = referral.referrer.profile.last_name

        # Send email to referred user
        mail_manager = SystemMailManager()
        sender = self.request.user
        recipients = [referred_email]
        subject = 'You have been referred!'
        context = {
            'referral_code': referral_code,
            'referrer_first_name' : referrer_first_name,
            'referrer_last_name' : referrer_last_name,
            }
        body = render_to_string('referral_email.html', context)
        # logger.info(f"{body}", extra={'request': self.request})
        try:
            mail_manager.create_and_send_mail(sender, recipients, subject, body)
        except Exception as e:
            referral.delete()
            logger.error(str(e), exc_info=True, extra={'request': self.request})
            return Response({'error': 'An error occurred while sending the email'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Send success message to requesting user
        return Response({'message': 'Referral sent successfully!'})


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]  # Set the permission class to IsAuthenticated

    def put(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            current_password = serializer.validated_data['current_password']
            new_password = serializer.validated_data['new_password']

            user = request.user

            # Update the user's password using the User Manager
            try:
                user_manager = User.objects
                user_manager.change_password(user, current_password, new_password)
                return Response({'success': 'Password changed successfully'}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def make_admin(request):
    """
    API endpoint to make a user an admin.
    Only superusers and admins can access this method.
    """
    try:
        # Get username from request
        username = request.data.get('username')
        
        # Check if username is provided
        if not username:
            return Response({'error': 'username is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if user exists
        user = User.objects.get(username=username)
        
        # Check if the logged in user is an admin
        if not request.user.is_superuser and not request.user.is_admin:
            return Response({'error': 'Only superusers and admins can make a user an admin'}, status=status.HTTP_403_FORBIDDEN)
        
        # Make user an admin
        UserManager().make_user_admin(user)
        
        # Serialize and return user data
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_admin(request, username):
    """
    API endpoint to remove adminship from a user.
    Only superusers can access this method.
    """
    try:
        # Check if user exists
        user = User.objects.get(username=username)
        
        # Check if the logged in user is a superuser
        if not request.user.is_superuser:
            return Response({'error': 'Only superusers can remove adminship from a user'}, status=status.HTTP_403_FORBIDDEN)
        
        # Check if user is a superuser
        if user.is_superuser:
            return Response({'error': 'Cannot remove adminship from a superuser'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Remove adminship from user
        UserManager().remove_user_adminship(user)
        
        # Serialize and return user data
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def accept_pending(request, username):
    """
    API endpoint to accept or decline a pending user.
    Only superusers can access this method.
    """
    try:
        # Check if user exists
        user = User.objects.get(username=username)

        is_accepted = request.data.get("accept")
        
        if is_accepted:
            # Remove adminship from user
            UserManager().accept_pending(user)
        else:
            user.delete()
        
        # Serialize and return user data
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
