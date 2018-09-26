from django.urls import path, include

from .views import index

urlpatterns = [
#    path('', KeyViewset.as_view())
    path('', include('main.api.urls')),
    path('', index)
]
