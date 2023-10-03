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

# Generic views
منبع  : https://www.django-rest-framework.org/api-guide/generic-views/

``` python
from django.contrib.auth.models import User
from myapp.serializers import UserSerializer
from rest_framework import generics
from rest_framework.permissions import IsAdminUser

class UserList(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]

    def list(self, request):
        # Note the use of `get_queryset()` instead of `self.queryset`
        queryset = self.get_queryset()
        serializer = UserSerializer(queryset, many=True)
        return Response(serializer.data)
```
For very simple cases you might want to pass through any class attributes using the `.as_view()` method.
``` python
path('users/', ListCreateAPIView.as_view(queryset=User.objects.all(), serializer_class=UserSerializer), name='user-list')
```

## Attrubutes
### Basic settings
- `queryset`
- `serializer_class`
- `lookup_field` (default=`'pk'`)
- `lookup_url_kwarg` (default=`lookup_field`)

### Pagination
- `pagination_class`

settings -> `DEFAULT_PAGINATION_CLASS`=`'rest_framework.pagination.PageNumberPagination'`

disable pagination on this view -> `pagination_class`=`None`

### Filtering
- `filter_backends`

settings -> `DEFAULT_FILTER_BACKENDS`

## Methods
### Base methods
- `get_queryset(self)`

Returns the queryset that should be used for `list views`, and that should be used as the base for lookups in `detail views`.
``` python
def get_queryset(self):
    user = self.request.user
    return user.accounts.all()
```
- `get_objects(self)`

Returns an object instance that should be used for `detail views`.

Defaults to using the `lookup_field` parameter to filter the base queryset.

``` python
def get_object(self):
    queryset = self.get_queryset()
    filter = {}
    for field in self.multiple_lookup_fields:
        filter[field] = self.kwargs[field]

    obj = get_object_or_404(queryset, **filter)
    self.check_object_permissions(self.request, obj)
    return obj
```

- `filter_queryset(self, queryset)`
``` python
def filter_queryset(self, queryset):
    filter_backends = [CategoryFilter]

    if 'geo_route' in self.request.query_params:
        filter_backends = [GeoRouteFilter, CategoryFilter]
    elif 'geo_point' in self.request.query_params:
        filter_backends = [GeoPointFilter, CategoryFilter]

    for backend in list(filter_backends):
        queryset = backend().filter_queryset(self.request, queryset, view=self)

    return queryset
```

- `get_serializer_class(self)`

May be overridden to provide dynamic behavior
``` python
def get_serializer_class(self):
    if self.request.user.is_staff:
        return FullAccountSerializer
    return BasicAccountSerializer
```

### Save and deletion hooks
- `perform_create(self, serializer)` called by `CreateModelMixin`
- `perform_update(self, serializer)` called by `UpdateModelMixin`
- `perform_destroy(self, instance)` called by `DestroyModelMixin`

``` python
def perform_create(self, serializer):
    serializer.save(user=self.request.user)

def perform_update(self, serializer):
    instance = serializer.save()
    send_email_confirmation(user=self.request.user, modified=instance)
```
You can also use these hooks to provide additional validation, by raising a `ValidationError()`.
``` python
def perform_create(self, serializer):
    queryset = SignupRequest.objects.filter(user=self.request.user)
    if queryset.exists():
        raise ValidationError('You have already signed up')
    serializer.save(user=self.request.user)
```
### Other methods
- `get_serializer_context(self)` (default=`request`, `view`, `format`)
- `get_serializer(self, instance=None, data=None, many=False, partial=False)`
- `get_paginated_response(self, data)`
- `paginate_queryset(self, queryset)` (`None` if pagination is not configured for this view.)
- `filter_queryset(self, queryset)`

## Mixins
`rest_framework.mixins`

### ListModelMixin
`.list(request, *args, **kwargs)`

- Response -> `200 OK`, serialized representation of the querysert [paginated]

### CreateModelMixin
`.create(request, *args, **kwargs)`

- Response -> `201 Created`, serialized representation of the object
- Response -> `400 Bad Request`, error details

If the representation contains a key named `url`, then the `Location` header of the response will be populated with that value.

### RetrieveModelMixin
`retrieve(request, *args, **kwargs)`

- Response -> `200 OK`, serialized representation of the object
- Response -> `404 Not Found`, None

### UPdateModelMixin
`.update(request, *args, **kwargs)` (`PUT`)

`.partial_update(request, *args, **kwargs)` (`PATH`)

- Response -> `200 OK`, serialized representation of the object
- Response -> `400 Bad Request`, error details

### DestroyModelMixin
`destroy(request, *args, **kwargs)`

- Response -> `204 No content`, None
- Response -> `404 Not Found`, None

## Concrete View Classes
`rest_framework.generics`

### CreateAPIView
(GenericAPIView, CreateModelMixin)

`create-only`, `single model instance`, `POST`

### ListAPIView
(GenericAPIView, ListModelMixin)

`read-only`, `collection of model instances`, `GET`

### RetrieveAPIView
(GenericAPIView, RetrieveModelMixin)

`read-only`, `single model instance`, `GET`

### DestroyAPIView
(GenericAPIView, DestroyModelMixin)

`read-only`, `single model instance`, `DELETE`

### UpdateAPIView
(GenericAPIView, UpdateModelMixin)

`update-only`, `single model instance`, `PUT`, `PATCH`

### ListCreateAPIView
(GenericAPIView, ListModelMixin, CreateModelMixin)


`read-write`, `collection of model instances`, `GET`, `POST`

### RetrieveUpdateAPIView
(GenericAPIView, RetrieveModelMixin, UpdateModelMixin)

`read-update`, `single model instance`, `GET`, `PUT`, `PATCH`

### RetrieveDestroyAPIView
(GenericAPIView, RetrieveModelMixin, DestroyModelMixin)

`read-delete`, `single model instance`, `GET`, `DELETE`

### RetrieveUpdateDestroyAPIView
(GenericAPIView, RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin)

`read-write-delete`, `single model instance`, `GET`, `PUT`, `PATCH`, `DELETE`


## Customizing the generic views
### Creating custom mixins
``` python
class MultipleFieldLookupMixin:
    """
    Apply this mixin to any view or viewset to get multiple field filtering
    based on a `lookup_fields` attribute, instead of the default single field filtering.
    """
    def get_object(self):
        queryset = self.get_queryset()             # Get the base queryset
        queryset = self.filter_queryset(queryset)  # Apply any filter backends
        filter = {}
        for field in self.lookup_fields:
            if self.kwargs.get(field): # Ignore empty fields.
                filter[field] = self.kwargs[field]
        obj = get_object_or_404(queryset, **filter)  # Lookup the object
        self.check_object_permissions(self.request, obj)
        return obj

class RetrieveUserView(MultipleFieldLookupMixin, generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_fields = ['account', 'username']
```

### Creating custom base classes
``` python
class BaseRetrieveView(MultipleFieldLookupMixin,
                       generics.RetrieveAPIView):
    pass

class BaseRetrieveUpdateDestroyView(MultipleFieldLookupMixin,
                                    generics.RetrieveUpdateDestroyAPIView):
    pass
```

## PUT as create
Both styles `PUT as 404` and `PUT as create` can be valid in different circumstances, but from version 3.0 onwards we now use `404` behavior as the default, due to it being simpler and more obvious.

If you need to generic `PUT-as-create` behavior you may want to include something like this [AllowPUTAsCreateMixin](https://gist.github.com/tomchristie/a2ace4577eff2c603b1b)https://gist.github.com/tomchristie/a2ace4577eff2c603b1b class as a mixin to your views.

## Third party packages
### Django Rest Multiple Models
[Django Rest Multiple Models](https://github.com/MattBroach/DjangoRestMultipleModels) provides a generic view (and mixin) for sending multiple serialized models and/or querysets via a single API request.
