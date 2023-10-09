import mysql.connector
from mysql.connector import Error
from datetime import datetime


def conectar_db():
    try:
        conexion = mysql.connector.connect(
            host='localhost',
            database='hospital',
            user='root',
            password='poligran'
        )
        if conexion.is_connected():
            print("Conexión a la base de datos exitosa.")
            return conexion
    except Error as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None


def iniciar_sesion_administrador(conexion):
    username = input("Nombre de usuario del administrador: ")
    password = input("Contraseña del administrador: ")

    try:
        cursor = conexion.cursor()
        cursor.execute("SELECT id, name FROM administrators WHERE username = %s AND password = %s",
                       (username, password))
        administrador = cursor.fetchone()
        cursor.close()

        if administrador:
            print(f"Bienvenido, {administrador[1]} (ID: {administrador[0]})")
            return administrador[0]
        else:
            print("Credenciales incorrectas. Por favor, vuelva a intentarlo.")
            return None
    except Error as e:
        print(f"Error al iniciar sesión como administrador: {e}")
        return None


def gestionar_citas(conexion, administrador_id):
    while True:
        print("\nOpciones:")
        print("1. Crear nueva cita")
        print("2. Reagendar cita")
        print("3. Cancelar cita")
        print("4. Consultar y modificar citas de un paciente")
        print("5. Salir")

        opcion = input("Seleccione una opción: ")

        if opcion == '1':
            crear_nueva_cita(conexion, administrador_id)
        elif opcion == '2':
            reagendar_cita(conexion)
        elif opcion == '3':
            cancelar_cita(conexion)
        elif opcion == '4':
            consultar_y_modificar_citas_paciente(conexion, administrador_id)
        elif opcion == '5':
            print("Saliendo del programa.")
            break
        else:
            print("Opción no válida. Por favor, seleccione una opción válida.")


def crear_nueva_cita(conexion, administrador_id):
    try:
        cursor = conexion.cursor()

        # Recopilar información del paciente
        paciente_id = int(input("Ingrese el ID del paciente: "))
        cursor.execute("SELECT names FROM patients WHERE id = %s", (paciente_id,))
        paciente_info = cursor.fetchone()

        if not paciente_info:
            print("Paciente no encontrado. Verifique el ID del paciente.")
            return

        print(f"Paciente encontrado: {paciente_info[0]}")

        # Recopilar información del médico
        doctor_id = int(input("Ingrese el ID del médico: "))
        cursor.execute("SELECT names, specialty_id FROM doctors WHERE id = %s", (doctor_id,))
        doctor_info = cursor.fetchone()

        if not doctor_info:
            print("Médico no encontrado. Verifique el ID del médico.")
            return

        print(f"Médico encontrado: {doctor_info[0]} (Especialidad: {doctor_info[1]})")

        confirmacion = input("¿Desea registrar la cita para este paciente (S/N)? ").strip().lower()

        if confirmacion == 's':
            # Recopilar fecha y hora de la cita
            fecha_hora_cita = input("Ingrese la fecha y hora de la cita (YYYY-MM-DD HH:MM): ")

            # Verificar disponibilidad del médico (puedes agregar esta lógica)

            # Obtener la fecha y hora actual
            fecha_actual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # Insertar nueva cita en la base de datos con la fecha actual en created_at
            cursor.execute(
                "INSERT INTO appointments (doctor_id, patient_id, appointment_status_id, administrator_id, appointment_date, created_at) VALUES (%s, %s, %s, %s, %s, %s)",
                (doctor_id, paciente_id, 1, administrador_id, fecha_hora_cita, fecha_actual)
            )
            conexion.commit()

            print(f"Cita creada con éxito para {paciente_info[0]} con el médico {doctor_info[0]} en {fecha_hora_cita}.")
        else:
            print("Registro de cita cancelado.")

    except Error as e:
        conexion.rollback()
        print(f"Error al crear la cita: {e}")
    finally:
        cursor.close()


def reagendar_cita(conexion):
    try:
        cursor = conexion.cursor()

        # Solicitar el ID de la cita que se desea reagendar
        cita_id = int(input("Ingrese el ID de la cita que desea reagendar: "))

        # Verificar si la cita existe y obtener los detalles
        cursor.execute("SELECT a.id, d.names AS doctor_name, p.names AS patient_name, s.status AS appointment_status, a.appointment_date FROM appointments a JOIN doctors d ON a.doctor_id = d.id JOIN patients p ON a.patient_id = p.id JOIN appointment_status s ON a.appointment_status_id = s.id WHERE a.id = %s", (cita_id,))
        cita = cursor.fetchone()

        if not cita:
            print("Cita no encontrada. Verifique el ID de la cita.")
            return

        print("Detalles de la cita a reagendar:")
        print(f"ID de la cita: {cita[0]}")
        print(f"Médico: {cita[1]}")
        print(f"Paciente: {cita[2]}")
        print(f"Estado de la cita: {cita[3]}")
        print(f"Fecha y hora actual de la cita: {cita[4]}")

        # Solicitar la nueva fecha y hora para la cita
        nueva_fecha_hora = input("Ingrese la nueva fecha y hora de la cita (YYYY-MM-DD HH:MM): ")

        # Verificar disponibilidad del médico (puedes agregar esta lógica)

        # Actualizar la fecha y hora de la cita en la base de datos
        cursor.execute(
            "UPDATE appointments SET appointment_date = %s WHERE id = %s",
            (nueva_fecha_hora, cita_id)
        )
        conexion.commit()

        print(f"Cita reagendada con éxito. Nueva fecha y hora de la cita: {nueva_fecha_hora}")

    except Error as e:
        conexion.rollback()
        print(f"Error al reagendar la cita: {e}")
    finally:
        cursor.close()


def cancelar_cita(conexion):
    try:
        cursor = conexion.cursor()

        # Solicitar el ID de la cita que se desea cancelar
        cita_id = int(input("Ingrese el ID de la cita que desea cancelar: "))

        # Verificar si la cita existe y obtener los detalles con nombres
        cursor.execute("SELECT a.id, d.names AS doctor_name, p.names AS patient_name, s.status AS appointment_status, a.appointment_date FROM appointments a JOIN doctors d ON a.doctor_id = d.id JOIN patients p ON a.patient_id = p.id JOIN appointment_status s ON a.appointment_status_id = s.id WHERE a.id = %s", (cita_id,))
        cita = cursor.fetchone()

        if not cita:
            print("Cita no encontrada. Verifique el ID de la cita.")
            return

        # Mostrar detalles de la cita con nombres
        print("Detalles de la cita a cancelar:")
        print(f"ID de la cita: {cita[0]}")
        print(f"Médico: {cita[1]}")
        print(f"Paciente: {cita[2]}")
        print(f"Estado de la cita: {cita[3]}")
        print(f"Fecha y hora de la cita: {cita[4]}")

        # Confirmar la cancelación de la cita
        confirmacion = input("¿Está seguro de que desea cancelar esta cita (S/N)? ").strip().lower()

        if confirmacion == 's':
            # Cambiar el estado de la cita a "Cancelada" (deberías tener un ID de estado correspondiente en la base de datos)
            cursor.execute(
                "UPDATE appointments SET appointment_status_id = %s WHERE id = %s",
                (2, cita_id)  # Suponemos que el ID 2 corresponde al estado "Cancelada"
            )
            conexion.commit()

            print("Cita cancelada con éxito.")
        else:
            print("Cancelación de cita cancelada.")

    except Error as e:
        conexion.rollback()
        print(f"Error al cancelar la cita: {e}")
    finally:
        cursor.close()


def consultar_y_modificar_citas_paciente(conexion, administrador_id):
    try:
        cursor = conexion.cursor()

        # Solicitar el ID del paciente cuyas citas se desean consultar
        paciente_id = int(input("Ingrese el ID del paciente para consultar sus citas: "))

        # Verificar si el paciente existe
        cursor.execute("SELECT names FROM patients WHERE id = %s", (paciente_id,))
        paciente_info = cursor.fetchone()

        if not paciente_info:
            print("Paciente no encontrado. Verifique el ID del paciente.")
            return

        print(f"Citas de {paciente_info[0]}:")

        # Consultar las citas del paciente
        cursor.execute("SELECT a.id, d.names AS doctor_name, s.status AS appointment_status, a.appointment_date FROM appointments a JOIN doctors d ON a.doctor_id = d.id JOIN appointment_status s ON a.appointment_status_id = s.id WHERE a.patient_id = %s", (paciente_id,))
        citas_paciente = cursor.fetchall()

        if not citas_paciente:
            print("Este paciente no tiene citas programadas.")
            return

        # Mostrar las citas del paciente
        for cita in citas_paciente:
            print(f"ID de la cita: {cita[0]}")
            print(f"Médico: {cita[1]}")
            print(f"Estado de la cita: {cita[2]}")
            print(f"Fecha y hora de la cita: {cita[3]}")
            print()

        # Solicitar el ID de la cita que se desea modificar
        cita_id_modificar = int(input("Ingrese el ID de la cita que desea modificar el estado: "))

        # Verificar si la cita existe
        cursor.execute("SELECT * FROM appointments WHERE id = %s", (cita_id_modificar,))
        cita_modificar = cursor.fetchone()

        if not cita_modificar:
            print("Cita no encontrada. Verifique el ID de la cita.")
            return

        # Solicitar el nuevo estado para la cita
        nuevo_estado = input("Ingrese el nuevo estado de la cita: ")

        # Actualizar el estado de la cita en la base de datos
        cursor.execute(
            "UPDATE appointments SET appointment_status_id = %s WHERE id = %s",
            (nuevo_estado, cita_id_modificar)
        )
        conexion.commit()

        print("Estado de la cita actualizado con éxito.")

    except Error as e:
        conexion.rollback()
        print(f"Error al consultar o modificar las citas del paciente: {e}")
    finally:
        cursor.close()



def main():
    conexion = conectar_db()
    if conexion:
        administrador_id = iniciar_sesion_administrador(conexion)
        if administrador_id:
            gestionar_citas(conexion, administrador_id)
        conexion.close()


if __name__ == "__main__":
    main()
