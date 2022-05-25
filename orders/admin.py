from django.contrib import admin
from .models import Payment,Order,OrderProduct
# Register your models here.
class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    readonly_fields = ('usuario', 'producto', 'cantidad', 'precio_producto', 'ordered')
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'order_number', 'nombre', 'numero', 'email', 'barrio', 'order_total', 'status', 'is_ordered', 'create_at']
    list_filter = ['status', 'is_ordered']
    search_filter=['order_nuber','nombre','apellido','numero', 'email']
    list_per_page = 20
    inlines = [OrderProductInline]


admin.site.register(Payment)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderProduct)