from rest_framework.routers import DefaultRouter
from .views import QueueTicketViewSet

router = DefaultRouter()
router.register(r'tickets', QueueTicketViewSet, basename='queue-ticket')

urlpatterns = router.urls
