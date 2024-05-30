from django.db import models
from apps.catalog.models import Product
# Create your models here.

class Wishlist(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    
    def __str__(self):
        return f'{self.user.username} - {self.product.title}'                       

    class Meta:
        verbose_name = 'Whislist'
        verbose_name_plural = 'Whislists'
        
    def get_total(self):
        return self.product.price * self.quantity