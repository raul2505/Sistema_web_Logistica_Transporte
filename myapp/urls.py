from django.urls import path
from . import views
from .views import role_view
from django.contrib.auth.views import LogoutView
from .views import profile_view, settings_view

urlpatterns = [
    
    #Pagina principal
    path('',views.create_solicitud,name= 'CreateSolicitudServicio'),
    path("logout/", LogoutView.as_view(next_page="login_view"), name="logout"),
    path("Perfil/", profile_view, name="profile"),
    path("Configuraciones/", settings_view, name="settings"),
    
    path('Login/', views.login_view, name='login_view'),
    path('Registrar/', views.register, name='register'),
    path('SolicitudesServicio/',views.solicitudServicio,name = 'SolicitudServicio'),
    
    

    

    #RUTAS PARA MECANICO
    path('mecanicos/', views.MecanicoController, name='addmecanico'),  # Lista de mecánicos
    path('mecanico/crear/<str:action>', views.MecanicoController, name='crear_mecanico'),  # Creación de mecánico
    path('mecanico/eliminar/<str:action>/<int:mecanico_id>/', views.MecanicoController, name='eliminar_mecanico'),  # Eliminación
    path('mecanico/editar/<int:id>/', views.modificar_mecanico, name='editar_mecanico'),  # Edición
    path('mecanico/<int:mecanico_id>/detalles/', views.MecanicoController,{'action': 'detalles'}, name='detalles_mecanico'),  # Detalles


    path('addchofer/',views.add_chofer,name='addchofer'),
    path('chofer/<str:action>/', views.add_chofer, name='chofer_action_simple'),
    path('modificarChofer/<int:id>/',views.modificarChofer,name='modificar_chofer'),
    # Ruta para editar o eliminaun camión (con 'camion_id')
    path('chofer/<str:action>/<int:chofer_id>/', views.add_chofer, name='chofer_action'),
    path('choferes/<int:chofer_id>/detalles/', views.add_chofer, {'action': 'detalles'}, name='detalles_chofer'),
    
    #RUTAS NECESARIAS PARA EL MODELO CAMION
    path('GestionCamion/',views.CamionController ,name = 'camion'),
    path('camiones/<str:action>/', views.CamionController, name='camion_action_simple'),
    path('camiones/<int:camion_id>/detalles/', views.CamionController, {'action': 'detalles'}, name='detalles_camion'),
    path('modificarCamion/<int:id>/',views.modificarCamion,name='modificar'),
    path('camiones/<str:action>/<int:camion_id>/', views.CamionController, name='camion_action'),

    #RUTAS PARA LAS EMPRESAS
    path('AddEmpresa/',views.EmpresaController ,name = 'empresa'),
    path('Empresa/<str:action>/', views.EmpresaController, name='empresa_action_simple'),
    path('Empresas/<int:empresa_id>/detalles/', views.EmpresaController, {'action': 'detalles'}, name='detalles_empresa'),
    path('modificarEmpresa/<int:id>/',views.modificarEmpresa,name='modificar_empresa'),
    path('Empresas/<str:action>/<int:empresa_id>/', views.EmpresaController, name='empresa_action'),

    #RUTAS PARA MOTIVO MANTENIMIENTO
    path('Mantenimientos/',views.ListarMantenimientos,name = 'listar_mantenimientos'),
    path('addmotivo/',views.MotivoMantenimientoController ,name = 'motivo_mantenimiento'),
    path('motivos/<str:action>/', views.MotivoMantenimientoController, name='motivo_action_simple'),
    path('motivos/<int:motivo_id>/detalles/', views.MotivoMantenimientoController, {'action': 'detalles'}, name='detalles_motivo'),
    path('modificarMotivo/<int:id>/',views.modificarMotivoMantenimiento,name='ModificarMotivo'),
    path('motivos/<str:action>/<int:motivo_id>/', views.MotivoMantenimientoController, name='motivo_action'),

    # URLs para Mantenimiento
    path('addmantenimiento/<int:camion_id>/<int:motivo_id>/<str:action>/', views.MantenimientoController, name='mantenimientos'),
    path('mantenimiento/<int:camion_id>/<int:motivo_id>/editar/<int:mantenimiento_id>/', 
     views.modificarMantenimiento, 
     name='mantenimiento_editar'),
    path('camion/<int:camion_id>/registros/', views.Registro_Mantenimiento_Controller, name='ver_registros_mantenimiento'),


    
    path('mantenimientos/<str:action>/', views.MantenimientoController, name='mantenimiento_action_simple'),
    path('mantenimientos/<int:mantenimiento_id>/detalles/', views.MantenimientoController, {'action': 'detalles'}, name='detalles_mantenimiento'),
    path('modificarMantenimiento/<int:id>/', views.modificarMantenimiento, name='modificar_mantenimiento'),
    path('mantenimientos/<str:action>/<int:mantenimiento_id>/', views.MantenimientoController, name='mantenimiento_action'),

    # URLs para MantenimientoDetalle
    
    path('mantenimiento/<int:mantenimiento_id>/detalle/crear/', views.Crear_Detalle_Mantenimiento, name='crear_mantenimiento_detalle'),

    # URLs para Factura
   # Listar facturas de un mantenimiento
    path('mantenimiento/<int:mantenimiento_id>/factura/', views.FacturaController, name='factura_list'),  # Listado de facturas
    path('mantenimiento/<int:mantenimiento_id>/factura/crear/', views.FacturaController, {'action': 'crear'}, name='factura_crear'),  # Crear factura
    path('mantenimiento/<int:mantenimiento_id>/factura/<int:factura_id>/editar/', views.FacturaController, {'action': 'editar'}, name='factura_editar'),  # Editar factura
    path('mantenimiento/<int:mantenimiento_id>/factura/<int:factura_id>/eliminar/', views.FacturaController, {'action': 'eliminar'}, name='factura_eliminar'),

    path('mantenimiento/<int:mantenimiento_id>/factura/<int:factura_id>/detalles/', views.FacturaController, {'action': 'detalles'}, name='factura_detalles'),  # Ver detalles de la factura

    # URLs para FacturaDetalle
    path('facturas/<int:factura_id>/', views.factura_detalle, name='factura_detalle'),
    path('facturas/', views.lista_facturas, name='lista_facturas'),
    path("camiones_en_mantenimiento/", views.camiones_mantenimiento, name="camiones_en_mantenimiento"),
    path('notificaciones/', views.lista_notificaciones, name='lista_notificaciones'),
    path('notificaciones/marcar-leida/<int:notificacion_id>/', views.marcar_notificacion_leida, name='marcar_notificacion_leida'),

    path('RegistrarAlianza/', views.registro_solicitud_alianza, name='registro_solicitud_alianza'),
    path('SeguimientoSolicitudes/', views.seguimiento_solicitud, name='seguimiento_solicitud'),
    path('SeguimientoSolicitudesGerente/', views.seguimiento_solicitud_gerente, name='seguimiento_solicitud_gerente'),
    path('RegistrarContrato/', views.registrar_contrato, name='registrar_contrato'),

    

    path('solicitud/<int:solicitud_id>/<str:estado>/', views.cambiar_estado_solicitud, name='cambiar_estado_solicitud'),

    path('VerContratos/', views.visualizar_contratos, name='visualizar_contratos'),
    path('ContratosRecibidos/', views.contratos_recibidos, name='contratos_recibidos'),
    path('CambiarEstadoContrato/<int:contrato_id>/<str:estado>/', views.cambiar_estado_contrato, name='cambiar_estado_contrato'),


    
    # URLs para HOJA DE RUTA 
    path('hoja-de-ruta/nuevo/<int:chofer_id>/', views.hoja_de_ruta_create, name='hoja_de_ruta_create'),
    path('hojas-de-ruta/', views.listar_hojas, name='hoja_de_ruta_list'),
    path('hoja_de_ruta/<int:pk>/delete/', views.hoja_de_ruta_delete, name='hoja_de_ruta_delete'),
    path('hoja_de_ruta/<int:pk>/update/', views.hoja_de_ruta_update, name='hoja_de_ruta_update'),
    path('hoja_de_ruta/<int:pk>/details/', views.hoja_de_ruta_details, name='hoja_de_ruta_details'),

    #URLs para GUIAS DE REMISION
    path('guias/listar', views.listar_guias, name='listar_guias'),
    path('guia-remision/nueva/<int:hoja_ruta_id>/', views.crear_guia_remision, name='crear_guia_remision'),
    path('mis-guias/', views.listar_guias_chofer, name='listar_guias_chofer'),
    
    path('guias/eliminar/<int:hoja_id>/', views.eliminar_guia, name='eliminar_guia'),
    #path('guias/eliminar/<int:pk>/', views.eliminar_guia, name='eliminar_guia'),

    path('guias/transportista/<int:pk>/pdf/', views.generar_pdf_transportista, name='generar_pdf_transportista'),
    path('guias/remitente/<int:pk>/pdf/', views.generar_pdf_remitente, name='generar_pdf_remitente'),
    #path('obtener_detalles_hoja/<int:hoja_id>/', views.obtener_detalles_hoja, name='obtener_detalles_hoja'),
    
    path('chofer/listado/', views.listado_chofer, name='listado_chofer'),# esto no sirve
    path('enviar-a-chofer/<int:guia_id>/', views.enviar_a_chofer, name='enviar_a_chofer'),#esto no sive
    path('crear-reporte/<int:guia_id>/', views.crear_reporte, name='crear_reporte'),
    path('mis-reportes/', views.listar_reportes_chofer, name='listar_reportes_chofer'),
    path('guias_chofer', views.chofer_dashboard, name='guias'),
    path('todos-los-reportes/', views.listar_todos_los_reportes, name='listar_todos_los_reportes'),
     path('reportes-empresa/', views.listar_reportes_empresa, name='listar_reportes_empresa'),




    #Chofer: Solicitudes de Recarga de Combustible
    path('addCombusExtraChofer/',views.CombusExtraChoferController, name = 'combusExtraChofer'),
    path('combusExtraChoferes/<str:action>/', views.CombusExtraChoferController, name='combus_extra_chofer_action_simple'),

    #Chofer: Estado
    path('chofer/estado', views.estado_solicitud_recarga, name='estado_solicitud_recarga'),

    #Jefe de despacho: Registro de Hojas de Rutas Largas Adicionales
    path('addruta/',views.RutaController ,name = 'rutas'),
    path('rutas/<str:action>/', views.RutaController, name='ruta_action_simple'),

    #Jefe de despacho: Facturas recibidas
    path('jefe_despacho/facturas', views.facturas_recibidas, name='facturas_recibidas'),
    

    #Chofer: Factura de combustible
    path('addFacturaCombustible/',views.FacturaCombustibleController, name = 'facturaCombustible'),
    path('facturasCombustibles/<str:action>/', views.FacturaCombustibleController, name='facturaCombustible_action_simple'),

    path('facturasCombustibles/<str:action>/<int:facturaCombustible_id>/', views.FacturaCombustibleController, name='facturaCombustible_action'),

    #Asistente de gerencia: Registro de gastos adicionales
    path('addGastoAdicional/',views.GastoAdicionalController, name = 'gastoAdicional'),
    path('gastosAdicionales/<str:action>/', views.GastoAdicionalController, name='gastoAdicional_action_simple'),

    path('listado_solicitudes/', views.listado_solicitudes, name='listado_solicitudes'),
    path('registro_gasto_adicional/<int:factura_id>/', views.registro_gasto_adicional, name='registro_gasto_adicional'),
    path('listado_gastos_adicionales/', views.listado_gastos_adicionales, name='listado_gastos_adicionales'),


    #Asistente de gerencia: Aprobacion de solicitudes
    path('addGastoAdicional/facturas_recibidas', views.aprobacion_solicitud, name='combus_extra_choferes'),
    path('solicitud/<int:solicitud_id>/<str:estado>/', views.cambiar_estado_solicitud, name='cambiar_estado_solicitud'),
    #Asistente de gerencia: Recepcion de facturas
    path('addGastoAdicional/recepcion_facturas', views.recepcion_facturas, name='recepcion_facturas'),

    #Asistente de gerencia: Registro Transferencias Pagadas
    path('transferencia_pagada', views.TransferenciaPagadaController, name='transferenciaPagada'),
    path('transferencia_pagada/<str:action>/', views.TransferenciaPagadaController, name='transferencia_pagada_action_simple'),

    #PIERO
    path('RegistroPostulantes/', views.register_applicant, name='register_applicant'),
    path('GestionPostulantes/', views.ApplicantListView.as_view(), name='applicant_list'),
    path('detail/<int:pk>/', views.ApplicantDetailView.as_view(), name='applicant_detail'),

    #POSTULANTE
    path('ListaPostulante/', views.PostulanteController, name = 'postulante'), 

    path('postulantes/<str:action>/', views.PostulanteController, name='postulante_action_simple'),
    path('postulantes/<int:postulante_id>/detalles/', views.PostulanteController, {'action': 'detalles'}, name='detalles_postulante'),
    path('postulantes/<str:action>/<int:postulante_id>/', views.PostulanteController, name='postulante_action'),
    path('aprobar_postulante/<int:postulante_id>/', views.aprobar_postulante, name='aprobar_postulante'),
    
    path('sendpostulante/', views.send_postulante, name='sendpostulante'),

    path('SegundaEtapa/', views.subir_documentos_postulante, name='documentspostulante'),
    path('aprobar_documentos_postulante/<int:postulante_id>/', views.aprobar_documentos_postulante, name='aprobar_documentos_postulante'),
    path('detalles_documentos_postulante/<int:postulante_id>/', views.PostulanteController, {'action': 'detalles_segunda'}, name='detalles_documentos_postulante'),
    path('generar_primer_reporte_pdf/', views.generar_primer_reporte_pdf, name='generar_primer_reporte_pdf'),
    path('generar_segundo_reporte_pdf/', views.generar_segundo_reporte_pdf, name='generar_segundo_reporte_pdf'),

    path('TerceraEtapa/', views.seleccionar_clinica_postulante, name='clinicapostulante'),
    path('detalles_clinica/<int:postulante_id>/', views.PostulanteController, {'action': 'detalles_clinica'}, name='detalles_clinica'),
    path('aprobar_clinica_postulante/<int:postulante_id>/', views.aprobar_clinica_postulante, name='aprobar_clinica_postulante'),
    path('generar_tercer_reporte_pdf/', views.generar_tercer_reporte_pdf, name='generar_tercer_reporte_pdf'),
    
    path('CuartaEtapa/', views.examenpostulante, name='examenpostulante'),
    path('registrar_resultados_medicos/<int:postulante_id>/', views.registrar_resultados_medicos, name='registrar_resultados_medicos'),
    path('aprobar_examen_postulante/<int:postulante_id>/', views.aprobar_examen_postulante, name='aprobar_examen_postulante'),

    path('registropostulante/', views.registro_postulante, name='registropostulante'),
    path('detalles_registro_postulante/<int:postulante_id>/', views.PostulanteController, {'action': 'detalles_registro'}, name='detalles_registro_postulante'),
    path('generar_cuarto_reporte_pdf/', views.generar_cuarto_reporte_pdf, name='generar_cuarto_reporte_pdf'),




    path('choferes/', views.choferes_por_empresa, name='choferes_por_empresa'),
    path('MiCamion/', views.camion_asignado, name='camion_asignado'),
    path('usuarios/', views.listar_usuarios, name='listar_usuarios'),
    path('<str:role>/', views.role_view, name='role_page'),
    
    
     
]