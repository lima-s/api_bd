from flask import Flask, request, jsonify
import pymysql
from neo4j import GraphDatabase

app = Flask(__name__)

# Configuración de la conexión a la base de datos MySQL
def get_db_connection():
    return pymysql.connect(
        host='junction.proxy.rlwy.net',
        user='root',
        passwd='YVdSgzJdeUHzlJEdBgUJIUabagObKLhH',
        db='BDproyecto',
        port=27810,
        cursorclass=pymysql.cursors.DictCursor
    )

# Configuración de la conexión a la base de datos Neo4j
class Neo4jConnection:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def execute_query(self, query, parameters=None):
        with self.driver.session() as session:
            result = session.run(query, parameters)
            return [record for record in result]

# Configuración de la conexión
uri = "bolt://34.205.32.22:7687"
user = "neo4j"
password = "space-top-moneys"
conn = Neo4jConnection(uri=uri, user=user, password=password)


#mysql
# Configuración de la conexión a la base de datos
def get_db_connection():
    return pymysql.connect(
        host='junction.proxy.rlwy.net',
        user='root',
        passwd='YVdSgzJdeUHzlJEdBgUJIUabagObKLhH',
        db='BDproyecto',
        port=27810,
        cursorclass=pymysql.cursors.DictCursor  # Retorna resultados como diccionarios
    )

# Ruta para obtener todos los pacientes o uno específico usando un query parameter (GET)
@app.route('/pacientes', methods=['GET'])
def get_pacientes():
    pacientes_id = request.args.get('pacientes')  # Obtiene el parámetro de consulta "pacientes"
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            if pacientes_id:
                # Si se proporciona el parámetro, busca un solo paciente
                cursor.execute("SELECT * FROM Informacion_Paciente WHERE idInformacion_Paciente = %s", (pacientes_id,))
                paciente = cursor.fetchone()
                connection.close()
                if paciente:
                    return jsonify(paciente), 200
                else:
                    return jsonify({"message": "Paciente no encontrado"}), 404
            else:
                # Si no se proporciona el parámetro, devuelve todos los pacientes
                cursor.execute("SELECT * FROM Informacion_Paciente")
                pacientes = cursor.fetchall()
                connection.close()
                return jsonify(pacientes), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Ruta para obtener un paciente por ID (GET)
@app.route('/pacientes/<int:id>', methods=['GET'])
def get_pacientess(id):
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Informacion_Paciente WHERE idInformacion_Paciente = %s", (id,))
            paciente = cursor.fetchone()
        connection.close()
        if paciente:
            return jsonify(paciente), 200
        else:
            return jsonify({"message": "Paciente no encontrado"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Ruta para agregar un paciente (POST)
# Ruta para agregar un nuevo paciente utilizando query parameters (POST)
@app.route('/pacientes', methods=['POST'])
def create_pacientes():
    # Obtener los parámetros de consulta
    tipo_documento = request.args.get('TipoDeDocumento')
    numero_documento = request.args.get('NumeroDocumento')
    nombre = request.args.get('Nombre')
    apellido_paterno = request.args.get('ApellidoPaterno')
    apellido_materno = request.args.get('ApellidoMaterno')
    fecha_nacimiento = request.args.get('FechaNacimiento')
    fecha_afiliacion = request.args.get('FechaAfiliacion')
    es_afiliado = request.args.get('EsAfiliado')
    celular = request.args.get('Celular')
    
    # Validar que se proporcionen todos los campos requeridos
    if not all([tipo_documento, numero_documento, nombre, apellido_paterno, apellido_materno, fecha_nacimiento, fecha_afiliacion, es_afiliado, celular]):
        return jsonify({"error": "Faltan datos obligatorios"}), 400  # Bad request

    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            sql = """
            INSERT INTO Informacion_Paciente 
            (TipoDeDocumento, NumeroDocumento, Nombre, ApellidoPaterno, ApellidoMaterno, FechaNacimiento, FechaAfiliacion, EsAfiliado, Celular)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                tipo_documento, numero_documento, nombre, apellido_paterno, apellido_materno,
                fecha_nacimiento, fecha_afiliacion, int(es_afiliado), celular
            ))
            connection.commit()
            new_id = cursor.lastrowid  # Obtener el ID del nuevo registro
        connection.close()

        # Retornar la información del nuevo paciente
        new_paciente = {
            "idInformacion_Paciente": new_id,
            "TipoDeDocumento": tipo_documento,
            "NumeroDocumento": numero_documento,
            "Nombre": nombre,
            "ApellidoPaterno": apellido_paterno,
            "ApellidoMaterno": apellido_materno,
            "FechaNacimiento": fecha_nacimiento,
            "FechaAfiliacion": fecha_afiliacion,
            "EsAfiliado": es_afiliado,
            "Celular": celular
        }
        return jsonify(new_paciente), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

# Ruta para actualizar un paciente existente utilizando query parameters (PUT)
@app.route('/pacientes', methods=['PUT'])
def update_pacientes():
    # Obtener el parámetro del ID del paciente desde los query parameters
    paciente_id = request.args.get('paciente_id')
    
    # Validar que se haya proporcionado el ID del paciente
    if not paciente_id:
        return jsonify({"error": "El ID del paciente es obligatorio"}), 400

    # Obtener los valores a actualizar desde los query parameters
    tipo_documento = request.args.get('TipoDeDocumento')
    numero_documento = request.args.get('NumeroDocumento')
    nombre = request.args.get('Nombre')
    apellido_paterno = request.args.get('ApellidoPaterno')
    apellido_materno = request.args.get('ApellidoMaterno')
    fecha_nacimiento = request.args.get('FechaNacimiento')
    fecha_afiliacion = request.args.get('FechaAfiliacion')
    es_afiliado = request.args.get('EsAfiliado')
    celular = request.args.get('Celular')

    # Validar que al menos un campo se haya proporcionado para actualizar
    if not any([tipo_documento, numero_documento, nombre, apellido_paterno, apellido_materno, fecha_nacimiento, fecha_afiliacion, es_afiliado, celular]):
        return jsonify({"error": "Se debe proporcionar al menos un campo para actualizar"}), 400

    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            # Construir dinámicamente la consulta de actualización
            fields = []
            values = []
            if tipo_documento:
                fields.append("TipoDeDocumento = %s")
                values.append(tipo_documento)
            if numero_documento:
                fields.append("NumeroDocumento = %s")
                values.append(numero_documento)
            if nombre:
                fields.append("Nombre = %s")
                values.append(nombre)
            if apellido_paterno:
                fields.append("ApellidoPaterno = %s")
                values.append(apellido_paterno)
            if apellido_materno:
                fields.append("ApellidoMaterno = %s")
                values.append(apellido_materno)
            if fecha_nacimiento:
                fields.append("FechaNacimiento = %s")
                values.append(fecha_nacimiento)
            if fecha_afiliacion:
                fields.append("FechaAfiliacion = %s")
                values.append(fecha_afiliacion)
            if es_afiliado:
                fields.append("EsAfiliado = %s")
                values.append(int(es_afiliado))
            if celular:
                fields.append("Celular = %s")
                values.append(celular)

            values.append(paciente_id)

            # Ejecutar la consulta de actualización
            sql = f"UPDATE Informacion_Paciente SET {', '.join(fields)} WHERE idInformacion_Paciente = %s"
            cursor.execute(sql, values)
            connection.commit()

            # Verificar si se realizó alguna actualización
            if cursor.rowcount == 0:
                return jsonify({"error": "Paciente no encontrado"}), 404

        connection.close()
        return jsonify({"message": "Paciente actualizado correctamente"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Ruta para eliminar un paciente por query parameter (DELETE)
@app.route('/pacientes', methods=['DELETE'])
def delete_pacientes():
    # Obtener el parámetro del ID del paciente desde los query parameters
    pacientes = request.args.get('pacientes')

    # Validar que se haya proporcionado el ID del paciente
    if not pacientes:
        return jsonify({"error": "El ID del paciente es obligatorio"}), 400

    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            # Intentar eliminar el paciente
            sql = "DELETE FROM Informacion_Paciente WHERE idInformacion_Paciente = %s"
            cursor.execute(sql, (pacientes,))
            connection.commit()

            # Verificar si se eliminó algún registro
            if cursor.rowcount == 0:
                return jsonify({"error": "Paciente no encontrado"}), 404

        connection.close()
        return jsonify({"message": "Paciente eliminado correctamente"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ----------------------- MÉTODOS PARA DOCTORES ----------------------- #

# Ruta para obtener todos los doctores o uno específico usando un query parameter (GET)
@app.route('/doctores', methods=['GET'])
def get_doctores():
    doctor_id = request.args.get('doctor_id')  # Obtiene el parámetro de consulta "doctor_id"
    print(f"DEBUG: doctor_id = {doctor_id}")  # Depuración: verificar el valor de doctor_id
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            if doctor_id:
                print("DEBUG: Buscando doctor por ID")  # Depuración
                cursor.execute("SELECT * FROM Informacion_Doctor WHERE idInformacion_Doctor = %s", (int(doctor_id),))
                doctor = cursor.fetchone()
                connection.close()
                if doctor:
                    return jsonify(doctor), 200
                else:
                    return jsonify({"message": "Doctor no encontrado"}), 404
            else:
                print("DEBUG: Buscando todos los doctores")  # Depuración
                cursor.execute("SELECT * FROM Informacion_Doctor")
                doctores = cursor.fetchall()
                connection.close()
                return jsonify(doctores), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500



# Ruta para agregar un paciente (POST)
@app.route('/doctores', methods=['POST'])
def create_doctores():
    # Obtener los parámetros de la URL
    tipo_documento = request.args.get('TipoDeDocumento')
    numero_documento = request.args.get('NumeroDocumento')
    nombre = request.args.get('Nombre')
    apellido_paterno = request.args.get('ApellidoPaterno')
    apellido_materno = request.args.get('ApellidoMaterno')
    fecha_nacimiento = request.args.get('FechaNacimiento')
    fecha_afiliacion = request.args.get('FechaAfiliacion')
    es_habilitado = request.args.get('EsHabilitado')

    # Validar que se proporcionen todos los campos requeridos
    if not all([tipo_documento, numero_documento, nombre, apellido_paterno, apellido_materno, fecha_nacimiento, fecha_afiliacion, es_habilitado]):
        return jsonify({"error": "Faltan datos obligatorios"}), 400  # Bad request

    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            sql = """
            INSERT INTO Informacion_Doctor 
            (TipoDeDocumento, NumeroDocumento, Nombre, ApellidoPaterno, ApellidoMaterno, FechaNacimiento, FechaAfiliacion, EsHabilitado)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                tipo_documento, numero_documento, nombre, apellido_paterno, apellido_materno,
                fecha_nacimiento, fecha_afiliacion, int(es_habilitado)
            ))
            connection.commit()
            new_id = cursor.lastrowid  # Obtener el ID del nuevo registro
        connection.close()

        # Retornar la información del nuevo doctor
        new_doctor = {
            "idInformacion_Doctor": new_id,
            "TipoDeDocumento": tipo_documento,
            "NumeroDocumento": numero_documento,
            "Nombre": nombre,
            "ApellidoPaterno": apellido_paterno,
            "ApellidoMaterno": apellido_materno,
            "FechaNacimiento": fecha_nacimiento,
            "FechaAfiliacion": fecha_afiliacion,
            "EsHabilitado": es_habilitado
        }
        return jsonify(new_doctor), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/doctores', methods=['PUT'])
def update_doctoress():
    # Obtener el parámetro del ID del doctor desde los query parameters
    doctor_id = request.args.get('doctor_id')
    
    # Validar que se haya proporcionado el ID del doctor
    if not doctor_id:
        return jsonify({"error": "El ID del doctor es obligatorio"}), 400

    # Obtener los valores a actualizar desde los query parameters
    tipo_documento = request.args.get('TipoDeDocumento')
    numero_documento = request.args.get('NumeroDocumento')
    nombre = request.args.get('Nombre')
    apellido_paterno = request.args.get('ApellidoPaterno')
    apellido_materno = request.args.get('ApellidoMaterno')
    fecha_nacimiento = request.args.get('FechaNacimiento')
    fecha_afiliacion = request.args.get('FechaAfiliacion')
    es_habilitado = request.args.get('EsHabilitado')

    # Validar que al menos un campo se haya proporcionado para actualizar
    if not any([tipo_documento, numero_documento, nombre, apellido_paterno, apellido_materno, fecha_nacimiento, fecha_afiliacion, es_habilitado]):
        return jsonify({"error": "Se debe proporcionar al menos un campo para actualizar"}), 400

    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            # Construir dinámicamente la consulta de actualización
            fields = []
            values = []
            if tipo_documento:
                fields.append("TipoDeDocumento = %s")
                values.append(tipo_documento)
            if numero_documento:
                fields.append("NumeroDocumento = %s")
                values.append(numero_documento)
            if nombre:
                fields.append("Nombre = %s")
                values.append(nombre)
            if apellido_paterno:
                fields.append("ApellidoPaterno = %s")
                values.append(apellido_paterno)
            if apellido_materno:
                fields.append("ApellidoMaterno = %s")
                values.append(apellido_materno)
            if fecha_nacimiento:
                fields.append("FechaNacimiento = %s")
                values.append(fecha_nacimiento)
            if fecha_afiliacion:
                fields.append("FechaAfiliacion = %s")
                values.append(fecha_afiliacion)
            if es_habilitado:
                fields.append("EsHabilitado = %s")
                values.append(int(es_habilitado))

            values.append(doctor_id)

            # Ejecutar la consulta de actualización
            sql = f"UPDATE Informacion_Doctor SET {', '.join(fields)} WHERE idInformacion_Doctor = %s"
            cursor.execute(sql, values)
            connection.commit()

            # Verificar si se realizó alguna actualización
            if cursor.rowcount == 0:
                return jsonify({"error": "Doctor no encontrado"}), 404

        connection.close()
        return jsonify({"message": "Doctor actualizado correctamente"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/doctores', methods=['DELETE'])
def delete_doctores():
    # Obtener el parámetro del ID del doctor desde los query parameters
    doctor_id = request.args.get('doctor_id')

    # Validar que se haya proporcionado el ID del doctor
    if not doctor_id:
        return jsonify({"error": "El ID del doctor es obligatorio"}), 400

    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            # Intentar eliminar el doctor
            sql = "DELETE FROM Informacion_Doctor WHERE idInformacion_Doctor = %s"
            cursor.execute(sql, (doctor_id,))
            connection.commit()

            # Verificar si se eliminó algún registro
            if cursor.rowcount == 0:
                return jsonify({"error": "Doctor no encontrado"}), 404

        connection.close()
        return jsonify({"message": "Doctor eliminado correctamente"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

#------------------------------------------------NEO4J
#Metodos para el nodo doctores

#METODO GET
@app.route('/doctores_neo4j', methods=['GET'])
def get_all_doctores():
    try:
        # Obtener el parámetro 'doctores' de la URL
        doctor_id = request.args.get('doctores_neo4j', type=int)

        if doctor_id:
            # Si se pasa un ID, buscar un doctor específico
            query = "MATCH (d:Doctor) WHERE d.id = $id RETURN d"
            result = conn.execute_query(query, parameters={"id": doctor_id})
        else:
            # Si no se pasa ningún ID, obtener todos los doctores
            query = "MATCH (d:Doctor) RETURN d"
            result = conn.execute_query(query)

        doctores = [
            {
                "id": record["d"]["id"],
                "nombre": record["d"]["nombre"],
                "apellidoPaterno": record["d"]["apellidoPaterno"],
                "apellidoMaterno": record["d"]["apellidoMaterno"],
                "tipoDocumento": record["d"]["tipoDocumento"],
                "numeroDocumento": record["d"]["numeroDocumento"],
                "fechaNacimiento": record["d"]["fechaNacimiento"],
                "fechaAfiliacion": record["d"]["fechaAfiliacion"],
                "esHabilitado": record["d"]["esHabilitado"]
            }
            for record in result
        ]
        return jsonify(doctores), 200  # Todos los doctores o el doctor específico
    except Exception as e:
        return jsonify({"error": str(e)}), 500  # Error del servidor

#METODO POST
@app.route('/doctores_neo4j', methods=['POST'])
def create_doctor():
    # Obtener los parámetros de la URL
    apellido_materno = request.args.get('apellidoMaterno')
    apellido_paterno = request.args.get('apellidoPaterno')
    es_habilitado = request.args.get('esHabilitado')
    fecha_afiliacion = request.args.get('fechaAfiliacion')
    fecha_nacimiento = request.args.get('fechaNacimiento')
    nombre = request.args.get('nombre')
    tipo_documento = request.args.get('tipoDocumento')
    numero_documento = request.args.get('numeroDocumento')

    # Validar que se proporcionen todos los campos requeridos
    if not all([apellido_materno, apellido_paterno, es_habilitado, fecha_afiliacion, fecha_nacimiento, nombre, tipo_documento, numero_documento]):
        return jsonify({"error": "Faltan datos obligatorios"}), 400  # Bad request

    try:
        # Obtener el siguiente ID disponible
        query_get_max_id = "MATCH (d:Doctor) RETURN coalesce(MAX(d.id), 0) AS max_id"
        result = conn.execute_query(query_get_max_id)
        next_id = result[0]["max_id"] + 1

        # Crear la consulta para insertar un nuevo doctor con el ID generado
        query_create_doctor = """
        CREATE (d:Doctor {
            id: $id,
            apellidoMaterno: $apellidoMaterno,
            apellidoPaterno: $apellidoPaterno,
            esHabilitado: $esHabilitado,
            fechaAfiliacion: $fechaAfiliacion,
            fechaNacimiento: $fechaNacimiento,
            nombre: $nombre,
            tipoDocumento: $tipoDocumento,
            numeroDocumento: $numeroDocumento
        })
        RETURN d
        """
        # Ejecutar la consulta para crear al doctor
        conn.execute_query(query_create_doctor, parameters={
            "id": next_id,
            "apellidoMaterno": apellido_materno,
            "apellidoPaterno": apellido_paterno,
            "esHabilitado": es_habilitado == 'true',  # Convertir el string "true" a booleano
            "fechaAfiliacion": fecha_afiliacion,
            "fechaNacimiento": fecha_nacimiento,
            "nombre": nombre,
            "tipoDocumento": tipo_documento,
            "numeroDocumento": numero_documento
        })

        # Retornar la información del nuevo doctor
        new_doctor = {
            "id": next_id,
            "apellidoMaterno": apellido_materno,
            "apellidoPaterno": apellido_paterno,
            "esHabilitado": es_habilitado,
            "fechaAfiliacion": fecha_afiliacion,
            "fechaNacimiento": fecha_nacimiento,
            "nombre": nombre,
            "tipoDocumento": tipo_documento,
            "numeroDocumento": numero_documento
        }
        return jsonify(new_doctor), 201  # Created

    except Exception as e:
        return jsonify({"error": str(e)}), 500  # Error del servidor

#METODO PUT
@app.route('/doctores_neo4j', methods=['PUT'])
def update_doctor():
    # Obtener el parámetro del ID del doctor desde los query parameters
    doctor_id = request.args.get('id', type=int)
    
    # Validar que se haya proporcionado el ID del doctor
    if not doctor_id:
        return jsonify({"error": "El ID del doctor es obligatorio"}), 400

    # Obtener los valores a actualizar desde los query parameters
    apellido_materno = request.args.get('apellidoMaterno')
    apellido_paterno = request.args.get('apellidoPaterno')
    es_habilitado = request.args.get('esHabilitado')
    fecha_afiliacion = request.args.get('fechaAfiliacion')
    fecha_nacimiento = request.args.get('fechaNacimiento')
    nombre = request.args.get('nombre')
    tipo_documento = request.args.get('tipoDocumento')
    numero_documento = request.args.get('numeroDocumento')

    # Validar que al menos un campo se haya proporcionado para actualizar
    if not any([apellido_materno, apellido_paterno, es_habilitado, fecha_afiliacion, fecha_nacimiento, nombre, tipo_documento, numero_documento]):
        return jsonify({"error": "Se debe proporcionar al menos un campo para actualizar"}), 400

    try:
        # Construir dinámicamente la consulta de actualización
        set_clauses = []
        parameters = {"id": doctor_id}

        if apellido_materno:
            set_clauses.append("d.apellidoMaterno = $apellidoMaterno")
            parameters["apellidoMaterno"] = apellido_materno
        if apellido_paterno:
            set_clauses.append("d.apellidoPaterno = $apellidoPaterno")
            parameters["apellidoPaterno"] = apellido_paterno
        if es_habilitado is not None:
            set_clauses.append("d.esHabilitado = $esHabilitado")
            parameters["esHabilitado"] = es_habilitado.lower() == 'true'  # Convertir a booleano
        if fecha_afiliacion:
            set_clauses.append("d.fechaAfiliacion = $fechaAfiliacion")
            parameters["fechaAfiliacion"] = fecha_afiliacion
        if fecha_nacimiento:
            set_clauses.append("d.fechaNacimiento = $fechaNacimiento")
            parameters["fechaNacimiento"] = fecha_nacimiento
        if nombre:
            set_clauses.append("d.nombre = $nombre")
            parameters["nombre"] = nombre
        if tipo_documento:
            set_clauses.append("d.tipoDocumento = $tipoDocumento")
            parameters["tipoDocumento"] = tipo_documento
        if numero_documento:
            set_clauses.append("d.numeroDocumento = $numeroDocumento")
            parameters["numeroDocumento"] = numero_documento

        # Ejecutar la consulta de actualización
        query_update_doctor = f"""
        MATCH (d:Doctor {{id: $id}})
        SET {', '.join(set_clauses)}
        RETURN d
        """
        result = conn.execute_query(query_update_doctor, parameters=parameters)

        # Verificar si se realizó alguna actualización
        if not result:
            return jsonify({"error": "Doctor no encontrado"}), 404

        return jsonify({"message": "Doctor actualizado correctamente"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

#METODO DELETE
@app.route('/doctores_neo4j', methods=['DELETE'])
def delete_doctor():
    # Obtener el parámetro del ID del doctor desde los query parameters
    doctor_id = request.args.get('doctores_neo4j', type=int)

    # Validar que se haya proporcionado el ID del doctor
    if not doctor_id:
        return jsonify({"error": "El ID del doctor es obligatorio"}), 400

    try:
        # Intentar eliminar el doctor
        query_delete_doctor = """
        MATCH (d:Doctor {id: $id})
        DELETE d
        RETURN COUNT(d) AS count
        """
        result = conn.execute_query(query_delete_doctor, parameters={"id": doctor_id})

        # Verificar si se eliminó algún registro
        if result and result[0]["count"] == 0:
            return jsonify({"error": "Doctor no encontrado"}), 404

        return jsonify({"message": "Doctor eliminado correctamente"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

#Metodos para el nodo pacientes

#METODO GET
@app.route('/pacientes_neo4j', methods=['GET'])
def get_all_paciente():
    try:
        # Obtener el parámetro 'pacientes' de la URL
        paciente_id = request.args.get('pacientes_neo4j', type=int)

        if paciente_id:
            # Si se pasa un ID, buscar un paciente específico
            query = "MATCH (p:Paciente) WHERE p.id = $id RETURN p"
            result = conn.execute_query(query, parameters={"id": paciente_id})
        else:
            # Si no se pasa ningún ID, obtener todos los pacientes
            query = "MATCH (p:Paciente) RETURN p"
            result = conn.execute_query(query)

        pacientes = [
            {
                "id": record["p"]["id"],
                "nombre": record["p"]["nombre"],
                "apellidoPaterno": record["p"]["apellidoPaterno"],
                "apellidoMaterno": record["p"]["apellidoMaterno"],
                "tipoDocumento": record["p"]["tipoDocumento"],
                "numeroDocumento": record["p"]["numeroDocumento"],
                "fechaNacimiento": record["p"]["fechaNacimiento"],
                "fechaAfiliacion": record["p"]["fechaAfiliacion"],
                "esAfiliado": record["p"]["esAfiliado"],
                "celular": record["p"]["celular"],
                "enfermedad": record["p"]["enfermedad"]
            }
            for record in result
        ]
        return jsonify(pacientes), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
#METODO POST
@app.route('/pacientes_neo4j', methods=['POST'])
def create_paciente():
    # Obtener los parámetros de la URL
    nombre = request.args.get('nombre')
    apellido_paterno = request.args.get('apellidoPaterno')
    apellido_materno = request.args.get('apellidoMaterno')
    tipo_documento = request.args.get('tipoDocumento')
    numero_documento = request.args.get('numeroDocumento')
    fecha_nacimiento = request.args.get('fechaNacimiento')
    fecha_afiliacion = request.args.get('fechaAfiliacion')
    es_afiliado = request.args.get('esAfiliado')
    celular = request.args.get('celular')
    enfermedad = request.args.get('enfermedad')

    # Validar que se proporcionen todos los campos requeridos
    if not all([nombre, apellido_paterno, apellido_materno, tipo_documento, numero_documento, fecha_nacimiento, fecha_afiliacion, es_afiliado, celular, enfermedad]):
        return jsonify({"error": "Faltan datos obligatorios"}), 400

    try:
        # Obtener el siguiente ID disponible
        query_get_max_id = "MATCH (p:Paciente) RETURN coalesce(MAX(p.id), 0) AS max_id"
        result = conn.execute_query(query_get_max_id)
        next_id = result[0]["max_id"] + 1

        # Crear el nuevo paciente
        query_create_paciente = """
        CREATE (p:Paciente {
            id: $id,
            nombre: $nombre,
            apellidoPaterno: $apellidoPaterno,
            apellidoMaterno: $apellidoMaterno,
            tipoDocumento: $tipoDocumento,
            numeroDocumento: $numeroDocumento,
            fechaNacimiento: $fechaNacimiento,
            fechaAfiliacion: $fechaAfiliacion,
            esAfiliado: $esAfiliado,
            celular: $celular,
            enfermedad: $enfermedad
        })
        RETURN p
        """
        conn.execute_query(query_create_paciente, parameters={
            "id": next_id,
            "nombre": nombre,
            "apellidoPaterno": apellido_paterno,
            "apellidoMaterno": apellido_materno,
            "tipoDocumento": tipo_documento,
            "numeroDocumento": numero_documento,
            "fechaNacimiento": fecha_nacimiento,
            "fechaAfiliacion": fecha_afiliacion,
            "esAfiliado": es_afiliado.lower() == 'true',  # Convertir a booleano
            "celular": celular,
            "enfermedad": enfermedad
        })

        new_paciente = {
            "id": next_id,
            "nombre": nombre,
            "apellidoPaterno": apellido_paterno,
            "apellidoMaterno": apellido_materno,
            "tipoDocumento": tipo_documento,
            "numeroDocumento": numero_documento,
            "fechaNacimiento": fecha_nacimiento,
            "fechaAfiliacion": fecha_afiliacion,
            "esAfiliado": es_afiliado,
            "celular": celular,
            "enfermedad": enfermedad
        }
        return jsonify(new_paciente), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500
#METODO PUT
@app.route('/pacientes_neo4j', methods=['PUT'])
def update_paciente():
    paciente_id = request.args.get('pacientes', type=int)
    
    if not paciente_id:
        return jsonify({"error": "El ID del paciente es obligatorio"}), 400

    nombre = request.args.get('nombre')
    apellido_paterno = request.args.get('apellidoPaterno')
    apellido_materno = request.args.get('apellidoMaterno')
    tipo_documento = request.args.get('tipoDocumento')
    numero_documento = request.args.get('numeroDocumento')
    fecha_nacimiento = request.args.get('fechaNacimiento')
    fecha_afiliacion = request.args.get('fechaAfiliacion')
    es_afiliado = request.args.get('esAfiliado')
    celular = request.args.get('celular')
    enfermedad = request.args.get('enfermedad')

    if not any([nombre, apellido_paterno, apellido_materno, tipo_documento, numero_documento, fecha_nacimiento, fecha_afiliacion, es_afiliado, celular, enfermedad]):
        return jsonify({"error": "Se debe proporcionar al menos un campo para actualizar"}), 400

    try:
        set_clauses = []
        parameters = {"id": paciente_id}

        if nombre:
            set_clauses.append("p.nombre = $nombre")
            parameters["nombre"] = nombre
        if apellido_paterno:
            set_clauses.append("p.apellidoPaterno = $apellidoPaterno")
            parameters["apellidoPaterno"] = apellido_paterno
        if apellido_materno:
            set_clauses.append("p.apellidoMaterno = $apellidoMaterno")
            parameters["apellidoMaterno"] = apellido_materno
        if tipo_documento:
            set_clauses.append("p.tipoDocumento = $tipoDocumento")
            parameters["tipoDocumento"] = tipo_documento
        if numero_documento:
            set_clauses.append("p.numeroDocumento = $numeroDocumento")
            parameters["numeroDocumento"] = numero_documento
        if fecha_nacimiento:
            set_clauses.append("p.fechaNacimiento = $fechaNacimiento")
            parameters["fechaNacimiento"] = fecha_nacimiento
        if fecha_afiliacion:
            set_clauses.append("p.fechaAfiliacion = $fechaAfiliacion")
            parameters["fechaAfiliacion"] = fecha_afiliacion
        if es_afiliado is not None:
            set_clauses.append("p.esAfiliado = $esAfiliado")
            parameters["esAfiliado"] = es_afiliado.lower() == 'true'
        if celular:
            set_clauses.append("p.celular = $celular")
            parameters["celular"] = celular
        if enfermedad:
            set_clauses.append("p.enfermedad = $enfermedad")
            parameters["enfermedad"] = enfermedad

        query_update_paciente = f"""
        MATCH (p:Paciente {{id: $id}})
        SET {', '.join(set_clauses)}
        RETURN p
        """
        result = conn.execute_query(query_update_paciente, parameters=parameters)

        if not result:
            return jsonify({"error": "Paciente no encontrado"}), 404

        return jsonify({"message": "Paciente actualizado correctamente"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
#METODO DELETE
@app.route('/pacientes_neo4j', methods=['DELETE'])
def delete_paciente():
    paciente_id = request.args.get('pacientes', type=int)

    if not paciente_id:
        return jsonify({"error": "El ID del paciente es obligatorio"}), 400

    try:
        query_delete_paciente = """
        MATCH (p:Paciente {id: $id})
        DELETE p
        RETURN COUNT(p) AS count
        """
        result = conn.execute_query(query_delete_paciente, parameters={"id": paciente_id})

        if result and result[0]["count"] == 0:
            return jsonify({"error": "Paciente no encontrado"}), 404

        return jsonify({"message": "Paciente eliminado correctamente"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
#Metodos para el nodo especialidades

# METODO GET para Especialidades
@app.route('/especialidades_neo4j', methods=['GET'])
def get_all_especialidades():
    try:
        especialidad_id = request.args.get('especialidades_neo4j', type=int)

        if especialidad_id:
            query = "MATCH (e:Especialidad) WHERE e.id = $id RETURN e"
            result = conn.execute_query(query, parameters={"id": especialidad_id})
        else:
            query = "MATCH (e:Especialidad) RETURN e"
            result = conn.execute_query(query)

        especialidades = [
            {
                "id": record["e"]["id"],
                "nombre": record["e"]["nombre"]
            }
            for record in result
        ]
        return jsonify(especialidades), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# METODO POST para Especialidades
@app.route('/especialidades_neo4j', methods=['POST'])
def create_especialidad():
    nombre = request.args.get('nombre')

    if not nombre:
        return jsonify({"error": "El nombre de la especialidad es obligatorio"}), 400

    try:
        query_get_max_id = "MATCH (e:Especialidad) RETURN coalesce(MAX(e.id), 0) AS max_id"
        result = conn.execute_query(query_get_max_id)
        next_id = result[0]["max_id"] + 1

        query_create_especialidad = """
        CREATE (e:Especialidad {id: $id, nombre: $nombre})
        RETURN e
        """
        conn.execute_query(query_create_especialidad, parameters={"id": next_id, "nombre": nombre})

        new_especialidad = {
            "id": next_id,
            "nombre": nombre
        }
        return jsonify(new_especialidad), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# METODO PUT para Especialidades
@app.route('/especialidades_neo4j', methods=['PUT'])
def update_especialidad():
    especialidad_id = request.args.get('especialidades_neo4j', type=int)
    nombre = request.args.get('nombre')

    if not especialidad_id:
        return jsonify({"error": "El ID de la especialidad es obligatorio"}), 400

    if not nombre:
        return jsonify({"error": "Se debe proporcionar el nuevo nombre para actualizar"}), 400

    try:
        query_update_especialidad = """
        MATCH (e:Especialidad {id: $id})
        SET e.nombre = $nombre
        RETURN e
        """
        result = conn.execute_query(query_update_especialidad, parameters={"id": especialidad_id, "nombre": nombre})

        if not result:
            return jsonify({"error": "Especialidad no encontrada"}), 404

        return jsonify({"message": "Especialidad actualizada correctamente"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# METODO DELETE para Especialidades
@app.route('/especialidades_neo4j', methods=['DELETE'])
def delete_especialidad():
    especialidad_id = request.args.get('especialidades_neo4j', type=int)

    if not especialidad_id:
        return jsonify({"error": "El ID de la especialidad es obligatorio"}), 400

    try:
        query_delete_especialidad = """
        MATCH (e:Especialidad {id: $id})
        DELETE e
        RETURN COUNT(e) AS count
        """
        result = conn.execute_query(query_delete_especialidad, parameters={"id": especialidad_id})

        if result and result[0]["count"] == 0:
            return jsonify({"error": "Especialidad no encontrada"}), 404

        return jsonify({"message": "Especialidad eliminada correctamente"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
#-------------------------------------------------------------------
# METODO GET para obtener especialidades de un doctor
@app.route('/doctores_neo4j/especialidades_neo4j', methods=['GET'])
def get_especialidades_by_doctor():
    doctor_id = request.args.get('doctores_neo4j', type=int)

    if not doctor_id:
        return jsonify({"error": "El ID del doctor es obligatorio"}), 400

    try:
        query = """
        MATCH (d:Doctor {id: $doctor_id})-[:TIENE_ESPECIALIDAD]->(e:Especialidad)
        RETURN d.nombre AS doctor_nombre, e.id AS especialidad_id, e.nombre AS especialidad_nombre
        """
        result = conn.execute_query(query, parameters={"doctor_id": doctor_id})

        if not result:
            return jsonify({"error": "No se encontraron especialidades para este doctor"}), 404

        doctor_especialidades = {
            "doctor": result[0]["doctor_nombre"],  # El nombre del doctor será el mismo para todas las relaciones
            "especialidades": [
                {"id": record["especialidad_id"], "nombre": record["especialidad_nombre"]}
                for record in result
            ],
        }

        return jsonify(doctor_especialidades), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# METODO POST para asignar una especialidad a un doctor
@app.route('/doctores_neo4j/especialidades_neo4j', methods=['POST'])
def add_especialidad_to_doctor():
    doctor_id = request.args.get('doctores_neo4j', type=int)
    especialidad_id = request.args.get('especialidades_neo4j', type=int)

    if not doctor_id or not especialidad_id:
        return jsonify({"error": "El ID del doctor y el ID de la especialidad son obligatorios"}), 400

    try:
        query = """
        MATCH (d:Doctor {id: $doctor_id}), (e:Especialidad {id: $especialidad_id})
        MERGE (d)-[:TIENE_ESPECIALIDAD]->(e)
        RETURN d.nombre AS doctor_nombre, e.nombre AS especialidad_nombre
        """
        result = conn.execute_query(query, parameters={"doctor_id": doctor_id, "especialidad_id": especialidad_id})

        if not result:
            return jsonify({"error": "No se encontró el doctor o la especialidad"}), 404

        return jsonify({
            "message": f"Especialidad '{result[0]['especialidad_nombre']}' asignada a'{result[0]['doctor_nombre']}'"
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# METODO PUT para actualizar las especialidades de un doctor
@app.route('/doctores_neo4j/especialidades_neo4j', methods=['PUT'])
def update_especialidad_for_doctor():
    doctor_id = request.args.get('doctores_neo4j', type=int)
    old_especialidad_id = request.args.get('especialidades_neo4j', type=int)
    new_especialidad_id = request.args.get('nuevo_especialidades_neo4j', type=int)

    if not doctor_id or not old_especialidad_id or not new_especialidad_id:
        return jsonify({"error": "El ID del doctor, la especialidad actual y la nueva especialidad son obligatorios"}), 400

    try:
        query = """
        MATCH (d:Doctor {id: $doctor_id})-[rel:TIENE_ESPECIALIDAD]->(e:Especialidad {id: $old_especialidad_id})
        DELETE rel
        WITH d
        MATCH (new_e:Especialidad {id: $new_especialidad_id})
        MERGE (d)-[:TIENE_ESPECIALIDAD]->(new_e)
        RETURN d.nombre AS doctor_nombre, new_e.nombre AS nueva_especialidad
        """
        result = conn.execute_query(query, parameters={
            "doctor_id": doctor_id,
            "old_especialidad_id": old_especialidad_id,
            "new_especialidad_id": new_especialidad_id
        })

        if not result:
            return jsonify({"error": "No se encontró el doctor o la especialidad"}), 404

        return jsonify({
            "message": f"Especialidad actualizada a '{result[0]['nueva_especialidad']}' para  '{result[0]['doctor_nombre']}'"
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# METODO DELETE para eliminar una especialidad de un doctor
@app.route('/doctores_neo4j/especialidades_neo4j', methods=['DELETE'])
def delete_especialidad_from_doctor():
    doctor_id = request.args.get('doctores_neo4j', type=int)
    especialidad_id = request.args.get('especialidades_neo4j', type=int)

    if not doctor_id or not especialidad_id:
        return jsonify({"error": "El ID del doctor y el ID de la especialidad son obligatorios"}), 400

    try:
        query = """
        MATCH (d:Doctor {id: $doctor_id})-[rel:TIENE_ESPECIALIDAD]->(e:Especialidad {id: $especialidad_id})
        DELETE rel
        RETURN d.nombre AS doctor_nombre, e.nombre AS especialidad_nombre
        """
        result = conn.execute_query(query, parameters={"doctor_id": doctor_id, "especialidad_id": especialidad_id})

        if not result:
            return jsonify({"error": "No se encontró la relación entre el doctor y la especialidad"}), 404

        return jsonify({
            "message": f"Especialidad '{result[0]['especialidad_nombre']}' eliminada del doctor '{result[0]['doctor_nombre']}'"
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
#-----------------------------------------------------------------------------
#Método GET: Consultar horarios por especialidad
@app.route('/consultorios_neo4j/especialidades_neo4j/horarios_neo4j', methods=['GET'])
def get_horarios_y_especialidades():
    especialidad_id = request.args.get('consultorios_neo4j', type=int)

    try:
        if especialidad_id:
            # Si se proporciona un ID de especialidad, se filtra por este.
            query = """
            MATCH (c:Consultorio)-[:OFRECE]->(e:Especialidad {id: $especialidad_id})
            RETURN c.id AS consultorio_id, c.horario AS horario, e.nombre AS especialidad
            """
            result = conn.execute_query(query, parameters={"especialidad_id": especialidad_id})
        else:
            # Si no se proporciona un ID de especialidad, se obtienen todos los consultorios y especialidades.
            query = """
            MATCH (c:Consultorio)-[:OFRECE]->(e:Especialidad)
            RETURN c.id AS consultorio_id, c.horario AS horario, e.nombre AS especialidad
            """
            result = conn.execute_query(query)

        consultorios = [{"consultorio_id": record["consultorio_id"], "horario": record["horario"], "especialidad": record["especialidad"]} for record in result]

        if not consultorios:
            return jsonify({"error": "No se encontraron consultorios ni especialidades asociadas"}), 404

        return jsonify(consultorios), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


#Método POST: Asignar horario a una especialidad
@app.route('/consultorios_neo4j/especialidades_neo4j/horarios_neo4j', methods=['POST'])
def create_consultorio():
    # Obtener los parámetros desde la URL
    especialidad_id = request.args.get('especialidades_neo4j', type=int)
    horario = request.args.get('horario', type=str)

    # Verificar que los parámetros sean proporcionados
    if not especialidad_id or not horario:
        return jsonify({"error": "Los parámetros especialidad_neo4j y horario son obligatorios"}), 400

    try:
        # Obtener el próximo ID disponible para el nuevo consultorio
        query_get_last_id = """
        MATCH (c:Consultorio)
        RETURN MAX(c.id) AS last_id
        """
        result = conn.execute_query(query_get_last_id)
        last_id = result[0]["last_id"] if result else 0
        consultorio_id = last_id + 1  # Generar el siguiente ID automáticamente

        # Crear el nuevo consultorio y asignar la especialidad correspondiente
        query = """
        MATCH (e:Especialidad {id: $especialidad_id})
        CREATE (c:Consultorio {id: $consultorio_id, horario: $horario})-[:OFRECE]->(e)
        RETURN c.id AS consultorio_id, c.horario AS horario, e.nombre AS especialidad
        """
        result = conn.execute_query(
            query,
            parameters={
                "consultorio_id": consultorio_id,
                "horario": horario,
                "especialidad_id": especialidad_id,
            },
        )

        return jsonify({"message": "Consultorio creado exitosamente", "data": result}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Método PUT: Actualizar horario de un consultorio
@app.route('/consultorios_neo4j/especialidades_neo4j/horarios_neo4j', methods=['PUT'])
def update_consultorio():
    # Obtener los parámetros de la query string
    consultorio_id = request.args.get('consultorio_neo4j', type=int)
    nuevo_horario = request.args.get('horario')

    if not consultorio_id or not nuevo_horario:
        return jsonify({"error": "Faltan datos obligatorios: consultorio_neo4j, horario"}), 400

    try:
        # Actualizar el horario del consultorio en Neo4j
        query = """
        MATCH (c:Consultorio {id: $consultorio_id})
        SET c.horario = $nuevo_horario
        RETURN c.id AS consultorio_id, c.horario AS horario
        """
        result = conn.execute_query(
            query,
            parameters={"consultorio_id": consultorio_id, "nuevo_horario": nuevo_horario},
        )

        if not result:
            return jsonify({"error": "Consultorio no encontrado"}), 404
        
        return jsonify({"message": "Consultorio actualizado exitosamente", "data": result}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500



# Método DELETE: Eliminar consultorio
@app.route('/consultorios_neo4j/especialidades_neo4j/horarios_neo4j', methods=['DELETE'])
def delete_consultorio():
    # Obtener el ID del consultorio desde la query string
    consultorio_id = request.args.get('consultorios_neo4j', type=int)

    if not consultorio_id:
        return jsonify({"error": "El ID del consultorio es obligatorio"}), 400

    try:
        # Consultar si el consultorio existe
        query_check = """
        MATCH (c:Consultorio {id: $consultorio_id})
        RETURN c
        """
        result_check = conn.execute_query(query_check, parameters={"consultorio_id": consultorio_id})

        if not result_check:
            return jsonify({"error": "Consultorio no encontrado"}), 404

        # Eliminar el consultorio y sus relaciones
        query_delete = """
        MATCH (c:Consultorio {id: $consultorio_id})
        DETACH DELETE c
        """
        conn.execute_query(query_delete, parameters={"consultorio_id": consultorio_id})

        return jsonify({"message": "Consultorio eliminado exitosamente"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

#------------------------------------------------------RESERVAS-------------
#GET: Obtener todas las reservas o filtradas por parámetros (consultorio, especialidad, doctor)
@app.route('/reservas_neo4j', methods=['GET'])
def get_reservas():
    # Obtener parámetros opcionales desde la query string
    especialidad_id = request.args.get('especialidades_neo4j', type=int)
    consultorio_id = request.args.get('consultorios_neo4j', type=int)
    doctor_id = request.args.get('doctores_neo4j', type=int)

    try:
        # Query base para obtener todas las reservas
        query = """
        MATCH (r:Reserva)-[:PERTENECE_A]->(p:Paciente),
              (r)-[:ASIGNADA_A]->(d:Doctor),
              (r)-[:DE_ESPECIALIDAD]->(e:Especialidad),
              (r)-[:EN_CONSULTORIO]->(c:Consultorio)
        """

        # Filtro por especialidad
        if especialidad_id:
            query += "WHERE e.id = $especialidad_id "

        # Filtro por consultorio
        if consultorio_id:
            query += "WHERE c.id = $consultorio_id "

        # Filtro por doctor
        if doctor_id:
            query += "WHERE d.id = $doctor_id "

        query += "RETURN r.id AS reserva_id, r.fechaReserva AS fecha_reserva, "
        query += "r.fechaInicio AS fecha_inicio, r.fechaTermino AS fecha_termino, "
        query += "p.nombre AS paciente, d.nombre AS doctor, e.nombre AS especialidad, "
        query += "c.horario AS consultorio"

        result = conn.execute_query(query, parameters={
            "especialidad_id": especialidad_id,
            "consultorio_id": consultorio_id,
            "doctor_id": doctor_id
        })

        reservas = [{"reserva_id": record["reserva_id"],
                     "fecha_reserva": record["fecha_reserva"],
                     "fecha_inicio": record["fecha_inicio"],
                     "fecha_termino": record["fecha_termino"],
                     "paciente": record["paciente"],
                     "doctor": record["doctor"],
                     "especialidad": record["especialidad"],
                     "consultorio": record["consultorio"]} for record in result]

        if not reservas:
            return jsonify({"error": "No se encontraron reservas"}), 404

        return jsonify(reservas), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
#POST: Crear una nueva reserva
@app.route('/reservas_neo4j', methods=['POST'])
def create_reserva():
    # Obtener parámetros de la query string
    paciente_id = request.args.get('paciente_id', type=int)
    doctor_id = request.args.get('doctor_id', type=int)
    especialidad_id = request.args.get('especialidad_id', type=int)
    consultorio_id = request.args.get('consultorio_id', type=int)
    fecha_reserva = request.args.get('fecha_reserva', type=str)
    fecha_inicio = request.args.get('fecha_inicio', type=str)
    fecha_termino = request.args.get('fecha_termino', type=str)

    # Verificar que todos los parámetros estén presentes
    if not all([paciente_id, doctor_id, especialidad_id, consultorio_id, fecha_reserva, fecha_inicio, fecha_termino]):
        return jsonify({"error": "Faltan datos obligatorios"}), 400

    try:
        # Obtener el próximo ID disponible para la reserva
        query_get_last_id = """
        MATCH (r:Reserva)
        RETURN MAX(r.id) AS last_id
        """
        result = conn.execute_query(query_get_last_id)
        last_id = result[0]["last_id"] if result else 0
        reserva_id = last_id + 1  # Generar el siguiente ID automáticamente

        # Crear la reserva y asignar relaciones
        query = """
        MATCH (p:Paciente {id: $paciente_id}),
              (d:Doctor {id: $doctor_id}),
              (e:Especialidad {id: $especialidad_id}),
              (c:Consultorio {id: $consultorio_id})
        CREATE (r:Reserva {id: $reserva_id, fechaReserva: $fecha_reserva, fechaInicio: $fecha_inicio, fechaTermino: $fecha_termino})
        CREATE (r)-[:PERTENECE_A]->(p)
        CREATE (r)-[:ASIGNADA_A]->(d)
        CREATE (r)-[:DE_ESPECIALIDAD]->(e)
        CREATE (r)-[:EN_CONSULTORIO]->(c)
        RETURN r.id AS reserva_id, r.fechaReserva AS fecha_reserva, r.fechaInicio AS fecha_inicio, r.fechaTermino AS fecha_termino
        """
        result = conn.execute_query(query, parameters={
            "reserva_id": reserva_id,
            "fecha_reserva": fecha_reserva,
            "fecha_inicio": fecha_inicio,
            "fecha_termino": fecha_termino,
            "paciente_id": paciente_id,
            "doctor_id": doctor_id,
            "especialidad_id": especialidad_id,
            "consultorio_id": consultorio_id
        })

        return jsonify({"message": "Reserva creada exitosamente", "data": result}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

#Método PUT para actualizar una reserva:
@app.route('/reservas_neo4j', methods=['PUT'])
def update_reserva():
    # Obtener parámetros de la query string
    reserva_id = request.args.get('reserva_id', type=int)
    paciente_id = request.args.get('paciente_id', type=int)
    doctor_id = request.args.get('doctor_id', type=int)
    especialidad_id = request.args.get('especialidad_id', type=int)
    consultorio_id = request.args.get('consultorio_id', type=int)
    fecha_reserva = request.args.get('fecha_reserva', type=str)
    fecha_inicio = request.args.get('fecha_inicio', type=str)
    fecha_termino = request.args.get('fecha_termino', type=str)

    # Verificar que todos los parámetros estén presentes
    if not all([reserva_id, paciente_id, doctor_id, especialidad_id, consultorio_id, fecha_reserva, fecha_inicio, fecha_termino]):
        return jsonify({"error": "Faltan datos obligatorios"}), 400

    try:
        # Verificar si la reserva existe
        query_check_existence = """
        MATCH (r:Reserva {id: $reserva_id})
        RETURN r
        """
        result = conn.execute_query(query_check_existence, parameters={"reserva_id": reserva_id})
        
        if not result:
            return jsonify({"error": "Reserva no encontrada"}), 404

        # Actualizar la reserva y las relaciones
        query_update_reserva = """
        MATCH (r:Reserva {id: $reserva_id}),
              (p:Paciente {id: $paciente_id}),
              (d:Doctor {id: $doctor_id}),
              (e:Especialidad {id: $especialidad_id}),
              (c:Consultorio {id: $consultorio_id})
        SET r.fechaReserva = $fecha_reserva,
            r.fechaInicio = $fecha_inicio,
            r.fechaTermino = $fecha_termino
        MERGE (r)-[:PERTENECE_A]->(p)
        MERGE (r)-[:ASIGNADA_A]->(d)
        MERGE (r)-[:DE_ESPECIALIDAD]->(e)
        MERGE (r)-[:EN_CONSULTORIO]->(c)
        RETURN r.id AS reserva_id, r.fechaReserva AS fecha_reserva, r.fechaInicio AS fecha_inicio, r.fechaTermino AS fecha_termino
        """
        result = conn.execute_query(query_update_reserva, parameters={
            "reserva_id": reserva_id,
            "fecha_reserva": fecha_reserva,
            "fecha_inicio": fecha_inicio,
            "fecha_termino": fecha_termino,
            "paciente_id": paciente_id,
            "doctor_id": doctor_id,
            "especialidad_id": especialidad_id,
            "consultorio_id": consultorio_id
        })

        return jsonify({"message": "Reserva actualizada exitosamente", "data": result}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
#DELETE: Eliminar una reserva
@app.route('/reservas_neo4j', methods=['DELETE'])
def delete_reserva():
    # Obtener el parametro reserva_id de la query string
    reserva_id = request.args.get('reserva_id', type=int)

    # Verificar que el parametro reserva_id esté presente
    if not reserva_id:
        return jsonify({"error": "Falta el ID de la reserva"}), 400

    try:
        # Verificar si la reserva existe
        query_check_existence = """
        MATCH (r:Reserva {id: $reserva_id})
        RETURN r
        """
        result = conn.execute_query(query_check_existence, parameters={"reserva_id": reserva_id})
        
        if not result:
            return jsonify({"error": "Reserva no encontrada"}), 404

        # Eliminar la reserva y sus relaciones
        query_delete_reserva = """
        MATCH (r:Reserva {id: $reserva_id})
        DETACH DELETE r
        """
        conn.execute_query(query_delete_reserva, parameters={"reserva_id": reserva_id})

        return jsonify({"message": "Reserva eliminada exitosamente"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

#----------------------------------------------------Atencion Realizadas
#Método GET:  GET: Obtener todas las atenciones 
@app.route('/atenciones_neo4j', methods=['GET'])
def get_atenciones_realizadas():
    # Obtener parámetros opcionales de la query string
    atencion_id = request.args.get('atencion_id', type=int)
    reserva_id = request.args.get('reserva_id', type=int)

    try:
        # Consulta base
        query = """
        MATCH (a:AtencionRealizada)-[:ASOCIADA_A]->(r:Reserva),
              (a)-[:ATENDIDO_POR]->(p:Paciente)
        """

        # Filtros dinámicos
        filters = []
        if atencion_id:
            filters.append("a.id = $atencion_id")
        if reserva_id:
            filters.append("r.id = $reserva_id")

        # Agregar condiciones WHERE si hay filtros
        if filters:
            query += " WHERE " + " AND ".join(filters)

        # Campos a retornar
        query += """
        RETURN a.id AS atencion_id, a.horaInicio AS hora_inicio, a.horaTermino AS hora_termino,
               a.asistio AS asistio, r.id AS reserva_id, p.nombre AS paciente
        """

        # Ejecutar consulta con parámetros
        result = conn.execute_query(query, parameters={
            "atencion_id": atencion_id,
            "reserva_id": reserva_id
        })

        # Formatear resultados
        atenciones = [{"atencion_id": record["atencion_id"],
                       "hora_inicio": record["hora_inicio"],
                       "hora_termino": record["hora_termino"],
                       "asistio": record["asistio"],
                       "reserva_id": record["reserva_id"],
                       "paciente": record["paciente"]} for record in result]

        # Si no se encontraron resultados
        if not atenciones:
            return jsonify({"error": "No se encontraron atenciones"}), 404

        # Retornar resultados
        return jsonify(atenciones), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



#Método POST: Crear una nueva atención realizada.
@app.route('/atenciones_neo4j', methods=['POST'])
def create_atencion():
    # Obtener parámetros
    reserva_id = request.args.get('reserva_id', type=int)
    hora_inicio = request.args.get('hora_inicio', type=str)
    hora_termino = request.args.get('hora_termino', type=str)
    asistio = request.args.get('asistio', type=bool)

    if not all([reserva_id, hora_inicio, hora_termino, asistio is not None]):
        return jsonify({"error": "Faltan datos obligatorios"}), 400

    try:
        # Verificar si la reserva existe
        query_check_reserva = "MATCH (r:Reserva {id: $reserva_id}) RETURN r"
        result = conn.execute_query(query_check_reserva, parameters={"reserva_id": reserva_id})

        if not result:
            return jsonify({"error": "La reserva no existe"}), 404
        
        # Verificar si ya existe una atención para esta reserva
        query_check_atencion = """
        MATCH (a:AtencionRealizada)-[:ASOCIADA_A]->(r:Reserva {id: $reserva_id})
        RETURN a
        """
        result = conn.execute_query(query_check_atencion, parameters={"reserva_id": reserva_id})

        if result:
            return jsonify({"error": "Ya existe una atención para esta reserva"}), 400

        # Obtener los datos del paciente desde la reserva
        query_get_paciente = """
        MATCH (r:Reserva {id: $reserva_id})-[:PERTENECE_A]->(p:Paciente)
        RETURN p.nombre AS paciente_nombre
        """
        result = conn.execute_query(query_get_paciente, parameters={"reserva_id": reserva_id})

        if not result:
            return jsonify({"error": "No se encontró el paciente asociado a esta reserva"}), 404
        
        paciente_nombre = result[0]["paciente_nombre"]

        # Obtener el próximo ID disponible para la atención
        query_get_last_id = "MATCH (a:AtencionRealizada) RETURN MAX(a.id) AS last_id"
        result = conn.execute_query(query_get_last_id)
        last_id = result[0]["last_id"] if result else 0
        atencion_id = last_id + 1

        # Crear la atención
        query = """
        MATCH (r:Reserva {id: $reserva_id}),
              (p:Paciente {nombre: $paciente_nombre})
        CREATE (a:AtencionRealizada {id: $atencion_id, horaInicio: $hora_inicio,
                                     horaTermino: $hora_termino, asistio: $asistio})
        CREATE (a)-[:ASOCIADA_A]->(r)
        CREATE (a)-[:ATENDIDO_POR]->(p)
        RETURN a.id AS atencion_id
        """
        result = conn.execute_query(query, parameters={
            "atencion_id": atencion_id,
            "hora_inicio": hora_inicio,
            "hora_termino": hora_termino,
            "asistio": asistio,
            "reserva_id": reserva_id,
            "paciente_nombre": paciente_nombre
        })

        return jsonify({"message": "Atención creada exitosamente", "data": result}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


#PUT: Actualizar una atención realizada
# Método PUT para actualizar una atención
@app.route('/atenciones_neo4j', methods=['PUT'])
def update_atencion():
    # Obtener parámetros
    atencion_id = request.args.get('atencion_id', type=int)
    hora_inicio = request.args.get('hora_inicio', type=str)
    hora_termino = request.args.get('hora_termino', type=str)
    asistio = request.args.get('asistio', type=bool)

    if not all([atencion_id, hora_inicio, hora_termino, asistio is not None]):
        return jsonify({"error": "Faltan datos obligatorios"}), 400

    try:
        # Verificar si la atención existe
        query_check_atencion = """
        MATCH (a:AtencionRealizada {id: $atencion_id})
        RETURN a
        """
        result = conn.execute_query(query_check_atencion, parameters={"atencion_id": atencion_id})

        if not result:
            return jsonify({"error": "La atención no existe"}), 404

        # Verificar si la atención está asociada a una reserva
        query_check_reserva = """
        MATCH (a:AtencionRealizada {id: $atencion_id})-[:ASOCIADA_A]->(r:Reserva)
        RETURN r
        """
        result = conn.execute_query(query_check_reserva, parameters={"atencion_id": atencion_id})

        if not result:
            return jsonify({"error": "No se encuentra una reserva asociada a esta atención"}), 404

        # Obtener los datos del paciente desde la reserva
        query_get_paciente = """
        MATCH (r:Reserva {id: $reserva_id})-[:PERTENECE_A]->(p:Paciente)
        RETURN p.nombre AS paciente_nombre
        """
        result = conn.execute_query(query_get_paciente, parameters={"reserva_id": result[0]["r"]["id"]})

        if not result:
            return jsonify({"error": "No se encontró el paciente asociado a la reserva"}), 404

        paciente_nombre = result[0]["paciente_nombre"]

        # Actualizar la atención
        query_update_atencion = """
        MATCH (a:AtencionRealizada {id: $atencion_id})
        SET a.horaInicio = $hora_inicio, a.horaTermino = $hora_termino, a.asistio = $asistio
        RETURN a.id AS atencion_id, a.horaInicio AS hora_inicio, a.horaTermino AS hora_termino, a.asistio AS asistio
        """
        result = conn.execute_query(query_update_atencion, parameters={
            "atencion_id": atencion_id,
            "hora_inicio": hora_inicio,
            "hora_termino": hora_termino,
            "asistio": asistio
        })

        return jsonify({
            "message": "Atención actualizada exitosamente",
            "data": result
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



#DELETE: Eliminar una atención
@app.route('/atenciones_neo4j', methods=['DELETE'])
def delete_atencion():
    # Obtener el ID de la atención
    atencion_id = request.args.get('atencion_id', type=int)

    if not atencion_id:
        return jsonify({"error": "Falta el ID de la atención"}), 400

    try:
        # Verificar que la atención existe
        query_check_atencion = "MATCH (a:AtencionRealizada {id: $atencion_id}) RETURN a"
        result = conn.execute_query(query_check_atencion, parameters={"atencion_id": atencion_id})

        if not result:
            return jsonify({"error": "Atención no encontrada"}), 404

        # Eliminar la atención
        query_delete_atencion = "MATCH (a:AtencionRealizada {id: $atencion_id}) DETACH DELETE a"
        conn.execute_query(query_delete_atencion, parameters={"atencion_id": atencion_id})

        return jsonify({"message": "Atención eliminada exitosamente"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
#--------------------------------------------------SEGUIMIENTOS NEO4J

# Método GET: Obtener todos los seguimientos
@app.route('/seguimientos_neo4j', methods=['GET'])
def get_seguimientos():
    # Obtener parámetros opcionales de la query string
    seguimiento_id = request.args.get('seguimientos_id', type=int)
    atencion_id = request.args.get('atencion_id', type=int)

    try:
        # Consulta base
        query = """
        MATCH (s:Seguimiento)-[:ASOCIADO_A]->(a:AtencionRealizada)
        """

        # Filtros dinámicos
        filters = []
        if seguimiento_id:
            filters.append("s.id = $seguimiento_id")
        if atencion_id:
            filters.append("a.id = $atencion_id")

        # Agregar condiciones WHERE si hay filtros
        if filters:
            query += " WHERE " + " AND ".join(filters)

        # Campos a retornar
        query += """
        RETURN s.id AS seguimiento_id, s.frecuencia AS frecuencia, 
               a.id AS atencion_id
        """

        # Ejecutar consulta con parámetros
        result = conn.execute_query(query, parameters={
            "seguimiento_id": seguimiento_id,
            "atencion_id": atencion_id
        })

        # Formatear resultados
        seguimientos = [{"seguimiento_id": record["seguimiento_id"],
                         "frecuencia": record["frecuencia"],
                         "atencion_id": record["atencion_id"]} for record in result]

        # Si no se encontraron resultados
        if not seguimientos:
            return jsonify({"error": "No se encontraron seguimientos"}), 404

        # Retornar resultados
        return jsonify(seguimientos), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Método POST: Crear un seguimiento
@app.route('/seguimientos_neo4j', methods=['POST'])
def create_seguimiento():
    # Obtener parámetros
    atencion_id = request.args.get('atencion_id', type=int)
    frecuencia = request.args.get('frecuencia', type=str)

    if not all([atencion_id, frecuencia]):
        return jsonify({"error": "Faltan datos obligatorios"}), 400

    try:
        # Verificar si la atención existe y si asistio es true
        query_check_atencion = """
        MATCH (a:AtencionRealizada {id: $atencion_id})
        WHERE a.asistio = true
        RETURN a
        """
        result = conn.execute_query(query_check_atencion, parameters={"atencion_id": atencion_id})

        if not result:
            return jsonify({"error": "La atención no existe o no ha sido asistida"}), 404

        # Verificar si ya existe un seguimiento para esta atención
        query_check_seguimiento = """
        MATCH (s:Seguimiento)-[:ASOCIADO_A]->(a:AtencionRealizada {id: $atencion_id})
        RETURN s
        """
        result = conn.execute_query(query_check_seguimiento, parameters={"atencion_id": atencion_id})

        if result:
            return jsonify({"error": "Ya existe un seguimiento para esta atención"}), 400

        # Obtener el próximo ID disponible para el seguimiento
        query_get_last_id = "MATCH (s:Seguimiento) RETURN MAX(s.id) AS last_id"
        result = conn.execute_query(query_get_last_id)
        last_id = result[0]["last_id"] if result else 0
        seguimiento_id = last_id + 1

        # Crear el seguimiento
        query_create_seguimiento = """
        MATCH (a:AtencionRealizada {id: $atencion_id})
        CREATE (s:Seguimiento {id: $seguimiento_id, frecuencia: $frecuencia})
        CREATE (s)-[:ASOCIADO_A]->(a)
        RETURN s.id AS seguimiento_id
        """
        result = conn.execute_query(query_create_seguimiento, parameters={
            "seguimiento_id": seguimiento_id,
            "frecuencia": frecuencia,
            "atencion_id": atencion_id
        })

        return jsonify({"message": "Seguimiento creado exitosamente", "data": result}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Método PUT: Actualizar un seguimiento
@app.route('/seguimientos_neo4j', methods=['PUT'])
def update_seguimiento():
    # Obtener parámetros
    seguimiento_id = request.args.get('seguimiento_id', type=int)
    frecuencia = request.args.get('frecuencia', type=str)

    if not all([seguimiento_id, frecuencia]):
        return jsonify({"error": "Faltan datos obligatorios"}), 400

    try:
        # Verificar si el seguimiento existe
        query_check_seguimiento = """
        MATCH (s:Seguimiento {id: $seguimiento_id})
        RETURN s
        """
        result = conn.execute_query(query_check_seguimiento, parameters={"seguimiento_id": seguimiento_id})

        if not result:
            return jsonify({"error": "El seguimiento no existe"}), 404

        # Verificar si la atención asociada a este seguimiento existe y si asistio es true
        query_check_atencion = """
        MATCH (s:Seguimiento {id: $seguimiento_id})-[:ASOCIADO_A]->(a:AtencionRealizada)
        WHERE a.asistio = true
        RETURN a
        """
        result = conn.execute_query(query_check_atencion, parameters={"seguimiento_id": seguimiento_id})

        if not result:
            return jsonify({"error": "La atención no existe o no ha sido asistida"}), 404

        # Actualizar la frecuencia del seguimiento
        query_update_seguimiento = """
        MATCH (s:Seguimiento {id: $seguimiento_id})
        SET s.frecuencia = $frecuencia
        RETURN s.id AS seguimiento_id, s.frecuencia AS nueva_frecuencia
        """
        result = conn.execute_query(query_update_seguimiento, parameters={
            "seguimiento_id": seguimiento_id,
            "frecuencia": frecuencia
        })

        return jsonify({"message": "Seguimiento actualizado exitosamente", "data": result}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Método DELETE: Eliminar un seguimiento
@app.route('/seguimientos_neo4j', methods=['DELETE'])
def delete_seguimiento():
    # Obtener el parámetro seguimiento_id
    seguimiento_id = request.args.get('seguimiento_id', type=int)

    if not seguimiento_id:
        return jsonify({"error": "Falta el id del seguimiento"}), 400

    try:
        # Verificar si el seguimiento existe
        query_check_seguimiento = """
        MATCH (s:Seguimiento {id: $seguimiento_id})
        RETURN s
        """
        result = conn.execute_query(query_check_seguimiento, parameters={"seguimiento_id": seguimiento_id})

        if not result:
            return jsonify({"error": "El seguimiento no existe"}), 404

        # Verificar si la atención asociada a este seguimiento existe y si asistio es true
        query_check_atencion = """
        MATCH (s:Seguimiento {id: $seguimiento_id})-[:ASOCIADO_A]->(a:AtencionRealizada)
        WHERE a.asistio = true
        RETURN a
        """
        result = conn.execute_query(query_check_atencion, parameters={"seguimiento_id": seguimiento_id})

        if not result:
            return jsonify({"error": "La atención no existe o no ha sido asistida"}), 404

        # Eliminar el seguimiento
        query_delete_seguimiento = """
        MATCH (s:Seguimiento {id: $seguimiento_id})
        DETACH DELETE s
        """
        conn.execute_query(query_delete_seguimiento, parameters={"seguimiento_id": seguimiento_id})

        return jsonify({"message": "Seguimiento eliminado exitosamente"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

#-------------------------------------------------MEDICAMENTOS
#Método GET: Obtener los medicamentos relacionados con una atención
@app.route('/medicamentos_neo4j', methods=['GET'])
def get_medicamentos():
    # Obtener el ID del medicamento desde los parámetros de la consulta
    medicamento_id = request.args.get('medicamento_id', type=int)

    try:
        # Si no se pasa el ID del medicamento, devolver todos los medicamentos
        if not medicamento_id:
            query = """
            MATCH (m:Medicamento)
            OPTIONAL MATCH (m)-[:ASOCIADO_A]->(a:AtencionRealizada)
            OPTIONAL MATCH (a)-[:ATENDIDO_POR]->(p:Paciente)
            RETURN m.id AS medicamento_id, m.nombre AS nombre, m.dosis AS dosis, 
                   m.frecuencia AS frecuencia, m.fechaReceta AS fecha_receta,
                   a.id AS atencion_id, p.id AS paciente_id
            """
            result = conn.execute_query(query)

        else:
            # Si se pasa el ID del medicamento, obtener los detalles específicos
            query = """
            MATCH (m:Medicamento {id: $medicamento_id})
            OPTIONAL MATCH (m)-[:ASOCIADO_A]->(a:AtencionRealizada)
            OPTIONAL MATCH (a)-[:ATENDIDO_POR]->(p:Paciente)
            RETURN m.id AS medicamento_id, m.nombre AS nombre, m.dosis AS dosis, 
                   m.frecuencia AS frecuencia, m.fechaReceta AS fecha_receta,
                   a.id AS atencion_id, p.id AS paciente_id
            """
            result = conn.execute_query(query, parameters={"medicamento_id": medicamento_id})

        # Formatear los resultados
        medicamentos = [{"medicamento_id": record["medicamento_id"],
                         "nombre": record["nombre"],
                         "dosis": record["dosis"],
                         "frecuencia": record["frecuencia"],
                         "fecha_receta": record["fecha_receta"],
                         "atencion_id": record.get("atencion_id", None),
                         "paciente_id": record.get("paciente_id", None)} for record in result]

        # Si no se encontraron resultados
        if not medicamentos:
            return jsonify({"error": "No se encontraron medicamentos"}), 404

        # Retornar resultados
        return jsonify(medicamentos), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

#Método POST: Crear un medicamento y asociarlo a una atención
@app.route('/medicamentos_neo4j', methods=['POST'])
def create_medicamento():
    # Obtener parámetros
    atencion_id = request.args.get('atencion_id', type=int)
    nombre = request.args.get('nombre', type=str)
    dosis = request.args.get('dosis', type=str)
    frecuencia = request.args.get('frecuencia', type=str)
    fecha_receta = request.args.get('fecha_receta', type=str)

    if not all([atencion_id, nombre, dosis, frecuencia, fecha_receta]):
        return jsonify({"error": "Faltan datos obligatorios"}), 400

    try:
        # Verificar si la atención existe y si el paciente asistió
        query_check_atencion = """
        MATCH (a:AtencionRealizada {id: $atencion_id})
        RETURN a.asistio AS asistio
        """
        result = conn.execute_query(query_check_atencion, parameters={"atencion_id": atencion_id})

        if not result:
            return jsonify({"error": "Atención no encontrada"}), 404
        
        asistio = result[0]["asistio"]

        if not asistio:
            return jsonify({"error": "El paciente no asistió a la atención"}), 400

        # Obtener el próximo ID disponible para el medicamento
        query_get_last_id = "MATCH (m:Medicamento) RETURN MAX(m.id) AS last_id"
        result = conn.execute_query(query_get_last_id)
        last_id = result[0]["last_id"] if result else 0
        medicamento_id = last_id + 1

        # Crear el medicamento
        query = """
        MATCH (a:AtencionRealizada {id: $atencion_id})
        CREATE (m:Medicamento {id: $medicamento_id, nombre: $nombre, dosis: $dosis, 
                               frecuencia: $frecuencia, fechaReceta: $fecha_receta})
        CREATE (m)-[:ASOCIADO_A]->(a)
        RETURN m.id AS medicamento_id
        """
        result = conn.execute_query(query, parameters={
            "medicamento_id": medicamento_id,
            "nombre": nombre,
            "dosis": dosis,
            "frecuencia": frecuencia,
            "fecha_receta": fecha_receta,
            "atencion_id": atencion_id
        })

        return jsonify({"message": "Medicamento creado exitosamente", "data": result}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
#Método PUT: Actualizar un medicamento relacionado con una atención
@app.route('/medicamentos_neo4j', methods=['PUT'])
def update_medicamento():
    # Obtener parámetros
    medicamento_id = request.args.get('medicamento_id', type=int)
    nombre = request.args.get('nombre', type=str)
    dosis = request.args.get('dosis', type=str)
    frecuencia = request.args.get('frecuencia', type=str)
    fecha_receta = request.args.get('fecha_receta', type=str)

    if not all([medicamento_id, nombre, dosis, frecuencia, fecha_receta]):
        return jsonify({"error": "Faltan datos obligatorios"}), 400

    try:
        # Verificar si el medicamento existe
        query_check_medicamento = """
        MATCH (m:Medicamento {id: $medicamento_id})
        RETURN m
        """
        result = conn.execute_query(query_check_medicamento, parameters={"medicamento_id": medicamento_id})

        if not result:
            return jsonify({"error": "Medicamento no encontrado"}), 404

        # Verificar si la atención asociada a este medicamento existe y si asistio es true
        query_check_atencion = """
        MATCH (m:Medicamento {id: $medicamento_id})-[:ASOCIADO_A]->(a:AtencionRealizada)
        WHERE a.asistio = true
        RETURN a
        """
        result = conn.execute_query(query_check_atencion, parameters={"medicamento_id": medicamento_id})

        if not result:
            return jsonify({"error": "La atención asociada no ha sido asistida"}), 400

        # Actualizar los datos del medicamento
        query_update_medicamento = """
        MATCH (m:Medicamento {id: $medicamento_id})
        SET m.nombre = $nombre, m.dosis = $dosis, m.frecuencia = $frecuencia, m.fechaReceta = $fecha_receta
        RETURN m.id AS medicamento_id, m.nombre AS nuevo_nombre, m.dosis AS nueva_dosis, m.frecuencia AS nueva_frecuencia, m.fechaReceta AS nueva_fecha_receta
        """
        result = conn.execute_query(query_update_medicamento, parameters={
            "medicamento_id": medicamento_id,
            "nombre": nombre,
            "dosis": dosis,
            "frecuencia": frecuencia,
            "fecha_receta": fecha_receta
        })

        return jsonify({"message": "Medicamento actualizado exitosamente", "data": result}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
#Método DELETE: Eliminar medicamento
@app.route('/medicamentos_neo4j', methods=['DELETE'])
def delete_medicamento():
    # Obtener el ID del medicamento
    medicamento_id = request.args.get('medicamento_id', type=int)

    if not medicamento_id:
        return jsonify({"error": "Falta el ID del medicamento"}), 400

    try:
        # Verificar que el medicamento existe
        query_check_medicamento = "MATCH (m:Medicamento {id: $medicamento_id}) RETURN m"
        result = conn.execute_query(query_check_medicamento, parameters={"medicamento_id": medicamento_id})

        if not result:
            return jsonify({"error": "Medicamento no encontrado"}), 404

        # Eliminar el medicamento
        query_delete_medicamento = "MATCH (m:Medicamento {id: $medicamento_id}) DETACH DELETE m"
        conn.execute_query(query_delete_medicamento, parameters={"medicamento_id": medicamento_id})

        return jsonify({"message": "Medicamento eliminado exitosamente"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
#-------------------------------EXAMENES
#Método GET: Obtener todos los exámenes
@app.route('/examenes_neo4j', methods=['GET'])
def get_examenes():
    # Obtener parámetros opcionales
    examen_id = request.args.get('examen_id', type=int)
    atencion_id = request.args.get('atencion_id', type=int)

    try:
        # Consulta base
        query = """
        MATCH (e:Examen)-[:ASOCIADO_A]->(a:AtencionRealizada)-[:ATENDIDO_POR]->(p:Paciente)
        """

        # Agregar filtros dinámicos
        filters = []
        if examen_id:
            filters.append("e.id = $examen_id")
        if atencion_id:
            filters.append("a.id = $atencion_id")
        
        if filters:
            query += " WHERE " + " AND ".join(filters)
        
        # Campos a retornar
        query += """
        RETURN e.id AS examen_id, e.tipo AS tipo, e.fechaSolicitud AS fecha_solicitud,
               e.fechaResultado AS fecha_resultado, e.resultados AS resultados,
               a.id AS atencion_id, p.nombre AS paciente
        """

        # Ejecutar consulta
        result = conn.execute_query(query, parameters={
            "examen_id": examen_id,
            "atencion_id": atencion_id
        })

        # Formatear resultados
        examenes = [{"examen_id": record["examen_id"],
                     "tipo": record["tipo"],
                     "fecha_solicitud": record["fecha_solicitud"],
                     "fecha_resultado": record["fecha_resultado"],
                     "resultados": record["resultados"],
                     "atencion_id": record["atencion_id"],
                     "paciente": record["paciente"]} for record in result]

        if not examenes:
            return jsonify({"error": "No se encontraron exámenes"}), 404

        return jsonify(examenes), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    

# Método POST: Crear un nuevo examen
@app.route('/examenes_neo4j', methods=['POST'])
def create_examen():
    # Obtener los parámetros desde la URL
    atencion_id = request.args.get('atencion_id', type=int)
    tipo = request.args.get('tipo', type=str)
    fecha_solicitud = request.args.get('fechaSolicitud', type=str)
    fecha_resultado = request.args.get('fechaResultado', type=str)
    resultados = request.args.get('resultados', type=str)

    # Verificar que los parámetros sean proporcionados
    if not atencion_id or not tipo or not fecha_solicitud or not fecha_resultado or not resultados:
        return jsonify({"error": "Todos los parámetros son obligatorios"}), 400

    try:
        # Obtener el próximo ID disponible para el nuevo examen
        query_get_last_id = """
        MATCH (e:Examen)
        RETURN MAX(e.id) AS last_id
        """
        result = conn.execute_query(query_get_last_id)
        last_id = result[0]["last_id"] if result else 0
        examen_id = last_id + 1  # Generar el siguiente ID automáticamente

        # Consultar si la atención existe y si el paciente asistió
        query_check_atencion = """
        MATCH (a:AtencionRealizada {id: $atencion_id})-[:ATENDIDO_POR]->(p:Paciente)
        WHERE a.asistio = true
        RETURN p.id AS paciente_id
        """
        result_check = conn.execute_query(query_check_atencion, parameters={"atencion_id": atencion_id})

        if not result_check:
            return jsonify({"error": "La atención no existe o el paciente no asistió"}), 404

        paciente_id = result_check[0]["paciente_id"]

        # Crear el nuevo examen y establecer las relaciones
        query_create_examen = """
        MATCH (p:Paciente {id: $paciente_id}), (a:AtencionRealizada {id: $atencion_id})
        CREATE (e:Examen {id: $examen_id, tipo: $tipo, fechaSolicitud: $fecha_solicitud, 
                          fechaResultado: $fecha_resultado, resultados: $resultados})
        CREATE (e)-[:REALIZADO_A]->(p)
        CREATE (e)-[:ASOCIADO_A]->(a)
        RETURN e.id AS examen_id, e.tipo AS tipo, e.fechaSolicitud AS fecha_solicitud,
               e.fechaResultado AS fecha_resultado, e.resultados AS resultados, p.id AS paciente_id
        """
        result = conn.execute_query(
            query_create_examen,
            parameters={
                "examen_id": examen_id,
                "tipo": tipo,
                "fecha_solicitud": fecha_solicitud,
                "fecha_resultado": fecha_resultado,
                "resultados": resultados,
                "paciente_id": paciente_id,
                "atencion_id": atencion_id,
            },
        )

        return jsonify({"message": "Examen creado exitosamente", "data": result}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# Método PUT: Actualizar un examen existente
@app.route('/examenes_neo4j', methods=['PUT'])
def update_examen():
    # Obtener los parámetros de la query string
    examen_id = request.args.get('examen_id', type=int)
    tipo = request.args.get('tipo', type=str)
    fecha_solicitud = request.args.get('fechaSolicitud', type=str)
    fecha_resultado = request.args.get('fechaResultado', type=str)
    resultados = request.args.get('resultados', type=str)

    if not examen_id:
        return jsonify({"error": "El examen_id es obligatorio"}), 400

    try:
        # Actualizar los detalles del examen
        query = """
        MATCH (e:Examen {id: $examen_id})
        SET e.tipo = $tipo, e.fechaSolicitud = $fecha_solicitud, e.fechaResultado = $fecha_resultado, e.resultados = $resultados
        RETURN e.id AS examen_id, e.tipo AS tipo, e.fechaSolicitud AS fecha_solicitud,
               e.fechaResultado AS fecha_resultado, e.resultados AS resultados
        """
        result = conn.execute_query(
            query,
            parameters={
                "examen_id": examen_id,
                "tipo": tipo,
                "fecha_solicitud": fecha_solicitud,
                "fecha_resultado": fecha_resultado,
                "resultados": resultados,
            },
        )

        if not result:
            return jsonify({"error": "Examen no encontrado"}), 404

        return jsonify({"message": "Examen actualizado exitosamente", "data": result}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
# Método DELETE: Eliminar un examen
@app.route('/examenes_neo4j', methods=['DELETE'])
def delete_examen():
    # Obtener el ID del examen desde la query string
    examen_id = request.args.get('examen_id', type=int)

    if not examen_id:
        return jsonify({"error": "El examen_id es obligatorio"}), 400

    try:
        # Consultar si el examen existe
        query_check = """
        MATCH (e:Examen {id: $examen_id})
        RETURN e
        """
        result_check = conn.execute_query(query_check, parameters={"examen_id": examen_id})

        if not result_check:
            return jsonify({"error": "Examen no encontrado"}), 404

        # Eliminar el examen y sus relaciones
        query_delete = """
        MATCH (e:Examen {id: $examen_id})
        DETACH DELETE e
        """
        conn.execute_query(query_delete, parameters={"examen_id": examen_id})

        return jsonify({"message": "Examen eliminado exitosamente"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)



