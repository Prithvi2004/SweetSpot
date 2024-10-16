from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CustomerViewSet, CakeViewSet, CakeCustomizationViewSet, CartViewSet, OrderViewSet

router = DefaultRouter()
router.register(r'customers', CustomerViewSet)
router.register(r'cakes', CakeViewSet)
router.register(r'customizations', CakeCustomizationViewSet)
router.register(r'carts', CartViewSet)
router.register(r'orders', OrderViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('customers/login/', CustomerViewSet.as_view({'post': 'login'}), name='customer-login'),
]