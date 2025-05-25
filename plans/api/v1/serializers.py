from rest_framework import serializers

from plans.models import Plan, Subscription, Vertical


class VerticalSerializer(serializers.ModelSerializer):
    """Serializer for Vertical model"""

    display_name = serializers.ReadOnlyField(source="__str__")

    class Meta:
        model = Vertical
        fields = ["id", "name", "slug", "description", "display_name"]


class PlanSerializer(serializers.ModelSerializer):
    """Serializer for Plan model"""

    plan_type_display = serializers.ReadOnlyField(source="get_plan_type_display")
    verticals = VerticalSerializer(many=True, read_only=True)

    class Meta:
        model = Plan
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "plan_type",
            "plan_type_display",
            "price",
            "verticals",
            "is_active",
        ]


class PlanCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating plans"""

    verticals = serializers.PrimaryKeyRelatedField(
        queryset=Vertical.objects.all(), many=True, required=False
    )

    class Meta:
        model = Plan
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "plan_type",
            "price",
            "verticals",
            "is_active",
        ]


class SubscriptionSerializer(serializers.ModelSerializer):
    """Serializer for Subscription model"""

    plan = PlanSerializer(read_only=True)
    user_username = serializers.ReadOnlyField(source="user.username")
    status_display = serializers.ReadOnlyField(source="get_status_display")
    is_active = serializers.ReadOnlyField()

    class Meta:
        model = Subscription
        fields = [
            "id",
            "user",
            "user_username",
            "plan",
            "status",
            "status_display",
            "start_date",
            "end_date",
            "created_at",
            "updated_at",
            "is_active",
        ]
        read_only_fields = ["created_at", "updated_at"]


class SubscriptionCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating subscriptions"""

    class Meta:
        model = Subscription
        fields = ["id", "user", "plan", "status", "start_date", "end_date"]

    def validate(self, data):
        """Validate that end_date is after start_date"""
        if "start_date" in data and "end_date" in data:
            if data["end_date"] <= data["start_date"]:
                raise serializers.ValidationError(
                    {"end_date": "End date must be after start date"}
                )
        return data
