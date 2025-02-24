import tkinter as tk
from tkinter import filedialog, messagebox
import json
import os
from page_one import PageOne
from page_two import PageTwo

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("stacked LFQ")
        self.geometry("800x700")
        
        # Root Grid Layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0, minsize=33)
        self.grid_columnconfigure(0, weight=1)
        
        # Config Data
        self.config_data = {
            "file_path": "",
            "folder_path": "",
            "unique_runs": [],
            "removing_pattern_start": "",
            "removing_pattern_end": "",
            "contaminant_pattern": "",
            "mass_spec": "Astral",
            "diann_version": "1.8.1",
            "silac_starting_channel": "L",
            "silac_pulse_channel": "H",
            "start_precursor_per_protein": 2,
            "pulse_precursor_per_protein": 2,
            "precursor_ratios_per_protein": 2,
            "directLFQ_ions_per_protein": 3,
            "No_of_cores_dlfq": 8,
            "filters": {
                "Global.PG.Q.Value": {
                    "op": "<",
                    "value": 0.01
                },
                "Precursor.Charge": {
                    "op": ">",
                    "value": 1
                },
                "Channel.Q.Value": {
                    "op": "<",
                    "value": 0.03
                }
            }
        }
        
        # Frames
        self.container = tk.Frame(self)
        self.button_frame = tk.Frame(self, bg="lightblue")
        
        self.container.grid(row=0, column=0, sticky="nsew")
        self.button_frame.grid(row=1, column=0, sticky="nsew")
        
        # Container Grid Layout
        self.container.grid_columnconfigure(0, weight=1)
        self.container.grid_rowconfigure(0, weight=1)
        
        # Pages
        self.page_classes = (PageOne, PageTwo, )
        self.pages = []
        self.current_page = 0
        
        for page_class in self.page_classes:
            self.pages.append(page_class(self))
            
        self.pages[self.current_page].grid(row=0, column=0)
        
        # Next and Back Buttons
        button_font = ("Arial", 10, "bold")
        self.next_button = tk.Button(self.button_frame, text="Next", command=self.next_page, font=button_font, width=6)
        self.back_button = tk.Button(self.button_frame, text="Back", command=self.previous_page, font=button_font, width=6)
        
        self.next_button.pack(side="right", padx=20, pady=5)
        self.back_button.pack(side="left", padx=20, pady=5)
        
        self.show_frame(self.current_page)
        self.update_buttons()
        
    # Methods

    def show_frame(self, page):
        self.pages[self.current_page].grid_forget()  
        self.pages[page].grid(row=0, column=0, sticky="nsew")
        self.current_page = page
        self.update_buttons()
    
    def update_buttons(self):
        if self.current_page == 0:
            self.back_button.pack_forget()
        else:
            if not self.back_button.winfo_ismapped():
                self.back_button.pack(side="left", padx=20)

        if self.current_page == (len(self.pages) - 1):
            self.next_button.config(text="Run")
        else:
            self.next_button.config(text="Next")
            
    def next_page(self):
        if self.current_page == 0 and not self.config_data["file_path"]:
            messagebox.showwarning("Warning", "Please select a file before proceeding!")
            return
        
        if self.current_page == (len(self.pages) - 1):
            self.save_config()
        else:
            if self.current_page < (len(self.pages) - 1):
                self.show_frame(self.current_page + 1)
            
    def previous_page(self):
        if self.current_page > 0:
            self.show_frame(self.current_page - 1)
            
    def save_config(self):
        if self.config_data["folder_path"]:
            config_file = os.path.join(self.config_data["folder_path"], "params.json")
            if os.path.exists(config_file):
                overwrite = messagebox.askyesno("File Exists", f"The file '{config_file}' already exists. Do you want to overwrite it?")
                if not overwrite:
                    return
                
            with open(config_file, "w") as f:
                json.dump(self.config_data, f, indent=4)
            messagebox.showinfo("Success", f"Config file saved to {config_file}")
        else:
            messagebox.showwarning("Warning", "Your TSV file is not located in an accessable folder!")
            
            
if __name__ == "__main__":
    app = App()
    app.mainloop()