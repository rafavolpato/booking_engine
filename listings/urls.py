from rest_framework import routers
from listings.views import UnitViewSet

router = routers.SimpleRouter()
router.register(r'units', UnitViewSet)

urlpatterns = router.urls

