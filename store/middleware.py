from .models import Visitor

class VisitorTrackingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Process request - Track Visit
        self.track_visitor(request)
        
        response = self.get_response(request)
        return response

    def track_visitor(self, request):
        # Ignore admin, static, media, favicon
        path = request.path
        if any(x in path for x in ['/admin/', '/static/', '/media/', 'favicon.ico', '/admin-tools/']):
            return

        # Get IP
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')

        # Get User Agent & Referer
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        referer = request.META.get('HTTP_REFERER', '')

        # UTM Params
        utm_source = request.GET.get('utm_source')
        utm_medium = request.GET.get('utm_medium')
        utm_campaign = request.GET.get('utm_campaign')

        # Only save if we have useful info or distinct visit (simple logic: just save all for now)
        # To avoid spamming DB, we could check session or cache, 
        # but requested "track everything", so specific page views are good.
        
        try:
            Visitor.objects.create(
                ip_address=ip,
                user_agent=user_agent,
                path=path,
                referer=referer,
                utm_source=utm_source,
                utm_medium=utm_medium,
                utm_campaign=utm_campaign
            )
        except Exception:
            # Don't break site if tracking fails
            pass
