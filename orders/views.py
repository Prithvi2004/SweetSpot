from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.mail import send_mail
from .models import Customer, Cake, CakeCustomization, Cart, Order
from .serializers import CustomerSerializer, CakeSerializer, CakeCustomizationSerializer, CartSerializer, OrderSerializer

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

    @action(detail=False, methods=['post'])
    def login(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        try:
            customer = Customer.objects.get(email=email)
            if customer.check_password(password):
                return Response({"message": "Login Successful"}, status=status.HTTP_200_OK)
            return Response({"error": "Invalid password"}, status=status.HTTP_400_BAD_REQUEST)
        except Customer.DoesNotExist:
            return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'])
    def register(self, request):
        serializer = CustomerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CakeViewSet(viewsets.ModelViewSet):
    queryset = Cake.objects.all()
    serializer_class = CakeSerializer

class CakeCustomizationViewSet(viewsets.ModelViewSet):
    queryset = CakeCustomization.objects.all()
    serializer_class = CakeCustomizationSerializer

class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer

    @action(detail=False, methods=['post'])
    def add_to_cart(self, request):
        customer = request.user
        cake_id = request.data.get('cake_id')
        customization_data = request.data.get('customization')

        try:
            cake = Cake.objects.get(id=cake_id)
            if not cake.available:
                return Response({"error": "Cake not available"}, status=status.HTTP_400_BAD_REQUEST)

            cart, created = Cart.objects.get_or_create(customer=customer)

            if customization_data:
                customization = CakeCustomization.objects.create(
                    customer=customer,
                    cake=cake,
                    message=customization_data.get('message', ''),
                    egg_version=customization_data.get('egg_version', False),
                    toppings=customization_data.get('toppings', ''),
                    shape=customization_data.get('shape', '')
                )
                cart.customization = customization

            cart.cakes.add(cake)
            cart.quantity += 1
            cart.save()

            return Response({"message": "Cake added to cart"}, status=status.HTTP_200_OK)
        except Cake.DoesNotExist:
            return Response({"error": "Cake not found"}, status=status.HTTP_404_NOT_FOUND)

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    @action(detail=False, methods=['post'])
    def place_order(self, request):
        customer = request.user
        cart = Cart.objects.get(customer=customer)

        if not cart:
            return Response({"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)

        order = Order.objects.create(
            customer=customer,
            total_price=cart.total_amount,
            delivery_address=customer.address
        )

        for cake in cart.cakes.all():
            order.items.add(cake)
        order.save()

        # Clear cart
        cart.delete()

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['put'])
    def update_order(self, request, pk=None):
        order = self.get_object()
        order_status = request.data.get('order_status')
        payment_status = request.data.get('payment_status')
        payment_method = request.data.get('payment_method')

        order.order_status = order_status
        order.payment_status = payment_status
        order.payment_method = payment_method
        order.save()

        # Send email
        send_mail(
            "Payment Successful",
            "Your order has been placed successfully!",
            'from@example.com',
            [order.customer.email],
            fail_silently=False,
        )

        # Remove items from cart
        cart = Cart.objects.get(customer=order.customer)
        cart.delete()

        return Response({"message": "Order updated and email sent"}, status=status.HTTP_200_OK)