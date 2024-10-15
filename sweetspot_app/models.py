from django.db import models
from django.contrib.auth.hashers import make_password

class Customer(models.Model):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    phone_no = models.CharField(max_length=15)
    address = models.TextField(default="No address provided")
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    
    def save(self, *args, **kwargs):
        # Hash the password before saving the customer
        self.password = make_password(self.password)
        super(Customer, self).save(*args, **kwargs)

    # def __str__(self):
    #     return f"{self.first_name} {self.last_name} ({self.email})"

class Cake(models.Model):
    name = models.CharField(max_length=100)
    flavour = models.CharField(max_length=50)
    size = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    description = models.TextField()
    image = models.ImageField(upload_to='cakes/')
    available = models.BooleanField(default=True)

    # def __str__(self):
    #     return f"{self.name} - {self.flavour}"

class CakeCustomization(models.Model):
    message = models.CharField(max_length=255, blank=True, null=True)
    egg_version = models.BooleanField(default=False)
    toppings = models.CharField(max_length=255, blank=True, null=True)
    shape = models.CharField(max_length=50, blank=True, null=True)
    cake = models.ForeignKey(Cake, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)

    # def __str__(self):
    #     return f"Customization for {self.cake.name} by {self.customer.email}"
    
class Cart(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    cakes = models.ManyToManyField(Cake)
    quantity = models.PositiveIntegerField(default=1)
    customization = models.ForeignKey(CakeCustomization, on_delete=models.SET_NULL, null=True, blank=True)
    total_amount = models.DecimalField(max_digits=7, decimal_places=2, default=0.00)

    # def __str__(self):
    #     return f"Cart for {self.customer.email}"
    
class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    cake_customization = models.ForeignKey(CakeCustomization, on_delete=models.SET_NULL, null=True, blank=True)
    items = models.ManyToManyField(Cake)
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    order_date = models.DateTimeField(auto_now_add=True)
    delivery_address = models.TextField()
    order_status = models.CharField(max_length=50, choices=[('Pending', 'Pending'), ('Delivered', 'Delivered')], default='Pending')
    payment_status = models.CharField(max_length=50, choices=[('Pending', 'Pending'), ('Completed', 'Completed')], default='Pending')
    payment_method = models.CharField(max_length=50, choices=[('Card', 'Card'), ('Cash', 'Cash')], default='Card')

    # def __str__(self):
    #     return f"Order by {self.customer.email} on {self.order_date}"