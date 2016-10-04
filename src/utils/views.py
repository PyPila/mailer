from django.views.generic import View
from django.http import HttpResponseNotAllowed
from django.template.response import TemplateResponse
from django.conf.urls import url
from django.shortcuts import redirect


class ModelView(View):
    action = None
    namespace = None

    def get_obj(self, **lookup_kwargs):
        return self.model.objects.get(**lookup_kwargs)

    def get_queryset(self):
        return self.model.objects.all()

    def change_obj(self, **lookup_kwargs):
        recipient = self.get_obj(**lookup_kwargs)
        recipient.change(**self.request.POST)
        return recipient

    def create_obj(self):
        return self.model.objects.create(**self.request.POST)

    def dispatch(self, request, *args, **kwargs):
        handler = getattr(self, self.action)
        return handler(request, *args, **kwargs)

    def get_obj_context(self, extra_context=None):
        ctx = {}
        if extra_context is not None:
            ctx.update(extra_context)
        return ctx

    @classmethod
    def get_urls(cls, namespace):
        return [
            url(
                r'^$', cls.as_view(action='list', namespace=namespace),
                name='list'
            ),
            url(
                r'^add/$', cls.as_view(action='add', namespace=namespace),
                name='add'
            ),
            url(
                r'^(?P<pk>.+)/change/$',
                cls.as_view(action='change', namespace=namespace),
                name='change'
            ),
            url(
                r'^(?P<pk>.+)/delete/$',
                cls.as_view(action='delete', namespace=namespace),
                name='delete'
            ),
        ]

    def __get_template(self, action):
        return '{}_{}.html'.format(self.template_name, action)

    def list(self, request):
        return TemplateResponse(
            request=request,
            template=self.__get_template('list'),
            context={'object_list': self.get_queryset()}
        )

    def add(self, request):
        if request.method.lower() == 'post':
            obj = self.create_obj()
            return redirect(obj)
        elif request.method.lower() == 'get':
            return TemplateResponse(
                request=request,
                template=self.__get_template('detail'),
                context=self.get_obj_context()
            )
        return HttpResponseNotAllowed(['get', 'post', ])

    def change(self, request, pk):
        if request.method.lower() == 'get':
            obj = self.get_obj(pk=pk)
        elif request.method.lower() == 'post':
            obj = self.change_obj(pk=pk)
        else:
            return HttpResponseNotAllowed(['get', 'post', ])
        return TemplateResponse(
            request=request,
            template=self.__get_template('detail'),
            context=self.get_obj_context({'object': obj})
        )

    def delete(self, request, pk):
        self.get_obj(pk=pk).delete()
        return redirect('{}:list'.format(self.namespace))
