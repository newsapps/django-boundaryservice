from xml.sax.saxutils import escape

def generate_placemark(name, geom):
    return u"<Placemark><name>%s</name>%s</Placemark>" %(
        escape(name),
        geom.kml
    )

def generate_kml_document(placemarks):
    return """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
<Document>
%s
</Document>
</kml>""" % u"\n".join(placemarks)