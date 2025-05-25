from typing import Any, Dict, Optional

from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user model"""

    user_type_display = serializers.ReadOnlyField(source="get_user_type_display")

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "user_type",
            "user_type_display",
            "is_active",
            "date_joined",
        ]
        read_only_fields = ["id", "date_joined"]


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating users"""

    password = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"}
    )

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "user_type",
            "password",
            "is_active",
        ]

    def validate_user_type(self, value):
        """
        Valida se o usuário tem permissão para criar o tipo de usuário solicitado.
        - Usuários admin podem ser criados apenas por staff
        - Usuários editor podem ser criados por staff ou por usuários admin
        """
        request = self.context.get("request")

        # Verifica se há requisição e usuário autenticado
        if not request or not request.user.is_authenticated:
            if value in ["admin", "editor"]:
                raise serializers.ValidationError(
                    "Apenas usuários autorizados podem criar usuários do tipo admin ou editor."
                )
            return value

        # Para usuários do tipo admin, apenas staff pode criar
        if value == "admin" and not request.user.is_staff:
            raise serializers.ValidationError(
                "Apenas administradores com acesso staff podem criar usuários do tipo admin."
            )

        # Para usuários do tipo editor, staff ou admin podem criar
        if value == "editor" and not (
            request.user.is_staff or request.user.user_type == "admin"
        ):
            raise serializers.ValidationError(
                "Apenas administradores podem criar usuários do tipo editor."
            )

        return value

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserDetailSerializer(UserSerializer):
    """Detailed user serializer with subscription information"""

    active_subscription = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ["active_subscription"]

    def get_active_subscription(self, obj) -> Optional[Dict[str, Any]]:
        subscription = obj.get_active_subscription()
        if subscription:
            return {
                "id": subscription.id,
                "plan_name": subscription.plan.name,
                "plan_type": subscription.plan.plan_type,
                "start_date": subscription.start_date,
                "end_date": subscription.end_date,
                "status": subscription.status,
            }
        return None
