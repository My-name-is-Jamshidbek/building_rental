from django.db import models
from django.contrib.auth.models import User  # Using Django's default User model

#
class Client(models.Model):
    fullname = models.CharField(max_length=255)
    phone = models.CharField(max_length=50, blank=True, null=True)
    desc = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.fullname

#
class Trash(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    prepayment = models.BigIntegerField(default=0)
    total = models.BigIntegerField(default=0)
    is_end = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Transaction #{self.id} - {self.client.fullname}"

#
class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.BigIntegerField()
    count = models.PositiveIntegerField()

    def __str__(self):
        return self.name

class ProductHistory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    count = models.PositiveIntegerField()
    trash = models.ForeignKey(Trash, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.product.name} in Transaction #{self.trash.id}"

#
class ProductMold(models.Model):
    length = models.BigIntegerField()
    price = models.BigIntegerField()
    count = models.PositiveIntegerField()

    def __str__(self):
        return f"Mold (Length: {self.length})"

class ProductMoldHistory(models.Model):
    product_mold = models.ForeignKey(ProductMold, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    count = models.PositiveIntegerField()
    trash = models.ForeignKey(Trash, on_delete=models.CASCADE)

    def __str__(self):
        return f"Mold #{self.product_mold_id} in Transaction #{self.trash.id}"
