from rest_framework import serializers, validators
from .models import User, Subscribtion
from djoser.serializers import UserSerializer, UserCreateSerializer


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'is_subscribed',
        )
        read_only_fields = ('is_subscribed', )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Subscribtion.objects.filter(
            user=request.user, author=obj).exists()


class CustomUserCreateSerializer(UserCreateSerializer):
    email = serializers.EmailField(
        validators=[validators.UniqueValidator(
            queryset=User.objects.all()
        )]
    )
    username = serializers.CharField(
        validators=[validators.UniqueValidator(
            queryset=User.objects.all()
        )]
    )

    class Meta:
        model = User
        fields = (
            'email',
            'password',
            'username',
            'first_name',
            'last_name',
        )
