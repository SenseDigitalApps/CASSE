"""
Correlation ID middleware for request tracking.
"""
import uuid
import logging

logger = logging.getLogger(__name__)


class CorrelationIDMiddleware:
    """
    Middleware to add a correlation ID to each request for tracking.
    
    The correlation ID is:
    - Generated as a UUID for each request
    - Added to request.META as 'CORRELATION_ID'
    - Available in all views and services via request.META.get('CORRELATION_ID')
    - Can be included in logs for request tracing
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Generate correlation ID
        correlation_id = str(uuid.uuid4())
        
        # Add to request metadata
        request.META['CORRELATION_ID'] = correlation_id
        
        # Add to logger context (if using structured logging)
        # This allows correlation_id to be included in all logs for this request
        logger_adapter = logging.LoggerAdapter(logger, {'correlation_id': correlation_id})
        
        # Process request
        response = self.get_response(request)
        
        # Add correlation ID to response headers (optional, for client tracking)
        response['X-Correlation-ID'] = correlation_id
        
        return response

