import server
import convert
from tkinter import ttk, messagebox, filedialog
import customtkinter as ctk
from PIL import Image
import tkinter as tk
import os
import user_form
import admin_form
import master_form

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")
LOGO_PATH = "logo.png"


def show_message(text):
    root = ctk.CTk()
    root.title("Komunikat")
    root.geometry("400x200")

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width / 2) - (400 / 2)
    y = (screen_height / 2) - (200 / 2)
    root.geometry('%dx%d+%d+%d' % (400, 200, x, y))

    def close_msg():
        root.quit()

    frame = ctk.CTkFrame(root, corner_radius=20)
    frame.pack(expand=True, fill="both", padx=20, pady=20)
    ctk.CTkLabel(frame, text=text, font=("Roboto", 16), wraplength=350, justify="center").pack(pady=20)
    ctk.CTkButton(frame, text="OK", command=close_msg, width=100).pack(pady=10)
    root.mainloop()
    try:
        root.destroy()
    except:
        pass


def show_admin_tools(parent_root):
    admin_window = ctk.CTkToplevel(parent_root)
    admin_window.title("Panel Administracyjny")
    admin_window.geometry("800x700")
    admin_window.attributes("-topmost", True)

    ctk.CTkLabel(admin_window, text="ZARZĄDZANIE SYSTEMEM", font=("Roboto", 24, "bold")).pack(pady=30)

    def open_budget_mgmt():
        bud_win = ctk.CTkToplevel(admin_window)
        bud_win.title("Przydział Budżetów")
        bud_win.geometry("800x500")
        bud_win.attributes("-topmost", True)

        ctk.CTkLabel(bud_win, text="PRZYDZIELANIE BUDŻETU", font=("Roboto", 20, "bold")).pack(pady=10)
        ctk.CTkLabel(bud_win, text="Edytujesz PRZYZNANY LIMIT. Kolumna 'Pozostało' pokazuje stan konta pracownika.",
                     font=("Roboto", 12)).pack(
            pady=(0, 10))

        tree_frame = ctk.CTkFrame(bud_win)
        tree_frame.pack(fill="both", expand=True, padx=20, pady=10)

        cols = ("Login", "Rola", "Limit (Edytowalny)", "Pozostało (Stan Konta)")
        tree = ttk.Treeview(tree_frame, columns=cols, show='headings', height=8)

        tree.heading("Login", text="LOGIN")
        tree.heading("Rola", text="STANOWISKO")
        tree.heading("Limit (Edytowalny)", text="PRZYZNANY LIMIT (PLN)")
        tree.heading("Pozostało (Stan Konta)", text="POZOSTAŁO (PLN)")

        tree.column("Login", width=150)
        tree.column("Rola", width=120)
        tree.column("Limit (Edytowalny)", width=150)
        tree.column("Pozostało (Stan Konta)", width=150)
        tree.pack(side="left", fill="both", expand=True)

        scroll = ctk.CTkScrollbar(tree_frame, command=tree.yview)
        scroll.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scroll.set)

        edit_frame = ctk.CTkFrame(bud_win)
        edit_frame.pack(fill="x", padx=20, pady=20)

        lbl_sel = ctk.CTkLabel(edit_frame, text="Wybrany: Brak")
        lbl_sel.pack(side="left", padx=10)

        e_amount = ctk.CTkEntry(edit_frame, placeholder_text="Nowy Limit (np. 10000)")
        e_amount.pack(side="left", padx=10, fill="x", expand=True)

        selected_user = [None]

        def refresh_list():
            for item in tree.get_children():
                tree.delete(item)

            users = server.get_users_for_budget()
            for u in users:
                role_name = "Pracownik" if u['role'] == '1' else "Księgowy"
                tree.insert("", "end", values=(u['login'], role_name, u['limit'], u['remaining']))

        def on_select(event):
            sel_id = tree.selection()
            if sel_id:
                item = tree.item(sel_id)
                vals = item['values']
                selected_user[0] = vals[0]
                lbl_sel.configure(text=f"Wybrany: {vals[0]}")
                e_amount.delete(0, 'end')
                e_amount.insert(0, vals[2])

        tree.bind("<<TreeviewSelect>>", on_select)

        def save_budget():
            if not selected_user[0]:
                tk.messagebox.showwarning("Info", "Wybierz użytkownika z listy.", parent=bud_win)
                return

            amount = e_amount.get()
            if not amount: return

            success, msg = server.set_user_budget(selected_user[0], amount)
            if success:
                tk.messagebox.showinfo("Sukces", msg, parent=bud_win)
                refresh_list()
            else:
                tk.messagebox.showerror("Błąd", msg, parent=bud_win)

        ctk.CTkButton(edit_frame, text="ZAPISZ LIMIT", command=save_budget, fg_color="#2ecc71", width=120).pack(
            side="right", padx=10)
        ctk.CTkButton(edit_frame, text="ZAMKNIJ", command=bud_win.destroy, fg_color="#95a5a6", hover_color="#7f8c8d",
                      width=100).pack(side="right", padx=10)

        refresh_list()

    def open_add_user():
        add_win = ctk.CTkToplevel(admin_window)
        add_win.title("Dodaj użytkownika")
        add_win.geometry("400x550")
        add_win.attributes("-topmost", True)

        ctk.CTkLabel(add_win, text="NOWY UŻYTKOWNIK", font=("Roboto", 20, "bold")).pack(pady=20)

        e_user = ctk.CTkEntry(add_win, placeholder_text="Login")
        e_user.pack(pady=10, padx=20, fill="x")

        e_pass = ctk.CTkEntry(add_win, placeholder_text="Hasło")
        e_pass.pack(pady=10, padx=20, fill="x")

        e_db = ctk.CTkEntry(add_win, placeholder_text="Plik bazy (np. data.csv)")
        e_db.pack(pady=10, padx=20, fill="x")
        e_db.insert(0, "dane_glowne.csv")

        ctk.CTkLabel(add_win, text="Poziom uprawnień (1-3):").pack(pady=(10, 0))
        e_lvl = ctk.CTkEntry(add_win, placeholder_text="1=Prac, 2=Księg, 3=Admin")
        e_lvl.pack(pady=5, padx=20, fill="x")

        def save_new_user():
            u, p, d, l = e_user.get(), e_pass.get(), e_db.get(), e_lvl.get()
            if u and p and d and l:
                success, msg = server.admin_add_user(u, p, d, l)
                if success:
                    tk.messagebox.showinfo("Sukces", msg, parent=add_win)
                    add_win.destroy()
                else:
                    tk.messagebox.showerror("Błąd", msg, parent=add_win)
            else:
                tk.messagebox.showwarning("Błąd", "Wypełnij wszystkie pola", parent=add_win)

        ctk.CTkButton(add_win, text="ZAPISZ", command=save_new_user, fg_color="#2ecc71", hover_color="#27ae60").pack(
            pady=(30, 10))
        ctk.CTkButton(add_win, text="ANULUJ", command=add_win.destroy, fg_color="#95a5a6", hover_color="#7f8c8d").pack(
            pady=10)

    def open_del_user():
        del_win = ctk.CTkToplevel(admin_window)
        del_win.title("Usuń użytkownika")
        del_win.geometry("400x350")
        del_win.attributes("-topmost", True)

        ctk.CTkLabel(del_win, text="USUŃ UŻYTKOWNIKA", font=("Roboto", 20, "bold")).pack(pady=20)
        e_user = ctk.CTkEntry(del_win, placeholder_text="Nazwa użytkownika")
        e_user.pack(pady=20, padx=20, fill="x")

        def perform_delete():
            if messagebox.askyesno("Potwierdzenie", "Czy na pewno usunąć tego użytkownika?", parent=del_win):
                success, msg = server.admin_delete_user(e_user.get())
                if success:
                    tk.messagebox.showinfo("Sukces", msg, parent=del_win)
                    del_win.destroy()
                else:
                    tk.messagebox.showerror("Błąd", msg, parent=del_win)

        ctk.CTkButton(del_win, text="USUŃ TRWALE", command=perform_delete, fg_color="#e74c3c",
                      hover_color="#c0392b").pack(pady=(20, 10))
        ctk.CTkButton(del_win, text="ANULUJ", command=del_win.destroy, fg_color="#95a5a6", hover_color="#7f8c8d").pack(
            pady=10)

    def open_reset_db():
        reset_win = ctk.CTkToplevel(admin_window)
        reset_win.title("Reset Bazy")
        reset_win.geometry("400x350")
        reset_win.attributes("-topmost", True)

        ctk.CTkLabel(reset_win, text="RESET BAZY DANYCH", font=("Roboto", 20, "bold"), text_color="red").pack(pady=20)
        e_file = ctk.CTkEntry(reset_win, placeholder_text="Nazwa pliku (np. dane.csv)")
        e_file.pack(pady=10, padx=20, fill="x")

        def perform_reset():
            fname = e_file.get()
            if not fname: return
            if messagebox.askyesno("UWAGA", f"To usunie WSZYSTKIE dane z {fname}.\nCzy kontynuować?", parent=reset_win):
                success, msg = server.admin_hard_reset_db(fname)
                tk.messagebox.showinfo("Info", msg, parent=reset_win)
                if success: reset_win.destroy()

        ctk.CTkButton(reset_win, text="WYKONAJ RESET", command=perform_reset, fg_color="darkred",
                      hover_color="red").pack(pady=(20, 10))
        ctk.CTkButton(reset_win, text="ANULUJ", command=reset_win.destroy, fg_color="#95a5a6",
                      hover_color="#7f8c8d").pack(pady=10)

    btn_frame = ctk.CTkFrame(admin_window, fg_color="transparent")
    btn_frame.pack(fill="both", expand=True, padx=40, pady=20)

    ctk.CTkButton(btn_frame, text="DODAJ UŻYTKOWNIKA", command=open_add_user, height=50, font=("Roboto", 14)).pack(
        fill="x", pady=10)

    ctk.CTkButton(btn_frame, text="ZARZĄDZANIE BUDŻETAMI", command=open_budget_mgmt, height=50, fg_color="#e67e22",
                  hover_color="#d35400", font=("Roboto", 14)).pack(
        fill="x", pady=10)

    ctk.CTkButton(btn_frame, text="USUŃ UŻYTKOWNIKA", command=open_del_user, height=50, font=("Roboto", 14)).pack(
        fill="x", pady=10)

    ctk.CTkButton(btn_frame, text="TWARDY RESET BAZY", command=open_reset_db, height=50, fg_color="#c0392b",
                  hover_color="#e74c3c", font=("Roboto", 14)).pack(fill="x", pady=10)

    ctk.CTkButton(admin_window, text="ZAMKNIJ", command=admin_window.destroy, fg_color="gray").pack(pady=20)


def show_login_window():
    root = ctk.CTk()
    root.title("System Logowania")
    root.attributes("-fullscreen", True)

    result = {'username': '', 'password': ''}

    def ok_clicked():
        result['username'] = entry_username.get()
        result['password'] = entry_password.get()
        root.quit()

    def exit_app():
        result['username'] = None
        result['password'] = None
        root.quit()

    frame = ctk.CTkFrame(root, corner_radius=20)
    frame.place(relx=0.5, rely=0.5, anchor="center")

    try:
        if os.path.exists(LOGO_PATH):
            pil_image = Image.open(LOGO_PATH)

            target_width = 320
            w_percent = (target_width / float(pil_image.size[0]))
            target_height = int((float(pil_image.size[1]) * float(w_percent)))

            ctk_logo = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(target_width, target_height))

            ctk.CTkLabel(frame, image=ctk_logo, text="").pack(pady=(30, 5), padx=40)
        else:
            print(f"Nie znaleziono pliku logo: {LOGO_PATH}")
    except Exception as e:
        print(f"Błąd ładowania logo: {e}")

    ctk.CTkLabel(frame, text="SYSTEM EWIDENCJI", font=("Roboto", 24, "bold")).pack(pady=(5, 20), padx=50)

    entry_username = ctk.CTkEntry(frame, placeholder_text="Użytkownik", width=300, height=50, font=("Roboto", 16),
                                  corner_radius=15)
    entry_username.pack(pady=10, padx=40)

    entry_password = ctk.CTkEntry(frame, placeholder_text="Hasło", show="*", width=300, height=50, font=("Roboto", 16),
                                  corner_radius=15)
    entry_password.pack(pady=10, padx=40)

    ctk.CTkButton(frame, text="ZALOGUJ", command=ok_clicked, width=300, height=50, font=("Roboto", 16, "bold"),
                  corner_radius=15).pack(pady=(30, 40), padx=40)

    ctk.CTkButton(root, text="X", command=exit_app, width=50, height=50, fg_color="red", hover_color="darkred",
                  corner_radius=25).place(relx=0.95, rely=0.05, anchor="center")

    entry_username.focus_set()
    root.mainloop()
    try:
        root.destroy()
    except:
        pass
    return result['username'], result['password']


def show_data_window(dataframe, title_text, user_level, username):
    allow_edit = True
    role_name = {1: "PRACOWNIK", 2: "KSIĘGOWY", 3: "ADMINISTRATOR"}.get(user_level, "NIEZNANY")

    all_columns = list(dataframe.columns)
    visible_columns = all_columns

    dataframe_view = dataframe[visible_columns]

    root = ctk.CTk()
    root.title(f"Dane: {title_text}")
    root.attributes("-fullscreen", True)

    header_frame = ctk.CTkFrame(root, height=80, corner_radius=0, fg_color="transparent")
    header_frame.pack(fill="x", side="top")

    # --- NOWA FUNKCJA DO OBSŁUGI PRZYCISKU WYKRESU ---
    def btn_chart_action():
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("Plik PNG", "*.png")],
            initialfile=f"Wykres_{title_text}.png"
        )
        if file_path:
            success, msg = server.generuj_wykres_png(title_text, file_path)
            if success:
                tk.messagebox.showinfo("Sukces", f"{msg}\nZapisano w: {file_path}", parent=root)
            else:
                tk.messagebox.showerror("Błąd", msg, parent=root)
    # ------------------------------------------------

    # PRZYCISK W LEWYM GÓRNYM ROGU
    ctk.CTkButton(header_frame, text="WYKRES (PNG)", command=btn_chart_action,
                  fg_color="#d35400", hover_color="#e67e22", width=120, font=("Roboto", 12, "bold"))\
        .place(relx=0.01, rely=0.5, anchor="w")

    lbl_budget = None
    if user_level in [1, 2]:
        lbl_budget = ctk.CTkLabel(header_frame, text="STAN KONTA: Ładowanie...",
                                  font=("Roboto", 18, "bold"), text_color="#3498db")
        # Przesunięte w prawo (z 0.02 na 0.12), żeby nie zasłonił przycisk wykresu
        lbl_budget.place(relx=0.12, rely=0.5, anchor="w")

    def update_budget_label():
        if lbl_budget:
            try:
                rem_budget = server.get_remaining_budget(username, title_text)
                try:
                    val = float(rem_budget)
                    color = "#2ecc71" if val >= 0 else "#e74c3c"
                except:
                    color = "#3498db"
                lbl_budget.configure(text=f"POZOSTAŁY BUDŻET: {rem_budget} PLN", text_color=color)
            except Exception as e:
                print(f"Błąd aktualizacji budżetu: {e}")

    update_budget_label()

    ctk.CTkLabel(header_frame, text=f"PANEL: {title_text.upper()}", font=("Roboto", 24, "bold")).place(relx=0.5,
                                                                                                       rely=0.5,
                                                                                                       anchor="center")
    role_color = "#e74c3c" if user_level == 3 else ("#f1c40f" if user_level == 2 else "#2ecc71")
    ctk.CTkLabel(header_frame, text=f"ZALOGOWANO JAKO: {role_name}", text_color=role_color,
                 font=("Roboto", 12, "bold")).place(relx=0.5, rely=0.8, anchor="center")

    ctk.CTkButton(header_frame, text="WYLOGUJ", command=root.quit, fg_color="#c0392b", hover_color="#e74c3c",
                  width=120).place(relx=0.95, rely=0.5, anchor="e")

    # --- PRZYCISK PDF ---
    def export_to_pdf_action():
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("Plik PDF", "*.pdf")],
            initialfile=f"Raport_{username}.pdf"
        )
        if file_path:
            success, msg = convert.generate_pdf_from_csv(title_text, file_path, title=title_text)
            if success:
                tk.messagebox.showinfo("Sukces", msg, parent=root)
            else:
                tk.messagebox.showerror("Błąd", msg, parent=root)

    ctk.CTkButton(header_frame, text="POBIERZ PDF", command=export_to_pdf_action,
                  fg_color="#16a085", hover_color="#1abc9c", width=120).place(relx=0.85, rely=0.5, anchor="e")
    # --------------------

    if user_level == 3:
        ctk.CTkButton(header_frame, text="PANEL ADMIN", command=lambda: show_admin_tools(root),
                      fg_color="#8e44ad", hover_color="#9b59b6", width=120).place(relx=0.75, rely=0.5, anchor="e")

    table_frame = ctk.CTkFrame(root, corner_radius=10, fg_color="transparent")
    table_frame.pack(fill="both", expand=True, padx=10, pady=20)

    style = ttk.Style()
    style.theme_use("default")
    style.configure("Treeview", background="#2b2b2b", foreground="white", fieldbackground="#2b2b2b", rowheight=35,
                    borderwidth=0, font=("Roboto", 12))
    style.map('Treeview', background=[('selected', '#1f538d')])
    style.configure("Treeview.Heading", background="#1a1a1a", foreground="white", relief="flat",
                    font=("Roboto", 13, "bold"), padding=(10, 10))

    tree_scroll_y = ctk.CTkScrollbar(table_frame, orientation="vertical")
    tree_scroll_y.pack(side="right", fill="y", padx=(0, 5), pady=5)
    tree_scroll_x = ctk.CTkScrollbar(table_frame, orientation="horizontal")
    tree_scroll_x.pack(side="bottom", fill="x", padx=5, pady=(0, 5))

    cols = list(dataframe_view.columns)
    display_cols = ["Akcja"] + cols if allow_edit else cols

    tree = ttk.Treeview(table_frame, columns=display_cols, show='headings', yscrollcommand=tree_scroll_y.set,
                        xscrollcommand=tree_scroll_x.set)
    tree_scroll_y.configure(command=tree.yview)
    tree_scroll_x.configure(command=tree.xview)

    if allow_edit:
        tree.heading("Akcja", text="OPERACJE")
        tree.column("Akcja", width=100, anchor="center", stretch=False)

    for col in cols:
        tree.heading(col, text=col.upper())
        tree.column(col, width=150, anchor="w", stretch=True)

    def refresh_table():
        for item in tree.get_children():
            tree.delete(item)
        try:
            fresh_df = server.get_department_data(title_text)
            nonlocal dataframe
            dataframe = fresh_df
            view_df = fresh_df[visible_columns]
            for index, row in view_df.iterrows():
                values = ["✎ EDYTUJ"] + list(row)
                tree.insert("", "end", iid=index, values=values)
            update_budget_label()
        except Exception as e:
            print(f"Błąd odświeżania: {e}")

    for index, row in dataframe_view.iterrows():
        values = ["✎ EDYTUJ"] + list(row)
        tree.insert("", "end", iid=index, values=values)

    tree.pack(fill="both", expand=True, padx=5, pady=5)

    def handle_save_request(row_id, new_data_list):
        try:
            print(f"KLIENT: Wysyłam dane dla wiersza {row_id}")
            success, msg = server.update_record(title_text, row_id, new_data_list, username)
            if success:
                refresh_table()
            else:
                tk.messagebox.showerror("Błąd Zapisu", msg)
        except Exception as e:
            tk.messagebox.showerror("Błąd", f"Nie udało się zapisać: {e}")

    def on_tree_click(event):
        region = tree.identify_region(event.x, event.y)
        if region != "cell": return
        col_id = tree.identify_column(event.x)
        row_id = tree.identify_row(event.y)
        if not row_id: return

        if col_id == '#1':
            try:
                full_db = server.get_department_data(title_text)
                full_row_data = full_db.loc[int(row_id)].tolist()
                full_columns = list(full_db.columns)

                if user_level == 1:
                    user_form.open_form(root, row_id, full_row_data, full_columns, handle_save_request)
                elif user_level == 2:
                    admin_form.open_form(root, row_id, full_row_data, full_columns, handle_save_request)
                elif user_level == 3:
                    master_form.open_form(root, row_id, full_row_data, full_columns, handle_save_request)

            except Exception as e:
                print(f"Błąd otwierania formularza: {e}")
                import traceback
                traceback.print_exc()

    tree.bind("<ButtonRelease-1>", on_tree_click)

    root.mainloop()
    try:
        root.destroy()
    except:
        pass

if __name__ == "__main__":
    print("Klient: Start.")
    while True:
        username, password = show_login_window()
        if not username and not password:
            break

        try:
            user_info = server.zaloguj_uzytkownika(username, password)
        except AttributeError:
            show_message("Błąd: Brak połączenia z funkcjami serwera.")
            break

        if user_info and user_info.get("status") == "Sukces":
            target_file = user_info['baza_danych']
            try:
                level = int(user_info['poziom'])
            except ValueError:
                level = 1

            try:
                user_data = server.get_department_data(target_file)
                if user_data is not None:
                    show_data_window(user_data, target_file, level, username)
                else:
                    show_message(f"Błąd wczytywania bazy '{target_file}'.")
            except Exception as e:
                show_message(f"Błąd krytyczny: {e}")
        else:
            show_message("Niepoprawny login lub hasło")