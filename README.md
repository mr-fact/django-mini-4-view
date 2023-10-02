# django-mini-4-view
منبع  : https://www.django-rest-framework.org/api-guide/views/


## Class-based Views
`APIView` classes are different from regular `View` classes in the following ways:
- Requests passed to the handler methods will be REST framework's `Request` instances, not Django's `HttpRequest` instances.
- Handler methods may return REST framework's `Response`, instead of Django's `HttpResponse`. The view will manage content negotiation and setting the correct renderer on the response.
- Any `APIException` exceptions will be caught and mediated into appropriate responses.
- Incoming requests will be authenticated and appropriate permission and/or throttle checks will be run before dispatching the request to the handler method.

Using the `APIView` class is pretty much the same as using a regular `View` class
``` python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from django.contrib.auth.models import User

class ListUsers(APIView):
    """
    View to list all users in the system.

    * Requires token authentication.
    * Only admin users are able to access this view.
    """
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAdminUser]

    def get(self, request, format=None):
        """
        Return a list of all users.
        """
        usernames = [user.username for user in User.objects.all()]
        return Response(usernames)
```

**Note:**  the Classy Django REST Framework resource provides a browsable reference, with full methods and attributes, for each of Django REST Framework's class-based views.

### API policy attributes
`.renderer_classes`

`.parser_classes`

`.authentication_classes`

`.throttle_classes`

`.permission_classes`

`.content_negotiation_class`

### API policy instantiation methods
`.get_renderers(self)`

`.get_parsers(self)`

`.get_authenticators(self)`

`.get_throttles(self)`

`.get_permissions(self)`

`.get_content_negotiator(self)`

`.get_exception_handler(self)`

### API policy implementation methods

`.check_permissions(self, request)`

`.check_throttles(self, request)`

`.perform_content_negotiation(self, request, force=False)`

### Dispatch methods
`.dispatch()` -> `.initial(self, request, *args, **kwargs)` -> `.get()`, `.post()`, `put()`, `patch()` and `.delete()`

If you need to customize the error responses your API returns you should subclass `.handle_exception(self, exc)`.

`.initialize_request(self, request, *args, **kwargs)` -> handler -> `.finalize_response(self, request, response, *args, **kwargs)`

## Function Based Views
`@api_view(http_method_names=['GET'])`

By default only GET methods will be accepted

and other methods -> `405 Method Not Allowed`

``` python
@api_view(['GET', 'POST'])
def hello_world(request):
    if request.method == 'POST':
        return Response({"message": "Got some data!", "data": request.data})
    return Response({"message": "Hello, world!"})
```

### API policy decorators
uses a [throttle](https://www.django-rest-framework.org/api-guide/throttling/) to ensure it can only be called once per day by a particular user, use the `@throttle_classes` decorator, passing a list of throttle classes:
``` python
from rest_framework.decorators import api_view, throttle_classes
from rest_framework.throttling import UserRateThrottle

class OncePerDayUserThrottle(UserRateThrottle):
    rate = '1/day'

@api_view(['GET'])
@throttle_classes([OncePerDayUserThrottle])
def view(request):
    return Response({"message": "Hello for today! See you tomorrow!"})
```

- `@renderer_classes(...)`
- `@parser_classes(...)`
- `@authentication_classes(...)`
- `@throttle_classes(...)`
- `@permission_classes(...)`

### View schema decorator
`@schema` must come after **(below)** the `@api_view` decorator. For example:
``` python
from rest_framework.decorators import api_view, schema
from rest_framework.schemas import AutoSchema

class CustomAutoSchema(AutoSchema):
    def get_link(self, path, method, base_url):
        # override view introspection here...

@api_view(['GET'])
@schema(CustomAutoSchema())
def view(request):
    return Response({"message": "Hello for today! See you tomorrow!"})
```
You may pass `None` in order to exclude the view from schema generation. ([Schemas documentation](https://www.django-rest-framework.org/api-guide/schemas/))
``` python
@api_view(['GET'])
@schema(None)
def view(request):
    return Response({"message": "Will not appear in schema!"})
```
