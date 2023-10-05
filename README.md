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

# ViewSets
منبع  : https://www.django-rest-framework.org/api-guide/viewsets/

`ViewSet` in other frameworkds -> `Resources` or `Controllers`

~~`.get()`~~, ~~`.post()`~~ -> `.list()`, `.create()`

``` python
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from myapps.serializers import UserSerializer
from rest_framework import viewsets
from rest_framework.response import Response

class UserViewSet(viewsets.ViewSet):
    """
    A simple ViewSet for listing or retrieving users.
    """
    def list(self, request):
        queryset = User.objects.all()
        serializer = UserSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = User.objects.all()
        user = get_object_or_404(queryset, pk=pk)
        serializer = UserSerializer(user)
        return Response(serializer.data)
```

bind this viewset into two seprate views
``` python
user_list = UserViewSet.as_view({'get': 'list'})
user_detail = UserViewSet.as_view({'get': 'retrieve'})
```

automatically generated
``` python
from myapp.views import UserViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
urlpatterns = router.urls
```

`ModelViewSet`
``` python
class UserViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing user instances.
    """
    serializer_class = UserSerializer
    queryset = User.objects.all()
```

ViewSet is better:
- Repeated logic can be combined into a single class. In the above example, we only need to specify the `queryset` once, and it'll be used across multiple views.
- By using routers, we no longer need to deal with wiring up the URL conf ourselves.
- you want to get up and running quickly, or when you have a large API and you want to enforce a consistent URL configuration throughout.

View is better:
- Using regular views and URL confs is more explicit and gives you more control.

## ViewSet actions
``` python
class UserViewSet(viewsets.ViewSet):
    """
    Example empty viewset demonstrating the standard
    actions that will be handled by a router class.

    If you're using format suffixes, make sure to also include
    the `format=None` keyword argument for each action.
    """

    def list(self, request):
        pass

    def create(self, request):
        pass

    def retrieve(self, request, pk=None):
        pass

    def update(self, request, pk=None):
        pass

    def partial_update(self, request, pk=None):
        pass

    def destroy(self, request, pk=None):
        pass
```

## Introspecting ViewSet actions
ViewSet attrebutes:
- `basename` ->  the base to use for the URL names that are created.
- `action` -> the name of the current action (e.g., `list`, `create`).
- `detail` -> `true` for detail view and `false` for list view
- `suffix` -> the display suffix for the viewset type - mirrors the `detail` attribute.
- `name` -> the display name for the viewset. This argument is mutually exclusive to `suffix`.
- `description` -> the display description for the individual view of a viewset.

``` python
def get_permissions(self):
    """
    Instantiates and returns the list of permissions that this view requires.
    """
    if self.action == 'list':
        permission_classes = [IsAuthenticated]
    else:
        permission_classes = [IsAdminUser]
    return [permission() for permission in permission_classes]
```

## Marking extra actions for routing
``` python
from django.contrib.auth.models import User
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from myapp.serializers import UserSerializer, PasswordSerializer

class UserViewSet(viewsets.ModelViewSet):
    """
    A viewset that provides the standard actions
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=True, methods=['post'])
    def set_password(self, request, pk=None):
        user = self.get_object()
        serializer = PasswordSerializer(data=request.data)
        if serializer.is_valid():
            user.set_password(serializer.validated_data['password'])
            user.save()
            return Response({'status': 'password set'})
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False)
    def recent_users(self, request):
        recent_users = User.objects.all().order_by('-last_login')

        page = self.paginate_queryset(recent_users)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(recent_users, many=True)
        return Response(serializer.data)
```

The `action` decorator will route `GET` requests by default, but may also accept other `HTTP methods` by setting the methods argument.

``` python
    @action(detail=True, methods=['post', 'delete'])
    def unset_password(self, request, pk=None):
       ...
```

The decorator allows you to override any viewset-level configuration such as `permission_classes`, `serializer_class`, `filter_backends`...:
``` python
    @action(detail=True, methods=['post'], permission_classes=[IsAdminOrIsSelf])
    def set_password(self, request, pk=None):
       ...
```

The two new actions will then be available at the urls `^users/{pk}/set_password/$ ` and `^users/{pk}/unset_password/$`. Use the `url_path` and `url_name` parameters to change the URL segment and the reverse URL name of the action.

To view all extra actions, call the `.get_extra_actions()` method.

## Routing additional HTTP methods for extra actions
``` python
    @action(detail=True, methods=['put'], name='Change Password')
    def password(self, request, pk=None):
        """Update the user's password."""
        ...

    @password.mapping.delete
    def delete_password(self, request, pk=None):
        """Delete the user's password."""
        ...
```

## Reversing action URLs
`.reverse_action()` is a convenience wrapper for `reverse()`, automatically passing the view's `request` object and prepending the `url_name` with the `.basename` attribute.

If you are not using a router, then you must provide the `basename` argument to the `.as_view()` method.

```python
>>> view.reverse_action('set-password', args=['1'])
'http://localhost:8000/api/users/1/set_password'
```
``` python
>>> view.reverse_action(view.set_password.url_name, args=['1'])
'http://localhost:8000/api/users/1/set_password'
```

## API Reference
### ViewSet
- inherits from `APIView`
- use any of the standard attributes (`permission_classes`, `authentication_classes`)
- does not provide any implementation of `actions`
- define the `action` implementations explicity

### GenericViewSet
- inherits from `GenericAPIView`
- provides the default set of `.get_object()`, `.get_queryset()` methods
- does not include any `actions`
- to use this you'll define the `actions`

### ModelViewSet
- inherits from `GenericAPIView`
- includes implementations for various actions, by mixing in the behavior of the various mixin classes
- actions -> `.list()`, `.retrieve()`, `.create()`, `.update()`, `.partual_update()`, `.destroy()`

``` python

class AccountViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing the accounts
    associated with the user.
    """
    serializer_class = AccountSerializer
    permission_classes = [IsAccountAdminOrReadOnly]

    def get_queryset(self):
        return self.request.user.accounts.all()
```

### ReadOnlyModelViewSet
- inherits from `GenericAPIView`
- only provides the `'read-only'` actions, `.list()` and `.retrieve()`.

## Custom ViewSet base classes
``` python
from rest_framework import mixins

class CreateListRetrieveViewSet(mixins.CreateModelMixin,
                                mixins.ListModelMixin,
                                mixins.RetrieveModelMixin,
                                viewsets.GenericViewSet):
    """
    A viewset that provides `retrieve`, `create`, and `list` actions.

    To use it, override the class and set the `.queryset` and
    `.serializer_class` attributes.
    """
    pass
```
