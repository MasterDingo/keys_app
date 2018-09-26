from rest_framework.routers import SimpleRouter

from .views import KeyViewset

router = SimpleRouter()
router.register('api', KeyViewset)

urlpatterns = router.urls
