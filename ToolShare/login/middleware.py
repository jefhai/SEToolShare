from django.http import HttpResponseRedirect


class DemoSessionRecoveryMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.session.get('is_demo_session') and not request.user.is_authenticated:
            path = request.path
            if not path.startswith('/demo/') and not path.startswith('/static/') and not path.startswith('/admin/'):
                return HttpResponseRedirect('/demo/')
        return self.get_response(request)
