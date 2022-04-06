from django.conf import settings
from django.contrib import admin
from tastypie.models import ApiAccess, ApiKey
from boundaryservice.models import BoundarySet, Boundary

if "django.contrib.gis" in settings.INSTALLED_APPS:
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
    list_display = (
        "pk",
        "name",
        "authority",
        "domain",
        "count",
        "last_updated",
    )
    list_display_links = (
        "pk",
        "name",
    )
    list_filter = ("authority", "domain")


admin.site.register(BoundarySet, BoundarySetAdmin)


class BoundaryAdmin(BoundaryModelAdminParent):
    list_display = (
        "pk",
        "name",
        "external_id",
        "kind",
        "set",
    )
    list_display_links = (
        "pk",
        "name",
    )
    list_filter = (
        "kind",
        "set",
    )


admin.site.register(Boundary, BoundaryAdmin)
