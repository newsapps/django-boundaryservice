from django.conf import settings
from django.contrib import admin
from tastypie.models import ApiAccess, ApiKey
from boundaryservice.models import BoundarySet, Boundary

if ('django.contrib.gis' in settings.INSTALLED_APPS):
    try:
        from django.contrib.gis.admin import OSMGeoAdmin
        BoundaryModelAdminParent = OSMGeoAdmin
    except:
        BoundaryModelAdminParent = admin.ModelAdmin
else:
    BoundaryModelAdminParent = admin.ModelAdmin


class ApiAccessAdmin(admin.ModelAdmin):
    pass

admin.site.register(ApiAccess, ApiAccessAdmin)


class BoundarySetAdmin(admin.ModelAdmin):
    list_filter = ('authority', 'domain')

admin.site.register(BoundarySet, BoundarySetAdmin)


class BoundaryAdmin(BoundaryModelAdminParent):
    list_display = ('kind', 'name', 'external_id')
    list_display_links = ('name', 'external_id')
    list_filter = ('kind',)

admin.site.register(Boundary, BoundaryAdmin)
