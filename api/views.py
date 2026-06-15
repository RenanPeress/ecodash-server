from django.contrib.auth import authenticate, get_user_model
from django.conf import settings
from django.db.models import Avg, Count
from django.http import HttpResponse
from django.utils import timezone
from pathlib import Path
import anthropic as anthropic_exc
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

from .authentication import CollectorTokenAuthentication
from .models import CollectorToken, Analise
from .pdf import generate_pdf
from .serializers import (
    SignupRequestSerializer, LoginRequestSerializer, AuthResponseSerializer,
    CollectorTokenResponseSerializer, CollectorTokenRegenResponseSerializer,
    AnaliseListItemSerializer, AnaliseCreateSerializer, AnaliseCreateResponseSerializer,
    AnaliseDetailSerializer, DashboardResponseSerializer, ErrorSerializer,
    ChatRequestSerializer, RecommendationsResponseSerializer,
    SummaryResponseSerializer, ChatResponseSerializer,
)
from .ai.service import get_recommendations, get_summary, chat as ai_chat

User = get_user_model()
DUAL_AUTH = [JWTAuthentication, CollectorTokenAuthentication]


# ── Autenticação ──────────────────────────────────────────────────────────────

class SignupView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary='Cadastrar novo usuário',
        request=SignupRequestSerializer,
        responses={
            201: AuthResponseSerializer,
            400: ErrorSerializer,
        },
        tags=['Autenticação'],
    )
    def post(self, request):
        username = request.data.get('username', '').strip()
        password = request.data.get('password', '')
        email = request.data.get('email', '').strip()
        if not username or not password:
            return Response({'error': 'username e password são obrigatórios'}, status=400)
        if User.objects.filter(username=username).exists():
            return Response({'error': 'username já existe'}, status=400)
        user = User.objects.create_user(username=username, email=email, password=password)
        refresh = RefreshToken.for_user(user)
        return Response({
            'id': user.id, 'username': user.username,
            'access': str(refresh.access_token), 'refresh': str(refresh),
        }, status=201)


class LoginView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary='Autenticar usuário',
        request=LoginRequestSerializer,
        responses={
            200: AuthResponseSerializer,
            401: ErrorSerializer,
        },
        tags=['Autenticação'],
    )
    def post(self, request):
        user = authenticate(
            username=request.data.get('username'),
            password=request.data.get('password'),
        )
        if not user:
            return Response({'error': 'Credenciais inválidas'}, status=401)
        refresh = RefreshToken.for_user(user)
        return Response({
            'id': user.id, 'username': user.username,
            'access': str(refresh.access_token), 'refresh': str(refresh),
        })


# ── Coletor ───────────────────────────────────────────────────────────────────

class CollectorTokenView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary='Obter token do coletor',
        responses={200: CollectorTokenResponseSerializer},
        tags=['Coletor'],
    )
    def get(self, request):
        token, _ = CollectorToken.objects.get_or_create(user=request.user)
        return Response({
            'token': token.token,
            'created_at': token.created_at,
            'last_used_at': token.last_used_at,
        })

    @extend_schema(
        summary='Regenerar token do coletor',
        request=None,
        responses={200: CollectorTokenRegenResponseSerializer},
        tags=['Coletor'],
    )
    def post(self, request):
        CollectorToken.objects.filter(user=request.user).delete()
        token = CollectorToken.objects.create(user=request.user)
        return Response({'token': token.token})


class CollectorDownloadView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary='Download do script coletor',
        responses={
            200: OpenApiResponse(description='Arquivo Python (.py) para download'),
        },
        tags=['Coletor'],
    )
    def get(self, request):
        token, _ = CollectorToken.objects.get_or_create(user=request.user)
        template_path = Path(settings.BASE_DIR) / 'collector_template.py'
        api_url = getattr(settings, 'ECODASH_BASE_URL', 'http://localhost:8000')

        script = (template_path.read_text()
                  .replace('{{TOKEN}}', token.token)
                  .replace('{{API_URL}}', api_url)
                  .replace('{{USER_EMAIL}}', request.user.email or request.user.username)
                  .replace('{{GENERATED_AT}}', timezone.now().isoformat()))

        response = HttpResponse(script, content_type='text/x-python')
        response['Content-Disposition'] = 'attachment; filename="ecodash-collector.py"'
        return response


# ── Análises ──────────────────────────────────────────────────────────────────

class AnaliseView(APIView):
    authentication_classes = DUAL_AUTH
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary='Listar análises do usuário',
        responses={200: AnaliseListItemSerializer(many=True)},
        tags=['Análises'],
    )
    def get(self, request):
        qs = Analise.objects.filter(user=request.user)
        return Response(list(qs.values(
            'id', 'software_name', 'sci_score', 'grade', 'region', 'energy_kwh', 'created_at'
        )))

    @extend_schema(
        summary='Criar nova análise',
        request=AnaliseCreateSerializer,
        responses={
            201: AnaliseCreateResponseSerializer,
            400: ErrorSerializer,
        },
        tags=['Análises'],
    )
    def post(self, request):
        d = request.data
        required = ('sci_score', 'grade', 'software_name', 'energy_kwh', 'region', 'hardware_type')
        if any(k not in d for k in required):
            return Response({'error': f'Campos obrigatórios: {list(required)}'}, status=400)

        analise = Analise.objects.create(
            user=request.user,
            software_name=d['software_name'],
            sci_score=float(d['sci_score']),
            grade=d['grade'],
            energy_kwh=float(d['energy_kwh']),
            region=d['region'],
            hardware_type=d['hardware_type'],
            payload=d,
        )
        return Response({'id': analise.id, 'grade': analise.grade, 'sci_score': analise.sci_score}, status=201)


class AnaliseDetailView(APIView):
    authentication_classes = DUAL_AUTH
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary='Detalhar análise',
        parameters=[
            OpenApiParameter(name='pk', location='path', description='ID da análise', required=True, type=int),
        ],
        responses={
            200: AnaliseDetailSerializer,
            404: OpenApiResponse(description='Análise não encontrada'),
        },
        tags=['Análises'],
    )
    def get(self, request, pk):
        try:
            a = Analise.objects.get(pk=pk, user=request.user)
        except Analise.DoesNotExist:
            return Response(status=404)
        return Response(a.payload | {'id': a.id, 'created_at': a.created_at})

    @extend_schema(
        summary='Excluir análise',
        parameters=[
            OpenApiParameter(name='pk', location='path', description='ID da análise', required=True, type=int),
        ],
        responses={
            204: OpenApiResponse(description='Análise excluída com sucesso'),
        },
        tags=['Análises'],
    )
    def delete(self, request, pk):
        Analise.objects.filter(pk=pk, user=request.user).delete()
        return Response(status=204)


class AnaliseExportPDFView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary='Exportar análise como PDF',
        parameters=[
            OpenApiParameter(name='pk', location='path', description='ID da análise', required=True, type=int),
        ],
        responses={
            200: OpenApiResponse(description='Arquivo PDF para download'),
            404: OpenApiResponse(description='Análise não encontrada'),
        },
        tags=['Análises'],
    )
    def get(self, request, pk):
        try:
            analise = Analise.objects.select_related('user').get(pk=pk, user=request.user)
        except Analise.DoesNotExist:
            return Response(status=404)

        pdf_bytes = generate_pdf(analise)
        filename = f'ecodash-relatorio-{analise.id}.pdf'
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response


# ── Dashboard ─────────────────────────────────────────────────────────────────

class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary='Dados do dashboard',
        responses={200: DashboardResponseSerializer},
        tags=['Dashboard'],
    )
    def get(self, request):
        qs = Analise.objects.filter(user=request.user)
        agg = qs.aggregate(total=Count('id'), avg_sci=Avg('sci_score'))
        grades = {i['grade']: i['count'] for i in qs.values('grade').annotate(count=Count('id'))}
        recent = list(qs.values('id', 'software_name', 'sci_score', 'grade', 'created_at')[:5])
        return Response({
            'total': agg['total'] or 0,
            'avg_sci': round(agg['avg_sci'] or 0, 6),
            'grades': grades,
            'recent': recent,
        })


# ── IA ────────────────────────────────────────────────────────────────────────

_AI_ERROR = {'error': 'Serviço de IA indisponível. Tente novamente em instantes.'}


def _analise_to_dict(a: Analise) -> dict:
    return a.payload | {
        'id': a.id,
        'software_name': a.software_name,
        'sci_score': a.sci_score,
        'grade': a.grade,
        'energy_kwh': a.energy_kwh,
        'region': a.region,
        'hardware_type': a.hardware_type,
    }


class AnaliseRecommendationsView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary='Recomendações IA para reduzir o score SCI',
        parameters=[OpenApiParameter('pk', location='path', type=int)],
        responses={200: RecommendationsResponseSerializer, 404: OpenApiResponse(description='Não encontrada'), 503: ErrorSerializer},
        tags=['IA'],
    )
    def get(self, request, pk):
        try:
            analise = Analise.objects.get(pk=pk, user=request.user)
        except Analise.DoesNotExist:
            return Response(status=404)
        try:
            recommendations = get_recommendations(_analise_to_dict(analise))
        except anthropic_exc.APIError:
            return Response(_AI_ERROR, status=503)
        return Response({'recommendations': recommendations})


class AnaliseSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary='Resumo em linguagem natural da análise SCI',
        parameters=[OpenApiParameter('pk', location='path', type=int)],
        responses={200: SummaryResponseSerializer, 404: OpenApiResponse(description='Não encontrada'), 503: ErrorSerializer},
        tags=['IA'],
    )
    def get(self, request, pk):
        try:
            analise = Analise.objects.get(pk=pk, user=request.user)
        except Analise.DoesNotExist:
            return Response(status=404)
        try:
            summary = get_summary(_analise_to_dict(analise))
        except anthropic_exc.APIError:
            return Response(_AI_ERROR, status=503)
        return Response({'summary': summary})


class AIChatView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary='Chat IA sobre suas análises SCI',
        request=ChatRequestSerializer,
        responses={200: ChatResponseSerializer, 400: ErrorSerializer, 503: ErrorSerializer},
        tags=['IA'],
    )
    def post(self, request):
        serializer = ChatRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        qs = Analise.objects.filter(user=request.user)
        agg = qs.aggregate(total=Count('id'), avg_sci=Avg('sci_score'))
        grades = {i['grade']: i['count'] for i in qs.values('grade').annotate(count=Count('id'))}
        recent = list(qs.values('id', 'software_name', 'sci_score', 'grade', 'region', 'energy_kwh')[:10])

        context = {
            'total_analyses': agg['total'] or 0,
            'avg_sci_score': round(agg['avg_sci'] or 0, 6),
            'grade_distribution': grades,
            'recent_analyses': recent,
        }

        try:
            response_text = ai_chat(
                message=serializer.validated_data['message'],
                context=context,
                history=serializer.validated_data.get('history', []),
            )
        except anthropic_exc.APIError:
            return Response(_AI_ERROR, status=503)

        return Response({'response': response_text})
