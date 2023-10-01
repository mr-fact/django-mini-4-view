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
`.dispatch()` -> `.get()`, `.post()`, `put()`, `patch()` and `.delete()`
