import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import os
import dask.dataframe as dd
import time

class PageOne(tk.Frame):
    def __init__(self, controller):
        super().__init__(controller.container)  
        self.controller = controller
        
        self.grid_columnconfigure(1, weight=1)
        
        # Browse TSV File
        tk.Label(self, text="Select TSV File:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.entry = tk.Entry(self, width=50)
        self.entry.grid(row=0, column=1, columnspan=2, pady=5, sticky="ew")
        tk.Button(self, text="Browse", command=self.browse_file).grid(row=0, column=3, padx=5, pady=5)
        
        # Text Widget
        text_widget_frame = tk.Frame(self)
        text_widget_frame.grid(row=1, column=0, columnspan=3, padx=10, pady=5, sticky="nsew")
        text_widget_frame.grid_columnconfigure(0, weight=1)
        text_widget_frame.grid_rowconfigure(0, weight=1)
        
        self.text_widget = tk.Text(text_widget_frame, wrap="none", height=15, width=80)
        self.text_widget.grid(row=0, column=0, sticky="nsew")
        
        scrollbar = tk.Scrollbar(text_widget_frame, orient="vertical", command=self.text_widget.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.text_widget.config(yscrollcommand=scrollbar.set)
        self.text_widget.bind("<Control-c>", self.copy_selected_text)
        self.context_menu = tk.Menu(text_widget_frame, tearoff=0)
        self.context_menu.add_command(label="Copy", command=self.copy_selected_text)
        self.text_widget.bind("<Button-3>", self.show_context_menu)
        self.text_widget.bind("<Button-2>", self.show_context_menu)
        
        # Text Label Count Unique Runs
        self.label_unique_runs = tk.Label(self, text="Please Load Your File")
        self.label_unique_runs.grid(row=11, column=1)
        
        # Pattern Input Files
        remove_pattern_start_label = tk.Label(self, text="Pattern to Remove (Start):").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        remove_pattern_end_label = tk.Label(self, text="Pattern to Remove (End):").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        contaminant_pattern_label = tk.Label(self, text="Contaminant Pattern:").grid(row=4, column=0, padx=10, pady=5, sticky="w")

        self.remove_pattern_start_var = tk.StringVar()
        self.remove_pattern_end_var = tk.StringVar(value=".raw")
        self.contaminant_pattern_var = tk.StringVar(value="^Cont_")
        self.remove_pattern_start_var.trace_add("write", self.update_config)
        self.remove_pattern_end_var.trace_add("write", self.update_config)
        self.contaminant_pattern_var.trace_add("write", self.update_config)
        
        self.remove_pattern_start_entry = tk.Entry(self, width=40, textvariable=self.remove_pattern_start_var)
        self.remove_pattern_end_entry = tk.Entry(self, width=40, textvariable=self.remove_pattern_end_var)
        self.contaminant_pattern_entry = tk.Entry(self, width=40, textvariable=self.contaminant_pattern_var)
        self.remove_pattern_start_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        self.remove_pattern_end_entry.grid(row=3, column=1, padx=5, pady=5, sticky="ew")
        self.contaminant_pattern_entry.grid(row=4, column=1, padx=5, pady=5, sticky="ew")
        
        # Dropdown for MassSpec
        tk.Label(self, text="MassSpec:").grid(row=5, column=0, padx=10, pady=5, sticky="w")
        self.massspec_var = tk.StringVar(value="Astral")
        self.massspec_var.trace_add("write", self.update_pattern_end)
        massspec_dropdown = ttk.Combobox(self, textvariable=self.massspec_var, values=["Astral", "Exploris", "Ultra2", "HT"], state="readonly")
        massspec_dropdown.grid(row=5, column=1, padx=5, pady=5, sticky="ew")
        massspec_dropdown.bind("<<ComboboxSelected>>", self.update_selection_label)
        
        # Dropdown for DIANN Version
        tk.Label(self, text="DIANN Version:").grid(row=6, column=0, padx=10, pady=5, sticky="w")
        self.diann_var = tk.StringVar(value="1.8.1")
        diann_dropdown = ttk.Combobox(self, textvariable=self.diann_var, values=["1.8.1", "1.8.2", "2.0"], state="readonly")
        diann_dropdown.grid(row=6, column=1, padx=5, pady=5, sticky="ew")
        diann_dropdown.bind("<<ComboboxSelected>>", self.update_selection_label)
        
        # Dropdown for SILAC Channels
        tk.Label(self, text="SILAC starting Channel:").grid(row=7, column=0, padx=10, pady=5, sticky="w")
        tk.Label(self, text="SILAC pulse Channel:").grid(row=8, column=0, padx=10, pady=5, sticky="w")
        self.silac_starting_channel_var = tk.StringVar(value="L")
        self.silac_pulse_channel_var = tk.StringVar(value="H")
        silac_starting_channel_dropdown = ttk.Combobox(self, textvariable=self.silac_starting_channel_var, values=["L", "M", "H"])
        silac_pulse_channel_dropdown = ttk.Combobox(self, textvariable=self.silac_pulse_channel_var, values=["L", "M", "H"])
        silac_starting_channel_dropdown.grid(row=7, column=1, padx=5, pady=5, sticky="ew")
        silac_starting_channel_dropdown.bind("<<ComboboxSelected>>", self.update_selection_label)
        silac_pulse_channel_dropdown.grid(row=8, column=1, padx=5, pady=5, sticky="ew")
        silac_pulse_channel_dropdown.bind("<<ComboboxSelected>>", self.update_selection_label)
        
        # Selection Label
        self.selection_label = tk.Label(self, text="MassSpec: Astral | Selected DIANN: 1.8.1 | Starting Channel: L | Pulse Channel: H")
        self.selection_label.grid(row=9, column=1, pady=5, sticky="ew")
        
        # Preview Button
        preview_button = tk.Button(self, text="Preview Changes", command=self.preview_changes) 
        preview_button.grid(row=10, column=1, pady=10)
        
        # Output Loacation
        tk.Label(self, text="Output Location:").grid(row=12, column=0, padx=10, pady=5, sticky="w")
        self.output_location_entry = tk.Entry(self, width=50)
        self.output_location_entry.grid(row=12, column=1, columnspan=2, pady=5, sticky="ew")
        tk.Button(self, text="Browse", command=self.browse_folder).grid(row=12, column=3, padx=5, pady=5)
        
    def browse_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("TSV Files", "*.tsv"), ("All Files", "*.*")]
        )
        if file_path:
            folder_path = os.path.dirname(file_path)
            self.entry.delete(0, tk.END)
            self.entry.insert(0, file_path)
            self.output_location_entry.delete(0, tk.END)
            self.output_location_entry.insert(0, folder_path)
            self.controller.config_data["file_path"] = file_path
            self.controller.config_data["folder_path"] = folder_path
            self.load_unique_runs()
            
    def browse_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.output_location_entry.delete(0, tk.END)
            self.output_location_entry.insert(0, folder_path)
            self.controller.config_data["folder_path"] = folder_path
            
    def load_unique_runs(self):
        # if file path ends with .tsv, import tsv
        #elif file path ends with parquet, import parquet
        print('Beginning import of Run file names')
        start_time = time.time()
        
        try:
            # df = pd.read_csv(self.controller.config_data["file_path"], sep="\t", usecols=["Run"])
            #####
            df = dd.read_csv(
            self.controller.config_data["file_path"], 
            sep='\t',
            usecols=['Run'],
            dtype={'Run': 'str'}  # Only specify dtype for the column you're loading
            )
            ####
            runs = sorted(df["Run"].dropna().unique())
            self.controller.meta_data["Run"] = runs
            self.controller.meta_data["Sample"] = runs
            
            self.text_widget.delete("1.0", tk.END)
            for run in self.controller.meta_data["Run"]:
                self.text_widget.insert(tk.END, run + "\n")
    
            self.label_unique_runs.config(text=f"Unique Runs Loaded: [need to add len")
            
            #dont save to json but save to meta.csv
            
            print('Finished import')
            end_time = time.time()
            print(f"Time taken for import: {end_time - start_time} seconds")
            
        except ValueError:
            messagebox.showerror("Error", "Selected file does not contain a 'Run' column.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            
    def copy_selected_text(self, event=None):
        try:
            selected_text = self.text_widget.get(tk.SEL_FIRST, tk.SEL_LAST)  
            self.controller.clipboard_clear()  
            self.controller.clipboard_append(selected_text)  
            self.controller.update()  
        except tk.TclError:
            messagebox.showwarning("Warning", "No text selected to copy!")

    def show_context_menu(self, event):
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()
        
    def update_selection_label(self, event=None):
        selected_massspec = self.massspec_var.get()
        selected_diann = self.diann_var.get()
        selected_silac_starting_channel = self.silac_starting_channel_var.get()
        selected_silac_pulse_channel = self.silac_pulse_channel_var.get()
        self.selection_label.config(text=f"MassSpec: {selected_massspec} | Selected DIANN: {selected_diann} | Starting Channel: {selected_silac_starting_channel} | Pulse Channel: {selected_silac_pulse_channel}")
    
    def preview_changes(self):
        if self.controller.meta_data.empty:
            messagebox.showwarning("Warning", "No Runs loaded!")
            return
        pattern_start = self.remove_pattern_start_entry.get().strip()
        pattern_end = self.remove_pattern_end_entry.get().strip()

        df_runs = self.controller.meta_data
        
        if pattern_start:
            df_runs["Sample"] = df_runs["Sample"].str.replace(pattern_start, "", regex=True)
            
            
        if pattern_end:
            df_runs["Sample"] = df_runs["Sample"].str.replace(pattern_end, "", regex=True)
 
        self.text_widget.delete("1.0", tk.END)
        for run in df_runs["Sample"].values.tolist():
            self.text_widget.insert(tk.END, run + "\n")
        messagebox.showinfo("Preview", "Run names updated in preview! (Not applied yet)")
     
        self.controller.meta_data = df_runs
     
    def update_config(self, *args):
        self.controller.config_data["removing_pattern_start"] = self.remove_pattern_start_var.get().strip()
        self.controller.config_data["removing_pattern_end"] = self.remove_pattern_end_var.get().strip()
        self.controller.config_data["contaminant_pattern"] = self.contaminant_pattern_var.get().strip()
        #print(self.controller.config_data) # FOR DEBUGGING - CAN BE REMOVED
        
    def update_pattern_end(self, *args):
        massspec = self.massspec_var.get()

        pattern_defaults = {
            "Astral": ".raw",
            "Exploris": ".raw",
            "Ultra2": "_._....",
            "HT": "_._...."
        }

        new_pattern = pattern_defaults.get(massspec, "")
        self.remove_pattern_end_var.set(new_pattern)
        self.update_config()
        
        

