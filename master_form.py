import customtkinter as ctk


def open_form(parent, row_id, data_list, columns, on_save_callback):
    window = ctk.CTkToplevel(parent)
    window.title(f"MASTER CONTROL - ID: {row_id}")
    window.geometry("800x800")
    window.attributes("-topmost", True)
    window.grab_set()

    ctk.CTkLabel(window, text="[ ADMINISTRATOR MODE ]", font=("Courier New", 20, "bold"), text_color="#e74c3c").pack(
        pady=10)

    scroll_frame = ctk.CTkScrollableFrame(window, width=750, height=600)
    scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

    all_entries = []

    for i, col_name in enumerate(columns):
        val = str(data_list[i]).replace("nan", "")

        frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        frame.pack(fill="x", pady=2)

        ctk.CTkLabel(frame, text=f"[{i}] {col_name}", font=("Courier New", 12, "bold"), anchor="w").pack(fill="x")

        entry = ctk.CTkEntry(frame, font=("Courier New", 12))
        entry.insert(0, val)
        entry.pack(fill="x")

        all_entries.append(entry)

    def save():
        final_data = [e.get() for e in all_entries]
        on_save_callback(row_id, final_data)
        window.destroy()

    ctk.CTkButton(window, text="[ SAVE CHANGES ]", command=save, fg_color="#c0392b", height=50).pack(fill="x", padx=20,
                                                                                                     pady=20)