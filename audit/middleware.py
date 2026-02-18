from .models import OperationLog
from django.utils.deprecation import MiddlewareMixin

class AuditMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        if hasattr(request, 'user') and request.user.is_authenticated and request.method in ['POST','DELETE']:
            OperationLog.objects.create(
                user=request.user,
                action=self._get_action(request),
                details={'method':request.method,'path':request.path}
            )
        return response

    def _get_action(self, request):
        if 'sync' in request.path: return 'SYNC'
        if 'auth' in request.path: return 'LOGIN'
        return 'ACCESS'
