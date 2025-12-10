
from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Profile


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = ['id', 'user', 'role']


class UserDetailSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'profile']

    def update(self, instance, validated_data):
        request = self.context.get('request')
        # Prevent non-admins from changing role via nested profile data
        if 'profile' in self.initial_data:
            role = self.initial_data.get('profile', {}).get('role')
            if role is not None:
                if not (request and hasattr(request.user, 'profile') and request.user.profile.role == 'admin'):
                    # ignore role changes
                    validated_data.pop('profile', None)
        return super().update(instance, validated_data)


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        # Profile is created by signal `create_user_profile` in `signals.py`.
        # Avoid double-creation here.
        return user
