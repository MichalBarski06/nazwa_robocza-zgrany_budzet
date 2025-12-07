import customtkinter as ctk

ALLOWED_COLUMNS = [
    'Potrzeby finansowe na 2026 rok',
    'Potrzeby finansowe na 2027 rok',
    'Szczegółowe uzasadnienie realizacji zdania',
    'Uwagi'
]

def open_form(parent, row_id, data_list, columns, on_save_callback):
    window = ctk.CTkToplevel(parent)
    window.title(f"Edycja wiersza {row_id} - KSIĘGOWOŚĆ")
    window.geometry("700x700")
    window.attributes("-topmost", True)
    window.grab_set()

    ctk.CTkLabel(window, text="PANEL KSIĘGOWEGO", font=("Roboto", 20, "bold"), text_color="#f1c40f").pack(pady=15)

    scroll_frame = ctk.CTkScrollableFrame(window, width=650, height=500)
    scroll_frame.pack(fill="both", expand=True, padx=20, pady=10)

    all_entries = []
    clean_allowed = [col.upper().strip() for col in ALLOWED_COLUMNS]

    for i, col_name in enumerate(columns):
        val = str(data_list[i]).replace("nan", "")
        entry = ctk.CTkEntry(scroll_frame, width=400)
        entry.insert(0, val)

        clean_col_name = str(col_name).strip().upper()

        if clean_col_name in clean_allowed or "KWOTA" in clean_col_name or "LIMIT" in clean_col_name:
            label = ctk.CTkLabel(scroll_frame, text=col_name, font=("Roboto", 12, "bold"), anchor="w")
            label.pack(fill="x", pady=(5, 0))
            entry.pack(fill="x", pady=(0, 10))

        all_entries.append(entry)

    def save():
        final_data = [e.get() for e in all_entries]
        on_save_callback(row_id, final_data)
        window.destroy()

    ctk.CTkButton(window, text="Zatwierdź Finanse", command=save, fg_color="#f39c12", height=50).pack(fill="x", padx=20,
                                                                                                      pady=20)