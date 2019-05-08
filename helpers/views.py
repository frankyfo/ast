from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django import http
import json


class LoginRequiredMixin(object):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(request,*args,**kwargs)


def LoginRequired(cls=None, **login_args):
    if cls is not None:
        if not hasattr(cls, 'dispatch'):
            raise TypeError(('View class is not valid: %r.  Class-based views '
                             'must have a dispatch method.') % cls)

        original = cls.dispatch
        modified = method_decorator(login_required(**login_args))(original)
        cls.dispatch = modified

        return cls

    else:
        def inner_decorator(inner_cls):
            return LoginRequired(inner_cls, **login_args)

        return inner_decorator


def UserPassesTest(cls=None, **login_args):
    if cls is not None:
        if not hasattr(cls, 'dispatch'):
            raise TypeError(('View class is not valid: %r.  Class-based views '
                             'must have a dispatch method.') % cls)

        original = cls.dispatch
        modified = method_decorator(
            user_passes_test(**login_args))(original)
        cls.dispatch = modified

        return cls

    else:
        def inner_decorator(inner_cls):
            return UserPassesTest(inner_cls, **login_args)

        return inner_decorator


class AjaxableResponseMixin(object):
    def form_invalid(self, form):
        response = super(AjaxableResponseMixin, self).form_invalid(form)
        if self.request.is_ajax():
            response = JsonResponse(form.errors, status=400)
        return response

    def form_valid(self, form):
        response = super(AjaxableResponseMixin, self).form_valid(form)
        if self.request.is_ajax():
            data = {
                'pk': self.object.pk,
            }
            return JsonResponse(data)
        else:
            return response


class JSONResponseMixin(object):
    def render_to_response(self, context, **kwargs):
        return self.get_json_response(self.convert_context_to_json(context), **kwargs)

    def get_json_response(self, content, **httpresponse_kwargs):
        return http.HttpResponse(content,
                                 content_type='application/json',
                                 **httpresponse_kwargs)

    def convert_context_to_json(self, context):
        return json.dumps(context)