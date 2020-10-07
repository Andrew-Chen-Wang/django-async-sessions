"""
Index template's websockets
"""
import cgi
import codecs

from django.core.exceptions import ImproperlyConfigured
from django.core.cache import caches
from django.contrib.sessions.backends.cache import KEY_PREFIX as SESSION_KEY_PREFIX
from django.conf import settings
from django.utils.functional import cached_property
from django.http import parse_cookie


class WebsocketRequest:
    def __init__(self, scope):
        self.scope = scope
        self._post_parse_error = False
        self._read_started = False
        self.resolver_match = None
        self.script_name = self.scope.get('root_path', '')
        if self.script_name and scope['path'].startswith(self.script_name):
            # TODO: Better is-prefix checking, slash handling?
            self.path_info = scope['path'][len(self.script_name):]
        else:
            self.path_info = scope['path']
        # The Django path is different from ASGI scope path args, it should
        # combine with script name.
        if self.script_name:
            self.path = '%s/%s' % (
                self.script_name.rstrip('/'),
                self.path_info.replace('/', '', 1),
            )
        else:
            self.path = scope['path']
        # Ensure query string is encoded correctly.
        query_string = self.scope.get('query_string', '')
        if isinstance(query_string, bytes):
            query_string = query_string.decode()
        self.META = {
            'QUERY_STRING': query_string,
            'SCRIPT_NAME': self.script_name,
            'PATH_INFO': self.path_info,
            # WSGI-expecting code will need these for a while
            'wsgi.multithread': True,
            'wsgi.multiprocess': True,
        }
        if self.scope.get('client'):
            self.META['REMOTE_ADDR'] = self.scope['client'][0]
            self.META['REMOTE_HOST'] = self.META['REMOTE_ADDR']
            self.META['REMOTE_PORT'] = self.scope['client'][1]
        if self.scope.get('server'):
            self.META['SERVER_NAME'] = self.scope['server'][0]
            self.META['SERVER_PORT'] = str(self.scope['server'][1])
        else:
            self.META['SERVER_NAME'] = 'unknown'
            self.META['SERVER_PORT'] = '0'
        # Headers go into META.
        for name, value in self.scope.get('headers', []):
            name = name.decode('latin1')
            if name == 'content-length':
                corrected_name = 'CONTENT_LENGTH'
            elif name == 'content-type':
                corrected_name = 'CONTENT_TYPE'
            else:
                corrected_name = 'HTTP_%s' % name.upper().replace('-', '_')
            # HTTP/2 say only ASCII chars are allowed in headers, but decode
            # latin1 just in case.
            value = value.decode('latin1')
            if corrected_name in self.META:
                value = self.META[corrected_name] + ',' + value
            self.META[corrected_name] = value
        # Pull out request encoding, if provided.
        self._set_content_type_params(self.META)
        # Other bits.
        self.resolver_match = None

    def _set_content_type_params(self, meta):
        """Set content_type, content_params, and encoding."""
        self.content_type, self.content_params = cgi.parse_header(meta.get('CONTENT_TYPE', ''))
        if 'charset' in self.content_params:
            try:
                codecs.lookup(self.content_params['charset'])
            except LookupError:
                pass
            else:
                self.encoding = self.content_params['charset']

    def _get_scheme(self):
        return self.scope.get('scheme') or 'ws'

    @property
    def scheme(self):
        if settings.SECURE_PROXY_SSL_HEADER:
            try:
                header, secure_value = settings.SECURE_PROXY_SSL_HEADER
            except ValueError:
                raise ImproperlyConfigured(
                    'The SECURE_PROXY_SSL_HEADER setting must be a tuple containing two values.'
                )
            header_value = self.META.get(header)
            if header_value is not None:
                return 'wss' if header_value == secure_value else 'ws'
        return self._get_scheme()

    def is_secure(self):
        return self.scheme == 'wss'

    @cached_property
    def COOKIES(self):
        return parse_cookie(self.META.get('HTTP_COOKIE', ''))


async def websocket_application(scope, receive, send):

    request = WebsocketRequest(scope)
    cache = caches["async"]
    session = await cache.get_async(SESSION_KEY_PREFIX + request.COOKIES["sessionid"])

    event = await receive()
    if event['type'] == 'websocket.connect' and session is not None:
        await send({'type': 'websocket.accept'})
    else:
        await send({"type": "websocket.disconnect"})
        return

    print(session)

    while True:
        event = await receive()
        if event['type'] == 'websocket.disconnect':
            break

        if event['type'] == 'websocket.receive':
            if event['text'] == 'ping':
                await send({
                    'type': 'websocket.send',
                    'text': 'pong!'
                })
