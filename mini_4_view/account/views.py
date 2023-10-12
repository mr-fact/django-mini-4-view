from django.shortcuts import render
from rest_framework.exceptions import ValidationError
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import mixins

from account.models import User
from account.serializers import UserSerializer
from mini_4_view.logs import start_end_log, level_log, message_log


class CustomListModelMixin(
    mixins.ListModelMixin,
):
    @start_end_log
    @level_log(2)
    @message_log('LMM')
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class CustomRetrieveModelMixin(
    mixins.RetrieveModelMixin,
):
    @start_end_log
    @level_log(2)
    @message_log('LMM')
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


class CustomGenericAPIView(
    GenericAPIView,
    CustomListModelMixin,
    CustomRetrieveModelMixin,
):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'id'
    lookup_url_kwarg = 'key'

    @classmethod
    @start_end_log
    def as_view(cls, **initkwargs):
        return super().as_view(**initkwargs)

    @start_end_log
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    @start_end_log
    @level_log(1)
    def initialize_request(self, request, *args, **kwargs):
        return super().initialize_request(request, *args, **kwargs)

    @start_end_log
    @level_log(2)
    def get_parser_context(self, http_request):
        return super().get_parser_context(http_request)

    @start_end_log
    @level_log(1)
    def initial(self, request, *args, **kwargs):
        return super().initial(request, *args, **kwargs)

    @start_end_log
    @level_log(2)
    def perform_authentication(self, request):
        return super().perform_authentication(request)

    @start_end_log
    @level_log(2)
    def check_permissions(self, request):
        return super().check_permissions(request)

    @start_end_log
    @level_log(3)
    def get_permissions(self):
        return super().get_permissions()

    @start_end_log
    @level_log(2)
    def check_throttles(self, request):
        return super().check_throttles(request)

    @start_end_log
    @level_log(3)
    def get_throttles(self):
        return super().get_throttles()

    @start_end_log
    @level_log(1)
    def finalize_response(self, request, response, *args, **kwargs):
        return super().finalize_response(request, response, *args, **kwargs)

    @start_end_log
    @level_log(1)
    def get(self, request, key=None):
        if key:
            return self.retrieve(request)
        else:
            return self.list(request)

    @start_end_log
    @level_log(1)
    def get_queryset(self):
        return super().get_queryset()

    @start_end_log
    @level_log(1)
    def get_serializer_class(self):
        return super().get_serializer_class()

    @start_end_log
    @level_log(1)
    def get_object(self):
        return super().get_object()
