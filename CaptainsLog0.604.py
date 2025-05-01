# captainslog_v0600_final.py (Part 1 of 3)
# CaptainsLog V0.600 – Fully Rebuilt Version

import tkinter as tk
from tkinter import ttk, messagebox
import os
import json
import datetime
import subprocess

class PlaceholderEntry(tk.Entry):
    def __init__(self, master=None, placeholder="", color='grey', *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.placeholder = placeholder
        self.placeholder_color = color
        self.default_fg_color = self['fg']
        self.bind("<FocusIn>", self.clear_placeholder)
        self.bind("<FocusOut>", self.add_placeholder)
        self.add_placeholder()

    def clear_placeholder(self, event=None):
        if self['fg'] == self.placeholder_color:
            self.delete(0, 'end')
            self['fg'] = self.default_fg_color

    def add_placeholder(self, event=None):
        if not self.get():
            self.insert(0, self.placeholder)
            self['fg'] = self.placeholder_color

    def force_clear(self):
        if self['fg'] == self.placeholder_color:
            self.delete(0, 'end')
            self['fg'] = self.default_fg_color

    def refresh_placeholder(self):
        if not self.get():
            self.add_placeholder()

    def is_placeholder_active(self):
        return self['fg'] == self.placeholder_color

class CaptainsLog:
    def __init__(self, root):
        self.root = root
        self.root.title("CaptainsLog V0.600")
        self.qsos = []
        self.session_meta = {"station_callsign": "", "last_freq": "", "last_mode": ""}
        self.log_folder = os.path.join(os.getcwd(), "logs")
        os.makedirs(self.log_folder, exist_ok=True)
        self.log_file = os.path.join(self.log_folder, "current_log.json")
        self.partial_check_path = os.path.join(self.log_folder, "partial_check.json")
        self.setup_ui()
        self.load_previous_log()

    def setup_ui(self):
        style = ttk.Style()
        style.configure("Treeview", font=("Arial", 10))
        style.map("Treeview",
            background=[("selected", "#cce5ff")],
            foreground=[("selected", "black")]
        )
        self.tree = ttk.Treeview(self.root, columns=("callsign", "snt", "rcv", "freq", "mode", "name", "comments"), show="headings")
        self.tree.tag_configure("left", background="#dddddd", foreground="#555555")
        top_frame = tk.Frame(self.root, padx=10, pady=5)
        top_frame.pack(fill='x')

        tk.Label(top_frame, text="My Callsign:", font=("Arial", 10)).grid(row=0, column=0, sticky='w')
        self.my_callsign = tk.Entry(top_frame, font=("Arial", 10))
        self.my_callsign.grid(row=0, column=1, sticky='ew', padx=(5, 15))

        tk.Label(top_frame, text="Frequency (MHz):", font=("Arial", 10)).grid(row=0, column=2, sticky='w')
        self.my_frequency = tk.Entry(top_frame, font=("Arial", 10))
        self.my_frequency.grid(row=0, column=3, sticky='ew', padx=(5, 15))

        tk.Label(top_frame, text="Mode:", font=("Arial", 10)).grid(row=0, column=4, sticky='w')
        self.my_mode = tk.Entry(top_frame, font=("Arial", 10))
        self.my_mode.grid(row=0, column=5, sticky='ew')

        top_frame.columnconfigure(1, weight=1)
        top_frame.columnconfigure(3, weight=1)
        top_frame.columnconfigure(5, weight=1)

        self.my_callsign.bind('<KeyRelease>', lambda event: self.force_uppercase(self.my_callsign))
        self.my_mode.bind('<KeyRelease>', lambda event: self.force_uppercase(self.my_mode))

        for col in [("callsign", "Callsign", 100), ("snt", "SNT", 40), ("rcv", "RCV", 40),
                    ("freq", "Freq", 80), ("mode", "Mode", 60), ("name", "Name", 140), ("comments", "Comments", 260)]:
            self.tree.heading(col[0], text=col[1], anchor="w" if col[0] in ("callsign", "name", "comments") else "center")
            self.tree.column(col[0], width=col[2], anchor="w" if col[0] in ("callsign", "name", "comments") else "center", stretch=col[0] in ("name", "comments"))
        self.tree.pack(fill='both', expand=True)

        bottom_frame = tk.Frame(self.root, padx=10)
        bottom_frame.pack(fill='x', pady=(10, 10))

        self.callsign_entry = PlaceholderEntry(bottom_frame, placeholder="Call", font=("Arial", 10), width=16)
        self.callsign_entry.grid(row=0, column=0, padx=(0, 5))

        self.snt_entry = tk.Entry(bottom_frame, font=("Arial", 10), width=6)
        self.snt_entry.insert(0, "59")
        self.snt_entry.grid(row=0, column=1, padx=(0, 5))

        self.rcv_entry = tk.Entry(bottom_frame, font=("Arial", 10), width=6)
        self.rcv_entry.insert(0, "59")
        self.rcv_entry.grid(row=0, column=2, padx=(0, 5))

        self.name_entry = PlaceholderEntry(bottom_frame, placeholder="Name", font=("Arial", 10), width=24)
        self.name_entry.grid(row=0, column=3, padx=(0, 5), sticky='ew')

        self.comments_entry = PlaceholderEntry(bottom_frame, placeholder="Comments", font=("Arial", 10))
        self.comments_entry.grid(row=0, column=4, padx=(0, 5), sticky='ew')

        bottom_frame.columnconfigure(3, weight=1)
        bottom_frame.columnconfigure(4, weight=2)

        self.callsign_entry.focus()
        self.callsign_entry.bind("<Return>", self.fill_snt_rcv_move_name)
        self.callsign_entry.bind("<space>", self.fill_snt_rcv_move_name)

        for entry in [self.snt_entry, self.rcv_entry]:
            entry.bind("<Return>", self.next_focus)
            entry.bind("<space>", self.next_focus)

        self.name_entry.bind("<Return>", self.next_focus)
        self.comments_entry.bind("<Return>", self.log_qso)

        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.tree.bind("<Button-3>", self.show_context_menu)
        self.root.after(100, self.callsign_entry.focus_force)
        self.root.bind_all("<Alt-w>", self.clear_entry_fields)

    def force_uppercase(self, entry_widget):
        content = entry_widget.get()
        entry_widget.delete(0, 'end')
        entry_widget.insert(0, content.upper())

    def next_focus(self, event):
        event.widget.tk_focusNext().focus()
        return "break"

    def fill_snt_rcv_move_name(self, event):
        if not self.snt_entry.get():
            self.snt_entry.insert(0, "59")
        if not self.rcv_entry.get():
            self.rcv_entry.insert(0, "59")

        callsign = self.callsign_entry.get().strip().upper()
        if os.path.exists(self.partial_check_path):
            try:
                with open(self.partial_check_path, "r") as f:
                    partial_db = json.load(f)
                if callsign in partial_db:
                    known = partial_db[callsign]
                    if self.name_entry.is_placeholder_active() and known.get("name"):
                        self.name_entry.delete(0, 'end')
                        self.name_entry.insert(0, known["name"])
                        self.name_entry['fg'] = self.name_entry.default_fg_color
                    if self.comments_entry.is_placeholder_active() and known.get("comments"):
                        self.comments_entry.delete(0, 'end')
                        self.comments_entry.insert(0, known["comments"])
                        self.comments_entry['fg'] = self.comments_entry.default_fg_color
            except Exception:
                pass
        self.name_entry.focus()
        return "break"

    def clear_entry_fields(self, event=None):
        self.callsign_entry.delete(0, 'end')
        self.snt_entry.delete(0, 'end')
        self.rcv_entry.delete(0, 'end')
        self.name_entry.delete(0, 'end')
        self.comments_entry.delete(0, 'end')
        self.snt_entry.insert(0, "59")
        self.rcv_entry.insert(0, "59")
        self.callsign_entry.refresh_placeholder()
        self.name_entry.refresh_placeholder()
        self.comments_entry.refresh_placeholder()
        self.callsign_entry.focus()
        return "break"
        
    def log_qso(self, event=None):
        if not self.my_callsign.get().strip() or not self.my_frequency.get().strip() or not self.my_mode.get().strip():
            messagebox.showwarning("Missing Info", "Please enter your My Callsign, Frequency, and Mode before logging.")
            return
        callsign = self.callsign_entry.get().strip().upper()
        if callsign and callsign != "CALL":
            now = datetime.datetime.utcnow()
            name_val = "" if self.name_entry.is_placeholder_active() else self.name_entry.get().strip()
            comments_val = "" if self.comments_entry.is_placeholder_active() else self.comments_entry.get().strip()

            qso = {
                "callsign": callsign,
                "snt": self.snt_entry.get().strip(),
                "rcv": self.rcv_entry.get().strip(),
                "name": name_val,
                "comments": comments_val,
                "date": now.strftime("%Y%m%d"),
                "time_on": now.strftime("%H%M"),
                "time_off": now.strftime("%H%M"),
                "freq": self.my_frequency.get().strip(),
                "mode": self.my_mode.get().strip().upper(),
                "station_callsign": self.my_callsign.get().strip().upper(),
                "tags": []
            }

            self.qsos.append(qso)

            self.tree.insert("", "end", values=(
                qso["callsign"],
                qso["snt"],
                qso["rcv"],
                qso["freq"],
                qso["mode"],
                qso["name"],
                qso["comments"]
            ), tags=())

            if name_val:
                try:
                    if os.path.exists(self.partial_check_path):
                        with open(self.partial_check_path, "r") as f:
                            partial_data = json.load(f)
                    else:
                        partial_data = {}

                    if callsign not in partial_data:
                        partial_data[callsign] = {}
                    if name_val and not partial_data[callsign].get("name"):
                        partial_data[callsign]["name"] = name_val
                    if comments_val and not partial_data[callsign].get("comments"):
                        partial_data[callsign]["comments"] = comments_val

                    with open(self.partial_check_path, "w") as f:
                        json.dump(partial_data, f, indent=4)
                except Exception:
                    pass

            self.callsign_entry.delete(0, 'end')
            self.snt_entry.delete(0, 'end')
            self.rcv_entry.delete(0, 'end')
            self.name_entry.delete(0, 'end')
            self.comments_entry.delete(0, 'end')
            self.snt_entry.insert(0, "59")
            self.rcv_entry.insert(0, "59")
            self.callsign_entry.focus()
            self.callsign_entry.refresh_placeholder()
            self.name_entry.refresh_placeholder()
            self.comments_entry.refresh_placeholder()

            self.session_meta["station_callsign"] = self.my_callsign.get().strip().upper()
            self.session_meta["last_freq"] = self.my_frequency.get().strip()
            self.session_meta["last_mode"] = self.my_mode.get().strip().upper()

            self.save_current_log()
        else:
            messagebox.showwarning("Input Error", "Please enter a valid callsign.")

    def edit_entry(self):
        selected_item = self.tree.selection()
        if selected_item:
            index = self.tree.index(selected_item)
            qso = self.qsos[index]
            edit_win = tk.Toplevel(self.root)
            edit_win.title("Edit QSO")
            fields = ["callsign", "snt", "rcv", "freq", "mode", "name", "comments"]
            entries = {}

            for i, field in enumerate(fields):
                tk.Label(edit_win, text=field.capitalize()).grid(row=i, column=0, sticky='w', padx=10, pady=5)
                entry = tk.Entry(edit_win)
                entry.insert(0, qso[field])
                entry.grid(row=i, column=1, sticky='ew', padx=10, pady=5)
                entries[field] = entry

            def save_edit():
                for field in fields:
                    self.qsos[index][field] = entries[field].get().strip()
                updated = self.qsos[index]
                self.tree.item(selected_item, values=(
                    updated["callsign"],
                    updated["snt"],
                    updated["rcv"],
                    updated["freq"],
                    updated["mode"],
                    updated["name"],
                    updated["comments"]
                ))
                self.save_current_log()
                edit_win.destroy()

            def delete_entry():
                self.tree.delete(selected_item)
                self.qsos.pop(index)
                self.save_current_log()
                edit_win.destroy()

            def cancel_edit():
                edit_win.destroy()

            tk.Button(edit_win, text="Save", command=save_edit).grid(row=len(fields), column=0, padx=10, pady=10)
            tk.Button(edit_win, text="Delete", command=delete_entry).grid(row=len(fields), column=1, padx=10, pady=10)
            tk.Button(edit_win, text="Cancel", command=cancel_edit).grid(row=len(fields), column=2, padx=10, pady=10)

    def mark_left(self):
        selected_item = self.tree.selection()
        if selected_item:
            self.tree.item(selected_item, tags=("left",))
            self.tree.selection_remove(selected_item)

    def mark_rejoined(self):
        selected_item = self.tree.selection()
        if selected_item:
            self.tree.item(selected_item, tags=())
            self.tree.selection_remove(selected_item)

    def show_context_menu(self, event):
        row_id = self.tree.identify_row(event.y)
        self.context_menu.delete(0, 'end')
        if row_id:
            self.tree.selection_set(row_id)
            tags = self.tree.item(row_id, "tags")
            if "left" in tags:
                self.context_menu.add_command(label="REJOINED", command=self.mark_rejoined)
            else:
                self.context_menu.add_command(label="LEFT", command=self.mark_left)
            self.context_menu.add_separator()
            self.context_menu.add_command(label="Edit Entry", command=self.edit_entry)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Export to ADIF", command=self.export_adif)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Help / About", command=self.show_help)
        self.context_menu.tk_popup(event.x_root, event.y_root)
        self.context_menu.grab_release()

    def export_adif(self):
        if not self.qsos:
            messagebox.showinfo("Export", "No QSOs to export.")
            return
        base_name = f"{datetime.datetime.utcnow().strftime('%Y%m%d')}_{self.session_meta['station_callsign'] or 'LOG'}"
        adif_file = os.path.join(self.log_folder, base_name + ".adi")
        with open(adif_file, "w") as f:
            f.write("<ADIF_VER:5>3.1.0\n<PROGRAMID:12>CaptainsLog\n<EOH>\n")
            for qso in self.qsos:
                f.write(
                    f"<CALL:{len(qso['callsign'])}>{qso['callsign']}"
                    f"<QSO_DATE:8>{qso['date']}<TIME_ON:4>{qso['time_on']}"
                    f"<RST_SENT:2>{qso['snt']}<RST_RCVD:2>{qso['rcv']}"
                    f"<NAME:{len(qso['name'])}>{qso['name']}"
                    f"<COMMENT:{len(qso['comments'])}>{qso['comments']}"
                    f"<FREQ:{len(qso['freq'])}>{qso['freq']}"
                    f"<MODE:{len(qso['mode'])}>{qso['mode']}"
                    f"<STATION_CALLSIGN:{len(qso['station_callsign'])}>{qso['station_callsign']}<EOR>\n"
                )
        if messagebox.askyesno("Export", "ADIF export complete. Open in Notepad?"):
            subprocess.Popen(["notepad", adif_file])

    def save_current_log(self):
        with open(self.log_file, 'w') as f:
            json.dump({**self.session_meta, "qsos": self.qsos}, f, indent=4)

    def load_previous_log(self):
        if not os.path.exists(self.log_file):
            return

        answer = [None]
        def close_and_continue(): answer[0] = True; prompt.destroy()
        def close_and_cancel(): answer[0] = False; prompt.destroy()

        prompt = tk.Toplevel(self.root)
        prompt.title("Previous Log Found")
        prompt.geometry("360x120")
        prompt.grab_set()

        tk.Label(prompt, text="Continue previous log?", font=("Arial", 12)).pack(pady=10)
        btn_frame = tk.Frame(prompt)
        btn_frame.pack()

        tk.Button(btn_frame, text="Yes", width=10, command=close_and_continue).pack(side="left", padx=10)
        tk.Button(btn_frame, text="No", width=10, command=close_and_cancel).pack(side="right", padx=10)
        prompt.bind("<Return>", lambda e: close_and_continue())
        prompt.bind("<Escape>", lambda e: close_and_cancel())
        prompt.wait_window()

        if not answer[0]:
            self.callsign_entry.focus_force()
            return

        try:
            with open(self.log_file, 'r') as f:
                data = json.load(f)
                self.qsos = data.get("qsos", [])
                self.session_meta.update({
                    "station_callsign": data.get("station_callsign", ""),
                    "last_freq": data.get("last_freq", ""),
                    "last_mode": data.get("last_mode", "")
                })
                self.my_callsign.insert(0, self.session_meta["station_callsign"])
                self.my_frequency.insert(0, self.session_meta["last_freq"])
                self.my_mode.insert(0, self.session_meta["last_mode"])
                for qso in self.qsos:
                    self.tree.insert("", "end", values=(
                        qso["callsign"], qso["snt"], qso["rcv"],
                        qso["freq"], qso["mode"], qso["name"], qso["comments"]
                    ), tags=tuple(qso.get("tags", [])))
                self.callsign_entry.focus_force()
        except Exception as e:
            messagebox.showerror("Load Error", f"Unable to load previous log:\n\n{e}")

    def show_help(self):
        help_win = tk.Toplevel(self.root)
        help_win.title("About CaptainsLog")
        help_win.geometry("500x400")
        help_win.resizable(False, False)

        tk.Label(help_win, text="CaptainsLog V0.600", font=("Arial", 14, "bold")).pack(pady=(10, 5))
        tk.Label(help_win, text="Created by Callum M0MCX (DXCommander)", font=("Arial", 10)).pack()
        tk.Label(help_win, text="Rebuilt by ChatGPT Assistant – OpenAI", font=("Arial", 10)).pack()

        text_frame = tk.Frame(help_win, padx=10, pady=10)
        text_frame.pack(fill="both", expand=True)

        help_text = tk.Text(text_frame, wrap="word", font=("Arial", 10), height=15)
        help_text.insert("1.0",
            "This is a lightweight logging tool for Ham Radio net controllers.\n\n"
            "- Portable and requires no installation\n"
            "- Logs are stored as .json in a local /logs/ folder\n"
            "- Export logs to ADIF via right-click\n"
            "- Edit, delete, and mark QSOs as LEFT or Rejoined\n"
            "- Auto-fill operator name/comments from previous entries\n"
            "- Easy data entry with tab/return/space shortcuts\n\n"
            "GitHub: https://github.com/DXCommander/captainslog/releases\n\n"
            "This tool was co-developed interactively using ChatGPT to assist a non-programmer build a useful ham radio utility.")
        help_text.config(state="disabled")
        help_text.pack(fill="both", expand=True)

        tk.Button(help_win, text="Close", command=help_win.destroy).pack(pady=(0, 10))

if __name__ == "__main__":
    root = tk.Tk()
    app = CaptainsLog(root)
    root.geometry("1000x600")
    root.mainloop()
