from django.contrib import admin
from django.contrib.gis.admin import OSMGeoAdmin
from tastypie.models import ApiAccess, ApiKey

from boundaryservice.models import BoundarySet, Boundary

class ApiAccessAdmin(admin.ModelAdmin):
    pass

admin.site.register(ApiAccess, ApiAccessAdmin)

class ApiKeyAdmin(admin.ModelAdmin):
    pass

admin.site.register(ApiKey, ApiKeyAdmin)

class BoundarySetAdmin(admin.ModelAdmin):
    list_filter = ('authority', 'domain')

admin.site.register(BoundarySet, BoundarySetAdmin)

class BoundaryAdmin(OSMGeoAdmin):
    list_display = ('kind', 'name', 'external_id')
    list_display_links = ('name', 'external_id')
    list_filter = ('kind',)

admin.site.register(Boundary, BoundaryAdmin)
