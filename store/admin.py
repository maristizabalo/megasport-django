from django.contrib import admin
from .models import Producto, ReviewRating, Variation

# Register your models here.
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre_producto', 'precio', 'categoria', 'modified_date', 'is_available' )
    prepopulated_fields = { 'slug' : ('nombre_producto',)}

class VariationAdmin(admin.ModelAdmin):
    list_display = ('producto', 'variation_value', 'is_active',)
    list_editable = ('is_active',)
    list_filter = ('producto', 'variation_value', 'is_active',)

admin.site.register(Producto, ProductoAdmin)
admin.site.register(Variation, VariationAdmin)
admin.site.register(ReviewRating)