from django.shortcuts import render,redirect
from django.http import HttpResponse , JsonResponse,HttpResponseNotAllowed
from django.shortcuts import get_object_or_404,redirect
from .models import SolicitudServicio,User,Camion,Chofer,Mantenimiento,Factura,MotivoMantenimiento,Mantenimiento_Detalle,Mecanico,Empresa
from .forms import AddChofer,CamionForm,CreateNewSolicitud,FacturaForm,MecanicoForm,EmpresaForm
from .forms import LoginForm,SignUpForm,MantenimientoForm,MotivoMantenimientoForm,MantenimientoDetalleForm
from django.contrib.auth import authenticate,login
from django.views.generic import ListView
import json
from django.db.models import Subquery, OuterRef

from django.contrib.auth.decorators import login_required

@login_required
def profile_view(request):
    """ Vista para el perfil del usuario """
    return render(request, "profile.html", {"user": request.user})

@login_required
def settings_view(request):
    """ Vista para la configuración del usuario """
    return render(request, "settings.html", {"user": request.user})

#CONTROLADORES PARA EMPRESA-GERENTE
from django.core.exceptions import PermissionDenied
def role_required(role_name):
    """ Decorador para permitir acceso solo a usuarios con un rol específico """
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated or not request.user.has_role(role_name):
                raise PermissionDenied
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

@login_required
@role_required('gerente')
def EmpresaController(request, action=None, empresa_id=None):
    if request.method == 'POST':
        # Crear un nuevo camión
        if action == 'crear':
            form = EmpresaForm(request.POST,request.FILES)
            if form.is_valid():
                form.save()
                return redirect('empresa')

        # Eliminar un camión existente
        elif action == 'eliminar' and empresa_id:
            empresa = get_object_or_404(Empresa, id=empresa_id)
            empresa.delete()
            return redirect('empresa')

        else:
            return HttpResponseNotAllowed(['POST'])

    # Mostrar el formulario y lista de camiones
    if request.method == 'GET':
        empresas = Empresa.objects.all()
        form = EmpresaForm()

        # Si es para editar, carga el camión en el formulario
        if action == 'editar' and empresa_id:
            empresa = get_object_or_404(Empresa, id=empresa_id)
            form = EmpresaForm(instance=empresa)
            return render(request, 'GERENTE/Empresa/GestionEmpresas.html', {
                'empresas': empresas,
                'form': form,
                'action': action,
                'empresa_id': empresa_id,
            })
        
        elif action == 'detalles' and empresa_id:
            empresa_instance = get_object_or_404(Empresa, id=empresa_id)
            return render(request, 'GERENTE/Empresa/detalles_empresa.html', {
                'empresa': empresa_instance,  # Corregido el diccionario de contexto
            })
        
        return render(request, 'GERENTE/Empresa/GestionEmpresas.html', {
            'empresas': empresas,
            'form': form,
            'action': action,
            'empresa_id': empresa_id,
        })
    
    return HttpResponseNotAllowed(['GET', 'POST'])
@login_required
@role_required('gerente')
def modificarEmpresa(request, id):
    # Obtener el objeto Camion
    empresa = get_object_or_404(Empresa, id=id)

    # Crear el formulario con la instancia del camión
    form = EmpresaForm(instance=empresa)

    # Si la solicitud es POST, procesamos el formulario
    if request.method == 'POST':
        form = EmpresaForm(data=request.POST, instance=empresa, files=request.FILES)
        if form.is_valid():
            form.save()
            return redirect('empresa')  # Redirigir a la página de listado o éxito

    # En cualquier otro caso (GET o errores en el formulario), renderizamos el formulario
    data = {
        'form': form
    }
    return render(request, 'GERENTE/Empresa/modificarEmpresa.html', data)

#CONTROLADORES PARA SOLCIITUDES EXTERNAS-GERENTE
@login_required
@role_required('gerente')
def solicitudServicio(request):
    solicitudServicio = SolicitudServicio.objects.all()
    return render(request,'GERENTE/SolicitudServicio.html',
                  {
                      
                      'solicitudServicio':solicitudServicio
                  })

def create_solicitud(request):
    if request.method == 'GET': 
        return render(request,'HomePage.html',{
            'form':CreateNewSolicitud()
        })
    else:
        SolicitudServicio.objects.create(
        nombres = request.POST['nombres'],
        apellidos = request.POST['apellidos'],
        telefono = request.POST['telefono'],
        correo = request.POST['correo'],
        ruc_empresa = request.POST['ruc_empresa'],
        nombre_empresa = request.POST['nombre_empresa'],
        mensaje = request.POST['mensaje']
        
        )
        return redirect('CreateSolicitudServicio')
    
#CONTROLADOR PARA REGISTRAR USUARIOS - GERENTE
@login_required
@role_required('gerente')
def register(request):
    msg = None
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            msg = 'user created'
            return redirect('listar_usuarios')
        else:
            msg = 'form is not valid'
    else:
        form = SignUpForm()
    return render(request,'GERENTE/register.html', {'form': form, 'msg': msg})

#CONTROLADOR PARA LOGEARSE
def login_view(request):
    form = LoginForm(request.POST or None)
    msg = None

    if request.method == 'POST':
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)

            if user:
                login(request, user)

                # Obtener el rol del usuario
                user_groups = user.groups.all()
                if user_groups.exists():
                    role = user_groups.first().name  # Toma el primer grupo asignado
                    return redirect(reverse("role_page", args=[role.lower()]))  # Redirigir a la vista según el rol

                # Si no tiene rol, redirigir a una vista por defecto
                return redirect("CreateSolicitudServicio")  

            else:
                msg = "Credenciales inválidas"
        else:
            msg = "Error al validar el formulario"

    return render(request, "login.html", {"form": form, "msg": msg})  # Siempre retorna algo

# INTERFACES PARA LOS TIPOS DE USUARIO DEL SISTEMA
from django.contrib.auth.decorators import login_required

ROLE_TEMPLATES = {
    "admin": "admin.html",
    "representante": "REPRESENTANTE/representante.html",
    "jefedespacho": "JEFE_DESPACHO/jefedespacho.html",
    "mantenimiento": "S_MANTENIMIENTO/mantenimiento.html",
    "contador": "CONTADOR/contador.html",
    "agencia": "AGENCIA/agencia.html",
    "chofer": "CHOFER/chofer.html",
    "gerente": "GERENTE/gerente.html",
    "asistente": "ASISTENTE/asistente.html",
    "coordinador":"coordinador.html",
    "jefeseguridad":"jefeseguridad.html"
    
    
}

#CONTROLADOR PARA MANEJAR LAS VISTAS DE LOS ROLES
def role_view(request, role):
    """ Vista genérica para cargar páginas según el rol del usuario """
    template = ROLE_TEMPLATES.get(role)
    if template:
        return render(request, template)
    else:
        return render(request, "404.html", status=404)  # Muestra error si no hay plantilla
    
#CONTROLADORES PARA EL CAMION
@login_required
@role_required('asistente')
def CamionController(request, action=None, camion_id=None):
    if request.method == 'POST':
        # Crear un nuevo camión
        if action == 'crear':
            form = CamionForm(request.POST,request.FILES)
            if form.is_valid():
                form.save()
                return redirect('camion')

        # Eliminar un camión existente
        elif action == 'eliminar' and camion_id:
            camion = get_object_or_404(Camion, id=camion_id)
            camion.delete()
            return redirect('camion')

        else:
            return HttpResponseNotAllowed(['POST'])

    # Mostrar el formulario y lista de camiones
    if request.method == 'GET':
        camiones = Camion.objects.all()
        form = CamionForm()

        # Si es para editar, carga el camión en el formulario
        if action == 'editar' and camion_id:
            camion = get_object_or_404(Camion, id=camion_id)
            form = CamionForm(instance=camion)
            return render(request, 'ASISTENTE/Camion/list_and_create_camiones.html', {
                'camiones': camiones,
                'form': form,
                'action': action,
                'camion_id': camion_id,
            })
        
        elif action == 'detalles' and camion_id:
            camion_instance = get_object_or_404(Camion, id=camion_id)
            return render(request, 'ASISTENTE/Camion/detalles_camion.html', {
                'camion': camion_instance,  # Corregido el diccionario de contexto
            })
        
        return render(request, 'ASISTENTE/Camion/list_and_create_camiones.html', {
            'camiones': camiones,
            'form': form,
            'action': action,
            'camion_id': camion_id,
        })
    
    return HttpResponseNotAllowed(['GET', 'POST'])
@login_required
@role_required('asistente')
def modificarCamion(request, id):
    # Obtener el objeto Camion
    camion = get_object_or_404(Camion, id=id)

    # Crear el formulario con la instancia del camión
    form = CamionForm(instance=camion)

    # Si la solicitud es POST, procesamos el formulario
    if request.method == 'POST':
        form = CamionForm(data=request.POST, instance=camion, files=request.FILES)
        if form.is_valid():
            form.save()
            return redirect('camion')  # Redirigir a la página de listado o éxito

    # En cualquier otro caso (GET o errores en el formulario), renderizamos el formulario
    data = {
        'form': form
    }
    return render(request, 'ASISTENTE/Camion/modificarCamion.html', data)


#CONTROLADOR PARA MOSTRAR LOS CAMIONES QUE REQUIEREN MANTENIMIENTO -S_MANTENIMIENTO
@login_required
@role_required('mantenimiento')
def camiones_mantenimiento(request):
    # Subquery para obtener el último motivo de mantenimiento
    ultimo_motivo = MotivoMantenimiento.objects.filter(
        camion=OuterRef('pk')
    ).order_by('-fecha_registro').values('motivo')[:1]

    # Obtener camiones con estado "Requiere Mantenimiento" y su último motivo
    camiones = Camion.objects.filter(
        estado_operativo="Requiere Mantenimiento"
    ).annotate(
        ultimo_motivo=Subquery(ultimo_motivo)
    )

    return render(request, "S_MANTENIMIENTO/Mantenimiento/Generar_Mantenimiento.html", {"camiones": camiones})

#CONTROLADORES PARA MECANICO-S_MANTENIMIENTO
@login_required
@role_required('mantenimiento')
def MecanicoController(request, action=None, mecanico_id=None):
    if request.method == 'POST':
        # Crear un nuevo mecánico
        if action == 'crear':
            form = MecanicoForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                return redirect('addmecanico')

        # Eliminar un mecánico existente
        elif action == 'eliminar' and mecanico_id:
            mecanico = get_object_or_404(Mecanico, id=mecanico_id)
            mecanico.delete()
            return redirect('addmecanico')

        else:
            return HttpResponseNotAllowed(['POST'])

    # Mostrar el formulario y lista de mecánicos
    if request.method == 'GET':
        # Obtener todos los mecánicos para mostrarlos en la tabla
        mecanicos = Mecanico.objects.all()
        form = MecanicoForm()

        # Si es para editar, carga el mecánico en el formulario
        if action == 'editar' and mecanico_id:
            mecanico_instance = get_object_or_404(Mecanico, id=mecanico_id)
            form = MecanicoForm(instance=mecanico_instance)
            return render(request, 'S_MANTENIMIENTO/Mecanico/Gestion_Mecanicos.html', {
                'mecanicos': mecanicos,
                'form': form,
                'action': action,
                'mecanico_id': mecanico_id,
            })

        # Mostrar los detalles de un mecánico específico
        elif action == 'detalles' and mecanico_id:
            mecanico_instance = get_object_or_404(Mecanico, id=mecanico_id)
            return render(request, 'S_MANTENIMIENTO/Mecanico/detalles_mecanico.html', {
                'mecanico': mecanico_instance,  # Pasa la instancia del mecánico a la plantilla de detalles
            })
        
        # Renderizar la lista de mecánicos en la tabla si no hay acción específica
        return render(request, 'S_MANTENIMIENTO/Mecanico/Gestion_Mecanicos.html', {
            'mecanicos': mecanicos,  # Lista completa de mecánicos
            'form': form,            # Formulario vacío o prellenado
            'action': action,
            'mecanico_id': mecanico_id,
        })

    return HttpResponseNotAllowed(['GET', 'POST'])

@login_required
@role_required('mantenimiento')
def modificar_mecanico(request, id):
    # Obtener la instancia del mecánico
    mecanico = get_object_or_404(Mecanico, id=id)

    # Crear el formulario con la instancia del mecánico
    form = MecanicoForm(instance=mecanico)

    # Si la solicitud es POST, procesamos el formulario
    if request.method == 'POST':
        form = MecanicoForm(data=request.POST, instance=mecanico, files=request.FILES)
        if form.is_valid():
            form.save()
            return redirect('addmecanico')  # Redirigir a la página de listado o éxito

    # En cualquier otro caso (GET o errores en el formulario), renderizamos el formulario
    return render(request, 'S_MANTENIMIENTO/Mecanico/modificar_mecanico.html', {'form': form})
#CONTROLADORES PARA EL CHOFER
@login_required
@role_required('asistente')
def add_chofer(request, action=None, chofer_id=None):
    if request.method == 'POST':
        # Crear un nuevo chofer
        if action == 'crear':
            form = AddChofer(request.POST)
            if form.is_valid():
                form.save()
                return redirect('addchofer')

        # Eliminar un chofer existente
        elif action == 'eliminar' and chofer_id:
            chofer = get_object_or_404(Chofer, id=chofer_id)
            chofer.delete()
            return redirect('addchofer')

        else:
            return HttpResponseNotAllowed(['POST'])

    # Mostrar el formulario y lista de choferes
    if request.method == 'GET':
        # Obtener todos los choferes para mostrarlos en la tabla
        choferes = Chofer.objects.all()
        form = AddChofer()

        # Si es para editar, carga el chofer en el formulario
        if action == 'editar' and chofer_id:
            chofer_instance = get_object_or_404(Chofer, id=chofer_id)
            form = AddChofer(instance=chofer_instance)
            return render(request, 'ASISTENTE/Chofer/add_chofer.html', {
                'choferes': choferes,
                'form': form,
                'action': action,
                'chofer_id': chofer_id,
            })

        # Mostrar los detalles de un chofer específico
        elif action == 'detalles' and chofer_id:
            chofer_instance = get_object_or_404(Chofer, id=chofer_id)
            return render(request, 'ASISTENTE/Chofer/detalles_chofer.html', {
                'chofer': chofer_instance,  # Pasa la instancia del chofer a la plantilla de detalles
            })
        
        # Renderizar la lista de choferes en la tabla si no hay acción específica
        return render(request, 'ASISTENTE/Chofer/add_chofer.html', {
            'choferes': choferes,  # Lista completa de choferes
            'form': form,          # Formulario vacío o prellenado
            'action': action,
            'chofer_id': chofer_id,
        })

    return HttpResponseNotAllowed(['GET', 'POST'])

@login_required
@role_required('asistente')
def modificarChofer(request, id):

    # Obtener el objeto Camion
    chofer = get_object_or_404(Chofer, id=id)

    # Crear el formulario con la instancia del camión
    form = AddChofer(instance=chofer)

    # Si la solicitud es POST, procesamos el formulario
    if request.method == 'POST':
        form = AddChofer(data=request.POST, instance=chofer, files=request.FILES)
        if form.is_valid():
            form.save()
            return redirect('addchofer')  # Redirigir a la página de listado o éxito

    # En cualquier otro caso (GET o errores en el formulario), renderizamos el formulario
    data = {
        'form': form
    }
    return render(request, 'ASISTENTE/Chofer/modificarChofer.html', data)


#CONTROLADORES PARA MOTIVO_MANTENIMIENTO
@login_required
@role_required('asistente')
def MotivoMantenimientoController(request, action=None, motivo_id=None):
    if request.method == 'POST':
        if action == 'crear':
            form = MotivoMantenimientoForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('motivo_mantenimiento')

        elif action == 'eliminar' and motivo_id:
            motivo = get_object_or_404(MotivoMantenimiento, id=motivo_id)
            motivo.delete()
            return redirect('motivo_mantenimiento')
        else:
            return HttpResponseNotAllowed(['POST'])

    if  request.method == 'GET':
        # Obtener lista de motivos de mantenimiento
        motivos = MotivoMantenimiento.objects.all()
        form = MotivoMantenimientoForm()
        template = 'ASISTENTE/MotivoMantenimiento/list_and_create_motivos.html'
        context = {
            'motivos': motivos,
            'form': form,
            'action': action,
            'motivo_id': motivo_id,
        }

        # Si hay un motivo_id, obtener la instancia
        if action == 'editar' and motivo_id:
            motivo = get_object_or_404(MotivoMantenimiento,id = motivo_id)
            form = MotivoMantenimientoForm(imstance = motivo)
            return render(request, template, context)
        
        elif action == 'detalles' and motivo_id:
            motivo_instance = get_object_or_404(MotivoMantenimiento, id=motivo_id)
            return render(request, 'ASISTENTE/MotivoMantenimiento/detalles_motivo.html',{
                'motivo':motivo_instance,
            })
    
        return render(request, template, context)

    return HttpResponseNotAllowed(['GET', 'POST'])
@login_required
@role_required('asistente')
def modificarMotivoMantenimiento(request, id):
    # Obtener el objeto MotivoMantenimiento
    motivo = get_object_or_404(MotivoMantenimiento, id=id)

    # Crear el formulario con la instancia del motivo
    form = MotivoMantenimientoForm(instance=motivo)

    # Si la solicitud es POST, procesamos el formulario
    if request.method == 'POST':
        form = MotivoMantenimientoForm(data=request.POST, instance=motivo)
        if form.is_valid():
            form.save()
            return redirect('motivo_mantenimiento')  # Redirigir a la página de listado o éxito

    # En cualquier otro caso (GET o errores en el formulario), renderizamos el formulario
    return render(request, 'ASISTENTE/MotivoMantenimiento/modificar_motivo_mantenimiento.html', {'form': form})

#CONTORLADORES PARA EMPRESA 

#CONTROLADORES PARA MANTENIMIENTO
@login_required
@role_required('mantenimiento')
def ListarMantenimientos(request):
    mantenimiento = Mantenimiento.objects.all()
    return render(request,'S_MANTENIMIENTO/Mantenimiento/lista_mantenimiento.html',
                  {
                      
                      'mantenimiento':mantenimiento
                  })
@login_required
@role_required('mantenimiento')
def MantenimientoController(request, camion_id, motivo_id, action=None, mantenimiento_id=None):
    camion = get_object_or_404(Camion, id=camion_id)
    motivo = get_object_or_404(MotivoMantenimiento, id=motivo_id)

    if request.method == 'POST':
        if action == 'crear':
            form = MantenimientoForm(request.POST)
            if form.is_valid():
                mantenimiento = form.save(commit=False)  # No guardar aún en la base de datos
                mantenimiento.camion = camion  # Asignar el camión automáticamente
                mantenimiento.motivo = motivo  # Asignar el motivo automáticamente
                mantenimiento.save()  # Guardar en la base de datos
                return redirect('listar_mantenimientos')

        elif action == 'eliminar' and mantenimiento_id:
            mantenimiento = get_object_or_404(Mantenimiento, id=mantenimiento_id)
            mantenimiento.delete()
            return redirect('listar_mantenimientos')

        return HttpResponseNotAllowed(['POST'])

    elif request.method == 'GET':
        # Filtrar mantenimientos por camión
        mantenimientos = Mantenimiento.objects.filter(camion=camion)
        form = MantenimientoForm()
        template = 'S_MANTENIMIENTO/Mantenimiento/list_and_create_mantenimientos.html'
        context = {
            'mantenimientos': mantenimientos,  # Pasar los mantenimientos filtrados al contexto
            'form': form,
            'action': action,
            'mantenimiento_id': mantenimiento_id,
            'camion': camion,
            'motivo': motivo,
        }

        if action == 'editar' and mantenimiento_id:
            mantenimiento = get_object_or_404(Mantenimiento, id=mantenimiento_id)
            form = MantenimientoForm(instance=mantenimiento)
            context['form'] = form
            return render(request, template, context)

        elif action == 'detalles' and mantenimiento_id:
            mantenimiento_instance = get_object_or_404(Mantenimiento, id=mantenimiento_id)
            return render(request, 'S_MANTENIMIENTO/Mantenimiento/detalles_mantenimiento.html', {
                'mantenimiento': mantenimiento_instance,
                'camion': camion,
                'motivo': motivo,
            })

        return render(request, template, context)

    return HttpResponseNotAllowed(['GET', 'POST'])
from django.shortcuts import render, get_object_or_404, redirect
from .models import Mantenimiento
from .forms import MantenimientoForm

@login_required
@role_required('mantenimientos')
def modificarMantenimiento(request, camion_id, motivo_id, mantenimiento_id):
    # Obtener el objeto Mantenimiento o devolver 404 si no existe
    mantenimiento = get_object_or_404(Mantenimiento, id=mantenimiento_id, camion_id=camion_id, motivo_id=motivo_id)

    if request.method == 'POST':  # Si el formulario se envió
        form = MantenimientoForm(request.POST, instance=mantenimiento)
        if form.is_valid():
            form.save()
            return redirect('listar_mantenimientos')
    else:
        form = MantenimientoForm(instance=mantenimiento)  # Cargar el formulario con los datos actuales

    # Pasar el mantenimiento y el formulario al template
    context = {
        'form': form,
        'mantenimiento': mantenimiento,
        'camion': mantenimiento.camion,  
        'motivo': mantenimiento.motivo,  
    }

    return render(request, 'S_MANTENIMIENTO/Mantenimiento/modificar_mantenimiento.html', context)


@login_required
@role_required('mantenimiento')
def Registro_Mantenimiento_Controller(request, camion_id):
    camion = get_object_or_404(Camion, id=camion_id)
    registros_mantenimiento = Mantenimiento.objects.filter(camion=camion).order_by('-fecha_mantenimiento')

    return render(request, 'S_MANTENIMIENTO/Mantenimiento/registros_mantenimiento.html', {
        'camion': camion,
        'registros_mantenimiento': registros_mantenimiento
    })

#CONTROLADORES PARA MANTENIMIENTO DETALLE
from django.urls import reverse
from django.contrib import messages

@login_required
@role_required('mantenimiento')
def Crear_Detalle_Mantenimiento(request, mantenimiento_id):
    # Obtener el mantenimiento con el ID proporcionado
    mantenimiento = get_object_or_404(Mantenimiento, id=mantenimiento_id)

    # Obtener los detalles de mantenimiento ya registrados para ese mantenimiento
    mantenimiento_detalles = Mantenimiento_Detalle.objects.filter(mantenimiento=mantenimiento)

    if request.method == 'POST':
        # Verificamos si la solicitud es para eliminar un detalle
        if 'eliminar_detalle' in request.POST:
            detalle_id = request.POST.get('detalle_id')
            detalle = get_object_or_404(Mantenimiento_Detalle, id=detalle_id, mantenimiento=mantenimiento)
            detalle.delete()
            messages.success(request, "Detalle eliminado correctamente.")
            return redirect('crear_mantenimiento_detalle', mantenimiento_id=mantenimiento_id)
        
        # Si no es eliminación, entonces es una creación
        form = MantenimientoDetalleForm(request.POST)
        if form.is_valid():
            detalle = form.save(commit=False)
            detalle.mantenimiento = mantenimiento  # Asociar el mantenimiento al detalle
            detalle.save()
            messages.success(request, "Detalle añadido correctamente.")  # Mensaje de éxito
            return redirect('crear_mantenimiento_detalle', mantenimiento_id=mantenimiento_id)
    else:
        form = MantenimientoDetalleForm()

    # Renderizar el formulario en la plantilla
    return render(request, 'S_MANTENIMIENTO/MantenimientoDetalle/crear_detalle.html', {
        'form': form,
        'mantenimiento': mantenimiento,
        'mantenimiento_detalles': mantenimiento_detalles,  # Pasar detalles existentes al contexto
    })


#CONTROLADORES PARA FACTURA
from django.http import Http404

@login_required
@role_required('mantenimiento')
def FacturaController(request, mantenimiento_id=None, action=None, factura_id=None):
    # Validamos que se haya proporcionado un mantenimiento_id
    if mantenimiento_id is None:
        raise Http404("Debe proporcionar un ID de mantenimiento válido.")

    mantenimiento = get_object_or_404(Mantenimiento, id=mantenimiento_id)  # Obtener mantenimiento

    if request.method == 'POST':
        # Crear una nueva factura asociada al mantenimiento
        if action == 'crear':
            form = FacturaForm(request.POST)
            if form.is_valid():
                factura = form.save(commit=False)
                factura.mantenimiento = mantenimiento  # Asociar la factura al mantenimiento
                factura.save()
                return redirect(reverse('factura_list', kwargs={'mantenimiento_id': mantenimiento.id}))

        # Eliminar una factura existente
        elif action == 'eliminar' and factura_id:
            factura = get_object_or_404(Factura, id=factura_id, mantenimiento=mantenimiento)
            factura.delete()
            return redirect('factura_list', mantenimiento_id=mantenimiento.id)

        # Si la acción no es válida
        else:
            return HttpResponseNotAllowed(['POST'])

    elif request.method == 'GET':
        facturas = Factura.objects.filter(mantenimiento=mantenimiento)
        form = FacturaForm()

        # Si es para editar, carga la factura en el formulario
        if action == 'editar' and factura_id:
            factura = get_object_or_404(Factura, id=factura_id, mantenimiento=mantenimiento)
            form = FacturaForm(instance=factura)
            return render(request, 'S_MANTENIMIENTO/Factura/modificar_factura.html', {
                'facturas': facturas,
                'form': form,
                'action': action,
                'factura_id': factura_id,
                'mantenimiento': mantenimiento,
            })

        # Si es para ver los detalles de la factura
        elif action == 'detalles' and factura_id:
            factura_instance = get_object_or_404(Factura, id=factura_id, mantenimiento=mantenimiento)
            return render(request, 'S_MANTENIMIENTO/Factura/FacturaDetalle.html', {
                'factura': factura_instance,
                'mantenimiento': mantenimiento,
            })

        # En caso de que no se especifique ninguna acción
        return render(request, 'S_MANTENIMIENTO/Factura/GestionFactura.html', {
            'facturas': facturas,
            'form': form,
            'action': action,
            'factura_id': factura_id,
            'mantenimiento': mantenimiento,
        })

    # Si no es un método válido
    return HttpResponseNotAllowed(['GET', 'POST'])
@login_required
@role_required('mantenimiento')
def factura_detalle(request, factura_id):
    factura = get_object_or_404(Factura, id=factura_id)
    mantenimiento = factura.mantenimiento
    detalles = Mantenimiento_Detalle.objects.filter(mantenimiento=mantenimiento)
    
    return render(request, 'S_MANTENIMIENTO/Factura/Detalle_Factura.html', {
        'factura': factura,
        'mantenimiento': mantenimiento,
        'detalles': detalles
    })

@login_required
@role_required('mantenimiento')

def lista_facturas(request):
    facturas = Factura.objects.select_related('mantenimiento__camion').all()
    return render(request, 'S_MANTENIMIENTO/Factura/lista_facturas.html', {'facturas': facturas})

from .models import Notificacion



@login_required
def lista_notificaciones(request):
    notificaciones = Notificacion.objects.filter(usuario=request.user).order_by('-fecha_creacion')
    return render(request, 'Notificaciones/notificaciones.html', {'notificaciones': notificaciones})

def marcar_notificacion_leida(request, notificacion_id):
    notificacion = get_object_or_404(Notificacion, id=notificacion_id, usuario=request.user)
    notificacion.marcar_como_leida()
    return redirect('camiones_en_mantenimiento')

from django.utils.timezone import now
from .models import SolicitudAlianza, ContratoAlianza, RegistroNormativas
from .utils import role_required

# --- REPRESENTANTE ---
@login_required
@role_required('representante')
def registro_solicitud_alianza(request):
    if request.method == 'POST':
        descripcion = request.POST.get('descripcion')
        archivo = request.FILES.get('solicitud')  # Captura el archivo subido

        if not archivo:
            messages.error(request, 'Debe adjuntar un archivo de solicitud.')
            return redirect('registro_solicitud_alianza')

        SolicitudAlianza.objects.create(
            solicitante=request.user,
            descripcion=descripcion,
            solicitud=archivo
        )
        messages.success(request, 'Solicitud registrada correctamente.')
        return redirect('registro_solicitud_alianza')
    
    return render(request, 'REPRESENTANTE/registro_solicitud.html')


@login_required
@role_required('representante')
def seguimiento_solicitud(request):
    # Filtrar solo las solicitudes realizadas por el usuario actual (Shurtape Perú)
    solicitudes = SolicitudAlianza.objects.filter(solicitante=request.user).order_by('-fecha_solicitud')
    return render(request, 'REPRESENTANTE/seguimiento_solicitud.html', {'solicitudes': solicitudes})

@login_required
@role_required('gerente')
def seguimiento_solicitud_gerente(request):
    # Mostrar todas las solicitudes de alianza, ordenadas por fecha
    solicitudes = SolicitudAlianza.objects.all().order_by('-fecha_solicitud')
    return render(request, 'GERENTE/registro_aceptacion.html', {'solicitudes': solicitudes})


from .models import RechazoSolicitud

def cambiar_estado_solicitud(request, solicitud_id, estado):
    solicitud = get_object_or_404(SolicitudAlianza, id=solicitud_id)

    if solicitud.estado != 'pendiente':
        messages.info(request, 'Esta solicitud ya fue revisada.')
        return redirect('seguimiento_solicitud_gerente')

    if estado == 'rechazada':
        motivo = request.POST.get('motivo')
        if not motivo:
            messages.error(request, 'Debe indicar el motivo del rechazo.')
            return redirect('seguimiento_solicitud_gerente')

        RechazoSolicitud.objects.create(
            solicitud=solicitud,
            motivo=motivo
        )

    solicitud.estado = estado
    solicitud.fecha_revision = now()
    solicitud.save()

    messages.success(request, f'Solicitud {estado}.')
    return redirect('seguimiento_solicitud_gerente')

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import SolicitudAlianza, Empresa, ContratoAlianza


@login_required
@role_required('gerente')
def registrar_contrato(request):
    if request.method == 'POST':
        solicitud_id = request.POST.get('solicitud')
        empresa_id = request.POST.get('empresa')
        documento = request.FILES.get('documento')

        # Validación básica de campos
        if not solicitud_id or not empresa_id or not documento:
            messages.error(request, 'Todos los campos son obligatorios.')
            return redirect('registrar_contrato')

        try:
            # Validar que la solicitud y empresa existan
            solicitud = SolicitudAlianza.objects.get(id=solicitud_id, estado='aprobada')
            empresa = Empresa.objects.get(id=empresa_id)

            # Verificar que no exista un contrato para la misma solicitud
            if ContratoAlianza.objects.filter(solicitud=solicitud).exists():
                messages.error(request, 'Ya existe un contrato para esta solicitud.')
                return redirect('registrar_contrato')

            # Crear el contrato
            ContratoAlianza.objects.create(
                solicitud=solicitud,
                empresa=empresa,
                documento=documento,
                estado='pendiente'
            )
            messages.success(request, 'Contrato registrado correctamente.')
            return redirect('registrar_contrato')

        except (SolicitudAlianza.DoesNotExist, Empresa.DoesNotExist):
            messages.error(request, 'Solicitud o empresa no válida.')
            return redirect('registrar_contrato')
        except Exception as e:
            messages.error(request, f'Ocurrió un error inesperado: {e}')
            return redirect('registrar_contrato')

    # Contexto para el formulario
    solicitudes = SolicitudAlianza.objects.filter(estado='aprobada')
    empresas = Empresa.objects.all()

    return render(request, 'GERENTE/registrar_contrato.html', {
        'solicitudes': solicitudes,
        'empresas': empresas
    })

@login_required
@role_required('gerente')
def visualizar_contratos(request):
    contratos = ContratoAlianza.objects.select_related('solicitud', 'empresa').all()
    return render(request, 'GERENTE/visualizar_contratos.html', {'contratos': contratos})

@login_required
@role_required('representante')
def contratos_recibidos(request):
    empresa_usuario = request.user.empresa
    if not empresa_usuario:
        contratos = []
    else:
        contratos = ContratoAlianza.objects.filter(empresa=empresa_usuario)

    return render(request, 'REPRESENTANTE/contratos_recibidos.html', {
        'contratos': contratos
    })

from .models import ContratoAlianza, RechazoContrato

def cambiar_estado_contrato(request, contrato_id, estado):
    contrato = get_object_or_404(ContratoAlianza, id=contrato_id)

    if contrato.estado != 'pendiente':
        messages.info(request, 'Este contrato ya fue revisado.')
        return redirect('contratos_recibidos')

    if estado == 'rechazada':
        if request.method == 'POST':
            motivo = request.POST.get('motivo', '').strip()
            if not motivo:
                messages.error(request, 'Debe proporcionar un motivo para rechazar el contrato.')
                return redirect('contratos_recibidos')

            # Guardar el rechazo del contrato
            RechazoContrato.objects.create(contrato=contrato, motivo=motivo)

    contrato.estado = estado
    contrato.fecha_revision = now()
    contrato.save()

    messages.success(request, f'Contrato {estado}.')
    return redirect('contratos_recibidos')




import pdfkit

# Ruta correcta al ejecutable de wkhtmltopdf
path_wkhtmltopdf = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"

# Configurar pdfkit con la ruta correcta
config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)

##APARTIR DE ACA HOJA DE RUTA
from django.shortcuts import render, redirect, get_object_or_404
from .models import HojadeRuta, Chofer, Camion, Ubicacion
from .forms import HojadeRutaForm
import requests
# Función actualizada para geocodificar e incluir provincia
def geocode_address(address):
    url = 'https://nominatim.openstreetmap.org/search'
    params = {
        'q': address,
        'format': 'json',
        'limit': 1,
        'addressdetails': 1  # Solicita detalles de la dirección para obtener provincia
    }
    headers = {
        'User-Agent': 'transporte-verito/1.0 (www.miriamcamacho@gmail.com)'
    }
    
    response = requests.get(url, params=params, headers=headers)
    print(f"🌍 Geocodificando '{address}' - Status: {response.status_code}")
    
    if response.status_code == 200 and response.json():
        result = response.json()[0]
        print(f"✅ Coordenadas obtenidas: {result['lat']}, {result['lon']}")
        address_details = result.get("address", {})
        province = address_details.get("state", "Desconocida")
        return float(result['lat']), float(result['lon']), province
    
    print("⚠️ No se encontraron coordenadas")
    return None, None, "Desconocida"
#CONTROLADOR PARA OBTENER DISTANCIA DE RUTA
def get_route(start_coords, end_coords):
    valhalla_url = "https://valhalla1.openstreetmap.de/route"
    payload = {
        "locations": [
            {"lat": start_coords[0], "lon": start_coords[1]},
            {"lat": end_coords[0], "lon": end_coords[1]}
        ],
        "costing": "auto",
        "directions_options": {"units": "kilometers"}
    }
    
    response = requests.post(valhalla_url, json=payload)
    
    if response.status_code == 200:
        data = response.json()
        print("🚛 Ruta obtenida con éxito")
        return data
    else:
        print(f"❌ Error al obtener ruta: {response.status_code}")
    
    return None
#CONTROLADOR PARA CREAR HOJA DE RUTA
@login_required
@role_required('jefedespacho')
def hoja_de_ruta_create(request, chofer_id=None):
    chofer = None
    camion = None

    # Si se recibe un chofer_id, obtenemos el chofer y su camión
    if chofer_id:
        chofer = get_object_or_404(Chofer, id=chofer_id)

        # Verificar si el chofer tiene un camión asignado
        if hasattr(chofer, 'camion'):
            camion = chofer.camion
        else:
            camion = None

    if request.method == 'POST':
        form = HojadeRutaForm(request.POST)
        if form.is_valid():
            hoja_de_ruta = form.save(commit=False)

            # Si ya teníamos el chofer y camión, asignarlos
            if chofer:
                hoja_de_ruta.chofer = chofer
            if camion:
                hoja_de_ruta.camion = camion

            # Geocodificación de direcciones
            direccion_ida = form.cleaned_data['direccion_ida']
            direccion_vuelta = form.cleaned_data['direccion_vuelta']
            lat_ida, lon_ida, province_ida = geocode_address(direccion_ida)
            lat_vuelta, lon_vuelta, province_vuelta = geocode_address(direccion_vuelta)

            if lat_ida is not None and lat_vuelta is not None:
                route_data = get_route((lat_ida, lon_ida), (lat_vuelta, lon_vuelta))
                distancia_km = route_data["trip"]["summary"]["length"] if route_data and "trip" in route_data else None

                partida_ubicacion = Ubicacion.objects.create(
                    direccion=direccion_ida,
                    latitud=lat_ida,
                    longitud=lon_ida,
                    provincia=province_ida
                )
                llegada_ubicacion = Ubicacion.objects.create(
                    direccion=direccion_vuelta,
                    latitud=lat_vuelta,
                    longitud=lon_vuelta,
                    provincia=province_vuelta
                )

                hoja_de_ruta.partida_ubicacion = partida_ubicacion
                hoja_de_ruta.llegada_ubicacion = llegada_ubicacion
                hoja_de_ruta.distancia = distancia_km
                hoja_de_ruta.save()

                return redirect('hoja_de_ruta_list')  # Redirigir a la lista de hojas de ruta

    else:
        # Precargar el formulario con los datos del chofer y camión
        form = HojadeRutaForm(initial={'chofer': chofer, 'camion': camion})

    # Obtener datos para mostrar en la vista
    hojas = HojadeRuta.objects.all()
    choferes = Chofer.objects.all()
    camiones = Camion.objects.all()

    return render(request, 'HojaRuta/hoja_de_ruta_form.html', {
        'form': form,
        'chofer': chofer,
        'camion': camion,
        'choferes': choferes,
        'camiones': camiones,
        'hojas': hojas
    })
@login_required
@role_required('jefedespacho')
def listar_hojas(request):
    """
    Lista las Hojas de Ruta cuyo camión pertenezca a la empresa
    del usuario logueado.
    """
    hojas = HojadeRuta.objects.filter(camion__empresa_propietaria=request.user.empresa)
    
    return render(request, 'HojaRuta/hoja_de_ruta_list.html', {
        'hojas': hojas
    })

#HOJA DE RUTA ACTUALIZAR
@login_required
@role_required('jefedespacho')
def hoja_de_ruta_update(request, pk):
    # Función de actualización similar a "modificarChofer" sin cambiar las variables base
    hoja = get_object_or_404(HojadeRuta, pk=pk)
    if request.method == 'POST':
        form = HojadeRutaForm(request.POST, instance=hoja)
        if form.is_valid():
            hoja_de_ruta = form.save(commit=False)
            direccion_ida = form.cleaned_data['direccion_ida']
            direccion_vuelta = form.cleaned_data['direccion_vuelta']
            
            # Geocodificación con provincia para actualizar
            lat_ida, lon_ida, province_ida = geocode_address(direccion_ida)
            lat_vuelta, lon_vuelta, province_vuelta = geocode_address(direccion_vuelta)
            
            if lat_ida is not None and lat_vuelta is not None:
                route_data = get_route((lat_ida, lon_ida), (lat_vuelta, lon_vuelta))
                distancia_km = route_data["trip"]["summary"]["length"] if route_data and "trip" in route_data else None
                
                # Actualizamos la ubicación de partida
                if hoja.partida_ubicacion:
                    hoja.partida_ubicacion.direccion = direccion_ida
                    hoja.partida_ubicacion.latitud = lat_ida
                    hoja.partida_ubicacion.longitud = lon_ida
                    hoja.partida_ubicacion.provincia = province_ida
                    hoja.partida_ubicacion.save()
                else:
                    partida_ubicacion = Ubicacion.objects.create(
                        direccion=direccion_ida,
                        latitud=lat_ida,
                        longitud=lon_ida,
                        provincia=province_ida
                    )
                    hoja_de_ruta.partida_ubicacion = partida_ubicacion
                
                # Actualizamos la ubicación de llegada
                if hoja.llegada_ubicacion:
                    hoja.llegada_ubicacion.direccion = direccion_vuelta
                    hoja.llegada_ubicacion.latitud = lat_vuelta
                    hoja.llegada_ubicacion.longitud = lon_vuelta
                    hoja.llegada_ubicacion.provincia = province_vuelta
                    hoja.llegada_ubicacion.save()
                else:
                    llegada_ubicacion = Ubicacion.objects.create(
                        direccion=direccion_vuelta,
                        latitud=lat_vuelta,
                        longitud=lon_vuelta,
                        provincia=province_vuelta
                    )
                    hoja_de_ruta.llegada_ubicacion = llegada_ubicacion
                
                hoja_de_ruta.distancia = distancia_km
                hoja_de_ruta.save()
                return redirect('hoja_de_ruta_create')
    else:
        form = HojadeRutaForm(instance=hoja)
    
    hojas = HojadeRuta.objects.all()
    choferes = Chofer.objects.all()
    camiones = Camion.objects.all()
    return render(request, 'HojaRuta/hoja_de_ruta_update.html', {
        'form': form,
        'choferes': choferes,
        'camiones': camiones,
        'hojas': hojas,
        'action': 'editar',
        'hoja_id': hoja.id
    })
#HOJA DE RUTA ELIMINAR
def hoja_de_ruta_delete(request, pk):
    hoja = get_object_or_404(HojadeRuta, pk=pk)
    if request.method == 'POST':
        hoja.delete()
        return redirect('hoja_de_ruta_create')  # Redirigir a la lista de hojas de ruta después de eliminar
    return render(request, 'HojaRuta/hoja_de_ruta_confirm_delete.html', {'hoja': hoja})
def hoja_de_ruta_details(request, pk):
    hoja = get_object_or_404(HojadeRuta, pk=pk)
    return render(request, 'HojaRuta/hoja_de_ruta_details.html', {'hoja': hoja})
#GUIA DE REMISION

# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.template.loader import render_to_string
from .models import GuiaRemision, DetalleGuiaRemision

from django.template.loader import render_to_string
from django.utils import timezone
import pdfkit
from django.core.files.base import ContentFile
path_wkhtmltopdf = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)

import pdfkit
from django.core.files.base import ContentFile
from .forms import GuiaRemisionForm, DetalleFormSet

def generar_pdf_transportista(guia):
    html_string = render_to_string('guias/pdf_transportista.html', {'guia': guia})
    print("HTML para PDF transportista:", html_string[:200])  # Muestra los primeros 200 caracteres
    pdf_content = pdfkit.from_string(html_string, False, configuration=config)
    print("Tamaño del PDF transportista:", len(pdf_content))
    if not pdf_content:
        print("Error: PDF transportista no se generó correctamente.")
    pdf_file = ContentFile(pdf_content)
    filename = f'pdf_generado_{guia.id}.pdf'
    guia.pdf_generado.save(filename, pdf_file, save=False)
    return guia.pdf_generado.url

def generar_pdf_remitente(guia):
    html_string = render_to_string('guias/pdf_remitente.html', {'guia': guia})
    print("HTML para PDF remitente:", html_string[:200])
    pdf_content = pdfkit.from_string(html_string, False, configuration=config)
    print("Tamaño del PDF remitente:", len(pdf_content))
    if not pdf_content:
        print("Error: PDF remitente no se generó correctamente.")
    pdf_file = ContentFile(pdf_content)
    filename = f'pdf_firmado_{guia.id}.pdf'
    guia.pdf_firmado.save(filename, pdf_file, save=False)
    return guia.pdf_firmado.url

from django.utils import timezone
from datetime import date

def crear_guia_remision(request, hoja_ruta_id):
    hoja_de_ruta = get_object_or_404(HojadeRuta, id=hoja_ruta_id)
    if request.method == 'POST':
        form = GuiaRemisionForm(request.POST, request.FILES)
        detalle_formset = DetalleFormSet(request.POST, request.FILES)
        if form.is_valid():
            guia = form.save(commit=False)
            guia.hoja_de_ruta = hoja_de_ruta
            guia.empresa_emisora = hoja_de_ruta.camion.empresa_propietaria
            guia.save()
            
            detalle_formset = DetalleFormSet(request.POST, instance=guia)
            if detalle_formset.is_valid():
                detalle_formset.save()
                
                # Generamos los dos PDFs y almacenamos sus rutas en el modelo.
                pdf_transportista_url = generar_pdf_transportista(guia)  # Realmente está generando el pdf_generado
                pdf_remitente_url = generar_pdf_remitente(guia)   
                
                # Suponiendo que en tu modelo GuiaRemision tienes campos para almacenar los archivos,
                # por ejemplo: pdf_transportista y pdf_remitente (pueden ser FileField o CharField para la ruta)
                
                guia.save()
                messages.success(request, "✅ Guía de Remisión creada y PDFs generados correctamente.")
                
    
                return redirect('listar_guias')
            else:
                            messages.error(request, "⚠️ Corrige los errores en los detalles de la guía.")
        else:
            messages.error(request, "⚠️ Corrige los errores en el formulario.")
    else:
        initial_data = {
            'hoja_de_ruta': hoja_de_ruta.id,
            'empresa_emisora': hoja_de_ruta.camion.empresa_propietaria if hoja_de_ruta.camion else None,
            'fecha_emision': date.today(),
            'fecha_traslado': '',
        }
        form = GuiaRemisionForm(initial=initial_data)
        detalle_formset = DetalleFormSet(queryset=DetalleGuiaRemision.objects.none())
    
    return render(request, 'guias/crear_guia_completa.html', {
        'form': form,
        'detalle_formset': detalle_formset,
        'hoja_de_ruta': hoja_de_ruta,
    })
def listar_guias(request):
    usuario = request.user

    # Suponiendo que el usuario tiene un campo 'empresa' que lo relaciona con su empresa
    if hasattr(usuario, 'empresa') and usuario.empresa:
        empresa_usuario = usuario.empresa

        # Filtramos las guías donde la empresa del usuario sea emisora o remitente
        guias = GuiaRemision.objects.filter(
            empresa_emisora=empresa_usuario
        ).order_by('-id') | GuiaRemision.objects.filter(
            empresa_remitente=empresa_usuario
        ).order_by('-id')

    else:
        # Si el usuario no tiene una empresa asociada, no ve ninguna guía
        guias = GuiaRemision.objects.none()

    return render(request, 'guias/lista_guias.html', {'guias': guias})


def eliminar_guia(request, hoja_id):
    guia = get_object_or_404(GuiaRemision, pk=hoja_id)
    if request.method == 'POST':
        guia.delete()
        messages.success(request, "La guía ha sido eliminada correctamente.")
        return redirect('listar_guias')
    return render(request, 'guias/eliminar.html', {'guia': guia})
from .models import GuiaRemision  # Asegúrate de importar tu modelo
 # Asegúrate de importar el modelo correcto

from django.shortcuts import redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def enviar_a_chofer(request, guia_id):
    print(request.method)  # Agrega esta línea para acceder a request NO FUNCIONA
    guia = get_object_or_404(GuiaRemision, id=guia_id)
    guia.estado = "Enviado al Chofer"
    guia.save()
    return redirect('listado_chofer')


def listado_chofer(request):
    guias_enviadas = GuiaRemision.objects.filter(estado="Enviado al chofer") #NO FUNCIONA
    return render(request, 'chofer/listado_chofer.html', {'guias': guias_enviadas})



@login_required
def listar_guias_chofer(request):
    usuario = request.user

    # Verificar si el usuario tiene un chofer asociado
    chofer = Chofer.objects.filter(usuario=usuario).first()  # Obtener el chofer vinculado al usuario

    if chofer:
        # Filtrar guías de remisión donde el chofer esté asignado en la hoja de ruta
        guias = GuiaRemision.objects.filter(hoja_de_ruta__chofer=chofer).order_by('-fecha_emision')
    else:
        # Si el usuario no es un chofer, mostrar una lista vacía
        guias = GuiaRemision.objects.none()

    return render(request, 'guias/lista_guias_chofer.html', {'guias': guias})


@login_required
def chofer_dashboard(request):
    try:
        # Se obtiene el chofer asociado al usuario logueado
        chofer = Chofer.objects.get(usuario=request.user)
    except Chofer.DoesNotExist:
        messages.error(request, "No se encontró un chofer asociado a su cuenta.")
        return redirect('home')  # Redirige según tu lógica

    # Recuperar hojas de ruta asignadas a este chofer
    hojas_de_ruta = HojadeRuta.objects.filter(chofer=chofer)
    
    # Recuperar guías de remisión vinculadas a las hojas de ruta asignadas
    guias_remision = GuiaRemision.objects.filter(hoja_de_ruta__in=hojas_de_ruta)
    
    context = {
        'chofer': chofer,
        'hojas_de_ruta': hojas_de_ruta,
        'guias_remision': guias_remision,
    }
    return render(request, 'chofer_dashboard.html', context)

from .models import Reporte
from .forms import ReporteForm 

@login_required
def crear_reporte(request, guia_id):
    guia = get_object_or_404(GuiaRemision, id=guia_id)

    if request.method == "POST":
        form = ReporteForm(request.POST, request.FILES)
        if form.is_valid():
            reporte = form.save(commit=False)
            reporte.guia = guia
            reporte.save()
            return redirect('listar_guias_chofer')  # Redirige a la lista de guías del chofer

    else:
        form = ReporteForm()

    return render(request, 'CHOFER/Reporte/crear_reporte.html', {'form': form, 'guia': guia})



@login_required
def listar_reportes_chofer(request):
    usuario = request.user

    # Verificar si el usuario tiene un chofer asociado
    chofer = Chofer.objects.filter(usuario=usuario).first()

    if chofer:
        # Filtrar los reportes de las guías asignadas al chofer
        reportes = Reporte.objects.filter(guia__hoja_de_ruta__chofer=chofer).order_by('-fecha_reporte')
    else:
        # Si el usuario no es un chofer, mostrar una lista vacía
        reportes = Reporte.objects.none()

    return render(request, 'CHOFER/Reporte/lista_reportes_chofer.html', {'reportes': reportes})

@login_required
def listar_todos_los_reportes(request):
    # Obtener todos los reportes en orden descendente por fecha
    reportes = Reporte.objects.all().order_by('-fecha_reporte')

    return render(request, 'ASISTENTE/Reportes/lista_todos_los_reportes.html', {'reportes': reportes})

@login_required
def listar_reportes_empresa(request):
    usuario = request.user

    # Verificamos si el usuario tiene una empresa asociada
    if hasattr(usuario, 'empresa') and usuario.empresa:
        empresa_usuario = usuario.empresa

        # Filtramos los reportes de guías donde la empresa del usuario sea emisora o remitente
        reportes = Reporte.objects.filter(
            guia__empresa_emisora=empresa_usuario
        ).order_by('-fecha_reporte') | Reporte.objects.filter(
            guia__empresa_remitente=empresa_usuario
        ).order_by('-fecha_reporte')

    else:
        # Si el usuario no tiene una empresa asociada, no ve reportes
        reportes = Reporte.objects.none()

    return render(request, 'JEFE_DESPACHO/Reportes/lista_reportes_empresa.html', {'reportes': reportes})




def choferes_por_empresa(request):
    empresa_usuario = request.user.empresa  # Empresa del usuario autenticado

    if not empresa_usuario:
        return render(request, 'choferes_por_empresa.html', {'error': 'No tienes una empresa asignada'})

    # Filtrar choferes cuyo camión pertenece a la empresa del usuario
    choferes = Chofer.objects.filter(camion__empresa_propietaria=empresa_usuario)

    return render(request, 'choferes_por_empresa.html', {'choferes': choferes})

@login_required
def camion_asignado(request):
    # Se obtiene el chofer asociado al usuario logueado
    chofer = get_object_or_404(Chofer, usuario=request.user)
    # Se obtiene el camión asignado al chofer (puede ser None)
    camion = chofer.camion

    context = {
        'chofer': chofer,
        'camion': camion
    }
    return render(request, 'CHOFER/camion_asignado.html', context)

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
User = get_user_model()

@login_required
def listar_usuarios(request):
    # Recoger filtros desde la URL
    group_filter    = request.GET.get('group', '')
    username_filter = request.GET.get('username', '')
    empresa_filter  = request.GET.get('empresa', '')
    first_name_filter = request.GET.get('first_name', '')
    last_name_filter  = request.GET.get('last_name', '')
    dni_filter        = request.GET.get('dni', '')
    phone_filter      = request.GET.get('phone', '')
    
    # Inicializar queryset
    usuarios = User.objects.all()
    
    if group_filter:
        usuarios = usuarios.filter(groups__id=group_filter)
    
    if username_filter:
        usuarios = usuarios.filter(username__icontains=username_filter)
    
    if empresa_filter:
        usuarios = usuarios.filter(empresa__nombre_empresa__icontains=empresa_filter)
    
    if first_name_filter:
        usuarios = usuarios.filter(first_name__icontains=first_name_filter)
    
    if last_name_filter:
        usuarios = usuarios.filter(last_name__icontains=last_name_filter)
    
    if dni_filter:
        usuarios = usuarios.filter(dni__icontains=dni_filter)
    
    if phone_filter:
        usuarios = usuarios.filter(phone__icontains=phone_filter)
    
    # Evitar duplicados en caso de filtros por grupos
    usuarios = usuarios.distinct()
    
    # Obtener todos los grupos para llenar el combo box
    groups = Group.objects.all()
    
    context = {
        'usuarios': usuarios,
        'groups': groups,
    }
    return render(request, 'GERENTE/Usuarios/lista_usuarios.html', context)

from .models import Ruta,TransferenciaPagada,CombusExtraChofer,GastoAdicional,FacturaCombustible
from .forms import RutaForm,TransferenciaPagadaForm,CombusExtraChoferForm,GastoAdicionalForm,FacturaCombustibleForm

def RutaController(request, action=None, ruta_id=None):
    if request.method == 'POST':
        if action == 'crear':
            form = RutaForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('rutas')

        elif action == 'eliminar' and ruta_id:
            ruta = get_object_or_404(Ruta, id=ruta_id)
            ruta.delete()
            return redirect('rutas')

        return HttpResponseNotAllowed(['POST'])

    elif request.method == 'GET':
        # Obtener lista de rutas
        rutas = Ruta.objects.all()
        form = RutaForm()
        template = 'JEFE_DESPACHO/list_and_create_rutas.html'
        context = {
            'rutas': rutas,
            'form': form,
            'action': action,
            'ruta_id': ruta_id,
        }

        # Si hay un ruta_id, obtener la instancia
        if ruta_id:
            ruta_instance = get_object_or_404(Ruta, id=ruta_id)

            # Acción editar: cargar la instancia en el formulario
            if action == 'editar':
                context['form'] = RutaForm(instance=ruta_instance)

            # Acción detalles: cambiar template y contexto
            elif action == 'detalles':
                template = 'JEFE_DESPACHO/detalles_ruta.html'
                context = {'ruta': ruta_instance}

        return render(request, template, context)

    return HttpResponseNotAllowed(['GET', 'POST'])

def modificarRuta(request, id):
    # Obtener el objeto Ruta
    ruta = get_object_or_404(Ruta, id=id)

    # Crear el formulario con la instancia de la ruta
    form = RutaForm(instance=ruta)

    # Si la solicitud es POST, procesamos el formulario
    if request.method == 'POST':
        form = RutaForm(data=request.POST, instance=ruta)
        if form.is_valid():
            form.save()
            return redirect('rutas')  # Redirigir a la página de listado de rutas

    # En cualquier otro caso (GET o errores en el formulario), renderizamos el formulario
    return render(request, 'JEFE_DESPACHO/modificar_ruta.html', {'form': form})


def CombusExtraChoferController(request, action=None, combusExtraChofer_id=None):
    if request.method == 'POST':
        # Crear un nuevo camión
        if action == 'crear':
            form = CombusExtraChoferForm(request.POST,request.FILES)
            if form.is_valid():
                form.save()
                return redirect('combusExtraChofer')

        # Eliminar un camión existente
        elif action == 'eliminar' and combusExtraChofer_id:
            combusExtraChofer = get_object_or_404(CombusExtraChofer, id=combusExtraChofer_id)
            combusExtraChofer.delete()
            return redirect('combusExtraChofer')

        else:
            return HttpResponseNotAllowed(['POST'])

    # Mostrar el formulario y lista de camiones
    if request.method == 'GET':
        combusExtraChoferes = CombusExtraChofer.objects.all()
        form = CombusExtraChoferForm()

        # Si es para editar, carga el camión en el formulario
        if action == 'editar' and combusExtraChofer_id:
            combusExtraChofer = get_object_or_404(CombusExtraChofer, id=combusExtraChofer_id)
            form = CombusExtraChoferForm(instance=combusExtraChofer)
            return render(request, 'CHOFER/create_solicitud_de_rcbextra.html', {
                'combusExtraChoferes': combusExtraChoferes,
                'form': form,
                'action': action,
                'combusExtraChofer_id': combusExtraChofer_id,
            })
        
        elif action == 'detalles' and combusExtraChofer_id:
            combusExtraChofer_instance = get_object_or_404(CombusExtraChofer, id=combusExtraChofer_id)
            return render(request, 'CHOFER/detalles_camion.html', {
                'combusExtraChofer': combusExtraChofer_instance,  # Corregido el diccionario de contexto
            })
        
        return render(request, 'CHOFER/create_solicitud_de_rcbextra.html', {
            'combusExtraChoferes': combusExtraChoferes,
            'form': form,
            'action': action,
            'combus_extra_chofer_id': combusExtraChofer_id,
        })
    
    
    return HttpResponseNotAllowed(['GET', 'POST'])


def estado_solicitud_recarga(request):
    # Filtrar registros específicos si es necesario
    combus_extra_choferes = CombusExtraChofer.objects.all()

    return render(request, 'CHOFER/estado_solicitud_recarga.html', {
        'combus_extra_choferes': combus_extra_choferes  # Nombres claros para evitar errores
    })


def GastoAdicionalController(request, action=None, gastoAdicional_id=None):
    if request.method == 'POST':
        if action == 'crear':
            form = GastoAdicionalForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                return redirect('gastoAdicional')

        elif action == 'eliminar' and gastoAdicional_id:
            gastoAdicional = get_object_or_404(GastoAdicional, id=gastoAdicional_id)
            gastoAdicional.delete()
            return redirect('gastoAdicional')

        else:
            return HttpResponseNotAllowed(['POST'])

    if request.method == 'GET':
        gastosAdicionales = GastoAdicional.objects.all()
        recepcion_facturas = FacturaCombustible.objects.all()  # Agregando la segunda lista
        form = GastoAdicionalForm()

        if action == 'editar' and gastoAdicional_id:
            gastoAdicional = get_object_or_404(GastoAdicional, id=gastoAdicional_id)
            form = GastoAdicionalForm(instance=gastoAdicional)
            return render(request, 'ASISTENTE/create_gasto_adicional.html', {
                'gastosAdicionales': gastosAdicionales,
                'recepcion_facturas': recepcion_facturas,  # Pasar la nueva lista a la plantilla
                'form': form,
                'action': action,
                'gastoAdicional_id': gastoAdicional_id,
            })
        
        elif action == 'detalles' and gastoAdicional_id:
            gastoAdicional_instance = get_object_or_404(GastoAdicional, id=gastoAdicional_id)
            return render(request, 'ASISTENTE/detalles_gasto_adicional.html', {
                'gastoAdicional': gastoAdicional_instance,
            })
        
        return render(request, 'ASISTENTE/create_gasto_adicional.html', {
            'gastosAdicionales': gastosAdicionales,
            'recepcion_facturas': recepcion_facturas,  # Pasar la nueva lista a la plantilla
            'form': form,
            'action': action,
            'gastoAdicional_id': gastoAdicional_id,
        })
    
    return HttpResponseNotAllowed(['GET', 'POST'])


def listado_solicitudes(request):
    """
    Muestra la tabla con todas las facturas (solicitudes).
    """
    # Obtén todos los registros de Factura (o filtra según tu lógica)
    recepcion_facturas = GastoAdicional.objects.all()
    
    # Renderiza el template listado_solicitudes.html
    # y envía el queryset en el contexto.
    return render(request, 'ASISTENTE/listado_solicitudes.html', {
        'recepcion_facturas': recepcion_facturas
    })


def registro_gasto_adicional(request, factura_id):
    factura = GastoAdicional.objects.get(pk=factura_id)
    if request.method == 'POST':
        form = GastoAdicionalForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('ASISTENTE/listado_gastos_adicionales')
    else:
        # autocompletar datos del form con la info de la factura
        initial_data = {
            'chofer': factura.chofer,
            'placa': factura.placa,
            'ruta': factura.ruta,
            'montoRecarga': factura.montoRecarga,  # Ejemplo
        }
        form = GastoAdicionalForm(initial=initial_data)

    context = {
        'form': form,
        'factura': factura,
    }
    return render(request, 'ASISTENTE/registro_gasto_adicional.html', context)


def listado_gastos_adicionales(request):
    """
    Muestra el listado final de los gastos adicionales registrados.
    """
    # Obtén todos los registros de GastoAdicional
    gastosAdicionales = GastoAdicional.objects.all()
    
    # Renderiza el template listado_gastos_adicionales.html
    # y envía el queryset en el contexto.
    return render(request, 'ASISTENTE/listado_gastos_adicionales.html', {
        'gastosAdicionales': gastosAdicionales
    })


def FacturaCombustibleController(request, action=None, facturaCombustible_id=None):
    if request.method == 'POST':
        # Crear un nuevo camión
        if action == 'crear':
            form = FacturaCombustibleForm(request.POST,request.FILES)
            if form.is_valid():
                form.save()
                return redirect('facturaCombustible')

        # Eliminar un camión existente
        elif action == 'eliminar' and facturaCombustible_id:
            facturaCombustible = get_object_or_404(FacturaCombustible, id=facturaCombustible_id)
            facturaCombustible.delete()
            return redirect('facturaCombustible')

        else:
            return HttpResponseNotAllowed(['POST'])

    # Mostrar el formulario y lista de camiones
    if request.method == 'GET':
        facturasCombustibles = FacturaCombustible.objects.all()
        form = FacturaCombustibleForm()

        # Si es para editar, carga el camión en el formulario
        if action == 'editar' and facturaCombustible_id:
            facturaCombustible = get_object_or_404(FacturaCombustible, id=facturaCombustible_id)
            form = FacturaCombustibleForm(instance=facturaCombustible)
            return render(request, 'CHOFER/factura_combustible.html', {
                'facturasCombustible': facturasCombustibles,
                'form': form,
                'action': action,
                'facturaCombustible_id': facturaCombustible_id,
            })
        
        elif action == 'detalles' and facturaCombustible_id:
            facturaCombustible_instance = get_object_or_404(FacturaCombustible, id=facturaCombustible_id)
            return render(request, 'CHOFER/detalles_factura_combustible.html', {
                'facturaCombustible': facturaCombustible_instance,  # Corregido el diccionario de contexto
            })
        
        return render(request, 'CHOFER/factura_combustible.html', {
            'facturasCombustibles': facturasCombustibles,
            'form': form,
            'action': action,
            'facturaCombustible_id': facturaCombustible_id,
        })
    
    
    return HttpResponseNotAllowed(['GET', 'POST'])


def facturas_recibidas(request):
    # Obtener todas las facturas de combustible
    facturas_combustibles = FacturaCombustible.objects.all()

    return render(request, 'JEFE_DESPACHO/facturaRecibida.html', {
        'facturas_combustibles': facturas_combustibles  # Nombre de variable claro y consistente
    })




def recepcion_facturas(request):
    # Filtrar registros específicos si es necesario
    recepcion_facturas = FacturaCombustible.objects.all()

    return render(request, 'ASISTENTE/recepcion_facturas.html', {
        'recepcion_facturas': recepcion_facturas  # Nombres claros para evitar errores
    })


def aprobacion_solicitud(request):
    combus_extra_choferes = CombusExtraChofer.objects.all()
    return render(request, 'ASISTENTE/aprobacion_solicitud.html', {
        'combus_extra_choferes': combus_extra_choferes
    })


from .models import RechazoSoliCombus
def cambiar_estado_solicitud(request, solicitud_id, estado):
    solicitud = get_object_or_404(CombusExtraChofer, id=solicitud_id)

    if solicitud.estado != 'En proceso':
        messages.info(request, 'Esta solicitud ya fue revisada.')
        return redirect('combus_extra_choferes')

    if estado == 'Rechazado':
        motivo = request.POST.get('motivo')
        if not motivo:
            messages.error(request, 'Debe indicar el motivo del rechazo.')
            return redirect('combus_extra_choferes')

        RechazoSoliCombus.objects.create(
            solicitud=solicitud,
            motivo=motivo
        )

    solicitud.estado = estado
    solicitud.fecha_revision = now()
    solicitud.save()

    messages.success(request, f'Solicitud {estado}.')
    return redirect('combus_extra_choferes')



def TransferenciaPagadaController(request, action=None, transferenciaPagada_id=None):
    if request.method == 'POST':
        # Crear un nuevo camión
        if action == 'crear':
            form = TransferenciaPagadaForm(request.POST,request.FILES)
            if form.is_valid():
                form.save()
                return redirect('transferenciaPagada')

        # Eliminar un camión existente
        elif action == 'eliminar' and transferenciaPagada_id:
            transferenciaPagada = get_object_or_404(TransferenciaPagada, id=transferenciaPagada_id)
            transferenciaPagada.delete()
            return redirect('transferenciaPagada')

        else:
            return HttpResponseNotAllowed(['POST'])

    # Mostrar el formulario y lista de camiones
    if request.method == 'GET':
        transferenciasPagadas = GastoAdicional.objects.all()
        recepcion_facturas = TransferenciaPagada.objects.all() 
        form = TransferenciaPagadaForm()

        # Si es para editar, carga el camión en el formulario
        if action == 'editar' and transferenciaPagada_id:
            transferenciaPagada = get_object_or_404(TransferenciaPagada, id=transferenciaPagada_id)
            form = TransferenciaPagadaForm(instance=transferenciaPagada)
            return render(request, 'ASISTENTE/transferencia_pagada.html', {
                'transferenciasPagadas': transferenciasPagadas,
                'form': form,
                'action': action,
                'transferenciaPagada_id': transferenciaPagada_id,
            })
        
        elif action == 'detalles' and transferenciaPagada_id:
            transferenciaPagada_instance = get_object_or_404(TransferenciaPagada, id=transferenciaPagada_id)
            return render(request, 'ASISTENTE/transferencia_pagada.html', {
                'transferenciaPagada': transferenciaPagada_instance,  # Corregido el diccionario de contexto
            })
        
        return render(request, 'ASISTENTE//transferencia_pagada.html', {
            'transferenciasPagadas': transferenciasPagadas,
            'recepcion_facturas': recepcion_facturas,
            'form': form,
            'action': action,
            'transferenciaPagada_id': transferenciaPagada_id,
        })
    
    
    return HttpResponseNotAllowed(['GET', 'POST'])

from smtplib import SMTPException
from django.http import HttpResponseNotAllowed, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView
from django.core.mail import send_mail
from django.contrib import messages
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from io import BytesIO
from datetime import datetime, timezone
from .forms import ApplicantForm, PostulanteDocumentosForm, PostulanteForm
from .models import Applicant, ExamenMedico, Postulante
from transporte_verito import settings
import logging

def PostulanteController(request, action=None, postulante_id=None):
    if request.method == 'POST':
        # Crear un nuevo camión
        if action == 'crear':
            form = PostulanteForm(request.POST, request.FILES)
            if form.is_valid():
                postulante = form.save(commit=False)
                postulante.estado = 'primera_pendiente'  # Set the default state explicitly
                postulante.save()
                return redirect('postulante')
            else:
                # Si el formulario no es válido, imprime los errores en la consola
                print("Errores del formulario:", form.errors)
                # Y vuelve a renderizar la página con los errores
                return render(request, 'AGENCIA/list_and_create_postulantes.html', {
                    'postulantes': Postulante.objects.all(),
                    'form': form,
                    'action': action,
                })

        # Eliminar un camión existente
        elif action == 'eliminar' and postulante_id:
            postulante = get_object_or_404(Postulante, id=postulante_id)
            postulante.delete()
            postulantes = Postulante.objects.all()
            return render(request, 'ASISTENTE/sendpostulante.html', {
            'postulantes': postulantes,
        })
        
        elif action == 'rechazar' and postulante_id:
            postulante = get_object_or_404(Postulante, id=postulante_id)
            postulante.estado = "primera_rechazada"
            postulante.save()
            postulantes = Postulante.objects.all()
            return render(request, 'ASISTENTE/sendpostulante.html', {
            'postulantes': postulantes,
        })
        
        elif action == 'rechazar_segunda' and postulante_id:
            postulante = get_object_or_404(Postulante, id=postulante_id)
            postulante.estado = "segunda_rechazada"
            postulante.save()
            postulantes = Postulante.objects.all()
            return render(request, 'GERENTE/documentspostulante.html', {
            'postulantes': postulantes,
        })
        
        elif action == 'rechazar_tercera' and postulante_id:
            postulante = get_object_or_404(Postulante, id=postulante_id)
            postulante.estado = "rechazar_tercera"
            postulante.save()
            postulantes = Postulante.objects.all()
            return render(request, 'JefeDeSeguridad/clinicapostulante.html', {
            'postulantes': postulantes,
        })
        
        elif action == 'rechazar_cuarta' and postulante_id:
            postulante = get_object_or_404(Postulante, id=postulante_id)
            postulante.estado = "rechazar_cuarta"
            postulante.save()
            postulantes = Postulante.objects.all()
            return render(request, 'GERENTE/registropostulante.html', {
            'postulantes': postulantes,
        })

        else:
            return HttpResponseNotAllowed(['POST'])

    # Mostrar el formulario y lista de camiones
    if request.method == 'GET':
        postulantes = Postulante.objects.all()
        applicants = Applicant.objects.all()
        form = PostulanteForm()

        # Si es para editar, carga el camión en el formulario
        if action == 'editar' and postulante_id:
            postulante = get_object_or_404(Postulante, id=postulante_id)
            form = PostulanteForm(instance=postulante)
            return render(request, 'AGENCIA/RegistroPostulante/list_and_create_postulantes.html', {
                'postulantes': postulantes,
                'applicants': applicants,
                'form': form,
                'action': action,
                'postulante_id': postulante_id,
            })
        
        elif action == 'detalles' and postulante_id:
            postulante = get_object_or_404(Postulante, id=postulante_id)
            form = PostulanteForm(instance=postulante)
            return render(request, 'ASISTENTE/detalles_postulante.html', {
                'postulante': postulante,
                'form': form  # Corregido el diccionario de contexto
            })
        
        elif action == 'detalles_segunda' and postulante_id:
            postulante = get_object_or_404(Postulante, id=postulante_id)
            form = PostulanteForm(instance=postulante)
            return render(request, 'GERENTE/detalles_postulante.html', {
                'postulante': postulante,
                'form': form  # Corregido el diccionario de contexto
            })
        
        elif action == 'detalles_clinica' and postulante_id:
            postulante = get_object_or_404(Postulante, id=postulante_id)
            form = PostulanteForm(instance=postulante)
            return render(request, 'JefeDeSeguridad/detalles_postulante.html', {
                'postulante': postulante,
                'form': form  # Corregido el diccionario de contexto
            })
        
        elif action == 'detalles_registro' and postulante_id:
            postulante = get_object_or_404(Postulante, id=postulante_id)
            form = PostulanteForm(instance=postulante)
            return render(request, 'GERENTE/detalles_registro_postulante.html', {
                'postulante': postulante,
                'form': form  # Corregido el diccionario de contexto
            })
        
        return render(request, 'AGENCIA/list_and_create_postulantes.html', {
            'postulantes': postulantes,
            'applicants': applicants,
            'form': form,
            'action': action,
            'postulante_id': postulante_id,
        })
    
    return HttpResponseNotAllowed(['GET', 'POST'])

logger = logging.getLogger(__name__)  # Agregar logging para ver errores

def aprobar_postulante(request, postulante_id):
    postulante = get_object_or_404(Postulante, id=postulante_id)
    
    if postulante.estado == "primera_aprobada":
        return redirect('postulante')

    # Actualizar el estado
    postulante.estado = "primera_aprobada"
    postulante.save()

    # Enviar correo
    asunto = "Postulación como chofer de la empresa Transporte Verito"
    mensaje = f"Hola {postulante.nombres},\n\nSu PRIMER CONTROL HA SIDO APROBADO, ahora continuará con el SEGUNDO CONTROL. Por favor, adjuntar los siguientes requerimientos:\n\n- Referencias de Trabajos Anteriores (PDF o Word)\n- Record de Conducción - Verificable en MTC (PDF o Word)\n- Historial de Papeletas (Imagen)\n- Ceritificado de Antecedentes Penales (PDF o Word)"
    remitente = settings.EMAIL_HOST_USER
    destinatario = [postulante.correo]

    try:
        send_mail(asunto, mensaje, remitente, destinatario)
        logger.info(f"Correo enviado a {postulante.correo}")
        postulantes = Postulante.objects.all()
        return render(request, 'ASISTENTE/PostulantePrimera.html', {
            'postulantes': postulantes,
        })
    except Exception as e:
        logger.error(f"Error al enviar correo: {e}")
        return JsonResponse({"success": False, "error": f"No se pudo enviar el correo: {e}"}, status=500)
    
def send_postulante(request):
    postulantes = Postulante.objects.all()
    return render(request, 'ASISTENTE/PostulantePrimera.html', {
            'postulantes': postulantes,
    })

def subir_documentos_postulante(request):
    if request.method == 'POST':
        postulante_id = request.POST.get('postulante_id')
        postulante = get_object_or_404(Postulante, id=postulante_id)
        
        # Manejar la subida de archivos
        referencias_trabajos = request.FILES.get('referencias_trabajos')
        record_conduccion = request.FILES.get('record_conduccion')
        historial_papeletas = request.FILES.get('historial_papeletas')
        antecedentes_penales = request.FILES.get('antecedentes_penales')
        
        if referencias_trabajos:
            postulante.referencias_trabajos = referencias_trabajos
        if record_conduccion:
            postulante.record_conduccion = record_conduccion
        if historial_papeletas:
            postulante.historial_papeletas = historial_papeletas
        if antecedentes_penales:
            postulante.antecedentes_penales = antecedentes_penales
            
        postulante.estado = "segunda_pendiente"
        postulante.save()
        return redirect('documentspostulante')  # O la URL que prefieras después de guardar
        
    postulantes = Postulante.objects.all()
    return render(request, 'GERENTE/documentspostulante.html', {
        'postulantes': postulantes
    })

def aprobar_documentos_postulante(request, postulante_id):
    postulante = get_object_or_404(Postulante, id=postulante_id)
    
    if postulante.estado == "segunda_aprobada":
        return redirect('postulante')

    # Actualizar el estado
    postulante.estado = "segunda_aprobada"
    postulante.save()

    # Enviar correo
    asunto = "Postulación como chofer de la empresa Transporte Verito"
    mensaje = f"Hola {postulante.nombres},\n\nSu SEGUNDO CONTROL HA SIDO APROBADO, ahora continuará con el TERCER CONTROL."
    remitente = settings.EMAIL_HOST_USER
    destinatario = [postulante.correo]

    try:
        send_mail(asunto, mensaje, remitente, destinatario)
        logger.info(f"Correo enviado a {postulante.correo}")
        postulantes = Postulante.objects.all()
        return render(request, 'GERENTE/documentspostulante.html', {
            'postulantes': postulantes,
        })
    except Exception as e:
        logger.error(f"Error al enviar correo: {e}")
        return JsonResponse({"success": False, "error": f"No se pudo enviar el correo: {e}"}, status=500)
    
def generar_primer_reporte_pdf(request):
    # Crear el objeto BytesIO para el PDF
    buffer = BytesIO()
    
    # Crear el documento PDF con orientación horizontal y márgenes ajustados
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=landscape(letter),
        rightMargin=20,
        leftMargin=20,
        topMargin=30,
        bottomMargin=30
    )
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
        alignment=1  # Centrado
    )
    
    # Título del reporte
    title = Paragraph("Reporte de Postulantes (1ra Etapa) - Transporte Verito", title_style)
    elements.append(title)
    
    # Fecha del reporte
    date_style = ParagraphStyle(
        'DateStyle',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=20,
        alignment=1
    )
    date_text = Paragraph(f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", date_style)
    elements.append(date_text)
    
    # Obtener postulantes aprobados
    postulantes_aprobados = Postulante.objects.filter(estado="primera_aprobada")
    
    # Crear datos para la tabla con nombres más cortos para las columnas
    data = [[
        '#', 
        'Nombres', 
        'Apellidos', 
        'Celular',
        'Correo',
        'DNI\nFront.',
        'DNI\nPost.',
        'Tipo\nLic.',
        'Formato',
        'Lic.\nFront.',
        'Lic.\nPost.',
        'Lic.\nElect.',
        'Exp.'
    ]]
    
    # Estilo para el contenido de las celdas
    cell_style = ParagraphStyle(
        'CellStyle',
        parent=styles['Normal'],
        fontSize=8,
        wordWrap='CJK',
        alignment=1
    )
    
    for idx, postulante in enumerate(postulantes_aprobados, 1):
        # Formatear el correo para que se ajuste mejor
        correo = Paragraph(postulante.correo, cell_style)
        
        data.append([
            idx,
            Paragraph(postulante.nombres, cell_style),
            Paragraph(postulante.apellidos, cell_style),
            postulante.numero_celular,
            correo,
            'Verificado' if postulante.dni_frontal else 'No disp.',
            'Verificado' if postulante.dni_posterior else 'No disp.',
            Paragraph(postulante.tipo_licencia, cell_style),
            Paragraph(postulante.tipo_licencia_formato, cell_style),
            'Verificado' if postulante.licencia_frontal else 'No disp.',
            'Verificado' if postulante.licencia_posterior else 'No disp.',
            'Verificado' if postulante.licencia_electronica else 'No disp.',
            'Verificado' if postulante.experiencia else 'No disp.'
        ])
    
    # Ajustar los anchos de columna para una mejor distribución
    table = Table(data, colWidths=[
        30,   # #
        80,   # Nombres
        80,   # Apellidos
        60,   # Celular
        120,  # Correo (más espacio para emails largos)
        40,   # DNI Frontal
        40,   # DNI Posterior
        40,   # Tipo Licencia
        50,   # Formato Licencia
        40,   # Licencia Frontal
        40,   # Licencia Posterior
        40,   # Licencia Electrónica
        40    # Experiencia
    ], rowHeights=[25] * (len(data)))  # Aumentar altura de filas
    
    # Estilo mejorado de la tabla
    table.setStyle(TableStyle([
        # Encabezado
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2C3E50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        # Cuerpo de la tabla
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#FFFFFF')),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        # Espaciado de celdas
        ('TOPPADDING', (0, 0), (-1, -1), 8),  # Aumentado
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),  # Aumentado
        ('LEFTPADDING', (0, 0), (-1, -1), 3),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3),
        # Alternar colores de fila
        *[('BACKGROUND', (0, i), (-1, i), colors.HexColor('#F8F9F9')) 
          for i in range(2, len(data), 2)]
    ]))
    
    # Crear un contenedor para la tabla y el resumen
    elements.append(Table([[table]], colWidths=[700]))
    
    # Estadísticas específicas para la primera etapa
    total_postulantes = postulantes_aprobados.count()
    with_dni = postulantes_aprobados.filter(dni_frontal__isnull=False, dni_posterior__isnull=False).count()
    with_license = postulantes_aprobados.filter(licencia_frontal__isnull=False, licencia_posterior__isnull=False).count()
    with_experience = postulantes_aprobados.filter(experiencia__isnull=False).count()
    
    # Crear tabla para el resumen con alineación a la izquierda
    summary_data = [
        ['Resumen de postulantes'],
        [f'• Total de postulantes aprobados en primera etapa: {total_postulantes}'],
        [f'• Postulantes con DNI completo: {with_dni}'],
        [f'• Postulantes con licencia completa: {with_license}'],
        [f'• Postulantes con experiencia verificada: {with_experience}']
    ]
    
    summary_table = Table(summary_data, colWidths=[700])
    summary_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 20),  # Padding izquierdo para alinear con la tabla
    ]))
    
    # Agregar espaciado entre la tabla y el resumen
    elements.append(Spacer(1, 20))
    elements.append(summary_table)
    
    # Construir PDF
    doc.build(elements)
    
    # Obtener el valor del PDF del buffer
    pdf = buffer.getvalue()
    buffer.close()
    
    # Crear la respuesta HTTP
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Reporte Postulantes - 1ra Etapa.pdf"'
    response.write(pdf)
    
    return response
    
def generar_segundo_reporte_pdf(request):
    # Crear el objeto BytesIO para el PDF
    buffer = BytesIO()
    
    # Crear el documento PDF con márgenes personalizados reducidos
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=20,
        leftMargin=20,
        topMargin=30,
        bottomMargin=30
    )
    elements = []
    
    # Estilos mejorados
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
        alignment=1  # Centrado
    )
    
    # Título del reporte
    title = Paragraph("Reporte de Postulantes (2da Etapa) - Transporte Verito", title_style)
    elements.append(title)
    
    # Fecha del reporte con estilo mejorado
    date_style = ParagraphStyle(
        'DateStyle',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=20,
        alignment=2  # Alineación derecha
    )
    date_text = Paragraph(f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", date_style)
    elements.append(date_text)
    
    # Obtener postulantes aprobados
    postulantes_aprobados = Postulante.objects.filter(estado="segunda_aprobada")
    
    # Definir anchos de columna más compactos
    col_widths = [
        15,     # #
        65,     # Nombres
        65,     # Apellidos
        45,     # Tipo de Licencia
        50,     # Formato de Licencia
        75,     # Referencias
        60,     # Record
        60,     # Papeletas
        60      # Antecedentes
    ]
    
    # Crear datos para la tabla con encabezados más compactos
    headers = [
        '#',
        'Nombres',
        'Apellidos',
        'Tipo\nLicencia',
        'Formato\nLicencia',
        'Referencias\nTrabajo',
        'Record\nConducción',
        'Historial\nPapeletas',
        'Antecedentes\nPenales'
    ]
    
    data = [headers]
    
    for idx, postulante in enumerate(postulantes_aprobados, 1):
        data.append([
            idx,
            Paragraph(postulante.nombres, styles['Normal']),
            Paragraph(postulante.apellidos, styles['Normal']),
            postulante.tipo_licencia,
            postulante.tipo_licencia_formato,
            'Verificado' if postulante.referencias_trabajos else 'No disponible',
            'Verificado' if postulante.record_conduccion else 'No disponible',
            'Verificado' if postulante.historial_papeletas else 'No disponible',
            'Verificado' if postulante.antecedentes_penales else 'No disponible'
        ])
    
    # Crear tabla con anchos personalizados
    table = Table(data, colWidths=col_widths)
    
    # Estilo de tabla mejorado con fuentes más pequeñas
    table.setStyle(TableStyle([
        # Estilo del encabezado
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2C3E50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),  # Tamaño reducido para encabezados
        
        # Espaciado y padding reducidos
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        
        # Estilo del cuerpo
        ('BACKGROUND', (0, 1), (-1, -1), colors.Color(0.95, 0.95, 0.95)),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),  # Tamaño reducido para el contenido
        ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        
        # Bordes y líneas
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.HexColor('#2C3E50')),
        
        # Espaciado entre filas reducido
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
    ]))
    
    total_postulantes = postulantes_aprobados.count()
    total_style = ParagraphStyle(
        'Total',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#2C3E50'),
        fontName='Helvetica-Bold'
    )
    total_text = Paragraph(f"Total de postulantes aprobados: {total_postulantes}", total_style)
    
    total_width = sum(col_widths)
    
    total_table = Table([[total_text]], colWidths=[total_width])
    total_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 20),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    
    elements.append(table)
    elements.append(total_table)
    
    # Construir PDF
    doc.build(elements)
    
    # Obtener el valor del PDF del buffer
    pdf = buffer.getvalue()
    buffer.close()
    
    # Crear la respuesta HTTP
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Reporte Postulantes - 2da Etapa.pdf"'
    response.write(pdf)
    
    return response

def seleccionar_clinica_postulante(request):
    postulantes = Postulante.objects.all()

    if request.method == 'POST':
        postulante_id = request.POST.get('postulante_id')
        clinica = request.POST.get('clinica')
        examenes_seleccionados = request.POST.getlist('examenes_requeridos')

        if postulante_id and clinica:
            try:
                postulante = Postulante.objects.get(id=postulante_id)
                
                # Actualizar la clínica
                postulante.clinica = clinica
                
                # Actualizar el estado a tercera etapa pendiente
                postulante.estado = 'tercera_pendiente'
                
                # Guardar los cambios básicos
                postulante.save()
                
                # Limpiar exámenes anteriores si existen
                postulante.examenes_requeridos.clear()
                
                # Agregar los nuevos exámenes seleccionados
                for examen_tipo in examenes_seleccionados:
                    examen, created = ExamenMedico.objects.get_or_create(
                        tipo=examen_tipo
                    )
                    postulante.examenes_requeridos.add(examen)
                
                messages.success(request, 'Clínica y exámenes médicos registrados exitosamente.')
                return redirect('clinicapostulante')
            
            except Postulante.DoesNotExist:
                messages.error(request, 'Postulante no encontrado.')
            except Exception as e:
                messages.error(request, f'Error al procesar el registro: {str(e)}')
        else:
            messages.error(request, 'Por favor complete todos los campos requeridos.')

    return render(request, 'JefeDeSeguridad/clinicapostulante.html', {
        'postulantes': postulantes,
    })

def aprobar_clinica_postulante(request, postulante_id):
    postulante = get_object_or_404(Postulante, id=postulante_id)
    
    if postulante.estado == "tercera_aprobada":
        return redirect('postulante')

    # Actualizar el estado
    postulante.estado = "tercera_aprobada"
    postulante.save()

    # Enviar correo
    asunto = "Postulación como chofer de la empresa Transporte Verito"
    mensaje = f"Hola {postulante.nombres},\n\nSu TERCER CONTROL HA SIDO APROBADO, ahora continuará con el CUARTO CONTROL."
    remitente = settings.EMAIL_HOST_USER
    destinatario = [postulante.correo]

    try:
        send_mail(asunto, mensaje, remitente, destinatario)
        logger.info(f"Correo enviado a {postulante.correo}")
        postulantes = Postulante.objects.all()
        return render(request, 'JefeDeSeguridad/clinicapostulante.html', {
            'postulantes': postulantes,
        })
    except Exception as e:
        logger.error(f"Error al enviar correo: {e}")
        return JsonResponse({"success": False, "error": f"No se pudo enviar el correo: {e}"}, status=500)

def generar_tercer_reporte_pdf(request):
    buffer = BytesIO()
    
    # Crear el documento PDF con márgenes más pequeños para dar más espacio
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(letter),  # Cambiado a orientación horizontal
        rightMargin=25,
        leftMargin=25,
        topMargin=40,
        bottomMargin=40
    )
    elements = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=1
    )
    
    title = Paragraph("Reporte de Postulantes de Clínica (3ra Etapa) - Transporte Verito", title_style)
    elements.append(title)
    
    date_style = ParagraphStyle(
        'DateStyle',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=20,
        alignment=2
    )
    date_text = Paragraph(f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", date_style)
    elements.append(date_text)
    
    postulantes_aprobados = Postulante.objects.filter(estado="tercera_aprobada")
    
    # Anchos de columna ajustados para incluir exámenes
    col_widths = [
        25,     # #
        70,     # Nombres
        70,     # Apellidos
        45,     # Tipo Licencia
        50,     # Formato Licencia
        60,     # Licencia Frontal
        60,     # Licencia Posterior
        60,     # Licencia Electrónica
        80,     # Clínica
        120     # Exámenes Requeridos (nueva columna más ancha)
    ]
    
    headers = [
        '#',
        'Nombres',
        'Apellidos',
        'Tipo\nLicencia',
        'Formato\nLicencia',
        'Licencia\nFrontal',
        'Licencia\nPosterior',
        'Licencia\nElectrónica',
        'Clínica',
        'Exámenes\nRequeridos'
    ]
    
    data = [headers]
    
    for idx, postulante in enumerate(postulantes_aprobados, 1):
        examenes = postulante.examenes_requeridos.all()
        examenes_texto = "\n".join([examen.get_tipo_display() for examen in examenes]) if examenes else "No asignados"
        
        examenes_paragraph = Paragraph(examenes_texto, ParagraphStyle(
            'ExamenesStyle',
            parent=styles['Normal'],
            fontSize=8,
            leading=10,
            alignment=1
        ))
        
        data.append([
            idx,
            Paragraph(postulante.nombres, styles['Normal']),
            Paragraph(postulante.apellidos, styles['Normal']),
            postulante.tipo_licencia,
            postulante.tipo_licencia_formato,
            'Verificado' if postulante.licencia_frontal else 'No disponible',
            'Verificado' if postulante.licencia_posterior else 'No disponible',
            'Verificado' if postulante.licencia_electronica else 'No disponible',
            postulante.get_clinica_display() if postulante.clinica else 'No asignada',
            examenes_paragraph
        ])
    
    table = Table(data, colWidths=col_widths, repeatRows=1)
    
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2C3E50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),  

        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        
        ('BACKGROUND', (0, 1), (-1, -1), colors.Color(0.95, 0.95, 0.95)),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor('#2C3E50')),
        
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
    ]))
    
    total_postulantes = postulantes_aprobados.count()
    total_style = ParagraphStyle(
        'Total',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor('#2C3E50'),
        fontName='Helvetica-Bold'
    )
    total_text = Paragraph(f"Total de postulantes en evaluación clínica: {total_postulantes}", total_style)
    
    total_width = sum(col_widths)
    total_table = Table([[total_text]], colWidths=[total_width])
    total_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 15),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    
    elements.append(table)
    elements.append(total_table)
    
    doc.build(elements)
    
    pdf = buffer.getvalue()
    buffer.close()
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Reporte de Postulantes Clinica - 3ra Etapa.pdf"'
    response.write(pdf)
    
    return response

def examenpostulante(request):
    postulantes = Postulante.objects.all().prefetch_related('examenes_requeridos')
    return render(request, 'CoordinadorDeResultados/examenpostulante.html', {'postulantes': postulantes})

def registrar_resultados_medicos(request, postulante_id):
    postulante = get_object_or_404(Postulante, id=postulante_id)
    examenes = postulante.examenes_requeridos.all()
    
    try:
        # Procesar cada archivo subido según el examen
        for examen in examenes:
            archivo_campo = f'resultado_{examen.tipo}'
            if archivo_campo in request.FILES:
                # Mapeo de tipos de examen a campos del modelo
                campo_mapping = {
                    'medicina_general': 'resultado_medicina_general',
                    'toxicologico': 'resultado_toxicologico',
                    'oftalmologia': 'resultado_oftalmologia',
                    'otorrinolaringologia': 'resultado_otorrinolaringologia'
                }
                
                # Asignar el archivo al campo correspondiente del modelo
                if examen.tipo in campo_mapping:
                    setattr(postulante, campo_mapping[examen.tipo], request.FILES[archivo_campo])

        # Actualizar el estado del postulante
        postulante.estado = 'cuarta_pendiente'
        postulante.save()
        
        messages.success(request, 'Resultados médicos adjuntados exitosamente.')
        return redirect('examenpostulante')
        
    except Exception as e:
        messages.error(request, f'Error al registrar los resultados médicos: {str(e)}')
        return redirect('examenpostulante')

def registro_postulante(request):
    postulantes = Postulante.objects.all()
    return render(request, 'GERENTE/registropostulante.html', {
            'postulantes': postulantes,
    })

def aprobar_examen_postulante(request, postulante_id):
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Método no permitido"}, status=405)

    postulante = get_object_or_404(Postulante, id=postulante_id)
    
    if postulante.estado == "cuarta_aprobada":
        return JsonResponse({"success": False, "error": "Ya ha sido aprobado"}, status=400)

    # Actualizar el estado
    postulante.estado = "cuarta_aprobada"
    postulante.save()

    # Enviar correo
    asunto = "Postulación como chofer de la empresa Transporte Verito"
    mensaje = f"Hola {postulante.nombres},\n\nSu CUARTO CONTROL HA SIDO APROBADO, ahora continuará con el QUINTO CONTROL."
    remitente = settings.EMAIL_HOST_USER
    destinatario = [postulante.correo]

    try:
        send_mail(asunto, mensaje, remitente, destinatario)
        logger.info(f"Correo enviado a {postulante.correo}")
        postulantes = Postulante.objects.all()
        return render(request, 'GERENTE/registropostulante.html', {
            'postulantes': postulantes,
        })
    except Exception as e:
        logger.error(f"Error inesperado: {e}")
        return JsonResponse({"success": False, "error": "Error inesperado"}, status=500)

def generar_cuarto_reporte_pdf(request):
    buffer = BytesIO()
    
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(letter),
        rightMargin=25,
        leftMargin=25,
        topMargin=30,
        bottomMargin=30
    )
    elements = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,  # Reducido para mejor ajuste
        spaceAfter=20,
        alignment=1
    )
    
    title = Paragraph("Reporte de Postulantes APROBADOS (4ta Etapa) - Transporte Verito", title_style)
    elements.append(title)
    
    date_style = ParagraphStyle(
        'DateStyle',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=15,
        alignment=2
    )
    date_text = Paragraph(f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", date_style)
    elements.append(date_text)
    
    postulantes_aprobados = Postulante.objects.filter(estado="cuarta_aprobada")
    
    col_widths = [
        20, 50, 50, 40, 40, 50, 50, 50, 60, 80, 50, 55, 60, 60
    ]
    
    headers = [
        '#', 'Nombres', 'Apellidos', 'Tipo\nLicencia', 'Formato\nLicencia', 'Licencia\nFrontal',
        'Licencia\nPosterior', 'Licencia\nElectrónica', 'Clínica', 'Exámenes\nRequeridos',
        'Medicina\nGeneral', 'Toxicológico', 'Oftalmología', 
        'Otorrinola-\nringología'
    ]
    
    data = [headers]
    
    text_style = ParagraphStyle(
        'TableText',
        parent=styles['Normal'],
        fontSize=7,  # Reducido para mejor ajuste
        leading=9,
        alignment=1
    )
    
    for idx, postulante in enumerate(postulantes_aprobados, 1):
        examenes = postulante.examenes_requeridos.all()
        examenes_texto = "\n".join([examen.get_tipo_display() for examen in examenes]) if examenes else "No asignados"
        examenes_paragraph = Paragraph(examenes_texto, text_style)
        
        data.append([
            idx,
            Paragraph(postulante.nombres, text_style),
            Paragraph(postulante.apellidos, text_style),
            postulante.tipo_licencia,
            postulante.tipo_licencia_formato,
            'Verificado' if postulante.licencia_frontal else 'No disponible',
            'Verificado' if postulante.licencia_posterior else 'No disponible',
            'Verificado' if postulante.licencia_electronica else 'No disponible',
            postulante.get_clinica_display() if postulante.clinica else 'No asignada',
            examenes_paragraph,
            'Verificado' if postulante.resultado_medicina_general else 'No disponible',
            'Verificado' if postulante.resultado_toxicologico else 'No disponible',
            'Verificado' if postulante.resultado_oftalmologia else 'No disponible',
            'Verificado' if postulante.resultado_otorrinolaringologia else 'No disponible'
        ])
    
    table = Table(data, colWidths=col_widths, repeatRows=1)
    
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2C3E50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),  

        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('TOPPADDING', (0, 0), (-1, 0), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        
        ('BACKGROUND', (0, 1), (-1, -1), colors.Color(0.95, 0.95, 0.95)),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 7),
        ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('LINEBELOW', (0, 0), (-1, 0), 1.5, colors.HexColor('#2C3E50')),
        
        ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
        ('TOPPADDING', (0, 1), (-1, -1), 5),
    ]))
    
    total_postulantes = postulantes_aprobados.count()
    total_text = Paragraph(f"Total de postulantes APROBADOS: {total_postulantes}", text_style)
    total_table = Table([[total_text]], colWidths=[sum(col_widths)])
    total_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    
    elements.append(table)
    elements.append(total_table)
    
    doc.build(elements)
    
    pdf = buffer.getvalue()
    buffer.close()
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Reporte_Postulantes_Aprobados.pdf"'
    response.write(pdf)
    
    return response

def register_applicant(request):
    if request.method == 'POST':
        form = ApplicantForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('postulante')
    else:
        form = ApplicantForm()
    return render(request, 'AGENCIA/RegistroPostulante/form.html', {'form': form})

class ApplicantListView(ListView):
    model = Applicant
    template_name = 'AGENCIA/RegistroPostulante/list.html' #AGENCIA
    context_object_name = 'applicants'

class ApplicantDetailView(DetailView):
    model = Applicant
    template_name = "AGENCIA/RegistroPostulante/detail.html"
    context_object_name = "applicant"