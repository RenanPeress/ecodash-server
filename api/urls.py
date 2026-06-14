from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    SignupView, LoginView,
    CollectorTokenView, CollectorDownloadView,
    AnaliseView, AnaliseDetailView,
    DashboardView,
    AnaliseRecommendationsView, AnaliseSummaryView, AIChatView,
)

urlpatterns = [
    # Auth
    path('auth/signup/', SignupView.as_view(), name='signup'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Coletor
    path('collector/token/', CollectorTokenView.as_view(), name='collector_token'),
    path('collector/download/', CollectorDownloadView.as_view(), name='collector_download'),

    # Análises
    path('analyses/', AnaliseView.as_view(), name='analyse_list'),
    path('analyses/<int:pk>/', AnaliseDetailView.as_view(), name='analyse_detail'),

    # Dashboard
    path('dashboard/', DashboardView.as_view(), name='dashboard'),

    # IA
    path('analyses/<int:pk>/recommendations/', AnaliseRecommendationsView.as_view(), name='analise_recommendations'),
    path('analyses/<int:pk>/summary/', AnaliseSummaryView.as_view(), name='analise_summary'),
    path('chat/', AIChatView.as_view(), name='ai_chat'),
]
