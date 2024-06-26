import funciones_main
import reportes
import ventas
from datetime import datetime
from dateutil.relativedelta import relativedelta

# pip show dateutil
# pip install python-dateutil

# Formato docstring para copiar (esta linea no)
#     '''
#     ==> Recibe
#     <== Devuelve
#     '''


def agregar_usuario(data_in_kwargs, id):
    '''
    Agrega un usuario a la bdd
    ==> Recibe Diccionario
    '''
    print(">>>> Creacion de usuario")
    referencia_usuarios = data_in_kwargs.get("db").get("usuarios")
    referencia_reportes = data_in_kwargs.get("db").get("reportes")
    nombre = funciones_main.alpnum_val("Nombre del usuario: ", data_in_kwargs)
    direccion = funciones_main.alpnum_val(
        "Direccion de domicilio del usuario: ", data_in_kwargs)
    contacto = funciones_main.validar_email_regexp(
        input("Correo electronico del usuario: "), data_in_kwargs, es_validado=True)
    fecha = datetime.now().date()
    fecha = datetime.strftime(fecha, "%d-%m-%Y")

    user_to_fill = {
        "id": id,
        "nombre": nombre,
        "direccion": direccion,
        "contacto": contacto,
        "categoria": "cliente nuevo",
        "categoria gestionada": False,
        "antiguedad" : fecha,
        "servicios" : []
    }    
    finalizo = ventas.contratacion(data_in_kwargs, proviene_agregar_usuario=user_to_fill)
    if finalizo == 0:
        input("> Contratacion cancelada\n [Enter - Finalizar]")
    else:
        referencia_usuarios.append(user_to_fill)
        report_to_fill = {
            "id_usuario": id,
            "soporte": {
                "abiertas": [],
                "cerradas": []
            },
            "reclamaciones": {
                "abiertas": [],
                "cerradas": []
            },
            "sugerencias": [],
            "Cantidad Reportes": 0
        }
        referencia_reportes.append(report_to_fill)
        input("Contratacion exitosa, Bienvenid@ a la familia Claro\n[Enter - Continuar]")
        funciones_main.export_file(data_in_kwargs,"exported_db")


def editar_perfil_usuario(data_in_kwargs):
    '''
    Edita informacion del usuario seleccionado previamente
    ==> Recibe Diccionario
    '''
    op = data_in_kwargs.get("op")
    pos_user = data_in_kwargs.get("pos_user")
    data_in_kwargs = data_in_kwargs.get("data_in_kwargs")
    if op == 1:
        op = "nombre"
    elif op == 2:
        op = "dirección"
    elif op == 3:
        op = "contacto"
    print(f">>>> Editando {op} de usuario")
    nuevo_dato = None
    if op != "contacto":
        while True:
            nuevo_dato = funciones_main.alpnum_val(
                f"Nuevo {op} de usuario ('cancelar' para Cancelar)\n> ", data_in_kwargs)
            if nuevo_dato == "cancelar":
                print("> Cancelar")
                break
            try:
                int(nuevo_dato)
                funciones_main.reportes_txt("Intento de ingreso con valor numerico donde se requeria valor alfanumerico",data_in_kwargs)
                input(
                    f"{op.title()} debe ser alfanumerico\n[Enter - Reintentar]\n")
            except:
                break
    else:
        while True:
            nuevo_dato = funciones_main.alpnum_val(
                f"Nuevo {op} de usuario ('cancelar' para Cancelar)\n> ", data_in_kwargs)
            if funciones_main.validar_email_regexp(nuevo_dato,data_in_kwargs) or nuevo_dato == "cancelar":
                break
            else:
                input(
                    "Ingrese un correo electronico valido\n[Enter - Reintentar]\n")
    if nuevo_dato.lower() == "cancelar":
        print("Cancelando...")
    else:
        data_in_kwargs["db"]["usuarios"][pos_user][op] = nuevo_dato
        print(f"{op.title()} del usuario editado satisfactoriamente...")
        funciones_main.export_file(data_in_kwargs, "exported_db")
        return data_in_kwargs


def editar_categoria(data_in_kwargs):
    '''
    Reasigna la categoria del usuario
    ==> Recibe Diccionario
    <== Devuelve Diccionario
    '''
    pos_user = data_in_kwargs.get("pos_user")
    data_in_kwargs = data_in_kwargs.get("data_in_kwargs")
    print(">>>> Modificando categoria de usuario\nATENCION: MODIFICAR SIN AUTORIZACION ESTE VALOR SIN AUTORIZACION ES SANCIONABLE, ASEGURESE DE TENER EL PERMISO DE SU COORDINADOR PARA ESTO.")
    yo = input("Continuar? (y/n) ")
    if yo == "y":
        while True:
            op = funciones_main.int_val(
                "[1 - Modificar a Cliente Nuevo]\n[2 - Modificar a Cliente Regular]\n[3 - Modificar a Cliente Leal]\n[0 - Cancelar]\n> ", data_in_kwargs)
            if op >= 0 and op <= 3:
                if op != 0:
                    modificadores = ["cliente nuevo",
                                     "cliente regular", "cliente leal"]
                    data_in_kwargs["db"]["usuarios"][pos_user]["categoria"] = modificadores[op-1]
                    data_in_kwargs["db"]["usuarios"][pos_user]["categoria gestionada"] = True
                    funciones_main.export_file(data_in_kwargs, "exported_db")
                    print(f"> Modificacion: {modificadores[op-1].title()}")
                    return data_in_kwargs
                else:
                    print("> Cancelando...")
                    break
            else:
                funciones_main.reportes_txt("Opcion fuera de rango editando usuario",data_in_kwargs)
                input(
                    "Seleccione opcion dentro del rango\n[Enter - Reintentar]")


def eliminar_usuario(data_in_kwargs,pos_user):
    '''
    Elimina al usuario
    ==> Recibe Diccionario
    <== Devuelve Diccionario
    '''
    data = data_in_kwargs["db"]["usuarios"][pos_user]
    if len(data["servicios"]) == 0:
        op = input(
            "PRECAUCION: Esta accion es irreversible\n['BORRAR' para confirmar]\n[Cualquier otro ingreso para abortar]\n> ")
        if op == "BORRAR":
            data_in_kwargs["db"]["usuarios"].pop(pos_user)
            print("Usuario borrado de la base de datos con exito...")
            funciones_main.export_file(data_in_kwargs, "exported_db")
            return data_in_kwargs
        else:
            print("> Cancelando...")
    else:
        funciones_main.reportes_txt("Intento de eliminacion a perfil de usuario con servicios aun contratados",data_in_kwargs)
        input(
            "Accion no permitida.\nEl usuario seleccionado no debe tener servicios contradados. Se requiere descontratar todos los servicios.\n[Enter - Cancelar]\n")


def actualizar_categoria_automatico(data, ruta_db):
    '''
    En la version actual unicamente leer la base de datos para aplicar la logica de categoria a cada usuario segun su antiguedad
    ==> Recibe
    <== Devuelve
    '''
    print("Actualizando base de datos...")
    usuarios = data["usuarios"]
    fecha_actual = datetime.now().date()
    fecha_actual = datetime.strftime(fecha_actual, "%d-%m-%Y")
    fecha_actual = datetime.strptime(fecha_actual, "%d-%m-%Y")
    for usuario in usuarios:
        if usuario["categoria gestionada"] is False:
            fecha_antigua = datetime.strptime(
                usuario["antiguedad"], "%d-%m-%Y")
            diferencia_total = relativedelta(fecha_actual, fecha_antigua)
            meses_diferencia = diferencia_total.years * 12 + diferencia_total.months
            if meses_diferencia <= 11:
                usuario["categoria"] = "cliente nuevo"
            elif meses_diferencia <= 23:
                usuario["categoria"] = "cliente regular"
            else:
                usuario["categoria"] = "cliente leal"
    funciones_main.export_file(data, "db", no_kwargs=True)
    print("Actualizacion completa...")
