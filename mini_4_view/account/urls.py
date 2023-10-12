from django.urls import path

from account.views import CustomGenericAPIView

urlpatterns = [
    path('APIView/', CustomGenericAPIView.as_view()),
    path('APIView/<int:key>/', CustomGenericAPIView.as_view()),
]
