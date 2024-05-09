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
    cur.execute('SELECT * FROM "изображения_пациентов" WHERE пациентid = %s', (patient_id,))
    patient_img = cur.fetchone()
    cur.close
    return render_template('personal.html', patient=patient, patient_img=patient_img)


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
        cur.execute('''
            SELECT препараты."название_препарата", "Пациенты препараты"."начало_приёма", "Пациенты препараты"."конец_приёма", "Пациенты препараты"."дозировка"
            FROM препараты
            JOIN "Пациенты препараты" ON препараты."препаратid" = "Пациенты препараты"."препаратid"
            WHERE "Пациенты препараты"."пациентid" = %s;
        ''', (patient_id,))
        prescriptions = cur.fetchall()

        data = {"prescriptions": prescriptions, 'patient_id': patient_id}

        return render_template('prescriptions.html', data=data)


@app.route('/patient/<int:patient_id>/prescriptions/<int:prescription_id>/edit', methods=['GET'])
def edit_prescription(patient_id, prescription_id):
    with conn.cursor() as cur:
        cur.execute('SELECT название_препарата, начало_приёма, конец_приёма, дозировка FROM "Пациенты препараты" JOIN препараты ON "Пациенты препараты"."препаратid" = препараты."препаратid" WHERE "Пациенты препараты"."пациентid" = %s AND "Пациенты препараты"."препаратid" = %s;', (patient_id, prescription_id))
        prescription = cur.fetchone()
        data = { 'patient_id': patient_id}

        if prescription:
            return render_template('edit_prescription.html', prescription=prescription, patient_id=patient_id, prescription_id=prescription_id, data=data)
        else:
            return render_template('error.html', message='Препарат не найден')


@app.route('/patient/<int:patient_id>/prescriptions/<int:prescription_id>/update', methods=['POST'])
def update_prescription(patient_id, prescription_id):
    if request.method == 'POST':
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        dosage = request.form['dosage']

        with conn.cursor() as cur:
            cur.execute("UPDATE \"Пациенты препараты\" SET \"начало_приёма\" = %s, \"конец_приёма\" = %s, \"дозировка\" = %s WHERE \"пациентid\" = %s AND \"препаратid\" = %s", (start_date, end_date, dosage, patient_id, prescription_id))
            conn.commit()
            return redirect(url_for('get_prescriptions', patient_id=patient_id))


@app.route('/patient/<int:patient_id>/prescriptions/<int:prescription_id>/delete', methods=['POST'])
def delete_prescription(patient_id, prescription_id):
    with conn.cursor() as cur:
        cur.execute('DELETE FROM "Пациенты препараты" WHERE "пациентid" = %s AND "препаратid" = %s', (patient_id, prescription_id))
        conn.commit()
        return redirect(url_for('get_prescriptions', patient_id=patient_id))

@app.route('/patient/<int:patient_id>/prescriptions/add', methods=['GET'])
def add_prescription_form(patient_id):
    with conn.cursor() as cur:
        cur.execute('SELECT препаратid, название_препарата FROM препараты;')
        medicines = cur.fetchall()
        data = { "medicines": medicines, 'patient_id': patient_id}

    return render_template('add_prescription.html', data=data, patient_id=patient_id)

@app.route('/patient/<int:patient_id>/prescriptions/create', methods=['POST'])
def create_prescription(patient_id):
    if request.method == 'POST':
        medicine_id = request.form['medicine']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        dosage = request.form['dosage']
        
        with conn.cursor() as cur:
            cur.execute('INSERT INTO "Пациенты препараты" (пациентid, препаратid, начало_приёма, конец_приёма, дозировка) VALUES (%s, %s, %s, %s, %s)', (patient_id, medicine_id, start_date, end_date, dosage))
            conn.commit()
            return redirect(url_for('get_prescriptions', patient_id=patient_id))


@app.route('/patient/<int:patient_id>/procedures', methods=['GET'])
def get_procedures(patient_id):
    with conn.cursor() as cur:
        cur.execute('''
            SELECT процедуры, процедуры.название_процедуры, "Пациенты процедуры"."начало_процедуры", "Пациенты процедуры"."конец_процедуры"
            FROM процедуры
            JOIN "Пациенты процедуры" ON процедуры.процедураid = "Пациенты процедуры".процедураid
            WHERE "Пациенты процедуры".пациентid = %s;
        ''', (patient_id,))
        procedures = cur.fetchall()

        data = {"procedures": procedures, 'patient_id': patient_id}

        return render_template('procedures.html', data=data)


@app.route('/patient/<int:patient_id>/procedures/<int:procedure_id>/edit', methods=['GET'])
def edit_procedure(patient_id, procedure_id):
    # Получаем список процедур из базы данных
    with conn.cursor() as cur:
        cur.execute('SELECT процедураid, название_процедуры FROM процедуры;')
        procedures = cur.fetchall()

        # Получаем текущую процедуру для редактирования
        cur.execute('SELECT название_процедуры, начало_процедуры, конец_процедуры FROM "Пациенты процедуры" JOIN процедуры ON "Пациенты процедуры".процедураid = процедуры.процедураid WHERE "Пациенты процедуры".пациентid = %s AND "Пациенты процедуры".процедураid = %s;', (patient_id, procedure_id))
        procedure = cur.fetchone()
        data = {
            'patient_id': patient_id,
            'procedure_id': procedure_id
        }

        if procedure:
            return render_template('edit_procedure.html', data=data, patient_id=patient_id, procedure_id=procedure_id, procedures=procedures, procedure=procedure)
        else:
            return render_template('error.html', message='Процедура не найдена')

@app.route('/patient/<int:patient_id>/procedures/<int:procedure_id>/update', methods=['POST'])
def update_procedure(patient_id, procedure_id):
    if request.method == 'POST':
        procedure = request.form['procedure']
        start_time = request.form['start_time']
        end_time = request.form['end_time']


        with conn.cursor() as cur:
            data = {
                'patient_id': patient_id,
                'procedure_id': procedure_id
            }
            cur.execute("UPDATE \"Пациенты процедуры\" SET процедураid = %s, начало_процедуры = %s, конец_процедуры = %s WHERE пациентid = %s AND процедураid = %s", (procedure, start_time, end_time, patient_id, procedure_id))
            conn.commit()
            return redirect(url_for('get_procedures', data=data, patient_id=patient_id))


@app.route('/patient/<int:patient_id>/procedures/<int:procedure_id>/delete', methods=['POST'])
def delete_procedure(patient_id, procedure_id):
    with conn.cursor() as cur:
        data = {
            'patient_id': patient_id,
            'procedure_id': procedure_id
        }
        cur.execute('DELETE FROM "Пациенты процедуры" WHERE пациентid = %s AND процедураid = %s', (patient_id, procedure_id))
        conn.commit()
        return redirect(url_for('get_procedures', patient_id=patient_id, data=data))
    

@app.route('/patient/<int:patient_id>/procedures/add', methods=['GET'])
def add_procedure_form(patient_id):
    with conn.cursor() as cur:
        data = {
            'patient_id': patient_id
        }
        cur.execute('SELECT процедураid, название_процедуры FROM процедуры;')
        procedures = cur.fetchall()

    return render_template('add_procedure.html', patient_id=patient_id, procedures=procedures, data=data)

@app.route('/patient/<int:patient_id>/procedures/create', methods=['POST'])
def create_procedure(patient_id):
    if request.method == 'POST':
        procedure_id = request.form['procedure']
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        
        with conn.cursor() as cur:
            cur.execute('INSERT INTO "Пациенты процедуры" (пациентid, процедураid, начало_процедуры, конец_процедуры) VALUES (%s, %s, %s, %s)', (patient_id, procedure_id, start_time, end_time))
            conn.commit()
            return redirect(url_for('get_procedures', patient_id=patient_id))
        

if __name__ == "__main__":
    app.run(debug=True)

conn.close()
