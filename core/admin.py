from django.contrib import admin
from .models import Client, Trash, Product, ProductHistory, ProductMold, ProductMoldHistory

admin.site.register(Client)
admin.site.register(Trash)
admin.site.register(Product)
admin.site.register(ProductHistory)
admin.site.register(ProductMold)
admin.site.register(ProductMoldHistory)
