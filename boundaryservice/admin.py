from django.contrib import admin
from django.contrib.gis.admin import OSMGeoAdmin
from tastypie.models import ApiAccess, ApiKey

from boundaryservice.models import (BoundarySet, Boundary, PointSet, Point,
                                    Shapefile)


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


class PointSetAdmin(admin.ModelAdmin):
    list_filter = ('authority', 'domain')

admin.site.register(PointSet, PointSetAdmin)


class PointAdmin(OSMGeoAdmin):
    list_display = ('kind', 'name', 'external_id')
    list_display_links = ('name', 'external_id')
    list_filter = ('kind',)

admin.site.register(Point, PointAdmin)


class ShapefileAdmin(admin.ModelAdmin):
    list_display = ('name', 'authority', 'domain')
    list_display_links = ('name',)
    list_filter = ('authority', 'domain')

admin.site.register(Shapefile, ShapefileAdmin)
