import streamlit as st
import datetime
import json
import os
import sqlite3
import pandas as pd
from streamlit_calendar import calendar # Import the calendar component

# --- Database Management Class ---
class DatabaseManager:
    def __init__(self, db_name="school_data.db"):
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        self._connect()
        self._create_tables()

    def _connect(self):
        try:
            self.conn = sqlite3.connect(self.db_name, check_same_thread=False)
            self.cursor = self.conn.cursor()
            # print(f"Connected to database: {self.db_name}") # For debugging
        except sqlite3.Error as e:
            st.error(f"Database connection error: {e}")

    def _close(self):
        if self.conn:
            self.conn.close()
            # print("Database connection closed.") # For debugging

    def _create_tables(self):
        self._connect() # Ensure connection is open
        try:
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS students (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    date_of_birth TEXT NOT NULL
                )
            ''')
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS courses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome_corso TEXT NOT NULL UNIQUE,
                    durata TEXT NOT NULL,
                    docente TEXT NOT NULL
                )
            ''')
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS classrooms (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome_aula TEXT NOT NULL UNIQUE,
                    capacita_sedie INTEGER NOT NULL,
                    occupazione_aula TEXT
                )
            ''')
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS course_students (
                    course_id INTEGER,
                    student_id INTEGER,
                    PRIMARY KEY (course_id, student_id),
                    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
                    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
                )
            ''')
            # New table for attendance
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS attendance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER NOT NULL,
                    course_id INTEGER NOT NULL,
                    attendance_date TEXT NOT NULL,
                    status TEXT NOT NULL, -- e.g., 'Present', 'Absent', 'Late', 'Excused'
                    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
                    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
                    UNIQUE(student_id, course_id, attendance_date) -- Ensure only one entry per student, course, and date
                )
            ''')
            self.conn.commit()
            # print("Tables checked/created successfully.") # For debugging
        except sqlite3.Error as e:
            st.error(f"Error creating tables: {e}")
        finally:
            self._close()

    # --- Student Operations ---
    def insert_student(self, name, last_name, date_of_birth):
        self._connect()
        try:
            self.cursor.execute('''
                INSERT INTO students (name, last_name, date_of_birth) VALUES (?, ?, ?)
            ''', (name, last_name, date_of_birth))
            self.conn.commit()
            return self.cursor.lastrowid # Return the ID of the newly inserted student
        except sqlite3.IntegrityError as e:
            st.warning(f"Student '{name} {last_name}' might already exist. Error: {e}")
            return None
        except sqlite3.Error as e:
            st.error(f"Error inserting student: {e}")
            return None
        finally:
            self._close()

    def fetch_students(self):
        self._connect()
        try:
            self.cursor.execute('SELECT id, name, last_name, date_of_birth FROM students')
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            st.error(f"Error fetching students: {e}")
            return []
        finally:
            self._close()
    
    # --- Course Operations ---
    def insert_course(self, nome_corso, durata, docente):
        self._connect()
        try:
            self.cursor.execute('''
                INSERT INTO courses (nome_corso, durata, docente) VALUES (?, ?, ?)
            ''', (nome_corso, durata, docente))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.IntegrityError:
            st.warning(f"Course '{nome_corso}' already exists.")
            return None
        except sqlite3.Error as e:
            st.error(f"Error inserting course: {e}")
            return None
        finally:
            self._close()

    def fetch_courses(self):
        self._connect()
        try:
            self.cursor.execute('SELECT id, nome_corso, durata, docente FROM courses')
            courses_data = self.cursor.fetchall()
            
            # Fetch student assignments for each course
            courses_with_students = []
            for course_id, nome_corso, durata, docente in courses_data:
                self.cursor.execute('''
                    SELECT s.id, s.name, s.last_name, s.date_of_birth
                    FROM students s
                    JOIN course_students cs ON s.id = cs.student_id
                    WHERE cs.course_id = ?
                ''', (course_id,))
                assigned_students_data = self.cursor.fetchall()
                courses_with_students.append((course_id, nome_corso, durata, docente, assigned_students_data))
            return courses_with_students
        except sqlite3.Error as e:
            st.error(f"Error fetching courses: {e}")
            return []
        finally:
            self._close()

    def assign_student_to_course(self, course_id, student_id):
        self._connect()
        try:
            self.cursor.execute('''
                INSERT OR IGNORE INTO course_students (course_id, student_id) VALUES (?, ?)
            ''', (course_id, student_id))
            self.conn.commit()
        except sqlite3.Error as e:
            st.error(f"Error assigning student to course: {e}")
        finally:
            self._close()

    # --- Classroom Operations ---
    def insert_classroom(self, nome_aula, capacita_sedie, occupazione_aula):
        self._connect()
        try:
            # Store occupazione_aula as JSON string
            occupazione_aula_json = json.dumps(occupazione_aula)
            self.cursor.execute('''
                INSERT INTO classrooms (nome_aula, capacita_sedie, occupazione_aula) VALUES (?, ?, ?)
            ''', (nome_aula, capacita_sedie, occupazione_aula_json))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.IntegrityError:
            st.warning(f"Classroom '{nome_aula}' already exists.")
            return None
        except sqlite3.Error as e:
            st.error(f"Error inserting classroom: {e}")
            return None
        finally:
            self._close()

    def fetch_classrooms(self):
        self._connect()
        try:
            self.cursor.execute('SELECT id, nome_aula, capacita_sedie, occupazione_aula FROM classrooms')
            classrooms_data = []
            for aula_id, nome_aula, capacita_sedie, occupazione_aula_json in self.cursor.fetchall():
                # Load occupazione_aula from JSON string
                occupazione_aula = json.loads(occupazione_aula_json) if occupazione_aula_json else {}
                classrooms_data.append((aula_id, nome_aula, capacita_sedie, occupazione_aula))
            return classrooms_data
        except sqlite3.Error as e:
            st.error(f"Error fetching classrooms: {e}")
            return []
        finally:
            self._close()

    def update_classroom_schedule(self, aula_id, occupazione_aula):
        self._connect()
        try:
            occupazione_aula_json = json.dumps(occupazione_aula)
            self.cursor.execute('''
                UPDATE classrooms SET occupazione_aula = ? WHERE id = ?
            ''', (occupazione_aula_json, aula_id))
            self.conn.commit()
        except sqlite3.Error as e:
            st.error(f"Error updating classroom schedule: {e}")
        finally:
            self._close()

    # --- Attendance Operations ---
    def record_attendance(self, student_id, course_id, attendance_date, status):
        self._connect()
        try:
            # Use INSERT OR REPLACE to update if an entry for the same student, course, and date already exists
            self.cursor.execute('''
                INSERT OR REPLACE INTO attendance (student_id, course_id, attendance_date, status)
                VALUES (?, ?, ?, ?)
            ''', (student_id, course_id, attendance_date, status))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            st.error(f"Error recording attendance: {e}")
            return False
        finally:
            self._close()

    def fetch_attendance(self, course_id=None, student_id=None, attendance_date=None):
        self._connect()
        try:
            query = '''
                SELECT
                    a.id,
                    s.name,
                    s.last_name,
                    c.nome_corso,
                    a.attendance_date,
                    a.status
                FROM attendance a
                JOIN students s ON a.student_id = s.id
                JOIN courses c ON a.course_id = c.id
                WHERE 1=1
            '''
            params = []
            if course_id:
                query += " AND a.course_id = ?"
                params.append(course_id)
            if student_id:
                query += " AND a.student_id = ?"
                params.append(student_id)
            if attendance_date:
                query += " AND a.attendance_date = ?"
                params.append(attendance_date)
            
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            st.error(f"Error fetching attendance: {e}")
            return []
        finally:
            self._close()


# --- Classes (Modified for IDs and Database Interaction) ---
class Persona:
    def __init__(self, name, last_name, date_of_birth):
        self.name = name
        self.last_name = last_name
        self.date_of_birth = date_of_birth

class Alunni(Persona):
    def __init__(self, name, last_name, date_of_birth, id=None):
        super().__init__(name, last_name, date_of_birth)
        self.id = id # Database ID

    def display_alunno_info(self):
        return {
            "ID": self.id,
            "Name": self.name,
            "Last Name": self.last_name,
            "Date of Birth": self.date_of_birth
        }

class Corso:
    def __init__(self, nome_corso, durata, docente, id=None):
        self.id = id # Database ID
        self.nome_corso = nome_corso
        self.durata = durata
        self.docente = docente
        self.alunni_frequentanti_il_tal_corso = [] # In-memory list of Alunni objects

    def display_corso_info(self):
        return {
            "ID": self.id,
            "Course Name": self.nome_corso,
            "Duration": self.durata,
            "Teacher": self.docente,
            "Number of Students": len(self.alunni_frequentanti_il_tal_corso),
            "Assigned Students": ", ".join([f"{s.name} {s.last_name}" for s in self.alunni_frequentanti_il_tal_corso]) if self.alunni_frequentanti_il_tal_corso else "None"
        }

class Aula:
    def __init__(self, nome_aula, capacita_sedie, id=None):
        self.id = id # Database ID
        self.nome_aula = nome_aula
        self.capacita_sedie = capacita_sedie
        self.occupazione_aula = {} # Calendar of the aula: { 'Day Time': Corso.nome_corso }

    def display_aula_info(self):
        return {
            "ID": self.id,
            "Classroom Name": self.nome_aula,
            "Chair Capacity": self.capacita_sedie,
            "Occupancy Schedule": self.occupazione_aula if self.occupazione_aula else "No schedule defined."
        }

class UtilitySuite:
    @staticmethod
    def controlla_sedie(aula: Aula, numero_alunni_previsti: int) -> int:
        return numero_alunni_previsti - aula.capacita_sedie

class Segreteria(Persona):
    def __init__(self, name, last_name, date_of_birth): # <--- Corrected parameter name
        super().__init__(name, last_name, date_of_birth) # <--- Corrected usage in super() call
        self.db_manager = DatabaseManager()
        self.all_courses = []
        self.all_aule = []
        self.all_aula_schedules = {}

    def creazione_calendario(self, aula: Aula, corso: Corso, time_slot: str):
        aula.occupazione_aula[time_slot] = corso.nome_corso
        self.db_manager.update_classroom_schedule(aula.id, aula.occupazione_aula) # Update DB
        self.all_aula_schedules[aula.nome_aula] = aula.occupazione_aula
        st.success(f"✅ Schedule for '{aula.nome_aula}' at '{time_slot}' set to '{corso.nome_corso}'.")

    def creazione_classe(self, corso: Corso, students_to_assign: list):
        newly_assigned_count = 0
        for student in students_to_assign:
            if student not in corso.alunni_frequentanti_il_tal_corso:
                corso.alunni_frequentanti_il_tal_corso.append(student)
                self.db_manager.assign_student_to_course(corso.id, student.id) # Assign in DB
                newly_assigned_count += 1
        st.success(f"✅ {newly_assigned_count} new students assigned to course '{corso.nome_corso}'.")

    def stampa_calendario(self):
        output_content = ""
        output_content += "--- School Calendar ---\n"
        output_content += f"Generated On: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        if not self.all_aula_schedules:
            output_content += "No classroom schedules defined.\n"
        else:
            sorted_aula_names = sorted(self.all_aula_schedules.keys())
            for aula_name in sorted_aula_names:
                schedule_data = self.all_aula_schedules[aula_name]
                output_content += f"=== Classroom: {aula_name} ===\n"
                if not schedule_data:
                    output_content += "  No schedule for this classroom.\n"
                else:
                    sorted_schedule = sorted(schedule_data.items())
                    for time_slot, course_name in sorted_schedule:
                        output_content += f"  {time_slot}: {course_name}\n"
                output_content += "\n"
        return output_content, "calendario_scolastico.txt"

    def controllo_forniture(self, aula: Aula, numero_alunni_previsti: int):
        st.info(f"Secretariat: Performing supply check for classroom '{aula.nome_aula}'.")

        sedie_mancanti = UtilitySuite.controlla_sedie(aula, numero_alunni_previsti)

        if sedie_mancanti > 0:
            st.warning(f"🚨 Attention! {sedie_mancanti} chairs are missing for classroom '{aula.nome_aula}'.")
            order_content, order_filename = self._invia_ordine_fornitore(aula.nome_aula, sedie_mancanti)
            st.download_button(
                label=f"Download Purchase Order for {aula.nome_aula}",
                data=order_content.encode('utf-8'),
                file_name=order_filename,
                mime="text/plain",
                key=f"download_order_{aula.nome_aula}"
            )
            st.success(f"📧 Purchase order generated. Click the button above to download it.")
        else:
            st.success(f"✅ Sufficient chairs for classroom '{aula.nome_aula}'. No new orders needed.")

    def _invia_ordine_fornitore(self, nome_aula: str, quantita: int):
        data_odierna = datetime.date.today().strftime("%d-%m-%Y")
        nome_file_ordine = f"ordine_fornitore_{nome_aula.replace(' ', '_')}_{data_odierna}.txt"

        order_form_content = ""
        order_form_content += "--- SUPPLIER ORDER FORM ---\n"
        order_form_content += f"Date: {data_odierna}\n"
        order_form_content += "Recipient: School Material Supplier\n"
        order_form_content += "\n"
        order_form_content += "Subject: Additional Chair Order\n"
        order_form_content += "\n"
        order_form_content += f"Dear Supplier,\n"
        order_form_content += f"We kindly request the supply of {quantita} additional chairs for classroom '{nome_aula}'.\n"
        order_form_content += "Please confirm availability and delivery times.\n"
        order_form_content += "\n"
        order_form_content += "Sincerely,\n"
        order_form_content += f"The School Secretariat\n"
        
        return order_form_content, nome_file_ordine

    # --- Data Persistence Methods (now using DBManager) ---
    def save_data(self):
        # Data is saved incrementally as it's added/updated through UI methods
        # This method is primarily for a "Save All" button if needed, but not strictly necessary for every action
        st.info("Data is saved incrementally. No need for a full save button in this design yet.")

    def load_data(self):
        st.session_state.alunni_list = []
        self.all_courses = []
        self.all_aule = []
        self.all_aula_schedules = {}

        # Load Students
        students_data = self.db_manager.fetch_students()
        temp_alunni_dict = {} # Use a dict for quick lookup by ID
        for s_id, name, last_name, dob in students_data:
            alunno = Alunni(name, last_name, dob, id=s_id)
            st.session_state.alunni_list.append(alunno)
            temp_alunni_dict[s_id] = alunno
        # st.success(f"Loaded {len(st.session_state.alunni_list)} students from database.") # Removed for cleaner startup

        # Load Classrooms
        classrooms_data = self.db_manager.fetch_classrooms()
        temp_aula_dict = {} # For quick lookup
        for a_id, nome_aula, capacita_sedie, occupazione_aula in classrooms_data:
            aula = Aula(nome_aula, capacita_sedie, id=a_id)
            aula.occupazione_aula = occupazione_aula
            self.all_aule.append(aula)
            self.all_aula_schedules[aula.nome_aula] = aula.occupazione_aula # Update overall schedule
            temp_aula_dict[a_id] = aula
        # st.success(f"Loaded {len(self.all_aule)} classrooms from database.") # Removed for cleaner startup

        # Load Courses and assign students
        courses_data = self.db_manager.fetch_courses()
        for c_id, nome_corso, durata, docente, assigned_students_data in courses_data:
            corso = Corso(nome_corso, durata, docente, id=c_id)
            for s_id, s_name, s_last_name, s_dob in assigned_students_data:
                # Retrieve the actual Alunni object from temp_alunni_dict
                if s_id in temp_alunni_dict:
                    corso.alunni_frequentanti_il_tal_corso.append(temp_alunni_dict[s_id])
                else:
                    st.warning(f"Student with ID {s_id} for course '{nome_corso}' not found during loading.")
            self.all_courses.append(corso)
        # st.success(f"Loaded {len(self.all_courses)} courses from database.") # Removed for cleaner startup


# --- Streamlit UI ---
st.set_page_config(page_title="School Management System 🏫", layout="wide")
st.title("School Management System (with Database) 📚")

# Initialize session state for the secretariat and student list if not already present
if 'secretario' not in st.session_state:
    st.session_state.secretario = Segreteria("Ivan", "Rossi", "1980-05-15")
    st.session_state.alunni_list = [] # Centralized list for students
    st.session_state.secretario.load_data() # Load initial data from DB on app start

secretario = st.session_state.secretario # Reference the secretariat object

# Sidebar for navigation
st.sidebar.header("Navigation 🧭")
menu_choice = st.sidebar.selectbox(
    "Select an action:",
    [
        "🏠 Home",
        "➕ Add New Student",
        "➕ Create New Course",
        "➕ Create New Classroom",
        "Assign Students to Course",
        "Create Course Schedule",
        "Check Classroom Supplies",
        "Record Attendance",
        "View Attendance",
        "View School Calendar", # This section will be updated
        "📊 View All Data",
        "🔄 Reload Data (from DB)"
    ]
)

# --- UI Logic based on menu_choice ---

if menu_choice == "🏠 Home":
    st.markdown("""
    Welcome to the **School Management System!** Use the sidebar on the left to navigate through the different functionalities.
    
    This application helps you manage school data including:
    * **Students**: Register new students.
    * **Courses**: Define new educational courses.
    * **Classrooms**: Create and manage physical classrooms.
    * **Enrollment**: Assign students to courses.
    * **Scheduling**: Create schedules for courses in specific classrooms.
    * **Resource Management**: Check if classrooms have enough chairs and generate purchase orders if needed.
    * **Attendance**: Record and view student attendance for courses.
    * **Reporting**: View the school's complete calendar and data overviews.
    
    **All data is now saved to an SQLite database** (`school_data.db`) for persistence.
    """)
    st.info(f"Current Secretariat User: {secretario.name} {secretario.last_name}")

elif menu_choice == "➕ Add New Student":
    st.header("Add New Student 🧑‍🎓")
    with st.form("add_student_form", clear_on_submit=True):
        name = st.text_input("First Name:")
        last_name = st.text_input("Last Name:")
        date_of_birth = st.text_input("Date of Birth (YYYY-MM-DD):", placeholder="e.g., 2005-01-15")
        
        submitted = st.form_submit_button("Add Student")
        if submitted:
            if name and last_name and date_of_birth:
                try:
                    datetime.date.fromisoformat(date_of_birth) # Validate date format
                    # Insert into DB and get ID
                    student_id = secretario.db_manager.insert_student(name, last_name, date_of_birth)
                    if student_id:
                        new_alunno = Alunni(name, last_name, date_of_birth, id=student_id)
                        st.session_state.alunni_list.append(new_alunno) # Explicitly add to session state list
                        st.success(f"Student '{name} {last_name}' added successfully! 🎉 (ID: {student_id})")
                    else:
                        st.error("❌ Failed to add student to database. Check if student already exists.")
                except ValueError:
                    st.error("❌ Invalid date format. Please use YYYY-MM-DD.")
            else:
                st.error("❌ All fields are required.")

elif menu_choice == "➕ Create New Course":
    st.header("Create New Course 📚")
    with st.form("create_course_form", clear_on_submit=True):
        nome_corso = st.text_input("Course Name:")
        durata = st.text_input("Duration (e.g., '120 ore'):")
        docente = st.text_input("Teacher's Name (e.g., 'Prof. Rossi'):")
        
        submitted = st.form_submit_button("Create Course")
        if submitted:
            if nome_corso and durata and docente:
                # Insert into DB and get ID
                course_id = secretario.db_manager.insert_course(nome_corso, durata, docente)
                if course_id:
                    new_corso = Corso(nome_corso, durata, docente, id=course_id)
                    secretario.all_courses.append(new_corso)
                    st.success(f"Course '{nome_corso}' created successfully! 📝 (ID: {course_id})")
                else:
                    st.error("❌ Failed to create course. Check if course name already exists.")
            else:
                st.error("❌ All fields are required.")

elif menu_choice == "➕ Create New Classroom":
    st.header("Create New Classroom 🏢")
    with st.form("create_classroom_form", clear_on_submit=True):
        nome_aula = st.text_input("Classroom Name:")
        capacita_sedie = st.number_input("Chair Capacity:", min_value=1, step=1)
        
        submitted = st.form_submit_button("Create Classroom")
        if submitted:
            if nome_aula and capacita_sedie:
                # Insert into DB and get ID
                classroom_id = secretario.db_manager.insert_classroom(nome_aula, int(capacita_sedie), {}) # Initial empty schedule
                if classroom_id:
                    new_aula = Aula(nome_aula, int(capacita_sedie), id=classroom_id) # Ensure capacity is int
                    secretario.all_aule.append(new_aula)
                    st.success(f"Classroom '{nome_aula}' with {int(capacita_sedie)} chairs created! 🛋️ (ID: {classroom_id})")
                else:
                    st.error("❌ Failed to create classroom. Check if classroom name already exists.")
            else:
                st.error("❌ All fields are required.")

elif menu_choice == "Assign Students to Course":
    st.header("Assign Students to Course 🧑‍🏫")
    if not secretario.all_courses:
        st.warning("No courses available. Please create a course first.")
    elif not st.session_state.alunni_list:
        st.warning("No students registered. Please add students first.")
    else:
        with st.form("assign_students_form"):
            course_options = {c.nome_corso: c for c in secretario.all_courses}
            selected_course_name = st.selectbox("Select Course:", list(course_options.keys()))
            
            selected_course = course_options.get(selected_course_name)

            if selected_course:
                # Filter out students already assigned to this course (check in-memory list)
                current_assigned_student_ids = {s.id for s in selected_course.alunni_frequentanti_il_tal_corso}
                available_students = [a for a in st.session_state.alunni_list if a.id not in current_assigned_student_ids]
                
                assigned_students_names = [f"{a.name} {a.last_name}" for a in selected_course.alunni_frequentanti_il_tal_corso]
                if assigned_students_names:
                    st.info(f"Students currently assigned to '{selected_course.nome_corso}': {', '.join(assigned_students_names)}")
                
                student_options = [f"{a.name} {a.last_name}" for a in available_students]
                selected_student_names_to_add = st.multiselect(
                    "Select students to assign (only unassigned students shown):",
                    options=student_options
                )
                
                # Convert selected names back to Alunni objects
                students_to_assign_obj = [a for a in available_students if f"{a.name} {a.last_name}" in selected_student_names_to_add]

                submitted = st.form_submit_button("Assign Students")
                if submitted:
                    if students_to_assign_obj:
                        secretario.creazione_classe(selected_course, students_to_assign_obj)
                        # The creation_classe method already handles DB assignment now
                    else:
                        st.info("No new students selected or all selected students are already in the course.")
            else:
                st.error("Selected course not found. This should not happen.")


elif menu_choice == "Create Course Schedule":
    st.header("Create Course Schedule 🗓️")
    if not secretario.all_aule:
        st.warning("No classrooms available. Please create a classroom first.")
    elif not secretario.all_courses:
        st.warning("No courses available. Please create a course first.")
    else:
        with st.form("create_schedule_form"):
            aula_options = {a.nome_aula: a for a in secretario.all_aule}
            selected_aula_name = st.selectbox("Select Classroom:", list(aula_options.keys()))
            
            corso_options = {c.nome_corso: c for c in secretario.all_courses}
            selected_corso_name = st.selectbox("Select Course:", list(corso_options.keys()))
            
            # Use st.date_input for date and st.time_input for time
            schedule_date = st.date_input("Schedule Date:", datetime.date.today())
            start_time = st.time_input("Start Time:", datetime.time(9, 0))
            end_time = st.time_input("End Time:", datetime.time(11, 0))

            # Combine date and time for event description and start/end ISO format
            time_slot_desc = f"{schedule_date.strftime('%A')} {start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}"
            
            submitted = st.form_submit_button("Set Schedule")
            if submitted:
                if selected_aula_name and selected_corso_name and schedule_date and start_time and end_time:
                    aula_selected = aula_options.get(selected_aula_name)
                    corso_selected = corso_options.get(selected_corso_name)
                    
                    if aula_selected and corso_selected:
                        secretario.creazione_calendario(aula_selected, corso_selected, time_slot_desc) # Use combined string for display
                        st.success("Schedule created. Remember to refresh data to see it in calendar.")
                        # To display events in streamlit_calendar, we need start/end datetimes.
                        # For now, we only store a string in occupazione_aula, so we'll reconstruct for calendar display.
                    else:
                        st.error("Error: Selected classroom or course not found.")
                else:
                    st.error("All fields are required.")

elif menu_choice == "Check Classroom Supplies":
    st.header("Check Classroom Supplies 🪑")
    if not secretario.all_aule:
        st.warning("No classrooms available to check supplies.")
    else:
        with st.form("check_supplies_form"):
            aula_options = {a.nome_aula: a for a in secretario.all_aule}
            selected_aula_name = st.selectbox("Select Classroom:", list(aula_options.keys()))
            
            num_alunni = st.number_input("Number of students expected:", min_value=0, step=1)
            
            submitted = st.form_submit_button("Check Supplies")
            if submitted:
                if selected_aula_name:
                    aula_selected = aula_options.get(selected_aula_name)
                    if aula_selected:
                        secretario.controllo_forniture(aula_selected, num_alunni)
                    else:
                        st.error("Selected classroom not found.")
                else:
                    st.error("Please select a classroom.")

# --- Section: Record Attendance ---
elif menu_choice == "Record Attendance":
    st.header("Record Student Attendance 📝")
    if not secretario.all_courses:
        st.warning("No courses available. Please create a course and assign students first.")
    else:
        with st.form("record_attendance_form"):
            course_options = {c.nome_corso: c for c in secretario.all_courses}
            selected_course_name = st.selectbox("Select Course:", list(course_options.keys()))
            
            selected_course = course_options.get(selected_course_name)
            
            attendance_date = st.date_input("Attendance Date:", datetime.date.today())
            attendance_date_str = attendance_date.isoformat() # Convert date object to string for DB

            if selected_course and selected_course.alunni_frequentanti_il_tal_corso:
                st.subheader(f"Students in '{selected_course.nome_corso}' for {attendance_date_str}:")
                
                attendance_status = {}
                for student in selected_course.alunni_frequentanti_il_tal_corso:
                    # Fetch existing attendance for this student, course, and date
                    existing_attendance = secretario.db_manager.fetch_attendance(
                        student_id=student.id,
                        course_id=selected_course.id,
                        attendance_date=attendance_date_str
                    )
                    
                    current_status = "Absent" # Default
                    if existing_attendance:
                        # existing_attendance is a list of tuples, take the first one if it exists
                        current_status = existing_attendance[0][5] # Status is at index 5

                    status_options = ["Present", "Absent", "Late", "Excused"]
                    
                    col1, col2 = st.columns([0.7, 0.3])
                    with col1:
                        st.write(f"**{student.name} {student.last_name}** (ID: {student.id})")
                    with col2:
                        attendance_status[student.id] = st.radio(
                            f"Status for {student.name} {student.last_name}",
                            options=status_options,
                            index=status_options.index(current_status),
                            key=f"status_{selected_course.id}_{student.id}_{attendance_date_str}"
                        )
                
                submitted = st.form_submit_button("Save Attendance")
                if submitted:
                    all_saved = True
                    for student_id, status in attendance_status.items():
                        if not secretario.db_manager.record_attendance(student_id, selected_course.id, attendance_date_str, status):
                            all_saved = False
                            break
                    
                    if all_saved:
                        st.success("✅ Attendance recorded successfully!")
                    else:
                        st.error("❌ Failed to record some attendance entries.")
            elif selected_course:
                st.info(f"No students assigned to '{selected_course.nome_corso}' yet. Please assign students first.")
            else:
                st.info("Please select a course to record attendance.")

# --- Section: View Attendance ---
elif menu_choice == "View Attendance":
    st.header("View Student Attendance 📊")

    if not secretario.all_courses and not st.session_state.alunni_list:
        st.warning("No courses or students available to view attendance.")
    else:
        # Filters
        st.subheader("Filter Attendance Records:")
        
        all_courses_dict = {c.nome_corso: c for c in secretario.all_courses}
        selected_course_name_filter = st.selectbox(
            "Filter by Course (Optional):", 
            ["All Courses"] + list(all_courses_dict.keys())
        )
        
        all_students_dict = {f"{s.name} {s.last_name}": s for s in st.session_state.alunni_list}
        selected_student_name_filter = st.selectbox(
            "Filter by Student (Optional):", 
            ["All Students"] + list(all_students_dict.keys())
        )
        
        attendance_date_filter = st.date_input("Filter by Date (Optional):", value=None)
        attendance_date_filter_str = attendance_date_filter.isoformat() if attendance_date_filter else None

        course_id_filter = all_courses_dict[selected_course_name_filter].id if selected_course_name_filter != "All Courses" else None
        student_id_filter = all_students_dict[selected_student_name_filter].id if selected_student_name_filter != "All Students" else None

        st.markdown("---")
        
        # Fetch and display attendance
        attendance_records = secretario.db_manager.fetch_attendance(
            course_id=course_id_filter,
            student_id=student_id_filter,
            attendance_date=attendance_date_filter_str
        )

        if attendance_records:
            df_attendance = pd.DataFrame(
                attendance_records,
                columns=["ID", "Student First Name", "Student Last Name", "Course Name", "Date", "Status"]
            )
            st.dataframe(df_attendance, use_container_width=True)
        else:
            st.info("No attendance records found for the selected filters.")


# --- Updated Section: View School Calendar ---
elif menu_choice == "View School Calendar":
    st.header("School Calendar 📅")
    
    # Prepare events for streamlit-calendar
    events = []
    for aula_obj in secretario.all_aule:
        aula_name = aula_obj.nome_aula
        # Ensure occupazione_aula is a dictionary before iterating
        if isinstance(aula_obj.occupazione_aula, dict):
            for time_slot_str, course_name in aula_obj.occupazione_aula.items():
                # Parse the time_slot_str to get date and time for start/end
                # Expected format: 'Monday 09:00 - 11:00' or similar
                try:
                    # Attempt to parse as 'YYYY-MM-DD HH:MM - HH:MM'
                    # If the existing data isn't in this precise format, it will need adaptation.
                    # For this example, let's assume the 'time_slot_desc' from Create Course Schedule
                    # If `time_slot_desc` is "Monday 09:00 - 11:00", we need a date as well.
                    # For a robust solution, you'd store actual start/end datetimes in the DB.
                    # For now, let's mock a date for display if only day/time is stored.
                    # This is a common challenge when integrating non-datetime strings into a calendar.

                    # Let's simplify: if time_slot_str is "Monday 09:00 - 11:00", assume it's for the current week's Monday.
                    # A more robust solution would require storing full date-times in the DB for schedules.

                    # Simplified parsing assuming format "YYYY-MM-DD HH:MM - HH:MM" or similar
                    parts = time_slot_str.split(' ')
                    if len(parts) >= 4 and '-' in parts[-1]: # e.g., "YYYY-MM-DD 09:00 - 11:00" or "Monday 09:00 - 11:00"
                        if len(parts[0]) == 10 and parts[0].count('-') == 2: # Likely a YYYY-MM-DD date
                            date_part = parts[0]
                            start_time_part = parts[1]
                            end_time_part = parts[3]
                        else: # Assume it's a day name like "Monday"
                            # This is a hacky way to map a day name to a specific date for display.
                            # In a real system, schedules would link to specific full datetimes.
                            today = datetime.date.today()
                            day_name_map = {
                                "Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3,
                                "Friday": 4, "Saturday": 5, "Sunday": 6
                            }
                            target_day_of_week = day_name_map.get(parts[0], -1)
                            if target_day_of_week != -1:
                                days_diff = (target_day_of_week - today.weekday() + 7) % 7
                                current_week_day = today + datetime.timedelta(days=days_diff)
                                date_part = current_week_day.isoformat()
                                start_time_part = parts[1]
                                end_time_part = parts[3]
                            else:
                                # Fallback if parsing fails
                                date_part = datetime.date.today().isoformat()
                                start_time_part = "08:00"
                                end_time_part = "17:00"
                                st.warning(f"Could not parse schedule time '{time_slot_str}' for calendar. Using today's date and default times.")
                    else: # Fallback for other formats
                        date_part = datetime.date.today().isoformat()
                        start_time_part = "08:00"
                        end_time_part = "17:00"
                        st.warning(f"Could not parse schedule time '{time_slot_str}' for calendar. Using today's date and default times.")
                        
                    start_datetime_str = f"{date_part}T{start_time_part}:00"
                    end_datetime_str = f"{date_part}T{end_time_part}:00"

                    events.append({
                        "title": f"{course_name} ({aula_name})",
                        "start": start_datetime_str,
                        "end": end_datetime_str,
                        "resourceId": aula_name # Optional: to group by classroom if needed
                    })
                except Exception as e:
                    st.warning(f"Error parsing schedule '{time_slot_str}' for '{aula_name}': {e}. Skipping this event.")

    calendar_options = {
        "headerToolbar": {
            "left": "today prev,next",
            "center": "title",
            "right": "dayGridMonth,timeGridWeek,timeGridDay"
        },
        "initialView": "timeGridWeek", # Start with a weekly view
        "slotMinTime": "08:00:00", # Start day at 8 AM
        "slotMaxTime": "18:00:00", # End day at 6 PM
        "height": "auto" # Adjust height automatically
    }

    if events:
        calendar(events=events, options=calendar_options, key="school_calendar")
        st.info("Click on 'Week' or 'Day' view for detailed schedules. Events are labeled as 'Course Name (Classroom Name)'.")
    else:
        st.info("No school calendar entries yet to display in the interactive calendar.")

    st.markdown("---")
    st.subheader("Raw Calendar Export:")
    file_content, filename = secretario.stampa_calendario()
    st.text_area("Full School Calendar (Text Format):", value=file_content, height=300, disabled=True)
    st.download_button(
        label="Download Calendar (Text File) ⬇️",
        data=file_content.encode('utf-8'),
        file_name=filename,
        mime="text/plain"
    )


elif menu_choice == "📊 View All Data":
    st.header("All School Data")

    st.subheader("All Registered Students 🧑‍🎓")
    if st.session_state.alunni_list:
        alunni_data = [a.display_alunno_info() for a in st.session_state.alunni_list]
        st.dataframe(alunni_data, use_container_width=True)
    else:
        st.info("No students registered yet.")

    st.subheader("All Created Courses 📚")
    if secretario.all_courses:
        corsi_data = [c.display_corso_info() for c in secretario.all_courses]
        st.dataframe(corsi_data, use_container_width=True)
    else:
        st.info("No courses created yet.")

    st.subheader("All Created Classrooms 🏢")
    if secretario.all_aule:
        aule_data = [a.display_aula_info() for a in secretario.all_aule]
        st.dataframe(aule_data, use_container_width=True)
    else:
        st.info("No classrooms created yet.")

elif menu_choice == "🔄 Reload Data (from DB)":
    st.header("Reload Data from Database")
    st.warning("This will clear the current in-memory data and reload everything from the database. Unsaved changes will be lost (though most changes are saved immediately).")
    if st.button("Confirm Reload Data"):
        secretario.load_data()
        st.success("Data reloaded successfully from the database! ✨")
        st.rerun() # Rerun to update displayed data