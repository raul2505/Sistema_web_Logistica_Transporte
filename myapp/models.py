from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.core.validators import RegexValidator
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import date, timezone
from decimal import Decimal
# Create your models here.
from django.conf import settings

#MODELO NOTIFICACION
class Notificacion(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    mensaje = models.TextField()
    leido = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    def marcar_como_leida(self):
        self.leido = True
        self.save(update_fields=['leido'])
        
    def __str__(self):
        return f'Notificación para {self.usuario} - {self.mensaje[:30]}'

#MODELO EMPRESA
class Empresa(models.Model):
    logo_empresa = models.ImageField(upload_to='empresas/')
    nombre_empresa = models.CharField(max_length=50)
    ruc_empresa = models.CharField(max_length=11, unique=True)  # Ahora es CharField

    def __str__(self):
        return f"{self.nombre_empresa}"

#MODELO SOLICITUDES EXTERNAS
class SolicitudServicio(models.Model):
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    telefono = models.CharField(max_length=15)
    correo = models.EmailField(max_length=100)
    ruc_empresa = models.CharField(max_length=11)
    nombre_empresa = models.CharField(max_length=100)
    mensaje = models.TextField()

    def __str__(self):
        return f"{self.nombres} {self.apellidos} - {self.nombre_empresa}"
    
#MODELO PARA EL USUARIO
class User(AbstractUser):
    dni = models.CharField(max_length=8, unique=True, verbose_name="DNI")
    phone = models.CharField(max_length=15, blank=True, null=True, verbose_name="Teléfono")
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, verbose_name="Empresa", null=True, blank=True)
    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"

    def __str__(self):
        return self.username

    def __str__(self):
        return f"{self.username} - {self.empresa.nombre_empresa if self.empresa else 'Sin empresa'}"
    
    def has_role(self, role_name):
        """ Verifica si el usuario pertenece a un grupo (rol) específico """
        return self.groups.filter(name=role_name).exists()

#MODELO CHOFER 
class Chofer(models.Model):
    # Atributos básicos
     nombres = models.CharField(max_length=100)
     apellidos = models.CharField(max_length=100)
     fecha_nacimiento = models.DateField()
     domicilio = models.CharField(max_length=200)
     telefono = models.CharField(max_length=9)

    # Información de la licencia
     tipo_licencia = models.CharField(max_length=3)
     numero_licencia = models.CharField(max_length=20, unique=True)
     fecha_emision = models.DateField()
     fecha_vencimiento = models.DateField()

     #Estado de salud
     estado_salud = models.CharField(max_length=100)

    # Relación con el camión
     camion = models.ForeignKey('Camion', on_delete=models.SET_NULL, null=True, blank=True)
     # Relación con el usuario
     usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuario asociado", null=True, blank=True)

     def __str__(self):
        return f"{self.nombres} {self.apellidos} - Licencia: {self.numero_licencia}"


#CAMION MODELO
MARCAS_CAMIONES = [
    ('Isuzu', 'Isuzu'),
    ('Foton', 'Foton'),
    ('Hino', 'Hino'),
    ('International', 'International'),
    ('Mercedes-Benz', 'Mercedes-Benz'),
    ('Volvo', 'Volvo'),
    ('Scania', 'Scania'),
    ('MAN', 'MAN'),
    ('Hyundai', 'Hyundai'),
    ('Dongfeng', 'Dongfeng'),
    ('JAC', 'JAC'),
    ('FAW', 'FAW'),
    ('Sinotruk', 'Sinotruk'),
    ('Shacman', 'Shacman'),
    ('Kenworth', 'Kenworth'),
    ('Freightliner', 'Freightliner'),
]
TIPOS_CAMION = [
    ('Camión rígido', 'Camión rígido'),
    ('Tráiler', 'Tráiler'),
    ('Camión cisterna', 'Camión cisterna'),
    ('Camión frigorífico', 'Camión frigorífico'),
]
ESTADO_OPERATIVO_CHOICES = [
    ('Activo', 'Activo'),
    ('En mantenimiento', 'En mantenimiento'),
    ('Requiere Mantenimiento', 'Requiere Mantenimiento'),
]


    
class Camion(models.Model):

    foto_camion = models.ImageField(upload_to = 'camiones/')
    placa = models.CharField(max_length=10, unique=True, validators=[RegexValidator(regex=r'^[A-Z0-9-]+$', message="Formato inválido de placa.")])
    marca = models.CharField(max_length=50, choices=MARCAS_CAMIONES)
    modelo = models.CharField(max_length=50)
    year_fabricacion = models.PositiveIntegerField(validators=[MinValueValidator(1900), MaxValueValidator(date.today().year)])
    capacidad_carga = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    tipo_camion = models.CharField(max_length=50, choices=TIPOS_CAMION)
    estado_operativo = models.CharField(max_length=25, choices=ESTADO_OPERATIVO_CHOICES, default='Activo')
    fecha_adquisicion = models.DateField(default=date.today)  # Fecha actual por defecto
    def save(self, *args, **kwargs):
        if self.fecha_adquisicion > date.today():
            raise ValidationError("La fecha de adquisición no puede ser futura.")
        super().save(*args, **kwargs)
    propietario_vehiculo = models.CharField(max_length=100, default="Desconocido")
    rendimiento_combustible = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    empresa_propietaria = models.ForeignKey(Empresa,on_delete=models.CASCADE,related_name="camiones_empresa")
    notas = models.TextField(null=True, blank=True)

    def __str__(self):
       return f"{self.placa} - {self.marca} {self.modelo}"
    
#MOTIVO MANTENIMIENTO MODELO
from django.contrib.auth.models import Group

class MotivoMantenimiento(models.Model):
    camion = models.ForeignKey(Camion, on_delete=models.CASCADE, related_name="motivos_mantenimiento")
    motivo = models.TextField()
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        """Al guardar, cambia el estado del camión y envía la notificación."""
        self.camion.estado_operativo = "Requiere Mantenimiento"
        self.camion.save(update_fields=["estado_operativo"])
        super().save(*args, **kwargs)  # Guarda primero
        self.enviar_notificacion_mantenimiento()  # Luego envía la notificación

    def enviar_notificacion_mantenimiento(self):
        grupo_mantenimiento = Group.objects.get(name="mantenimiento")
        usuarios_mantenimiento = grupo_mantenimiento.user_set.all()
        mensaje = f"Se ha registro un camion el cual requiere mantenimiento  {self.camion.placa}."
        for usuario in usuarios_mantenimiento:
            Notificacion.objects.create(usuario=usuario, mensaje=mensaje) 

    def __str__(self):
        return f"Motivo de mantenimiento para {self.camion.placa} registrado el {self.fecha_registro.strftime('%Y-%m-%d %H:%M:%S')}"

#MECANICO MODELO
class Mecanico(models.Model):
    # Atributos básicos
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    telefono = models.CharField(max_length=9)
    
    # Campo para la foto
    foto = models.ImageField(upload_to='mecanicos/', null=True, blank=True)

    def __str__(self):
        return f"{self.nombres} {self.apellidos}"
    
#MANTENIMIENTO MODELO

TIPOS_MANTENIMIENTO = [
    ('Preventivo', 'Preventivo'),
    ('Correctivo', 'Correctivo'),
]
ESTADOS_MANTENIMIENTO = [
    ('Pendiente', 'Pendiente'),
    ('En Proceso', 'En Proceso'),
    ('Finalizado','Finalizado')
]
class Mantenimiento(models.Model):
    motivo = models.OneToOneField(MotivoMantenimiento, on_delete=models.CASCADE)
    camion = models.ForeignKey(Camion,on_delete=models.CASCADE)
    taller = models.ForeignKey(Mecanico,on_delete=models.CASCADE)
    fecha_mantenimiento = models.DateField()
    tipo_mantenimiento = models.CharField(max_length=50,choices=TIPOS_MANTENIMIENTO)  # Preventivo, Correctivo, etc.
    estado_mantenimiento = models.CharField(max_length=20, choices=ESTADOS_MANTENIMIENTO, default='Pendiente')


    def __str__(self):
        return f'Mantenimiento {self.id} - {self.camion.placa}'


#MANTENIMIENTO_DETALLE MODELO
from django.db.models import Sum
class Mantenimiento_Detalle(models.Model):
    mantenimiento = models.ForeignKey('Mantenimiento', on_delete=models.CASCADE)
    descripcion_servicio_repuesto = models.CharField(max_length=200)
    cantidad = models.PositiveIntegerField()
    costo_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    costo_total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"), editable=False)

    def save(self, *args, **kwargs):
        self.costo_total = self.cantidad * self.costo_unitario
        super().save(*args, **kwargs)  # Llamar al método save original
    def delete(self, *args, **kwargs):
        """ Al eliminar un detalle, también se debe actualizar la factura """
        mantenimiento_id = self.mantenimiento.id
        super().delete(*args, **kwargs)
        self.actualizar_factura(mantenimiento_id)

    def actualizar_factura(self, mantenimiento_id=None):
        """ Suma todos los costos totales de los detalles del mantenimiento y actualiza la factura """
        if not mantenimiento_id:
            mantenimiento_id = self.mantenimiento.id

        factura = Factura.objects.filter(mantenimiento_id=mantenimiento_id).first()
        if factura:
            total = Mantenimiento_Detalle.objects.filter(mantenimiento_id=mantenimiento_id).aggregate(Sum('costo_total'))['costo_total__sum'] or Decimal("0.00")
            factura.monto_total = total
            factura.save()

    def __str__(self):
        return f'Detalle {self.id} - {self.mantenimiento}'

#FACTURA MODELO
METODO_PAGO = [
                ('Efectivo', 'Efectivo'),
                ('Transferencia', 'Transferencia'),
              ]
ESTADO_PAGO = [
                ('Pagado','Pagado'),
                ('Pendiente','Pendiente')
              ]    
class Factura(models.Model):
    numero_factura = models.CharField(max_length=50, unique=True)
    fecha_emision = models.DateField()
    mantenimiento = models.OneToOneField(Mantenimiento, on_delete=models.SET_NULL,null=True,blank=True)
    taller = models.ForeignKey(Mecanico,on_delete=models.CASCADE)
    monto_total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    metodo_pago = models.CharField(max_length=15,choices=METODO_PAGO)  # Efectivo, Transferencia, etc.
    estado_pago = models.CharField(max_length=15,choices=ESTADO_PAGO)  # Pagado, Pendiente, etc.
    def save(self, *args, **kwargs):
        """ Al guardar la factura, recalcula el monto total si hay un mantenimiento asociado """
        super().save(*args, **kwargs)
        self.actualizar_monto_total()

    def actualizar_monto_total(self):
        """ Suma todos los costos totales de los detalles asociados al mantenimiento """
        if self.mantenimiento:
            total = Mantenimiento_Detalle.objects.filter(mantenimiento=self.mantenimiento).aggregate(Sum('costo_total'))['costo_total__sum'] or Decimal("0.00")
            self.monto_total = total
            super().save(update_fields=['monto_total'])

    def __str__(self):
        return self.numero_factura

#FACTURA_DETALLE MODELO

@receiver(post_save, sender=Mantenimiento)
def actualizar_estado_camion(sender, instance, created, **kwargs):
    """
    Actualiza el estado del camión a 'En mantenimiento' cuando se crea un mantenimiento.
    """
    if created:
        camion = instance.camion
        camion.estado_operativo = 'En mantenimiento'
        camion.save()

#MODELO SOLICITUD DE ALIANZA 
class SolicitudAlianza(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('aprobada', 'Aprobada'),
        ('rechazada', 'Rechazada'),
    ]
    solicitante = models.ForeignKey(User, on_delete=models.CASCADE)
    solicitud = models.FileField(upload_to='Solicitud/')
    descripcion = models.TextField()
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')

    def __str__(self):
        return f"Solicitud de {self.solicitante} - Estado: {self.estado}"

class RechazoSolicitud(models.Model):
    solicitud = models.OneToOneField(SolicitudAlianza, on_delete=models.CASCADE)
    motivo = models.TextField()
    fecha_rechazo = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Rechazo de {self.solicitud} - Motivo: {self.motivo[:30]}"

class ContratoAlianza(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('aprobado', 'Aprobado'),
        ('rechazada', 'Rechazado'),
    ]
    solicitud = models.OneToOneField(SolicitudAlianza, on_delete=models.CASCADE)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, default=1)
    documento = models.FileField(upload_to='contratos/')
    fecha_revision = models.DateTimeField(auto_now=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')

    def __str__(self):
        estado = dict(self.ESTADOS).get(self.estado, 'Desconocido')
        return f"Contrato ({self.id}) - Empresa: {self.empresa.nombre_empresa} - Estado: {estado}"
    
class RechazoContrato(models.Model):
    contrato = models.OneToOneField(ContratoAlianza, on_delete=models.CASCADE)
    motivo = models.TextField()
    fecha_rechazo = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Rechazo de {self.contrato} - Motivo: {self.motivo[:30]}"

class RegistroNormativas(models.Model):
    contador = models.ForeignKey(User, on_delete=models.CASCADE)
    descripcion = models.TextField()
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Registro de Normativas - {self.contador}"
    

class Ubicacion(models.Model):
    direccion = models.CharField(max_length=255, verbose_name="Dirección")
    latitud = models.DecimalField(max_digits=9, decimal_places=6, verbose_name="Latitud", default=0.000000)
    longitud = models.DecimalField(max_digits=9, decimal_places=6, verbose_name="Longitud", default=0.000000)
    provincia = models.CharField(max_length=100, verbose_name="Provincia")

    def __str__(self):
        return f"{self.direccion}, {self.provincia}"


#Utilizados para la asignación de las hojas de ruta
class HojadeRuta(models.Model):
    ESTADOS = (
        ('pendiente', 'Pendiente'),
        ('en_ruta', 'En Ruta'),
        ('finalizado', 'Finalizado'),
        ('iniciar', 'Iniciar'),
    )
    
    estado = models.CharField(
        max_length=50,
        choices=ESTADOS,
        default='pendiente',  # Valor por defecto
        verbose_name="Estado"
    )
    chofer = models.ForeignKey(Chofer, on_delete=models.CASCADE, verbose_name="Chofer")
    camion = models.ForeignKey(Camion, on_delete=models.CASCADE, verbose_name="Camión")
    partida_ubicacion = models.ForeignKey(Ubicacion, related_name='partida', on_delete=models.CASCADE, verbose_name="Ubicación de Partida")
    llegada_ubicacion = models.ForeignKey(Ubicacion, related_name='llegada', on_delete=models.CASCADE, verbose_name="Ubicación de Llegada")
    distancia = models.FloatField(null=True, blank=True, verbose_name="Distancia (km)")


    def __str__(self):
        return f"Hoja de Ruta {self.id} - {self.chofer.nombres} {self.chofer.apellidos} - {self.camion.placa}"


from django.db import models
from django.core.exceptions import ValidationError

class GuiaRemision(models.Model):
    """
    Modelo que representa una Guía de Remisión.
    Puede ser de tipo "Transporte" o "Remitente".
    """
    TRANSPORTE = "TRANSPORTE"
    REMITENTE = "REMITENTE"
    
    TIPO_CHOICES = [
        (TRANSPORTE, "Transporte"),
        (REMITENTE, "Remitente"),
    ]
    
    hoja_de_ruta = models.ForeignKey('HojadeRuta', on_delete=models.CASCADE, null=True, blank=True, verbose_name="Hoja de Ruta")
    tipo_guia = models.CharField(max_length=15, choices=TIPO_CHOICES, verbose_name="Tipo de Guía")
    
    fecha_emision = models.DateField(verbose_name="Fecha de Emisión")
    fecha_traslado = models.DateField(verbose_name="Fecha de Traslado")
    peso_total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Peso Total (kg)")
    

    # Campos específicos para cada tipo de guía
    costo_traslado = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Costo de Traslado", null=True, blank=True)  # Solo para Transporte
    fecha_traslado_chofer = models.DateField(verbose_name="Fecha de Traslado por Chofer", null=True, blank=True)  # Solo para Remitente
    observaciones = models.TextField(verbose_name="Observaciones", blank=True, null=True)  # Solo para Remitente
    
    empresa_emisora = models.ForeignKey(
        'Empresa', on_delete=models.CASCADE, related_name="guias_emitidas", verbose_name="Empresa Emisora",null=True,blank=True
    )
    empresa_remitente = models.ForeignKey(
        'Empresa', on_delete=models.CASCADE, related_name="guias_remitidas", verbose_name="Empresa Remitente",null=True,blank=True
    )
    empresa_destinataria = models.ForeignKey(
        'Empresa', on_delete=models.CASCADE, related_name="guias_recibidas", verbose_name="Empresa Destinataria",null=True,blank=True
    )

    # Proceso de firma
    pdf_generado = models.FileField(upload_to='guias/pdf_generado/', verbose_name="PDF Generado", null=True, blank=True) # pdf para tipo guia transportista
    pdf_firmado = models.FileField(upload_to='guias/pdf_firmado/', verbose_name="PDF Firmado", null=True, blank=True) # pdf para tipo guia remitente
    fecha_firma_destinatario = models.DateField(verbose_name="Fecha de Firma Destinatario", null=True, blank=True)

    def __str__(self):
        """
        Representación en cadena del objeto para su fácil identificación.
        """
        hoja_ruta_info = f" - Hoja de Ruta {self.hoja_de_ruta.id}" if self.hoja_de_ruta else ""
        return f"Guía {self.id} - {self.get_tipo_guia_display()} ({self.empresa_emisora} → {self.empresa_destinataria}){hoja_ruta_info}"
    
    def clean(self):
        """
        Validaciones personalizadas para asegurar que solo los campos correspondientes a cada tipo de guía se llenen.
        """
        if self.tipo_guia == self.TRANSPORTE:
            if self.fecha_traslado_chofer or self.observaciones:
                raise ValidationError("Una guía de transporte no debe tener fecha_traslado_chofer ni observaciones.")
        elif self.tipo_guia == self.REMITENTE:
            if self.costo_traslado:
                raise ValidationError("Una guía de remitente no debe tener costo_traslado.")
        super().clean()


class DetalleGuiaRemision(models.Model):
    """
    Modelo que representa el detalle de los productos o bienes transportados en la Guía de Remisión.
    """
    guia = models.ForeignKey(GuiaRemision, on_delete=models.CASCADE, related_name="detalles", verbose_name="Guía de Remisión")
    cantidad = models.PositiveIntegerField(verbose_name="Cantidad")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción Adicional")
    unidad = models.CharField(max_length=20, blank=True, null=True, verbose_name="Unidad")  # Permite valores vacíos

    def __str__(self):
        """
        Representación en cadena del objeto para su fácil identificación.
        """
        return f"Detalle {self.id}, {self.descripcion} ({self.cantidad} {self.unidad})"
    

class Reporte(models.Model):
    guia = models.ForeignKey(GuiaRemision, on_delete=models.CASCADE, related_name="reportes", verbose_name="Guía de Remisión")
    fecha_reporte = models.DateTimeField(auto_now_add=True, verbose_name="Fecha y Hora del Reporte")
    observaciones = models.TextField(verbose_name="Observaciones", blank=True, null=True)
    foto_transportista = models.ImageField(upload_to='reportes/', verbose_name="Foto Guía Transportista", null=True, blank=True)
    foto_remitente = models.ImageField(upload_to='reportes/', verbose_name="Foto Guía Remitente", null=True, blank=True)

    def _str_(self):
        return f"Reporte {self.id} - Guía {self.guia.id} ({self.fecha_reporte})"
    
#ESTEBAN

TIPO_GASTO = [
    ('Efectivo', 'Efectivo'),
]

TIPO_COMBUSTIBLE = [
    ('GLP', 'GLP'),
    ('GNV', 'GNV'),
]

METODO_PAGO = [
    ('Efectivo', 'Efectivo'),
    ('Transferencia', 'Transferencia'),
]

ESTADO = [
    ('Aprobado', 'Apobado'),
    ('En proceso', 'En proceso'),
    ('Rechazado', 'Rechazado'),
]
    
class Ruta(models.Model): 
    # Relación con el chofer
    chofer = models.ForeignKey('Chofer', on_delete=models.SET_NULL, null=True, blank=True)
    # Relación con el camión
    camion = models.ForeignKey('Camion', on_delete=models.SET_NULL, null=True, blank=True)
    partida = models.CharField(max_length=100)
    llegada = models.CharField (max_length=100)
    fecha = models.DateField()
    carga = models.CharField(max_length=200)
    destinatario = models.CharField(max_length=200)
    def _str_(self):
        return f"{self.chofer} - Ruta: {self.partida} - {self.llegada}"

class CombusExtraChofer(models.Model):
    # Relación con el camión
    chofer = models.ForeignKey('Chofer', on_delete=models.SET_NULL, null=True, blank=True)
    placa = models.CharField(max_length=50)
    ruta = models.ForeignKey('Ruta', on_delete=models.SET_NULL, null=True, blank=True)
    montoRecarga = models.CharField(max_length=50)
    fecha = models.DateField()
    tipoGasto = models.CharField(max_length=50, choices=TIPO_GASTO)
    tipoCombustible = models.CharField(max_length=50, choices=TIPO_COMBUSTIBLE)
    metodoPago = models.CharField(max_length=50, choices=METODO_PAGO)
    estado = models.CharField(max_length=50, choices=ESTADO, default='En proceso')

class GastoAdicional(models.Model):
    idGasto = models.CharField(max_length=4)
    chofer = models.ForeignKey('Chofer', on_delete=models.SET_NULL, null=True, blank=True)
    placa = models.CharField(max_length=50)
    ruta = models.ForeignKey('Ruta', on_delete=models.SET_NULL, null=True, blank=True)
    montoRecarga = models.CharField(max_length=50)
    tipoGasto = models.CharField(max_length=50, choices=TIPO_GASTO)

class FacturaCombustible(models.Model):
    monto = models.CharField(max_length=30)
    placa = models.CharField(max_length=50)
    ruc = models.CharField(max_length=16)
    fecha = models.DateField()
    ruta = models.ForeignKey('Ruta', on_delete=models.SET_NULL, null=True, blank=True)
    chofer = models.ForeignKey('Chofer', on_delete=models.SET_NULL, null=True, blank=True)
    factura = models.ImageField(upload_to = 'factura/')

class RechazoSoliCombus(models.Model):
    solicitud = models.OneToOneField(CombusExtraChofer, on_delete=models.CASCADE)
    motivo = models.TextField()
    fecha_rechazo = models.DateTimeField(auto_now_add=True)

    def str(self):
        return f"Rechazo de {self.solicitud} - Motivo: {self.motivo[:30]}"
    
class TransferenciaPagada(models.Model):
    chofer = models.ForeignKey('Chofer', on_delete=models.SET_NULL, null=True, blank=True)
    descripcion = models.TextField(null=True, blank=True)
    fecha = models.DateField()
    monto = models.CharField(max_length=30)
    estado = models.CharField(max_length=50, choices=ESTADO, default='En proceso')
    factura = models.ImageField(upload_to = 'facturaTransferencia/')


class Applicant(models.Model):
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    numero_celular = models.CharField(max_length=9, unique=True)
    correo = models.EmailField(unique=True)  # Nuevo campo de correo electrónico
    dni_frontal = models.ImageField(upload_to='dni/', null=True, blank=True)  # Nuevo campo para DNI frontal
    dni_posterior = models.ImageField(upload_to='dni/', null=True, blank=True)  # Nuevo campo para DNI posterior
    tipo_licencia = models.CharField(max_length=2, choices=[('A4', 'A4')])
    tipo_licencia_formato = models.CharField(
        max_length=11,
        choices=[('fisica', 'Física'), ('electronica', 'Electrónica')]
    )
    licencia_frontal = models.ImageField(upload_to='licencias/', null=True, blank=True)
    licencia_posterior = models.ImageField(upload_to='licencias/', null=True, blank=True)
    licencia_electronica = models.ImageField(upload_to='licencias/', null=True, blank=True)
    experiencia = models.CharField(
        max_length=2,
        choices=[('si', 'Sí'), ('no', 'No')]
    )
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombres} {self.apellidos} - {self.tipo_licencia}"
    
class Postulante(models.Model):
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    numero_celular = models.CharField(max_length=9, unique=True)
    correo = models.EmailField(unique=True)  # Nuevo campo de correo electrónico
    dni_frontal = models.ImageField(upload_to='dni/', null=True, blank=True)  # Nuevo campo para DNI frontal
    dni_posterior = models.ImageField(upload_to='dni/', null=True, blank=True)  # Nuevo campo para DNI posterior
    tipo_licencia = models.CharField(max_length=2, choices=[('A4', 'A4')])
    tipo_licencia_formato = models.CharField(
        max_length=11,
        choices=[('fisica', 'Física'), ('electronica', 'Electrónica')]
    )
    licencia_frontal = models.ImageField(upload_to='licencias/', null=True, blank=True)
    licencia_posterior = models.ImageField(upload_to='licencias/', null=True, blank=True)
    licencia_electronica = models.ImageField(upload_to='licencias/', null=True, blank=True)
    estado = models.CharField(
        max_length=30,
        choices=[('primera_pendiente', 'Primera Etapa - Pendiente'), 
                 ('primera_aprobada', 'Primera Etapa - Aprobada'), 
                 ('primera_rechazada', 'Primera Etapa - Rechazada'), 
                 ('segunda_pendiente', 'Segunda Etapa - Pendiente'), 
                 ('segunda_aprobada', 'Segunda Etapa - Aprobada'), 
                 ('segunda_rechazada', 'Segunda Etapa - Rechazada'), 
                 ('tercera_pendiente', 'Tercera Etapa - Pendiente'), 
                 ('tercera_aprobada', 'Tercera Etapa - Aprobada'), 
                 ('tercera_rechazada', 'Tercera Etapa - Rechazada'),
                 ('cuarta_pendiente', 'Cuarta Etapa - Pendiente'), 
                 ('cuarta_aprobada', 'Cuarta Etapa - Aprobada'), 
                 ('cuarta_rechazada', 'Cuarta Etapa - Rechazada')],
        default='primera_pendiente'
    )
    experiencia = models.CharField(
        max_length=2,
        choices=[('si', 'Sí'), ('no', 'No')]
    )
    referencias_trabajos = models.FileField(upload_to='documentos/', null=True, blank=True)
    record_conduccion = models.FileField(upload_to='documentos/', null=True, blank=True)
    historial_papeletas = models.ImageField(upload_to='documentos/', null=True, blank=True)
    antecedentes_penales = models.FileField(upload_to='documentos/', null=True, blank=True)
    clinica = models.CharField(
        max_length=50,
        choices=[('montefiori', 'Clínica Montefiori'), ('suiza_lab', 'Clínica Suiza Lab')],
        null=True,
        blank=True
    )
    examenes_requeridos = models.ManyToManyField('ExamenMedico', blank=True)
    resultado_medicina_general = models.FileField(
        upload_to='resultados_medicos/',
        null=True,
        blank=True,
        help_text='Resultado del examen de medicina general'
    )
    resultado_toxicologico = models.FileField(
        upload_to='resultados_medicos/',
        null=True,
        blank=True,
        help_text='Resultado del examen toxicológico'
    )
    resultado_oftalmologia = models.FileField(
        upload_to='resultados_medicos/',
        null=True,
        blank=True,
        help_text='Resultado del examen de oftalmología'
    )
    resultado_otorrinolaringologia = models.FileField(
        upload_to='resultados_medicos/',
        null=True,
        blank=True,
        help_text='Resultado del examen de otorrinolaringología'
    )
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombres} {self.apellidos} - {self.tipo_licencia}"
    
class ExamenMedico(models.Model):
    TIPO_EXAMEN_CHOICES = [
        ('medicina_general', 'Medicina General'),
        ('toxicologico', 'Toxicológico'),
        ('oftalmologia', 'Oftalmología'),
        ('otorrinolaringologia', 'Otorrinolaringología'),
    ]
    
    tipo = models.CharField(max_length=50, choices=TIPO_EXAMEN_CHOICES)

    def __str__(self):
        return self.get_tipo_display()