"""
Health check endpoint.
"""
import logging
from django.db import connection
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

logger = logging.getLogger(__name__)


class HealthView(APIView):
    """
    Health check endpoint.
    GET /api/v1/health/
    
    Returns service status and database connectivity.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        """
        Check service health and database connectivity.
        """
        # Verificar conexión a la base de datos
        db_status = "ok"
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
        except Exception as e:
            logger.error(f"Error de conexión a la base de datos: {e}", exc_info=True)
            db_status = "error"
        
        # Determinar status general
        overall_status = "ok" if db_status == "ok" else "error"
        http_status = status.HTTP_200_OK if db_status == "ok" else status.HTTP_503_SERVICE_UNAVAILABLE
        
        return Response({
            "status": overall_status,
            "service": "insurance-backend",
            "version": "v1",
            "database": db_status
        }, status=http_status)

