import pandas as pd
import os
import shutil
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Agg')


def get_user_role(username):
    try:
        if os.path.exists('departament_permission.txt'):
            with open('departament_permission.txt', 'r', encoding='utf-8') as f:
                for linia in f:
                    dane = linia.strip().split(';')
                    if len(dane) >= 3:
                        if dane[0] == username:
                            return dane[2]
    except Exception:
        pass
    return None


def zaloguj_uzytkownika(login_input, haslo_input):
    zalogowany = False
    try:
        if not os.path.exists('passwords.txt'):
            return {"status": "Błąd", "info": "Brak pliku passwords.txt"}

        with open('passwords.txt', 'r', encoding='utf-8') as f_pass:
            for linia in f_pass:
                dane = linia.strip().split(';')
                if len(dane) == 2:
                    login_plik, haslo_plik = dane
                    if login_plik == login_input and haslo_plik == haslo_input:
                        zalogowany = True
                        break
    except Exception as e:
        print(f"SERWER: Błąd odczytu haseł: {e}")
        return None

    if not zalogowany:
        return None

    try:
        if not os.path.exists('departament_permission.txt'):
            return {"status": "Błąd", "info": "Brak pliku departament_permission.txt"}

        with open('departament_permission.txt', 'r', encoding='utf-8') as f_perm:
            for linia in f_perm:
                dane = linia.strip().split(';')
                if len(dane) >= 3:
                    uzytkownik_perm = dane[0]
                    if uzytkownik_perm == login_input:
                        return {
                            "status": "Sukces",
                            "login": login_input,
                            "baza_danych": dane[1],
                            "poziom": dane[2]
                        }
    except Exception as e:
        print(f"SERWER: Błąd odczytu uprawnień: {e}")

    return {"status": "Błąd", "info": "Użytkownik nie ma uprawnień."}


def get_department_data(filename):
    if not os.path.exists(filename):
        print(f"SERWER: Plik {filename} nie istnieje. Tworzę nowy.")
        df = pd.DataFrame(columns=['Część budżetowa', 'Dział', 'Rozdział', 'Plan WI', 'Potrzeby finansowe na 2026 rok',
                                   'Potrzeby finansowe na 2027 rok'])
        df.to_csv(filename, sep=';', index=False, encoding='utf-8')
        return df

    try:
        try:
            df = pd.read_csv(filename, sep=';', encoding='utf-8', dtype=str)
            if len(df.columns) < 2:
                df = pd.read_csv(filename, sep=',', encoding='utf-8', dtype=str)
        except:
            df = pd.read_csv(filename, sep=',', encoding='utf-8', dtype=str)

        df.columns = df.columns.str.replace('\n', ' ', regex=False).str.strip()
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        df = df.dropna(how='all', axis=1)
        df = df.dropna(how='all')

        if 'Dział' in df.columns:
            df = df[df['Dział'].notna()]
            df = df[df['Dział'].str.strip() != '']
            df = df[df['Dział'].str.lower() != 'nan']

        df = df.reset_index(drop=True)
        df = df.fillna("")

        target_cols = ['Potrzeby finansowe na 2026 rok', 'Potrzeby finansowe na 2027 rok']
        for col in target_cols:
            if col not in df.columns:
                df[col] = ""

        df.to_csv(filename, sep=';', index=False, encoding='utf-8')
        return df
    except Exception as e:
        print(f"SERWER: Błąd wczytywania {filename}: {e}")
        return None


def get_user_budget_limit(username):
    try:
        if os.path.exists('user_budgets.csv'):
            b_df = pd.read_csv('user_budgets.csv', sep=';', dtype=str)
            row = b_df[b_df['Login'] == username]
            if not row.empty:
                val_str = str(row.iloc[0]['Budget']).replace(' ', '').replace(',', '.')
                return float(val_str)
    except:
        pass
    return 0.0


def update_record(filename, row_id, new_data_list, username=None):
    print(f"SERWER: Aktualizacja wiersza ID: {row_id}")
    try:
        df = get_department_data(filename)
        if df is not None:
            idx = int(row_id)
            if len(new_data_list) == len(df.columns):

                if username:
                    if get_user_role(username) != '3':
                        budget_limit = get_user_budget_limit(username)

                        current_usage_others = 0.0
                        target_cols = ['Potrzeby finansowe na 2026 rok', 'Potrzeby finansowe na 2027 rok']
                        col_indices = [df.columns.get_loc(c) for c in target_cols if c in df.columns]

                        for i, row in df.iterrows():
                            if i == idx: continue
                            for col_name in target_cols:
                                if col_name in df.columns:
                                    val = str(row[col_name]).replace(' ', '').replace(',', '.')
                                    try:
                                        if val: current_usage_others += float(val)
                                    except:
                                        pass

                        new_row_usage = 0.0
                        for col_idx in col_indices:
                            if col_idx < len(new_data_list):
                                val = str(new_data_list[col_idx]).replace(' ', '').replace(',', '.')
                                try:
                                    if val: new_row_usage += float(val)
                                except:
                                    pass

                        total_projected = current_usage_others + new_row_usage

                        if total_projected > budget_limit:
                            return False, f"Przekroczono budżet! Limit: {budget_limit}, Wymagane: {total_projected:.2f}"

                df.loc[idx] = new_data_list
                df.to_csv(filename, sep=';', index=False, encoding='utf-8')
                print("SERWER: Zapisano poprawnie.")
                return True, "Zapisano pomyślnie."
            else:
                return False, f"Oczekiwano {len(df.columns)} kolumn, otrzymano {len(new_data_list)}."
    except Exception as e:
        print(f"SERWER BŁĄD: {e}")
        return False, str(e)
    return False, "Nieznany błąd zapisu."


def admin_add_user(username, password, db_file, level):
    try:
        with open('passwords.txt', 'r', encoding='utf-8') as f:
            if any(line.startswith(f"{username};") for line in f):
                return False, "Użytkownik już istnieje"

        with open('passwords.txt', 'a', encoding='utf-8') as f:
            f.write(f"\n{username};{password}")

        with open('departament_permission.txt', 'a', encoding='utf-8') as f:
            f.write(f"\n{username};{db_file};{level}")

        return True, "Dodano użytkownika"
    except Exception as e:
        return False, str(e)


def admin_delete_user(username):
    try:
        found = False
        lines = []
        with open('passwords.txt', 'r', encoding='utf-8') as f:
            lines = f.readlines()

        with open('passwords.txt', 'w', encoding='utf-8') as f:
            for line in lines:
                if not line.startswith(f"{username};"):
                    f.write(line)
                else:
                    found = True

        lines = []
        with open('departament_permission.txt', 'r', encoding='utf-8') as f:
            lines = f.readlines()

        with open('departament_permission.txt', 'w', encoding='utf-8') as f:
            for line in lines:
                if not line.startswith(f"{username};"):
                    f.write(line)

        if found:
            return True, "Użytkownik usunięty"
        else:
            return False, "Nie znaleziono użytkownika"
    except Exception as e:
        return False, str(e)


def admin_hard_reset_db(filename):
    try:
        if os.path.exists(filename):
            shutil.copy(filename, f"{filename}.bak")

        df = pd.DataFrame(columns=['Część budżetowa', 'Dział', 'Rozdział', 'Plan WI', 'Potrzeby finansowe na 2026 rok',
                                   'Potrzeby finansowe na 2027 rok'])
        df.to_csv(filename, sep=';', index=False, encoding='utf-8')
        return True, "Baza zresetowana (kopia .bak utworzona)"
    except Exception as e:
        return False, str(e)


def get_remaining_budget_value(username, filename, limit):
    current_usage = 0.0
    try:
        if os.path.exists(filename):
            try:
                df = pd.read_csv(filename, sep=';', dtype=str)
            except:
                df = pd.read_csv(filename, sep=',', dtype=str)

            target_cols = ['Potrzeby finansowe na 2026 rok', 'Potrzeby finansowe na 2027 rok']

            for col in target_cols:
                if col in df.columns:
                    for val in df[col]:
                        if pd.isna(val): continue
                        try:
                            clean_val = str(val).replace(' ', '').replace(',', '.')
                            if clean_val:
                                current_usage += float(clean_val)
                        except ValueError:
                            pass
    except Exception:
        pass
    return limit - current_usage


def get_users_for_budget():
    users_data = []
    user_db_map = {}
    try:
        if os.path.exists('departament_permission.txt'):
            with open('departament_permission.txt', 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split(';')
                    if len(parts) >= 3:
                        user, db_file, role = parts[0], parts[1], parts[2]
                        if role in ['1', '2']:
                            user_db_map[user] = {'role': role, 'db': db_file}
    except Exception as e:
        print(f"SERWER: Błąd odczytu uprawnień: {e}")
        return []

    budget_map = {}
    budget_file = 'user_budgets.csv'
    if os.path.exists(budget_file):
        try:
            b_df = pd.read_csv(budget_file, sep=';', dtype=str)
            for _, row in b_df.iterrows():
                try:
                    val_str = str(row['Budget']).replace(' ', '').replace(',', '.')
                    budget_map[row['Login']] = float(val_str)
                except:
                    budget_map[row['Login']] = 0.0
        except Exception as e:
            print(f"SERWER: Błąd odczytu budżetów: {e}")

    for login, info in user_db_map.items():
        limit = budget_map.get(login, 0.0)
        remaining = get_remaining_budget_value(login, info['db'], limit)

        users_data.append({
            'login': login,
            'role': info['role'],
            'limit': f"{limit:.2f}",
            'remaining': f"{remaining:.2f}"
        })

    return users_data


def set_user_budget(username, amount):
    budget_file = 'user_budgets.csv'
    try:
        if os.path.exists(budget_file):
            df = pd.read_csv(budget_file, sep=';', dtype=str)
        else:
            df = pd.DataFrame(columns=['Login', 'Budget'])

        clean_amount = str(amount).replace(',', '.')

        if username in df['Login'].values:
            df.loc[df['Login'] == username, 'Budget'] = clean_amount
        else:
            new_row = pd.DataFrame([{'Login': username, 'Budget': clean_amount}])
            df = pd.concat([df, new_row], ignore_index=True)

        df.to_csv(budget_file, sep=';', index=False, encoding='utf-8')
        return True, "Zapisano budżet."
    except Exception as e:
        return False, str(e)


def get_user_budget(username):
    return str(get_user_budget_limit(username))


def get_remaining_budget(username, filename):
    if get_user_role(username) == '3':
        return "Bez limitu"

    allocated_limit = get_user_budget_limit(username)
    current_usage = 0.0
    try:
        if os.path.exists(filename):
            try:
                df = pd.read_csv(filename, sep=';', dtype=str)
            except:
                df = pd.read_csv(filename, sep=',', dtype=str)

            target_cols = ['Potrzeby finansowe na 2026 rok', 'Potrzeby finansowe na 2027 rok']

            for col in target_cols:
                if col in df.columns:
                    for val in df[col]:
                        if pd.isna(val): continue
                        try:
                            clean_val = str(val).replace(' ', '').replace(',', '.')
                            if clean_val:
                                current_usage += float(clean_val)
                        except ValueError:
                            pass
    except Exception as e:
        print(f"SERWER: Błąd obliczania zużycia: {e}")

    remaining = allocated_limit - current_usage
    return f"{remaining:.2f}"


def generuj_wykres_png(filename, output_path):
    print(f"SERWER: Generowanie wykresu dla {filename}...")
    try:
        df = get_department_data(filename)
        if df is None or df.empty:
            return False, "Brak danych do wygenerowania wykresu."

        def clean_currency(val):
            if pd.isna(val) or str(val).strip() == "":
                return 0.0
            try:
                clean_str = str(val).replace(' ', '').replace(',', '.')
                return float(clean_str)
            except ValueError:
                return 0.0

        col_2026 = 'Potrzeby finansowe na 2026 rok'
        col_2027 = 'Potrzeby finansowe na 2027 rok'

        sum_2026 = df[col_2026].apply(clean_currency).sum() if col_2026 in df.columns else 0.0
        sum_2027 = df[col_2027].apply(clean_currency).sum() if col_2027 in df.columns else 0.0

        fig, ax = plt.subplots(figsize=(10, 6))
        lata = ['2026', '2027']
        wartosci = [sum_2026, sum_2027]
        kolory = ['#3498db', '#e74c3c']

        bars = ax.bar(lata, wartosci, color=kolory, width=0.5)

        ax.set_title(f'Zestawienie potrzeb finansowych: {filename}', fontsize=14, fontweight='bold')
        ax.set_ylabel('Kwota (PLN)', fontsize=12)
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        ax.ticklabel_format(style='plain', axis='y')

        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{height:,.2f}'.replace(',', ' ').replace('.', ','),
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom', fontweight='bold')

        plt.savefig(output_path, dpi=100)
        plt.close(fig)

        return True, "Wykres został wygenerowany pomyślnie."

    except Exception as e:
        print(f"SERWER BŁĄD WYKRESU: {e}")
        return False, f"Błąd generowania wykresu: {str(e)}"