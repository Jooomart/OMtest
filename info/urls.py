from django.urls import path
from .views import CombinedView

urlpatterns = [
    path('<str:lang>/combined/', CombinedView.as_view(), name='combined-view'),
]
