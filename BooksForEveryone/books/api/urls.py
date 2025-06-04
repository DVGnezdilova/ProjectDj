from rest_framework.routers import DefaultRouter
from books.api.views import BookViewSet

router = DefaultRouter()
router.register(r'books', BookViewSet, basename='book')


urlpatterns = router.urls
