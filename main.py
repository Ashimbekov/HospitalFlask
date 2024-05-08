from flask import Flask, render_template, jsonify, request, url_for, redirect
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


@app.route('/patient/<int:patient_id>/personal_info', methods=['GET'])
def get_personal_info(patient_id):
    with conn.cursor() as cur:
        cur.execute("SELECT имя, фамилия, отчество, пол, дата_рождения FROM пациенты WHERE пациентid = %s;", (patient_id,))
        patient_data = cur.fetchone()

        if patient_data:
            data = {
                "name": patient_data[0],
                "surname": patient_data[1],
                "patronymic": patient_data[2],
                "gender": patient_data[3],
                "birthdate": str(patient_data[4]),
                "patient_id": patient_id 
            }
            return render_template('personalInfo.html', data=data)

        return render_template('error.html', message='Пациент не найден')


@app.route('/patient/<int:patient_id>/edit', methods=['POST'])
def edit_personal_info(patient_id):
    if request.method == 'POST':
        name = request.form['name']
        surname = request.form['surname']
        patronymic = request.form['patronymic']
        birthdate = request.form['birthdate']
        
        with conn.cursor() as cur:
            cur.execute("UPDATE пациенты SET имя = %s, фамилия = %s, отчество = %s, дата_рождения = %s WHERE пациентid = %s", (name, surname, patronymic, birthdate, patient_id))
            conn.commit()

        return redirect(url_for('get_personal_info', patient_id=patient_id))

        

@app.route('/patient/<int:patient_id>/contact', methods=['GET'])
def get_contact(patient_id):
    with conn.cursor() as cur:
        cur.execute("SELECT телефон, почта FROM пациенты WHERE пациентid = %s;", (patient_id,))
        patient_data = cur.fetchone()

        if patient_data:
            data = {
                "phone": patient_data[0],
                "email": patient_data[1],
                "patient_id": patient_id 
            }
            return render_template('contact.html', data=data)

        return render_template('error.html', message='Пациент не найден')


@app.route('/patient/<int:patient_id>/edit_contact', methods=['POST'])
def edit_contact(patient_id):
    if request.method == 'POST':
        phone = request.form['phone']
        email = request.form['email']
        
        with conn.cursor() as cur:
            cur.execute("UPDATE пациенты SET телефон = %s, почта = %s WHERE пациентid = %s", (phone, email, patient_id))
            conn.commit()

        return redirect(url_for('get_contact', patient_id=patient_id))


# @app.route('/patient/<int:patient_id>/diagnosis', methods=['GET'])
# def get_diagnosis(patient_id):
#     with conn.cursor() as cur:
#         cur.execute('SELECT диагнозы.название_диагноза FROM диагнозы JOIN "диагнозы пациентов" ON диагнозы.диагнозid = "диагнозы пациентов".диагнозid WHERE "диагнозы пациентов".пациентid = %s;', (patient_id,))
#         patient_diagnosis = cur.fetchone()

#         if patient_diagnosis:
#             data = {
#                 "diagnosis_name" : patient_diagnosis[0],
#             }
#             return render_template('diagnosis.html', data=data)

#         return render_template('error.html', message='Диагноз не найден')


@app.route('/patient/<int:patient_id>/diagnosis', methods=['GET'])
def get_diagnosis(patient_id):
    with conn.cursor() as cur:
        cur.execute('SELECT диагнозы.диагнозid, диагнозы.название_диагноза FROM диагнозы JOIN "диагнозы пациентов" ON диагнозы.диагнозid = "диагнозы пациентов".диагнозid WHERE "диагнозы пациентов".пациентid = %s;', (patient_id,))
        diagnoses = cur.fetchall()
        cur.execute('SELECT * FROM диагнозы')
        dis = cur.fetchall()
        data = {
            'patient_id': patient_id
        }

    return render_template('diagnosis.html', patient_id=patient_id, diagnoses=diagnoses, dis=dis, data=data)

# @app.route('/patient/<int:patient_id>/diagnosis/add', methods=['POST'])
# def add_diagnosis(patient_id):
#     if request.method == 'POST':
#         diagnosis_name = request.form['diagnosis_name']

#         with conn.cursor() as cur:
#             cur.execute('INSERT INTO диагнозы (название_диагноза) VALUES (%s) RETURNING диагнозid', (diagnosis_name,))
#             diagnosis_id = cur.fetchone()[0]
#             cur.execute('INSERT INTO "диагнозы пациентов" (пациентid, диагнозid) VALUES (%s, %s)', (patient_id, diagnosis_id))
#         conn.commit()

#     return redirect(url_for('get_diagnosis', patient_id=patient_id))



@app.route('/patient/<int:patient_id>/diagnosis/add', methods=['POST'])
def add_diagnosis(patient_id):
    if request.method == 'POST':
        diagnosis_id = request.form['diagnosis_id']

        with conn.cursor() as cur:
            cur.execute('INSERT INTO "диагнозы пациентов" (пациентid, диагнозid) VALUES (%s, %s)', (patient_id, diagnosis_id))
        conn.commit()

    return redirect(url_for('get_diagnosis', patient_id=patient_id))


@app.route('/patient/<int:patient_id>/diagnosis/edit/<int:diagnosis_id>', methods=['POST'])
def edit_diagnosis(patient_id, diagnosis_id):
    if request.method == 'POST':
        new_diagnosis_name = request.form['new_diagnosis_name']

        with conn.cursor() as cur:
            cur.execute('UPDATE диагнозы SET название_диагноза = %s WHERE диагнозid = %s', (new_diagnosis_name, diagnosis_id))
        conn.commit()

    return redirect(url_for('get_diagnosis', patient_id=patient_id))

@app.route('/patient/<int:patient_id>/diagnosis/delete/<int:diagnosis_id>', methods=['POST'])
def delete_diagnosis(patient_id, diagnosis_id):
    if request.method == 'POST':
        with conn.cursor() as cur:
            cur.execute('DELETE FROM "диагнозы пациентов" WHERE диагнозid = %s', (diagnosis_id,))
            cur.execute('DELETE FROM диагнозы WHERE диагнозid = %s', (diagnosis_id,))
        conn.commit()

    return redirect(url_for('get_diagnosis', patient_id=patient_id))


@app.route('/patient/<int:patient_id>/prescriptions', methods=['GET'])
def get_prescriptions(patient_id):
    with conn.cursor() as cur:
        cur.execute('SELECT препараты.название_препарата, "Пациенты препараты"."начало_приёма", "Пациенты препараты"."конец_приёма", "Пациенты препараты".дозировка FROM препараты JOIN "Пациенты препараты" ON препараты.препаратid = "Пациенты препараты".препаратid WHERE "Пациенты препараты".пациентid = %s;', (patient_id,))
        prescriptions = cur.fetchall()

        data = {"prescriptions": prescriptions, "patient_id": patient_id}
        return render_template('prescriptions.html', data=data)

@app.route('/patient/<int:patient_id>/prescriptions/edit_prescription', methods=['POST'])
def edit_prescription(patient_id):
    if request.method == 'POST':
        prescription_id = request.form['prescription_id']
        prescription_name = request.form['prescription_name']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        dosage = request.form['dosage']

        with conn.cursor() as cur:
            cur.execute("UPDATE препараты SET название_препарата = %s, начало_приёма = %s, конец_приёма = %s, дозировка = %s WHERE препаратid = %s", (prescription_name, start_date, end_date, dosage, prescription_id))
            conn.commit()

        return redirect(url_for('get_prescriptions', patient_id=patient_id))
    
@app.route('/add_prescription', methods=['POST'])
def add_prescription():
    if request.method == 'POST':
        return redirect(url_for('prescriptions'))

@app.route('/patient/<int:patient_id>/procedures', methods=['GET'])
def get_procedures(patient_id):
    with conn.cursor() as cur:
        cur.execute('''
            SELECT процедуры.название_процедуры, "Пациенты процедуры"."начало_процедуры", "Пациенты процедуры"."конец_процедуры"
            FROM процедуры
            JOIN "Пациенты процедуры" ON процедуры.процедураid = "Пациенты процедуры".процедураid
            WHERE "Пациенты процедуры".пациентid = %s;
        ''', (patient_id,))
        procedures = cur.fetchall()

        data = {"procedures": procedures}
        return render_template('procedures.html', data=data)


if __name__ == "__main__":
    app.run(debug=True)

conn.close()
