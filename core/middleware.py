from user_agents import parse

class MobileDetectionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user_agent = parse(request.META.get('HTTP_USER_AGENT', ''))
        request.is_mobile = user_agent.is_mobile
        return self.get_response(request)
