from flask import Flask, render_template, jsonify
import psycopg2

app = Flask(__name__)

conn = psycopg2.connect(
    dbname='hospital',
    user='postgres',
    password='nurik',
    host='localhost'
)
cur = conn.cursor()


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/patients')
def patients():
    cur.execute("SELECT * FROM пациенты")
    patients = cur.fetchall()
    return render_template('patients.html', patients=patients)

@app.route('/patient/<int:patient_id>', methods=['GET'])
def personal(patient_id):
    cur.execute("SELECT * FROM пациенты WHERE пациентid = %s", (patient_id,))
    patient = cur.fetchone()
    cur.close
    return render_template('personal.html', patient=patient)


# @app.route('/patient/<int:patient_id>/personal_info', methods=['GET', 'POST'])
# def personal_info(patient_id):
#     if request.method == 'GET':
#         # Здесь ваш код для получения персональной информации о пациенте с patient_id из базы данных
#         personal_info = [...]  # Получите персональную информацию о пациенте
#         return render_template('personal_info.html', personal_info=personal_info)

#     elif request.method == 'POST':
#         # Здесь ваш код для обработки изменений в персональной информации и сохранения их в базе данных
#         return redirect(url_for('personal_info', patient_id=patient_id))


@app.route('/patient/<int:patient_id>/personal_info', methods=['GET'])
def get_personal_info(patient_id):
    
    cur.execute("SELECT имя, фамилия, отчество, пол, дата_рождения FROM пациенты WHERE пациентid = %s;", (patient_id,))
    patient_data = cur.fetchone()
    
    if patient_data:
        data = {
            "name": patient_data[0],
            "surname": patient_data[1],
            "patronymic": patient_data[2],
            "gender": patient_data[3],
            "birthdate": str(patient_data[4])
        }
        cur.close()
        return render_template('personalInfo.html', data=data)


@app.route('/patient/<int:patient_id>/contact', methods=['GET'])
def get_contact(patient_id):
    
    cur.execute("SELECT телефон, почта FROM пациенты WHERE пациентid = %s;", (patient_id,))
    patient_data = cur.fetchone()
    
    if patient_data:
        data = {
            "phone": patient_data[0],
            "email": patient_data[1],
        }
        cur.close()
        return render_template('contact.html', data=data)


@app.route('/patient/<int:patient_id>/diagnosis', methods=['GET'])
def get_diagnosis(patient_id):
    cur.execute('SELECT диагнозы.название_диагноза FROM диагнозы JOIN "диагнозы пациентов" ON диагнозы.диагнозid = "диагнозы пациентов".диагнозid WHERE "диагнозы пациентов".пациентid = %s;', (patient_id,))
    patient_diagnosis = cur.fetchone()
    if patient_diagnosis:
        data = {
            "diagnosis_name" : patient_diagnosis[0],

        }
        cur.close()
        return render_template('diagnosis.html', data=data)


@app.route('/patient/<int:patient_id>/prescriptions', methods=['GET'])
def get_prescriptions(patient_id):
    cur.execute('SELECT препараты.название_препарата, "Пациенты препараты"."начало_приёма", "Пациенты препараты"."конец_приёма", "Пациенты препараты".дозировка FROM препараты JOIN "Пациенты препараты" ON препараты.препаратid = "Пациенты препараты".препаратid WHERE "Пациенты препараты".пациентid = %s;', (patient_id,))
    
    prescriptions = cur.fetchall()

    data = {"prescriptions": prescriptions}

    cur.close()
    return render_template('prescriptions.html', data=data)

@app.route('/patient/<int:patient_id>/procedures', methods=['GET'])
def get_procedures(patient_id):
    cur.execute('''
        SELECT процедуры.название_процедуры, "Пациенты процедуры"."начало_процедуры", "Пациенты процедуры"."конец_процедуры"
        FROM процедуры
        JOIN "Пациенты процедуры" ON процедуры.процедураid = "Пациенты процедуры".процедураid
        WHERE "Пациенты процедуры".пациентid = %s;
    ''', (patient_id,))
    
    procedures = cur.fetchall()

    data = {"procedures": procedures}

    cur.close()
    return render_template('procedures.html', data=data)


if __name__ == "__main__":
    app.run(debug=True)

conn.close()
