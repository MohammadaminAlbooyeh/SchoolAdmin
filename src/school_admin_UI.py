import streamlit as st
import datetime
import json
import os

# --- Classes ---
class Persona:
    def __init__(self, name, last_name, date_of_birth):
        self.name = name
        self.last_name = last_name
        self.date_of_birth = date_of_birth

class Alunni(Persona):
    lista_alunni = []
    def __init__(self, name, last_name, date_of_birth):
        super().__init__(name, last_name, date_of_birth)
        Alunni.lista_alunni.append(self)

class Corso:
    def __init__(self, nome_corso, durata, docente):
        self.nome_corso = nome_corso
        self.durata = durata
        self.docente = docente
        self.alunni_frequentanti_il_tal_corso = []

class Aula:
    def __init__(self, nome_aula, capacita_sedie):
        self.nome_aula = nome_aula
        self.capacita_sedie = capacita_sedie
        self.occupazione_aula = {}

class UtilitySuite:
    @staticmethod
    def controlla_sedie(aula: Aula, numero_alunni_previsti: int) -> int:
        return numero_alunni_previsti - aula.capacita_sedie

class Segreteria(Persona):
    def __init__(self, name, last_name, date_of_birth):
        super().__init__(name, last_name, date_of_birth)
        self.all_courses = []
        self.all_aule = []
        self.all_aula_schedules = {}

    def creazione_calendario(self, aula: Aula, corso: Corso, time_slot: str):
        aula.occupazione_aula[time_slot] = corso.nome_corso
        self.all_aula_schedules[aula.nome_aula] = aula.occupazione_aula

    def creazione_classe(self, corso: Corso, students_to_assign: list):
        for student in students_to_assign:
            if student not in corso.alunni_frequentanti_il_tal_corso:
                corso.alunni_frequentanti_il_tal_corso.append(student)

# --- Streamlit UI ---
st.set_page_config(page_title="School Management CLI to Streamlit", layout="wide")
st.title("School Management System")

if "secretario" not in st.session_state:
    st.session_state.secretario = Segreteria("Ivan", "Rossi", "1980-05-15")
    st.session_state.alunni_list = []
    st.session_state.corsi_list = []
    st.session_state.aule_list = []

secretario = st.session_state.secretario

menu = st.sidebar.selectbox("Menu", [
    "Add Student",
    "Create Course",
    "Create Classroom",
    "Assign Students to Course",
    "Create Course Schedule",
    "Check Classroom Supplies",
    "View All Students",
    "View All Courses",
    "View All Classrooms"
])

if menu == "Add Student":
    st.header("Add New Student")
    name = st.text_input("First Name")
    last_name = st.text_input("Last Name")
    dob = st.text_input("Date of Birth (YYYY-MM-DD)")
    if st.button("Add Student"):
        if name and last_name and dob:
            try:
                datetime.date.fromisoformat(dob)
                new_alunno = Alunni(name, last_name, dob)
                st.session_state.alunni_list.append(new_alunno)
                st.success(f"Student '{name} {last_name}' added!")
            except ValueError:
                st.error("Invalid date format.")
        else:
            st.error("All fields required.")

elif menu == "Create Course":
    st.header("Create New Course")
    nome_corso = st.text_input("Course Name")
    durata = st.text_input("Duration (e.g., '120 ore')")
    docente = st.text_input("Teacher's Name")
    if st.button("Create Course"):
        if nome_corso and durata and docente:
            new_corso = Corso(nome_corso, durata, docente)
            secretario.all_courses.append(new_corso)
            st.success(f"Course '{nome_corso}' created!")
        else:
            st.error("All fields required.")

elif menu == "Create Classroom":
    st.header("Create New Classroom")
    nome_aula = st.text_input("Classroom Name")
    capacita_sedie = st.number_input("Chair Capacity", min_value=1, step=1)
    if st.button("Create Classroom"):
        if nome_aula and capacita_sedie:
            new_aula = Aula(nome_aula, capacita_sedie)
            secretario.all_aule.append(new_aula)
            st.success(f"Classroom '{nome_aula}' created!")
        else:
            st.error("All fields required.")

elif menu == "Assign Students to Course":
    st.header("Assign Students to Course")
    if not secretario.all_courses or not st.session_state.alunni_list:
        st.warning("Add courses and students first.")
    else:
        course_names = [c.nome_corso for c in secretario.all_courses]
        selected_course = st.selectbox("Select Course", course_names)
        corso_obj = next((c for c in secretario.all_courses if c.nome_corso == selected_course), None)
        student_names = [f"{a.name} {a.last_name}" for a in st.session_state.alunni_list]
        selected_students = st.multiselect("Select Students", student_names)
        students_obj = [a for a in st.session_state.alunni_list if f"{a.name} {a.last_name}" in selected_students]
        if st.button("Assign Students"):
            secretario.creazione_classe(corso_obj, students_obj)
            st.success("Students assigned!")

elif menu == "Create Course Schedule":
    st.header("Create Course Schedule")
    if not secretario.all_aule or not secretario.all_courses:
        st.warning("Add classrooms and courses first.")
    else:
        aula_names = [a.nome_aula for a in secretario.all_aule]
        selected_aula = st.selectbox("Select Classroom", aula_names)
        corso_names = [c.nome_corso for c in secretario.all_courses]
        selected_corso = st.selectbox("Select Course", corso_names)
        time_slot = st.text_input("Time Slot (e.g., 'Monday 09:00')")
        if st.button("Set Schedule"):
            aula_obj = next((a for a in secretario.all_aule if a.nome_aula == selected_aula), None)
            corso_obj = next((c for c in secretario.all_courses if c.nome_corso == selected_corso), None)
            secretario.creazione_calendario(aula_obj, corso_obj, time_slot)
            st.success("Schedule set!")

elif menu == "Check Classroom Supplies":
    st.header("Check Classroom Supplies")
    if not secretario.all_aule:
        st.warning("Add classrooms first.")
    else:
        aula_names = [a.nome_aula for a in secretario.all_aule]
        selected_aula = st.selectbox("Select Classroom", aula_names)
        num_alunni = st.number_input("Number of students expected", min_value=0, step=1)
        if st.button("Check Supplies"):
            aula_obj = next((a for a in secretario.all_aule if a.nome_aula == selected_aula), None)
            sedie_mancanti = UtilitySuite.controlla_sedie(aula_obj, num_alunni)
            if sedie_mancanti > 0:
                st.warning(f"{sedie_mancanti} chairs are missing for '{selected_aula}'.")
            else:
                st.success("Sufficient chairs available.")

elif menu == "View All Students":
    st.header("All Students")
    if st.session_state.alunni_list:
        for a in st.session_state.alunni_list:
            st.write(f"{a.name} {a.last_name} - {a.date_of_birth}")
    else:
        st.info("No students registered.")

elif menu == "View All Courses":
    st.header("All Courses")
    if secretario.all_courses:
        for c in secretario.all_courses:
            st.write(f"{c.nome_corso} - {c.durata} - Teacher: {c.docente}")
    else:
        st.info("No courses created.")

elif menu == "View All Classrooms":
    st.header("All Classrooms")
    if secretario.all_aule:
        for a in secretario.all_aule:
            st.write(f"{a.nome_aula} - Capacity: {a.capacita_sedie}")
    else:
        st.info("No classrooms created.")