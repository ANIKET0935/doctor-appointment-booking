from flask import Flask, render_template, request, redirect, session, url_for, flash
from flask_mysqldb import MySQL
from datetime import datetime, time, timedelta
from MySQLdb.cursors import DictCursor

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MySQL Config
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'docbook'

mysql = MySQL(app)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register/patient', methods=['GET', 'POST'])
def register_patient():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        age = request.form['age']
        gender = request.form['gender']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO patients (name, email, password, age, gender) VALUES (%s, %s, %s, %s, %s)", (name, email, password, age, gender))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('login'))
    return render_template('register_patient.html')

@app.route('/register/doctor', methods=['GET', 'POST'])
def register_doctor():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        specialization = request.form['specialization']
        experience = request.form['experience']
        available_time = request.form['available_time']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO doctors (name, email, password, specialization, experience, available_time) VALUES (%s, %s, %s, %s, %s, %s)", (name, email, password, specialization, experience, available_time))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('login'))
    return render_template('register_doctor.html')

@app.route('/dashboard/patient')
def patient_dashboard():
    if 'patient_id' in session:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM doctors")
        doctors = cur.fetchall()
        cur.close()
        return render_template('patient_dashboard.html', doctors=doctors)
    return redirect(url_for('login'))
@app.route('/dashboard/doctor')
def doctor_dashboard():
    if 'doctor_id' in session:
        cur = mysql.connection.cursor(DictCursor)  # <-- must use DictCursor
        cur.execute("""
            SELECT a.id, p.name, a.appointment_date, a.time_slot, a.status
            FROM appointments a
            JOIN patients p ON a.patient_id = p.id
            WHERE doctor_id = %s
        """, (session['doctor_id'],))
        appointments = cur.fetchall()
        cur.close()
        return render_template('doctor_dashboard.html', appointments=appointments)
    return redirect(url_for('login'))

@app.route('/book_appointment/<int:doctor_id>', methods=['GET', 'POST'])
def book_appointment(doctor_id):
    if 'patient_id' not in session:
        return redirect(url_for('login'))

    cur = mysql.connection.cursor(DictCursor)

    if request.method == 'POST':
        date = request.form['appointment_date']
        time_slot = request.form['time_slot']
        cur.execute("""
            INSERT INTO appointments (patient_id, doctor_id, appointment_date, time_slot, status)
            VALUES (%s, %s, %s, %s, 'Pending')
        """, (session['patient_id'], doctor_id, date, time_slot))
        mysql.connection.commit()
        cur.close()
        flash('Appointment booked successfully!', 'success')
        return redirect(url_for('patient_dashboard'))

    # Generate 30-minute time slots from 9:00 AM to 5:00 PM
    start_time = time(9, 0)
    end_time = time(17, 0)
    slots = []
    current = datetime.combine(datetime.today(), start_time)
    end = datetime.combine(datetime.today(), end_time)

    while current <= end:
        slots.append(current.strftime("%H:%M"))
        current += timedelta(minutes=30)

    selected_date = request.args.get('date', datetime.today().strftime('%Y-%m-%d'))
    cur.execute("""
        SELECT time_slot FROM appointments
        WHERE doctor_id = %s AND appointment_date = %s
    """, (doctor_id, selected_date))
    booked_slots = [row['time_slot'] for row in cur.fetchall()]
    cur.close()

    available_slots = [slot for slot in slots if slot not in booked_slots]

    return render_template('book_appointment.html', doctor_id=doctor_id, time_slots=available_slots, selected_date=selected_date)

@app.route('/add_prescription/<int:appointment_id>', methods=['GET', 'POST'])
def add_prescription(appointment_id):
    if request.method == 'POST':
        text = request.form['prescription_text']
        date_issued = datetime.today().date()
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO prescriptions (appointment_id, prescription_text, date_issued) VALUES (%s, %s, %s)", (appointment_id, text, date_issued))
        cur.execute("UPDATE appointments SET status='Completed' WHERE id=%s", (appointment_id,))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('doctor_dashboard'))
    return render_template('add_prescription.html', appointment_id=appointment_id)

@app.route('/doctor_info')
def doctor_info():
    specialization = request.args.get('specialization', 'All')
    cur = mysql.connection.cursor()
    if specialization == 'All':
        cur.execute("SELECT * FROM doctors")
    else:
        cur.execute("SELECT * FROM doctors WHERE specialization=%s", (specialization,))
    doctors = cur.fetchall()
    cur.close()
    return render_template('doctor_info.html', doctors=doctors)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']

        if role == 'doctor':
            doctor = get_doctor_from_db(email, password)
            if doctor:
                session['doctor_id'] = doctor['id']
                session['user'] = doctor['name']
                session['role'] = 'doctor'
                return redirect(url_for('doctor_dashboard'))

        elif role == 'patient':
            patient = get_patient_from_db(email, password)
            if patient:
                session['patient_id'] = patient['id']
                session['user'] = patient['name']
                session['role'] = 'patient'
                return redirect(url_for('patient_dashboard'))

        flash("Invalid credentials", "danger")
    
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

def get_doctor_from_db(email, password):
    cur = mysql.connection.cursor(DictCursor)
    cur.execute("SELECT * FROM doctors WHERE email = %s AND password = %s", (email, password))
    doctor = cur.fetchone()
    cur.close()
    return doctor

def get_patient_from_db(email, password):
    cur = mysql.connection.cursor(DictCursor)
    cur.execute("SELECT * FROM patients WHERE email = %s AND password = %s", (email, password))
    patient = cur.fetchone()
    cur.close()
    return patient

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
