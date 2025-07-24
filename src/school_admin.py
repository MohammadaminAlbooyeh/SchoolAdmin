import datetime
import json
import os

# --- Base Class ---
class Persona:
    def __init__(self, name, last_name, date_of_birth):
        self.name = name
        self.last_name = last_name
        self.date_of_birth = date_of_birth # Format 'YYYY-MM-DD'

class Alunni(Persona):
    lista_alunni = [] # Class attribute to keep track of all students

    def __init__(self, name, last_name, date_of_birth):
        super().__init__(name, last_name, date_of_birth)
        Alunni.lista_alunni.append(self) # Update global list of students
        print(f"Student '{self.name} {self.last_name}' added to global list.")

    def display_alunno_info(self):
        """Prints details about the student."""
        print(f"  Student Name: {self.name} {self.last_name}")
        print(f"  Date of Birth: {self.date_of_birth}")

class Corso:
    def __init__(self, nome_corso, durata, docente):
        self.nome_corso = nome_corso
        self.durata = durata # e.g., '120 ore'
        self.docente = docente # Persona object or string
        self.alunni_frequentanti_il_tal_corso = [] # Students attending this course (Enrico's job to populate)
        
        print(f"Course '{self.nome_corso}' created.")

    def display_corso_info(self):
        """Prints details about the course."""
        print(f"  Course Name: {self.nome_corso}")
        print(f"  Duration: {self.durata}")
        print(f"  Teacher: {self.docente.name if hasattr(self.docente, 'name') else self.docente}")
        print(f"  Number of Students: {len(self.alunni_frequentanti_il_tal_corso)}")

class Aula:
    def __init__(self, nome_aula, capacita_sedie):
        self.nome_aula = nome_aula
        self.capacita_sedie = capacita_sedie # Number of chairs
        self.occupazione_aula = {} # Calendar of the aula: { 'Day Time': Corso.nome_corso } (Emilian's job to populate)
        
        print(f"Classroom '{self.nome_aula}' with {self.capacita_sedie} chairs created.")

    def display_aula_info(self):
        """Prints details about the classroom."""
        print(f"  Classroom Name: {self.nome_aula}")
        print(f"  Chair Capacity: {self.capacita_sedie}")
        print("  Occupancy Schedule:")
        if not self.occupazione_aula:
            print("    No schedule defined.")
        for time, course_name in self.occupazione_aula.items():
            print(f"    {time}: {course_name}")

# --- Andrea's Utility Suite ---
class UtilitySuite:
    @staticmethod
    def controlla_sedie(aula: Aula, numero_alunni_previsti: int) -> int:
        """
        Checks if there are enough chairs in a classroom for a given number of students.
        Returns the number of missing chairs (positive value), 0 if sufficient,
        or a negative value if there are excess chairs.
        """
        sedie_mancanti = numero_alunni_previsti - aula.capacita_sedie
        print(f"Utility: Checking chairs for classroom '{aula.nome_aula}'. Needed: {numero_alunni_previsti}, Available: {aula.capacita_sedie}")
        return sedie_mancanti
    
# --- Ivan's Class: Segreteria ---
class Segreteria(Persona):
    def __init__(self, name, last_name, date_of_birth):
        super().__init__(name, last_name, date_of_birth)
        self.all_courses = [] # Managed by Ivan
        self.all_aule = []    # Managed by Ivan
        self.all_aula_schedules = {} # To store calendars of all aulas for printing (Jay's usage)
        print(f"Secretariat user '{self.name} {self.last_name}' initialized.")

    # --- Emilian's method ---
    def creazione_calendario(self, aula: Aula, corso: Corso, time_slot: str):
        """
        Emilian's method: Creates or updates the calendar for a specific classroom and course.
        Example: aula.occupazione_aula['Lunedì 9:00'] = corso.nome_corso
        """
        print(f"Secretariat: Creating calendar for classroom '{aula.nome_aula}' and course '{corso.nome_corso}' at '{time_slot}'.")
        aula.occupazione_aula[time_slot] = corso.nome_corso
        # Update central schedule maintained by Segreteria
        self.all_aula_schedules[aula.nome_aula] = aula.occupazione_aula
        print(f"✅ Schedule for '{aula.nome_aula}' at '{time_slot}' set to '{corso.nome_corso}'.")


    # --- Enrico's method ---
    def creazione_classe(self, corso: Corso, students_to_assign: list):
        """
        Enrico's method: Populates the student list for a given course.
        `students_to_assign` should contain Alunni objects.
        """
        print(f"Secretariat: Assigning students to course '{corso.nome_corso}'.")
        newly_assigned_count = 0
        for student in students_to_assign:
            if student not in corso.alunni_frequentanti_il_tal_corso:
                corso.alunni_frequentanti_il_tal_corso.append(student)
                newly_assigned_count += 1
        print(f"✅ {newly_assigned_count} new students assigned to course '{corso.nome_corso}'.")


    # --- Jay's method ---
    def stampa_calendario(self):
        """
        Jay's method: Prints the complete schedule of all classrooms to a single TXT file.
        It uses self.all_aula_schedules.
        """
        print("Secretariat: Printing overall calendar to file (Jay's task).")
        output_filename = "calendario_scolastico.txt"
        try:
            with open(output_filename, "w", encoding="utf-8") as f:
                f.write("--- School Calendar ---\n")
                f.write(f"Generated On: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                if not self.all_aula_schedules:
                    f.write("No classroom schedules defined.\n")
                else:
                    # Sort classrooms by name for consistent output
                    sorted_aula_names = sorted(self.all_aula_schedules.keys())
                    for aula_name in sorted_aula_names:
                        schedule_data = self.all_aula_schedules[aula_name]
                        f.write(f"=== Classroom: {aula_name} ===\n")
                        if not schedule_data:
                            f.write("  No schedule for this classroom.\n")
                        else:
                            # Sort schedule by key (time slot) for consistent output
                            sorted_schedule = sorted(schedule_data.items())
                            for time_slot, course_name in sorted_schedule:
                                f.write(f"  {time_slot}: {course_name}\n")
                        f.write("\n")
            print(f"✅ Calendar printed successfully to '{output_filename}'.")
        except IOError as e:
            print(f"❌ Error printing calendar to file: {e}")


    # --- Amin's method ---
    def controllo_forniture(self, aula: Aula, numero_alunni_previsti: int):
        """
        Amin's method: Verifies if there are enough chairs in a given 'aula' for the 'numero_alunni_previsti'.
        If chairs are missing (positive value from utility suite), it generates a purchase order.
        """
        print(f"\nSecretariat: Performing supply check for classroom '{aula.nome_aula}' (Amin's task).")

        # Calls Andrea's utility function
        sedie_mancanti = UtilitySuite.controlla_sedie(aula, numero_alunni_previsti)

        if sedie_mancanti > 0:
            print(f"🚨 Attention! {sedie_mancanti} chairs are missing for classroom '{aula.nome_aula}'.")
            self._invia_ordine_fornitore(aula.nome_aula, sedie_mancanti) # Calls Amin's internal method
        else:
            print(f"✅ Sufficient chairs for classroom '{aula.nome_aula}'. No new orders needed.")

    # Amin's internal helper method
    def _invia_ordine_fornitore(self, nome_aula: str, quantita: int):
        """
        Amin's helper method: Generates a written purchase order form for the supplier.
        This method is private (convention with underscore) as it's called internally.
        """
        data_odierna = datetime.date.today().strftime("%d-%m-%Y")
        nome_file_ordine = f"ordine_fornitore_{nome_aula.replace(' ', '_')}_{data_odierna}.txt"

        print(f"📧 Generating supplier order: '{nome_file_ordine}'...")
        try:
            with open(nome_file_ordine, "w", encoding="utf-8") as f:
                f.write("--- SUPPLIER ORDER FORM ---\n")
                f.write(f"Date: {data_odierna}\n")
                f.write("Recipient: School Material Supplier\n")
                f.write("\n")
                f.write("Subject: Additional Chair Order\n")
                f.write("\n")
                f.write(f"Dear Supplier,\n")
                f.write(f"We kindly request the supply of {quantita} additional chairs for classroom '{nome_aula}'.\n")
                f.write("Please confirm availability and delivery times.\n")
                f.write("\n")
                f.write("Sincerely,\n")
                f.write(f"The School Secretariat\n")
            print(f"✅ Order generated successfully in '{nome_file_ordine}'.")
        except IOError as e:
            print(f"❌ Error generating order file: {e}")

    # --- Data Persistence Methods (Moved from UtilitySuite to Segreteria) ---
    def save_data(self, filename_alunni="alunni.json", filename_corsi="corsi.json", filename_aule="aule.json"):
        """Saves school data (students, courses, classrooms) to JSON files."""
        try:
            # Save Alunni (students)
            with open(filename_alunni, 'w', encoding='utf-8') as f:
                alunni_data = []
                for alunno in Alunni.lista_alunni:
                    alunni_data.append({
                        'name': alunno.name,
                        'last_name': alunno.last_name,
                        'date_of_birth': alunno.date_of_birth
                    })
                json.dump(alunni_data, f, indent=4)
            print(f"✅ Students data saved to {filename_alunni}")

            # Save Corsi (courses)
            with open(filename_corsi, 'w', encoding='utf-8') as f:
                corsi_data = []
                for corso in self.all_courses: 
                    corsi_data.append({
                        'nome_corso': corso.nome_corso,
                        'durata': corso.durata,
                        'docente_name': corso.docente.name if hasattr(corso.docente, 'name') else corso.docente,
                        'alunni_frequentanti_ids': [a.name + a.last_name for a in corso.alunni_frequentanti_il_tal_corso] # Simple ID based on name for linking
                    })
                json.dump(corsi_data, f, indent=4)
            print(f"✅ Courses data saved to {filename_corsi}")

            # Save Aule (classrooms)
            with open(filename_aule, 'w', encoding='utf-8') as f:
                aule_data = []
                for aula in self.all_aule:
                    aula_data = {
                        'nome_aula': aula.nome_aula,
                        'capacita_sedie': aula.capacita_sedie,
                        'occupazione_aula': aula.occupazione_aula
                    }
                    aule_data.append(aula_data)
                json.dump(aule_data, f, indent=4)
            print(f"✅ Classrooms data saved to {filename_aule}")

        except IOError as e:
            print(f"❌ Error saving data: {e}")
        except AttributeError as e:
            print(f"❌ Data saving error: Missing attribute for data lists (e.g., self.all_courses or self.all_aule). {e}")

    def load_data(self, filename_alunni="alunni.json", filename_corsi="corsi.json", filename_aule="aule.json"):
        """Loads school data (students, courses, classrooms) from JSON files."""
        # Clear existing data before loading
        Alunni.lista_alunni = []
        self.all_courses = []
        self.all_aule = []
        temp_alunni_dict = {} # Helper to quickly find students by 'ID' (name+lastname)

        try:
            # Load Alunni (students)
            if os.path.exists(filename_alunni):
                with open(filename_alunni, 'r', encoding='utf-8') as f:
                    alunni_data = json.load(f)
                    for data in alunni_data:
                        alunno = Alunni(data['name'], data['last_name'], data['date_of_birth'])
                        temp_alunni_dict[alunno.name + alunno.last_name] = alunno # Store for linking
                print(f"✅ Students data loaded from {filename_alunni}")
            else:
                print(f"ℹ️ No students data file found: {filename_alunni}. Starting with empty student list.")

            # Load Aule (classrooms) first, as courses might refer to their schedule
            if os.path.exists(filename_aule):
                with open(filename_aule, 'r', encoding='utf-8') as f:
                    aule_data = json.load(f)
                    for data in aule_data:
                        aula = Aula(data['nome_aula'], data['capacita_sedie'])
                        aula.occupazione_aula = data['occupazione_aula']
                        self.all_aule.append(aula)
                print(f"✅ Classrooms data loaded from {filename_aule}")
            else:
                print(f"ℹ️ No classrooms data file found: {filename_aule}. Starting with empty classroom list.")

            # Load Corsi (courses)
            if os.path.exists(filename_corsi):
                with open(filename_corsi, 'r', encoding='utf-8') as f:
                    corsi_data = json.load(f)
                    for data in corsi_data:
                        # Recreate Corso object
                        corso = Corso(data['nome_corso'], data['durata'], data['docente_name'])
                        # Re-link students to the course
                        for alunno_id in data['alunni_frequentanti_ids']:
                            if alunno_id in temp_alunni_dict:
                                corso.alunni_frequentanti_il_tal_corso.append(temp_alunni_dict[alunno_id])
                            else:
                                print(f"⚠️ Warning: Student with ID '{alunno_id}' for course '{corso.nome_corso}' not found during load.")
                        self.all_courses.append(corso)
                print(f"✅ Courses data loaded from {filename_corsi}")
            else:
                print(f"ℹ️ No courses data file found: {filename_corsi}. Starting with empty course list.")

            # Update all_aula_schedules in Segreteria from loaded Aule
            self.all_aula_schedules = {aula.nome_aula: aula.occupazione_aula for aula in self.all_aule}


        except (IOError, json.JSONDecodeError) as e:
            print(f"❌ Error loading data: {e}")
        except AttributeError as e:
            print(f"❌ Data loading error: Ensure 'self.all_courses' and 'self.all_aule' are initialized in Segreteria __init__. {e}")
        
# --- Main Program Execution (CLI) ---
if __name__ == "__main__":
    print("--- School Management System ---")

    # Initialize the secretariat and attempt to load previous data
    secretario = Segreteria("Ivan", "Rossi", "1980-05-15")
    secretario.load_data() # Load data after initializing lists in __init__


    while True:
        print("\n--- Main Menu ---")
        print("1. Add New Student (Alunni)")
        print("2. Create New Course (Corso)")
        print("3. Create New Classroom (Aula)")
        print("4. Assign Students to Course (creazione_classe)")
        print("5. Create Course Schedule (creazione_calendario)")
        print("6. Check Classroom Supplies (controllo_forniture)")
        print("7. Print School Calendar (stampa_calendario)")
        print("8. List All Students")
        print("9. List All Courses")
        print("10. List All Classrooms")
        print("11. Save Data")
        print("12. Exit")

        choice = input("Enter your choice: ").strip()

        if choice == '1':
            name = input("Enter student's first name: ")
            last_name = input("Enter student's last name: ")
            dob = input("Enter student's date of birth (YYYY-MM-DD): ")
            new_alunno = Alunni(name, last_name, dob)

        elif choice == '2':
            nome_corso = input("Enter course name: ")
            durata = input("Enter course duration (e.g., '120 ore'): ")
            docente = input("Enter teacher's name (e.g., 'Prof. Bianchi'): ")
            new_corso = Corso(nome_corso, durata, docente)
            secretario.all_courses.append(new_corso)

        elif choice == '3':
            nome_aula = input("Enter classroom name: ")
            try:
                capacita_sedie = int(input("Enter chair capacity: "))
                new_aula = Aula(nome_aula, capacita_sedie)
                secretario.all_aule.append(new_aula)
            except ValueError:
                print("❌ Invalid capacity. Please enter a number.")

        elif choice == '4':
            if not secretario.all_courses:
                print("❌ No courses available. Please create a course first.")
                continue
            if not Alunni.lista_alunni:
                print("❌ No students registered. Please add students first.")
                continue

            print("\n--- Available Courses ---")
            for i, corso in enumerate(secretario.all_courses):
                print(f"{i+1}. {corso.nome_corso}")
            course_index = input("Select course number to assign students: ")

            try:
                corso_selected = secretario.all_courses[int(course_index) - 1]
                print(f"\n--- Available Students (All) ---")
                for i, alunno in enumerate(Alunni.lista_alunni):
                    status = "(Already in this course)" if alunno in corso_selected.alunni_frequentanti_il_tal_corso else ""
                    print(f"{i+1}. {alunno.name} {alunno.last_name} {status}")
                
                student_indices_str = input("Enter student numbers to assign (comma-separated, e.g., 1,3,5): ")
                student_indices = [int(idx.strip()) - 1 for idx in student_indices_str.split(',') if idx.strip().isdigit()]
                
                students_to_assign = []
                for idx in student_indices:
                    if 0 <= idx < len(Alunni.lista_alunni):
                        alunno = Alunni.lista_alunni[idx]
                        if alunno not in corso_selected.alunni_frequentanti_il_tal_corso:
                            students_to_assign.append(alunno)
                        else:
                            print(f"Student '{alunno.name} {alunno.last_name}' is already in '{corso_selected.nome_corso}'.")
                    else:
                        print(f"Invalid student number: {idx+1}")
                
                if students_to_assign:
                    secretario.creazione_classe(corso_selected, students_to_assign)
                else:
                    print("No new students selected or all selected students are already in the course.")

            except (ValueError, IndexError):
                print("❌ Invalid course or student selection.")

        elif choice == '5':
            if not secretario.all_aule:
                print("❌ No classrooms available. Please create a classroom first.")
                continue
            if not secretario.all_courses:
                print("❌ No courses available. Please create a course first.")
                continue

            print("\n--- Available Classrooms ---")
            for i, aula in enumerate(secretario.all_aule):
                print(f"{i+1}. {aula.nome_aula}")
            aula_index = input("Select classroom number for schedule: ")

            print("\n--- Available Courses ---")
            for i, corso in enumerate(secretario.all_courses):
                print(f"{i+1}. {corso.nome_corso}")
            corso_index = input("Select course number for schedule: ")

            try:
                aula_selected = secretario.all_aule[int(aula_index) - 1]
                corso_selected = secretario.all_courses[int(corso_index) - 1]
                time_slot = input("Enter time slot for schedule (e.g., 'Monday 09:00'): ")
                
                secretario.creazione_calendario(aula_selected, corso_selected, time_slot)

            except (ValueError, IndexError):
                print("❌ Invalid classroom or course selection.")

        elif choice == '6':
            if not secretario.all_aule:
                print("❌ No classrooms available to check supplies.")
                continue

            print("\n--- Available Classrooms ---")
            for i, aula in enumerate(secretario.all_aule):
                print(f"{i+1}. {aula.nome_aula} (Capacity: {aula.capacita_sedie})")
            aula_index = input("Select classroom number to check supplies: ")

            try:
                aula_selected = secretario.all_aule[int(aula_index) - 1]
                num_alunni = int(input(f"Enter number of students expected for '{aula_selected.nome_aula}': "))
                secretario.controllo_forniture(aula_selected, num_alunni)
            except (ValueError, IndexError):
                print("❌ Invalid classroom selection or number of students.")

        elif choice == '7':
            secretario.stampa_calendario()

        elif choice == '8':
            print("\n--- All Registered Students ---")
            if not Alunni.lista_alunni:
                print("No students registered yet.")
            for i, alunno in enumerate(Alunni.lista_alunni):
                print(f"{i+1}.")
                alunno.display_alunno_info()
                print("---")
            print("------------------------------")

        elif choice == '9':
            print("\n--- All Created Courses ---")
            if not secretario.all_courses:
                print("No courses created yet.")
            for i, corso in enumerate(secretario.all_courses):
                print(f"{i+1}.")
                corso.display_corso_info()
                print("---")
            print("---------------------------")

        elif choice == '10':
            print("\n--- All Created Classrooms ---")
            if not secretario.all_aule:
                print("No classrooms created yet.")
            for i, aula in enumerate(secretario.all_aule):
                print(f"{i+1}.")
                aula.display_aula_info()
                print("---")
            print("-----------------------------")

        elif choice == '11':
            secretario.save_data()

        elif choice == '12':
            print("Exiting School Management System. Remember to save your data!")
            break
        else:
            print("Invalid choice. Please try again.")

    print("--- Program Ended ---")