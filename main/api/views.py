from django.utils.translation import ugettext_lazy as _

from rest_framework import generics, status, viewsets
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.decorators import action
from rest_framework.response import Response

from .serializers import KeySymbolsSerializer, KeyDetailsSerializer
from ..models import Key, status2text
from .decorators import api_permission_required


RESPONSE_STATUS_OK = 'ok'
RESPONSE_STATUS_ERROR = 'error'


def make_response(data=None, status=RESPONSE_STATUS_OK, message=None,
                  http_code=200):
    '''
    Создает ответ заданного формата:
    status - общий успех операции, ok либо error
    message - сообщение для пользователя. Не обязателен.
    data - данные из запроса. Не обязателен.

    Аргументы:
    data - данные для возврата, по умолчанию отсутствуют
    status - общий успех операции. По умолчанию "ok"
    message - сообщение для показа пользователю. По умолчанию отсутствует.
    http_code - HTTP-код ответа, по умолчанию 200
    '''

    body = {'status': status}

    if data is not None:
        body['data'] = data
    if message:
        body['message'] = message

    return Response(body, status=http_code)



class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return


class KeyViewset(viewsets.GenericViewSet):
    queryset = Key.objects.all()
    lookup_field = 'symbols'
    serializer_class = KeySymbolsSerializer
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)

    @action(methods=['post'], detail=False)
    @api_permission_required('generate_key')
    def generate(self, request):
        ''' Гененрировать один ключ '''
        key = Key.gen_new()
        serializer = KeySymbolsSerializer(key)
        return make_response(serializer.data['symbols'])

    @action(methods=['post'], detail=False)
    @api_permission_required('generate_key')
    def bulk_generate(self, request):
        ''' Генерировать несколько ключей '''
        count = request.POST.get('count')
        if not count:
            return self.bad_request()
        else:
            try:
                count = int(count)
            except:
                return self.bad_request()
        for i in range(count):
            key = Key.gen_new()
        return make_response()

    @action(detail=False)
    @api_permission_required('get_key')
    def acquire(self, request):
        ''' Выдать ключ '''
        key = Key.objects.free.first()
        if key:
            key.acquire()
            serializer = KeySymbolsSerializer(key)
            return make_response(serializer.data['symbols'])
        else:
            return make_response(status=RESPONSE_STATUS_ERROR,
                                 message=_("no more free keys"))

    @action(detail=False, url_path='count', url_name='count')
    @api_permission_required('get_key_count')
    def free_count(self, request):
        ''' Количество невыданных ключей '''
        count = Key.objects.free.count()
        return make_response(count)

    @action(detail=True, url_path='status', url_name='status')
    @api_permission_required('check_key_status')
    def key_status(self, request, symbols):
        ''' Статус заданного ключа '''
        key = Key.by_symbols(symbols)

        if key:
            serializer = KeyDetailsSerializer(key)
            return make_response(serializer.data['status'],
                               message=key.verbose_status)
        else:
            return self.key_not_found()

    @action(methods=['post'], detail=False)
    @api_permission_required('use_key')
    def activate(self, request):
        ''' Активировать ключ '''
        key = Key.by_symbols(request.POST.get('symbols', ''))

        if key:
            if key.is_activated:
                return make_response(message=_("key is already activated"),
                                     status=RESPONSE_STATUS_ERROR)
            if key.activate():
                return make_response(message=_("key activated"))
            else:
                return self.key_not_found()
        else:
            return self.key_not_found()

    def key_not_found(self):
        ''' Ответ, если ключ не найден '''
        return make_response(status=RESPONSE_STATUS_ERROR,
                             message=_("key not found"))

    def bad_request(self):
        ''' Ответ при некорректном запросе '''
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def forbidden(self):
        ''' Ответ при недостатке привилегий '''
        return Response(status=status.HTTP_403_FORBIDDEN)
