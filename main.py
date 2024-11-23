from flask import Flask, request, jsonify
import pymysql

app = Flask(__name__)

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
def get_paciente(id):
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
def create_paciente():
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
def update_paciente():
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
def delete_paciente():
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


if __name__ == '__main__':
    app.run(debug=True)



