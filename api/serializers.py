from rest_framework import serializers


# ── Auth ──────────────────────────────────────────────────────────────────────

class SignupRequestSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField(required=False, default='')


class LoginRequestSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class AuthResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    access = serializers.CharField()
    refresh = serializers.CharField()


class TokenRefreshRequestSerializer(serializers.Serializer):
    refresh = serializers.CharField()


# ── Collector ─────────────────────────────────────────────────────────────────

class CollectorTokenResponseSerializer(serializers.Serializer):
    token = serializers.CharField()
    created_at = serializers.DateTimeField()
    last_used_at = serializers.DateTimeField(allow_null=True)


class CollectorTokenRegenResponseSerializer(serializers.Serializer):
    token = serializers.CharField()


# ── Análises ──────────────────────────────────────────────────────────────────

class AnaliseListItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    software_name = serializers.CharField()
    sci_score = serializers.FloatField()
    grade = serializers.ChoiceField(choices=['AAA', 'AA', 'A', 'B', 'C', 'D'])
    region = serializers.CharField()
    energy_kwh = serializers.FloatField()
    created_at = serializers.DateTimeField()


class AnaliseCreateSerializer(serializers.Serializer):
    software_name = serializers.CharField(max_length=255)
    sci_score = serializers.FloatField()
    grade = serializers.ChoiceField(choices=['AAA', 'AA', 'A', 'B', 'C', 'D'])
    energy_kwh = serializers.FloatField()
    region = serializers.CharField(max_length=10)
    hardware_type = serializers.CharField(max_length=20)


class AnaliseCreateResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    grade = serializers.CharField()
    sci_score = serializers.FloatField()


class AnaliseDetailSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    created_at = serializers.DateTimeField()
    software_name = serializers.CharField()
    sci_score = serializers.FloatField()
    grade = serializers.CharField()
    energy_kwh = serializers.FloatField()
    region = serializers.CharField()
    hardware_type = serializers.CharField()


# ── Dashboard ─────────────────────────────────────────────────────────────────

class DashboardRecentItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    software_name = serializers.CharField()
    sci_score = serializers.FloatField()
    grade = serializers.CharField()
    created_at = serializers.DateTimeField()


class DashboardResponseSerializer(serializers.Serializer):
    total = serializers.IntegerField()
    avg_sci = serializers.FloatField()
    grades = serializers.DictField(child=serializers.IntegerField())
    recent = DashboardRecentItemSerializer(many=True)


# ── Erros ─────────────────────────────────────────────────────────────────────

class ErrorSerializer(serializers.Serializer):
    error = serializers.CharField()


# ── IA ────────────────────────────────────────────────────────────────────────

class ChatHistoryItemSerializer(serializers.Serializer):
    role    = serializers.ChoiceField(choices=['user', 'assistant'])
    content = serializers.CharField(max_length=4000)


class ChatRequestSerializer(serializers.Serializer):
    message = serializers.CharField(min_length=1, max_length=2000)
    history = ChatHistoryItemSerializer(many=True, required=False, default=list)

    def validate_history(self, value):
        if len(value) > 10:
            raise serializers.ValidationError('Histórico limitado a 10 mensagens.')
        return value


class RecommendationItemSerializer(serializers.Serializer):
    title       = serializers.CharField()
    description = serializers.CharField()
    impact      = serializers.ChoiceField(choices=['alto', 'medio', 'baixo'])


class RecommendationsResponseSerializer(serializers.Serializer):
    recommendations = RecommendationItemSerializer(many=True)


class SummaryResponseSerializer(serializers.Serializer):
    summary = serializers.CharField()


class ChatResponseSerializer(serializers.Serializer):
    response = serializers.CharField()
