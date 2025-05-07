from django.contrib import admin
from .models import SolicitudServicio,User,Camion,Chofer,Factura,Mantenimiento ,MotivoMantenimiento,Mantenimiento_Detalle,Mecanico,Empresa
from .models import SolicitudAlianza,ContratoAlianza,RechazoSolicitud,RechazoContrato,HojadeRuta,GuiaRemision,DetalleGuiaRemision,Reporte
admin.site.register(SolicitudServicio)
admin.site.register(User)
admin.site.register(Camion)
admin.site.register(Chofer)
admin.site.register(Factura)
admin.site.register(Mecanico)
admin.site.register(Mantenimiento)
admin.site.register(MotivoMantenimiento)
admin.site.register(Mantenimiento_Detalle)
admin.site.register(Empresa)
admin.site.register(SolicitudAlianza)
admin.site.register(ContratoAlianza)
admin.site.register(RechazoSolicitud)
admin.site.register(RechazoContrato)
admin.site.register(HojadeRuta)
admin.site.register(GuiaRemision)
admin.site.register(DetalleGuiaRemision)
admin.site.register(Reporte)

# Register your models here.
