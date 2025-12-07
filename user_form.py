import customtkinter as ctk

ALLOWED_COLUMNS = [
    'Nazwa programu/projektu',
    'Potrzeby finansowe na 2026 rok',
    'Potrzeby finansowe na 2027 rok',
    'Nazwa zadania',
    'Szczegółowe uzasadnienie realizacji zdania',
    'Uwagi'
]

def open_form(parent, row_id, data_list, columns, on_save_callback):
    window = ctk.CTkToplevel(parent)
    window.title(f"Edycja wiersza {row_id} - PRACOWNIK")
    window.geometry("600x700")
    window.attributes("-topmost", True)
    window.grab_set()

    ctk.CTkLabel(window, text="FORMULARZ PRACOWNIKA", font=("Roboto", 20, "bold"), text_color="#2ecc71").pack(pady=15)
    ctk.CTkLabel(window, text="Edytuj dane opisowe i klasyfikację", font=("Roboto", 12)).pack(pady=(0, 10))

    scroll_frame = ctk.CTkScrollableFrame(window, width=550, height=500)
    scroll_frame.pack(fill="both", expand=True, padx=20, pady=10)

    all_entries = []

    clean_allowed = [col.upper().strip() for col in ALLOWED_COLUMNS]

    for i, col_name in enumerate(columns):
        val = str(data_list[i]).replace("nan", "")
        entry = ctk.CTkEntry(scroll_frame, width=400)
        entry.insert(0, val)

        clean_col_name = str(col_name).strip().upper()

        if clean_col_name in clean_allowed:
            label = ctk.CTkLabel(scroll_frame, text=col_name, font=("Roboto", 12, "bold"), anchor="w")
            label.pack(fill="x", pady=(5, 0))
            entry.pack(fill="x", pady=(0, 10))
        else:
            pass

        all_entries.append(entry)

    def save():
        final_data = [e.get() for e in all_entries]
        on_save_callback(row_id, final_data)
        window.destroy()

    def cancel():
        window.destroy()

    btn_frame = ctk.CTkFrame(window, fg_color="transparent")
    btn_frame.pack(fill="x", padx=20, pady=20)
    ctk.CTkButton(btn_frame, text="Anuluj", command=cancel, fg_color="red", width=100).pack(side="left")
    ctk.CTkButton(btn_frame, text="Zapisz Zmiany", command=save, fg_color="green", width=200).pack(side="right")