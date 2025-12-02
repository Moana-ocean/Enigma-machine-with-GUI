import tkinter as tk
from tkinter import ttk, messagebox
from Enigma import Rotor, Reflector, Plugboard, Enigma_machine, ROTORS, REFLECTOR
import string
import ast, re, datetime

class SimpleEnigmaGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple Enigma Machine Simulator")
        self.create_widgets()

    def create_widgets(self):
        # Main frame
        frame = tk.Frame(self.root)
        frame.pack(side='left', padx=10, pady=10)
        # Plaintext/ciphertext
        tk.Label(frame, text="Text:").grid(row=0, column=0, sticky='e')
        self.text_entry = tk.Entry(frame, width=40)
        self.text_entry.grid(row=0, column=1, columnspan=4, padx=5, pady=5)
        # Rotor selection and positions
        self.rotor_vars = []
        self.position_vars = []
        rotor_names = list(ROTORS.keys())
        for i in range(3):
            tk.Label(frame, text=f"Rotor {i+1}:").grid(row=1, column=i*2, sticky='e')
            rotor_var = tk.StringVar(value=rotor_names[i])
            rotor_menu = ttk.Combobox(frame, textvariable=rotor_var, values=rotor_names, width=5, state='readonly')
            rotor_menu.grid(row=1, column=i*2+1, sticky='w')
            self.rotor_vars.append(rotor_var)
            tk.Label(frame, text=f"Pos {i+1}:").grid(row=2, column=i*2, sticky='e')
            pos_var = tk.StringVar(value=ROTORS[rotor_var.get()][0])
            pos_entry = tk.Entry(frame, textvariable=pos_var, width=3)
            pos_entry.grid(row=2, column=i*2+1, sticky='w')
            self.position_vars.append(pos_var)
            # Update position to first letter when rotor selection changes
            def make_on_rotor_change(idx):
                def on_rotor_change_var(*args):
                    new_first = ROTORS[self.rotor_vars[idx].get()][0]
                    self.position_vars[idx].set(new_first)
                return on_rotor_change_var
            rotor_var.trace_add('write', make_on_rotor_change(i))
        # Reflector display
        tk.Label(frame, text=f"Reflector: {REFLECTOR}").grid(row=3, column=0, columnspan=6, sticky='w', pady=(5,0))
        # Plugboard visual
        tk.Label(frame, text="Plugboard:").grid(row=4, column=0, sticky='ne', pady=(10,0))
        self.plugboard_frame = tk.Frame(frame)
        self.plugboard_frame.grid(row=4, column=1, columnspan=5, sticky='w', padx=5, pady=(10,0))
        self.letter_buttons = {}
        self.selected_letter = None
        self.plug_pairs = []
        self.pair_label = tk.Label(frame, text="Pairs: []")
        self.pair_label.grid(row=5, column=0, columnspan=6, sticky='w', padx=5, pady=(0,10))
        self.plug_colors = [
            '#FFB347', '#77DD77', '#AEC6CF', '#FF6961', '#CBAACB',
            '#FFD700', '#779ECB', '#B39EB5', '#FFB7CE', '#03C03C'
        ]
        self.pair_color_map = {}
        self.create_plugboard_buttons()
        # Buttons
        self.encrypt_btn = tk.Button(frame, text="Encrypt/Decrypt", command=self.encrypt, width=16)
        self.encrypt_btn.grid(row=6, column=1, pady=10, padx=5, sticky='e')
        self.reset_btn = tk.Button(frame, text="Reset", command=self.reset, width=10)
        self.reset_btn.grid(row=6, column=2, pady=10, padx=5, sticky='w')
        # --- History Log ---
        self.log_frame = tk.Frame(self.root, bd=2, relief='groove')
        self.log_frame.pack(side='right', fill='both', expand=True, padx=(10, 5), pady=5)
        tk.Label(self.log_frame, text="History Log").pack(anchor='w', padx=5, pady=(5,0))
        self.log_listbox = tk.Listbox(self.log_frame, width=70, height=35)
        self.log_listbox.pack(side='left', fill='both', expand=True, padx=(5,0), pady=5)
        self.log_scrollbar = tk.Scrollbar(self.log_frame, orient='vertical', command=self.log_listbox.yview)
        self.log_scrollbar.pack(side='right', fill='y', pady=5)
        self.log_listbox.config(yscrollcommand=self.log_scrollbar.set)
        self.restore_btn = tk.Button(self.log_frame, text="Restore Settings from Log", command=self.restore_settings_from_log)
        self.restore_btn.pack(anchor='w', padx=5, pady=(5,10))

    def create_plugboard_buttons(self):
        for i, letter in enumerate(string.ascii_uppercase):
            btn = tk.Button(self.plugboard_frame, text=letter, width=3, command=lambda l=letter: self.handle_plugboard_click(l))
            btn.grid(row=i//13, column=i%13, padx=2, pady=2)
            self.letter_buttons[letter] = btn

    def handle_plugboard_click(self, letter):
        for idx, pair in enumerate(self.plug_pairs):
            if letter in pair:
                self.plug_pairs.remove(pair)
                color = self.pair_color_map.pop(pair, None)
                for l in pair:
                    self.letter_buttons[l].config(bg='SystemButtonFace')
                self.update_pair_label()
                self.selected_letter = None
                return
        if not self.selected_letter:
            self.selected_letter = letter
            self.letter_buttons[letter].config(bg='yellow')
        else:
            if self.selected_letter == letter:
                self.letter_buttons[letter].config(bg='SystemButtonFace')
                self.selected_letter = None
                return
            for pair in self.plug_pairs:
                if self.selected_letter in pair or letter in pair:
                    self.letter_buttons[self.selected_letter].config(bg='SystemButtonFace')
                    self.selected_letter = None
                    return
            if len(self.plug_pairs) >= 10:
                messagebox.showwarning("Plugboard Limit", "Maximum of 10 plugboard pairs allowed.")
                self.letter_buttons[self.selected_letter].config(bg='SystemButtonFace')
                self.selected_letter = None
                return
            pair = (self.selected_letter, letter)
            self.plug_pairs.append(pair)
            color = self.plug_colors[len(self.plug_pairs)-1 % len(self.plug_colors)]
            self.pair_color_map[pair] = color
            self.letter_buttons[self.selected_letter].config(bg=color)
            self.letter_buttons[letter].config(bg=color)
            self.update_pair_label()
            self.selected_letter = None

    def update_pair_label(self):
        self.pair_label.config(text=f"Pairs: {self.plug_pairs}")

    def get_rotors(self):
        rotors = []
        for i in range(3):
            wiring = ROTORS[self.rotor_vars[i].get()]
            pos = self.position_vars[i].get().strip().upper()
            rotors.append(Rotor(wiring, notch=None, position=pos))
        return rotors

    def get_plugboard(self):
        return Plugboard(self.plug_pairs)

    def encrypt(self):
        rotors = self.get_rotors()
        if rotors is None:
            return
        plugboard = self.get_plugboard()
        if plugboard is None:
            return
        reflector = Reflector(REFLECTOR)
        machine = Enigma_machine(rotors, reflector, plugboard)
        text = self.text_entry.get()
        result = ''
        for c in text:
            if c.upper() in string.ascii_uppercase:
                result += machine.encrypt_char(c.upper())
        self.text_entry.delete(0, tk.END)
        self.text_entry.insert(0, result)
        # Log
        timestamp = datetime.datetime.now().strftime('%H:%M:%S')
        pos_settings = [self.position_vars[i].get().strip().upper() for i in range(3)]
        rotor_settings = [self.rotor_vars[i].get() for i in range(3)]
        plugboard_settings = list(self.plug_pairs)
        reflector_setting = REFLECTOR
        log_entry = (
            f"[{timestamp}] PT/CT: {text}  OUT: {result}\n"
            f"  POS: {pos_settings}  R: {rotor_settings}\n"
            f"  Plugboard: {plugboard_settings}\n"
            f"  Reflector: {reflector_setting}"
        )
        self.log_listbox.insert(tk.END, log_entry)
        self.log_listbox.yview_moveto(1)

    def reset(self):
        self.text_entry.delete(0, tk.END)
        for i in range(3):
            first_letter = ROTORS[self.rotor_vars[i].get()][0]
            self.position_vars[i].set(first_letter)
            self.rotor_vars[i].set(list(ROTORS.keys())[i])
        self.plug_pairs = []
        self.selected_letter = None
        self.pair_color_map = {}
        for btn in self.letter_buttons.values():
            btn.config(bg='SystemButtonFace')
        self.update_pair_label()

    def restore_settings_from_log(self):
        selection = self.log_listbox.curselection()
        if not selection:
            messagebox.showinfo("Restore Settings", "Please select a log entry to restore settings.")
            return
        entry = self.log_listbox.get(selection[0])
        pos_match = re.search(r"POS: (\[.*?\])", entry)
        r_match = re.search(r"R: (\[.*?\])", entry)
        plug_match = re.search(r"Plugboard: (\[.*?\])", entry)
        refl_match = re.search(r"Reflector: ([A-Z]+)", entry)
        if not (pos_match and r_match and plug_match and refl_match):
            messagebox.showerror("Restore Settings", "Could not parse settings from the selected log entry.")
            return
        pos_list = ast.literal_eval(pos_match.group(1))
        r_list = ast.literal_eval(r_match.group(1))
        plug_list = ast.literal_eval(plug_match.group(1))
        reflector = refl_match.group(1)
        for i in range(3):
            self.rotor_vars[i].set(r_list[i])
            self.position_vars[i].set(pos_list[i])
        self.plug_pairs = plug_list
        self.pair_color_map = {}
        for btn in self.letter_buttons.values():
            btn.config(bg='SystemButtonFace')
        for idx, pair in enumerate(self.plug_pairs):
            color = self.plug_colors[idx % len(self.plug_colors)]
            self.pair_color_map[pair] = color
            for l in pair:
                self.letter_buttons[l].config(bg=color)
        self.update_pair_label()

if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleEnigmaGUI(root)
    root.mainloop() 