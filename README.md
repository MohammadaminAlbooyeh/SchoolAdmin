
# Sistema di Gestione Scolastica 🏫

Questa applicazione consente la gestione completa di una scuola tramite una interfaccia web realizzata con Streamlit.

## Funzionalità principali
- **Gestione Studenti**: aggiungi nuovi studenti e visualizza i dati.
- **Gestione Corsi**: crea corsi, assegna docenti e studenti.
- **Gestione Aule**: definisci aule e capacità.
- **Assegnazione Studenti ai Corsi**: iscrivi studenti ai corsi.
- **Pianificazione Orari**: assegna corsi alle aule e agli orari.
- **Controllo Forniture**: verifica la disponibilità di sedie e genera ordini.
- **Calendario Scolastico Interattivo**: visualizza il calendario delle lezioni tramite componente interattivo.
- **Presenze Studenti**: registra e visualizza le presenze degli studenti ai corsi.
- **Salvataggio e Caricamento Dati**: persistenza su database SQLite.


## Come avviare l'applicazione

1. Installa le dipendenze:
   ```bash
   pip install -r requirements.txt
   ```
2. Avvia Streamlit:
   ```bash
   streamlit run src/school_admin_UI.py
   ```


## Requisiti
- Python 3.8+
- streamlit
- pandas
- streamlit-calendar

## Autori
- Ivan, Nathalie, Alberto, Matteo, Andrea, Enrico, Emilian, Jay, Amin


## Note
Tutti i dati vengono salvati automaticamente nel database. Puoi visualizzare e scaricare il calendario scolastico e gestire le presenze direttamente dall'applicazione.
