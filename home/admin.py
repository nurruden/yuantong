from django.contrib import admin
from .models import MaterialMapping, CostObjectMapping

@admin.register(MaterialMapping)
class MaterialMappingAdmin(admin.ModelAdmin):
    list_display = ('id', 'material_code', 'material_name', 'created_at')
    search_fields = ('material_code', 'material_name') 



@admin.register(CostObjectMapping)
class CostObjectMappingAdmin(admin.ModelAdmin):
    list_display = ('id', 'cost_object_code', 'cost_object_name', 'created_at')
    search_fields = ('cost_object_code', 'cost_object_name') 