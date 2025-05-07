from .models import SolicitudServicio,Mantenimiento, Factura,User,Chofer,Camion,MotivoMantenimiento,Mantenimiento_Detalle,Mecanico
from .models import Empresa,ContratoAlianza,SolicitudAlianza
from django import forms  
from ftplib import MAXLINE  
from django import forms
from django.contrib.auth.models import Group
from django.contrib.auth.forms import UserCreationForm


class CreateNewSolicitud(forms.Form):
    
    nombres = forms.CharField(label = "Nombres ",max_length=100)
    apellidos = forms.CharField(label = "Apellidos",max_length=100)
    telefono = forms.CharField(label = "Telefono",max_length=15)
    correo = forms.EmailField(label = "Correo Gmail",max_length=100)
    ruc_empresa = forms.CharField(label="RUC Empresa",max_length=11)
    nombre_empresa = forms.CharField(label = "Nombre Empresa",max_length=100)
    mensaje = forms.CharField(label = "Mensaje",widget=forms.Textarea)

from .models import Reporte

class ReporteForm(forms.ModelForm):
    class Meta:
        model = Reporte
        fields = ['observaciones', 'foto_transportista', 'foto_remitente']
        widgets = {
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'foto_transportista': forms.FileInput(attrs={'class': 'form-control'}),
            'foto_remitente': forms.FileInput(attrs={'class': 'form-control'}),
        }       

class LoginForm (forms.Form):
    username = forms.CharField(
        widget= forms.TextInput(
            attrs={
                "class" :"form-control"
            }
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control"
            }
        )
    )

class SignUpForm(UserCreationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Nombre de usuario"}),
        required=True
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "Correo electrónico"}),
        required=True
    )
    dni = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "DNI"}),
        max_length=8,
        required=True
    )
    phone = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Teléfono"}),
        max_length=15,
        required=True
    )
    empresa = forms.ModelChoiceField(
        queryset=Empresa.objects.all(),
        widget=forms.Select(attrs={"class": "form-control"}),
        required=True,
        label="Empresa"
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Contraseña"}),
        required=True
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Confirmar contraseña"}),
        required=True
    )
    roles = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),  # Obtiene todos los grupos disponibles
        widget=forms.CheckboxSelectMultiple,  # Permite seleccionar múltiples roles
        required=True,  # Evita que se registre sin rol asignado
        label="Selecciona los roles"
    )

    class Meta:
        model = User
        fields = ("username", "email", "dni", "phone", "empresa", "password1", "password2", "roles")

    def save(self, commit=True):
        user = super().save(commit=False)  # Guarda el usuario sin confirmarlo aún
        user.empresa = self.cleaned_data["empresa"]  # Asigna la empresa seleccionada
        if commit:
            user.save()  # Guarda el usuario en la base de datos
            user.groups.set(self.cleaned_data["roles"])  # Asigna los roles seleccionados
        return user
        
class AddChofer(forms.ModelForm):
    class Meta:
        model = Chofer
        fields = [
            'usuario',  # Agregamos el campo usuario
            'nombres',
            'apellidos',
            'fecha_nacimiento',
            'domicilio',
            'telefono',
            'tipo_licencia',
            'numero_licencia',
            'fecha_emision',
            'fecha_vencimiento',
            'estado_salud',
            'camion',
        ]
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
            'fecha_emision': forms.DateInput(attrs={'type': 'date'}),
            'fecha_vencimiento': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            grupo_chofer = Group.objects.get(name="chofer")
            self.fields['usuario'].queryset = User.objects.filter(groups=grupo_chofer)
        except Group.DoesNotExist:
            self.fields['usuario'].queryset = User.objects.none()  # Si no existe el grupo, no muestra opciones

#FORMULARIO PARA EMPRESA
class EmpresaForm(forms.ModelForm):
    class Meta:
        model = Empresa
        fields = ['logo_empresa', 'nombre_empresa', 'ruc_empresa']  # Campos específicos

    # Validación personalizada para el RUC (11 dígitos numéricos)
    def clean_ruc_empresa(self):
        ruc = self.cleaned_data.get('ruc_empresa')
        if not ruc.isdigit() or len(ruc) != 11:
            raise forms.ValidationError("El RUC debe contener exactamente 11 dígitos numéricos.")
        return ruc
#FORMULARIO PARA CAMION
class CamionForm(forms.ModelForm):
    class Meta:
        model = Camion
        fields = [
            'foto_camion',
            'placa',
            'marca',
            'modelo',
            'year_fabricacion',
            'capacidad_carga',
            'tipo_camion',
            'estado_operativo',
            'fecha_adquisicion',
            'propietario_vehiculo',
            'rendimiento_combustible',
            'empresa_propietaria',
            'notas',
        ]
        widgets = {
            'foto_camion': forms.ClearableFileInput(attrs={'accept': 'image/*'}),
            'fecha_adquisicion': forms.DateInput(attrs={'type': 'date'}),
            'notas': forms.Textarea(attrs={'rows': 4}),
        }
        labels = {
            'foto_camion': 'Foto del camión',
            'placa': 'Placa del camión',
            'marca': 'Marca',
            'modelo': 'Modelo',
            'year_fabricacion': 'Año de fabricación',
            'capacidad_carga': 'Capacidad de carga (toneladas)',
            'tipo_camion': 'Tipo de camión',
            'estado_operativo': 'Estado operativo',
            'fecha_adquisicion': 'Fecha de adquisición',
            'propietario_vehiculo': 'Propietario del vehículo',
            'rendimiento_combustible': 'Rendimiento de combustible (km/l)',
            'empresa_propietaria': 'Empresa propietaria',
            'notas': 'Notas adicionales',
        }

#FORMULARIO MOTIVO_MANTENIMIENTO
class MotivoMantenimientoForm(forms.ModelForm):
    class Meta:
        model = MotivoMantenimiento
        fields = ['camion', 'motivo']
        labels = {
            'camion': 'Camión',
            'motivo': 'Motivo de mantenimiento',
        }
        widgets = {
            'motivo': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtra los camiones con estado operativo "Activo"
        self.fields['camion'].queryset = Camion.objects.filter(estado_operativo="Activo")

#FORMULARIO MANTENIMIENTO
class MantenimientoForm(forms.ModelForm):
    class Meta:
        model = Mantenimiento
        fields = [
            'motivo',
            'camion',
            'taller',
            'fecha_mantenimiento',
            'tipo_mantenimiento',
            'estado_mantenimiento',
        ]
        widgets = {
            'fecha_mantenimiento': forms.DateInput(attrs={'type': 'date'}),
            'motivo': forms.TextInput(attrs={'readonly': 'readonly'}),
            'camion': forms.TextInput(attrs={'readonly': 'readonly'}),
        }
        labels = {
            'motivo': 'Motivo de mantenimiento',
            'camion':'Camion',
            'taller': 'Taller de mantenimiento',
            'fecha_mantenimiento': 'Fecha de mantenimiento',
            'tipo_mantenimiento': 'Tipo de mantenimiento',
            'estado_mantenimiento': 'Estado del mantenimiento',
        }

#FORMULARIO MECANICO

class MecanicoForm(forms.ModelForm):
    class Meta:
        model = Mecanico
        fields = ['nombres', 'apellidos', 'telefono', 'foto']
        widgets = {
            'foto': forms.ClearableFileInput(attrs={'accept': 'image/*'}),  # Solo imágenes
        }
        labels = {
            'nombres': 'Nombres del mecánico',
            'apellidos': 'Apellidos del mecánico',
            'telefono': 'Teléfono',
            'foto': 'Foto del mecánico',
        }

#FORMULARIO MANTENIMIENTO_DETALLE
class MantenimientoDetalleForm(forms.ModelForm):
    class Meta:
        model = Mantenimiento_Detalle
        exclude = ['mantenimiento']  # Excluir el campo de mantenimiento
        widgets = {
            'descripcion_servicio_repuesto': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'descripcion_servicio_repuesto': 'Descripción del servicio/repuesto',
            'cantidad': 'Cantidad',
            'costo_unitario': 'Costo unitario',
            'costo_total': 'Costo total',
        }

#FORMULARIO FACTURA 
class FacturaForm(forms.ModelForm):
    class Meta:
        model = Factura
        fields = [
            'numero_factura',
            'fecha_emision',
            'mantenimiento',
            'taller',
            'monto_total',
            'metodo_pago',
            'estado_pago',
        ]
        widgets = {
            'fecha_emision': forms.DateInput(attrs={'type': 'date'}),
        }
        labels = {
            'numero_factura': 'Número de factura',
            'fecha_emision': 'Fecha de emisión',
            'mantenimiento': 'Mantenimiento relacionado',
            'taller': 'Taller',
            'monto_total': 'Monto total',
            'metodo_pago': 'Método de pago',
            'estado_pago': 'Estado de pago',
        }

class ContratoAlianzaForm(forms.ModelForm):
    solicitud = forms.ModelChoiceField(
        queryset=SolicitudAlianza.objects.filter(estado='aprobada'),
        label="Solicitud (solo aprobadas)",
        empty_label="Seleccione una solicitud"
    )
    empresa = forms.ModelChoiceField(
        queryset=Empresa.objects.all(),
        label="Empresa"
    )
    documento = forms.FileField(label="Documento del Contrato")

    class Meta:
        model = ContratoAlianza
        fields = ['solicitud', 'empresa', 'documento']

    def save(self, commit=True):
        contrato = super().save(commit=False)
        contrato.estado = 'pendiente'  # Asigna estado 'pendiente' automáticamente
        if commit:
            contrato.save()
        return contrato    


from .models import HojadeRuta, Ubicacion
import requests 

class HojadeRutaForm(forms.ModelForm):
    direccion_ida = forms.CharField(max_length=255, required=True, label="Dirección de Ida")
    direccion_vuelta = forms.CharField(max_length=255, required=True, label="Dirección de Vuelta")

    class Meta:
        model = HojadeRuta
        fields = ['chofer', 'camion', 'estado', 'direccion_ida', 'direccion_vuelta']
        labels = {
            'chofer': 'Chofer',
            'camion': 'Camión',
            'estado': 'Estado',
        }

    def obtener_coordenadas(self, direccion):
        """
        Obtiene las coordenadas (latitud y longitud) de una dirección utilizando la API de OpenStreetMap.
        Retorna valores numéricos. En caso de no encontrar resultados, retorna 0.0, 0.0 y 'Desconocida' como provincia.
        """
        url = 'https://nominatim.openstreetmap.org/search'
        params = {'q': direccion, 'format': 'json', 'limit': 1, 'addressdetails': 1}
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            if data:
                try:
                    lat = float(data[0]['lat'])
                    lon = float(data[0]['lon'])
                except (ValueError, TypeError):
                    lat, lon = 0.0, 0.0
                address_details = data[0].get('address', {})
                provincia = address_details.get('state', 'Desconocida')
                return lat, lon, provincia
        # En caso de fallo, se retornan valores por defecto:
        return 0.0, 0.0, 'Desconocida'

    def save(self, commit=True):
        """
        Sobrescribe el método save para almacenar las coordenadas basadas en la dirección.
        Se asegura de que se asignen valores numéricos a latitud y longitud.
        """
        hoja = super().save(commit=False)

        # Obtener o crear ubicación de partida
        lat_ida, lon_ida, provincia_ida = self.obtener_coordenadas(self.cleaned_data['direccion_ida'])
        partida = Ubicacion.objects.filter(direccion=self.cleaned_data['direccion_ida']).first()
        if not partida:
            partida = Ubicacion.objects.create(
                direccion=self.cleaned_data['direccion_ida'],
                latitud=lat_ida,
                longitud=lon_ida,
                provincia=provincia_ida
            )

        # Obtener o crear ubicación de llegada
        lat_vuelta, lon_vuelta, provincia_vuelta = self.obtener_coordenadas(self.cleaned_data['direccion_vuelta'])
        llegada = Ubicacion.objects.filter(direccion=self.cleaned_data['direccion_vuelta']).first()
        if not llegada:
            llegada = Ubicacion.objects.create(
                direccion=self.cleaned_data['direccion_vuelta'],
                latitud=lat_vuelta,
                longitud=lon_vuelta,
                provincia=provincia_vuelta
            )

        hoja.partida_ubicacion = partida
        hoja.llegada_ubicacion = llegada

        if commit:
            hoja.save()
        return hoja
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hacer los campos de solo lectura
        self.fields['chofer'].widget.attrs['readonly'] = True
        self.fields['camion'].widget.attrs['readonly'] = True
        self.fields['estado'].widget.attrs['readonly'] = True

from django import forms
from django.forms import inlineformset_factory
from .models import GuiaRemision, DetalleGuiaRemision

class GuiaRemisionForm(forms.ModelForm):
    class Meta:
        model = GuiaRemision
        fields = [
            'fecha_emision', 'fecha_traslado',
            'peso_total', 'costo_traslado', 'fecha_traslado_chofer', 'observaciones',
            'empresa_emisora', 'empresa_remitente', 'empresa_destinataria',
        ]
        widgets = {
            'fecha_emision': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'fecha_traslado': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'fecha_traslado_chofer': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class DetalleGuiaRemisionForm(forms.ModelForm):
    class Meta:
        model = DetalleGuiaRemision
        fields = ['descripcion', 'cantidad', 'unidad']
        widgets = {
            'descripcion': forms.TextInput(attrs={'class': 'form-control'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control'}),
            'unidad': forms.TextInput(attrs={'class': 'form-control'}),
        }

DetalleFormSet = inlineformset_factory(
    GuiaRemision, DetalleGuiaRemision,
    form=DetalleGuiaRemisionForm,
    extra=5,
    can_delete=True
)

#ESTEBAN

from .models import Ruta,CombusExtraChofer,GastoAdicional,FacturaCombustible,TransferenciaPagada

class RutaForm(forms.ModelForm):
    class Meta:
        model = Ruta
        fields = [
            'chofer',
            'camion',
            'partida', 
            'llegada', 
            'fecha', 
            'carga', 
            'destinatario']
        widgets = {
            'partida': forms.Textarea(attrs={'rows': 3}),
            'llegada': forms.Textarea(attrs={'rows': 3}),
            'fecha': forms.DateInput(attrs={'type': 'date'}),
        }
        labels = {
            'chofer': 'Chofer',
            'camion': 'Camion',
            'partida': 'Punto de partida',
            'llegada': 'Punto de llegada',
            'fecha': 'Fecha',
            'carga': 'Carga',
            'destinatario': 'Destinatario',
        }

class CombusExtraChoferForm(forms.ModelForm):
    class Meta:
        model = CombusExtraChofer
        fields = ['chofer', 
                  'placa', 
                  'ruta', 
                  'montoRecarga', 
                  'fecha',
                  'tipoGasto', 
                  'tipoCombustible', 
                  'metodoPago',
                  'estado']
        widgets = {
            'placa': forms.TextInput(attrs={'placeholder': 'Ingrese la placa'}),
            'montoRecarga': forms.TextInput(attrs={'placeholder': 'Ingrese el monto'}),
            'fecha': forms.DateInput(attrs={'type': 'date'}),
            'tipoGasto': forms.Select(),
            'tipoCombustible': forms.Select(),
            'metodoPago': forms.Select(),
            'estado': forms.Select(),
        }
        labels = {
            'chofer': 'Chofer',
            'placa': 'Placa del vehículo',
            'ruta': 'Ruta',
            'montoRecarga': 'Monto de recarga',
            'fecha': 'Fecha',
            'tipoGasto': 'Tipo de gasto',
            'tipoCombustible': 'Tipo de combustible',
            'metodoPago': 'Método de pago',
            'estado': 'Estado',
        }

class GastoAdicionalForm(forms.ModelForm):
    class Meta:
        model = GastoAdicional
        fields = ['idGasto', 
                  'chofer', 
                  'placa', 
                  'ruta', 
                  'montoRecarga', 
                  'tipoGasto']
        widgets = {
            'idGasto': forms.TextInput(attrs={'placeholder': 'Ingrese el ID del gasto'}),
            'placa': forms.TextInput(attrs={'placeholder': 'Ingrese la placa'}),
            'montoRecarga': forms.TextInput(attrs={'placeholder': 'Ingrese el monto'}),
            'tipoGasto': forms.Select(),
        }
        labels = {
            'idGasto': 'ID del Gasto',
            'chofer': 'Chofer',
            'placa': 'Placa del vehículo',
            'ruta': 'Ruta',
            'montoRecarga': 'Monto de recarga',
            'tipoGasto': 'Tipo de gasto',

        }

class FacturaCombustibleForm(forms.ModelForm):
    class Meta:
        model = FacturaCombustible
        fields = ['monto',
                  'placa',
                  'ruc',
                  'fecha',
                  'ruta',
                  'chofer',
                  'factura']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
            'factura': forms.ClearableFileInput(attrs={'accept': 'image/*'}),
        }
        labels = {
            'monto': 'Monto',
            'placa': 'Placa',
            'ruc': 'Ruc',
            'fecha': 'Fecha',
            'ruta': 'Ruta',
            'chofer': 'Chofer',
            'factura': 'Factura',
        }

class TransferenciaPagadaForm(forms.ModelForm):
    class Meta:
        model = TransferenciaPagada
        fields = ['chofer', 
                  'descripcion', 
                  'fecha', 
                  'monto', 
                  'estado',
                  'factura']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 4}),
            'fecha': forms.DateInput(attrs={'type': 'date'}),
            'monto': forms.TextInput(attrs={'placeholder': 'Ingrese el monto'}),
            'estado': forms.Select(),
            'factura': forms.ClearableFileInput(attrs={'accept': 'image/*'}),
        }
        labels = {
            'chofer': 'Chofer',
            'descripcion': 'Descripción',
            'fecha': 'Fecha',
            'monto': 'Monto',
            'estado': 'Estado',
            'factura': 'Factura',
        }

from django import forms
from .models import Applicant, ExamenMedico, Postulante

class ApplicantForm(forms.ModelForm):
    class Meta:
        model = Applicant
        fields = [
            'nombres', 'apellidos', 'numero_celular', 'correo', 'dni_frontal', 'dni_posterior', 'tipo_licencia',
            'tipo_licencia_formato', 'licencia_frontal', 'licencia_posterior',
            'licencia_electronica', 'experiencia'
        ]

class PostulanteForm(forms.ModelForm):
    class Meta:
        model = Postulante
        fields = [
            'nombres', 'apellidos', 'numero_celular', 'correo', 'dni_frontal', 'dni_posterior', 'tipo_licencia',
            'tipo_licencia_formato', 'licencia_frontal', 'licencia_posterior',
            'licencia_electronica', 'experiencia',
        ]
        widgets = {
            'dni_frontal': forms.ClearableFileInput(attrs={'accept': 'image/*'}),
            'dni_posterior': forms.ClearableFileInput(attrs={'accept': 'image/*'}),
            'licencia_frontal': forms.ClearableFileInput(attrs={'accept': 'image/*'}),
            'licencia_posterior': forms.ClearableFileInput(attrs={'accept': 'image/*'}),
            'licencia_electronica': forms.ClearableFileInput(attrs={'accept': 'image/*'}),
        }
        labels = {
            'nombres': 'Nombres',
            'apellidos': 'Apellidos',
            'numero_celular': 'Celular',
            'correo': 'Correo',
            'dni_frontal': 'DNI Frontal',
            'dni_posterior': 'DNI Posterior',
            'tipo_licencia': 'Tipo de Licencia',
            'tipo_licencia_formato': 'Formato de licencia',
            'licencia_frontal': 'Licencia Frontal',
            'licencia_posterior': 'Licencia Posterior',
            'licencia_electronica': 'Licencia Electrónica',
            'estado': 'Estado',
            'experiencia': 'Experiencia',
        }

class PostulanteDocumentosForm(forms.ModelForm):
    class Meta:
        model = Postulante
        fields = [
            'referencias_trabajos', 'record_conduccion', 'historial_papeletas', 'antecedentes_penales',
        ]

        widgets = {
            'referencias_trabajos': forms.ClearableFileInput(attrs={'accept': '.pdf,.doc,.docx'}),
            'record_conduccion': forms.ClearableFileInput(attrs={'accept': '.pdf,.doc,.docx'}),
            'historial_papeletas': forms.ClearableFileInput(attrs={'accept': 'image/*'}),
            'antecedentes_penales': forms.ClearableFileInput(attrs={'accept': '.pdf,.doc,.docx'}),
        }

        labels = {
            'referencias_trabajos': 'Referencias de Trabajos Anteriores',
            'record_conduccion': 'Récord de Conducción (MTC)',
            'historial_papeletas': 'Historial de Papeletas',
            'antecedentes_penales': 'Certificado de Antecedentes Penales',
        }

class PostulanteClinicaForm(forms.ModelForm):
    class Meta:
        model = Postulante
        fields = ['clinica']

        widgets = {
            'clinica': forms.Select(attrs={'class': 'form-control'}),
        }

        labels = {
            'clinica': 'Clínica',
        }

class ExamenesMedicosForm(forms.ModelForm):
    examenes_requeridos = forms.MultipleChoiceField(
        choices=ExamenMedico.TIPO_EXAMEN_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Exámenes Médicos Requeridos'
    )

    class Meta:
        model = Postulante
        fields = ['examenes_requeridos']

class ResultadosMedicosForm(forms.ModelForm):
    class Meta:
        model = Postulante
        fields = [
            'resultado_medicina_general', 'resultado_toxicologico', 'resultado_oftalmologia', 'resultado_otorrinolaringologia',
        ]

        widgets = {
            'resultado_medicina_general': forms.ClearableFileInput(attrs={'accept': '.pdf,.doc,.docx'}),
            'resultado_toxicologico': forms.ClearableFileInput(attrs={'accept': '.pdf,.doc,.docx'}),
            'resultado_oftalmologia': forms.ClearableFileInput(attrs={'accept': '.pdf,.doc,.docx'}),
            'resultado_otorrinolaringologia': forms.ClearableFileInput(attrs={'accept': '.pdf,.doc,.docx'}),
        }

        labels = {
            'resultado_medicina_general': 'Resultado del Examen de Medicina General',
            'resultado_toxicologico': 'Resultado del examen toxicológico',
            'resultado_oftalmologia': 'Resultado del examen de oftalmología',
            'resultado_otorrinolaringologia': 'Resultado del examen de otorrinolaringología',
        }