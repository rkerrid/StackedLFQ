import tkinter as tk
from tkinter import filedialog, messagebox
import json
import os
import copy
import pandas as pd
from stackedLFQ.gui.page_one import PageOne
from stackedLFQ.gui.page_two import PageTwo

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("stacked LFQ")
        self.geometry("800x700")
  
        try:
            from PIL import Image, ImageTk
            import os
            
            # Get the directory where the current script is located
            current_dir = os.path.dirname(os.path.abspath(__file__))
            
            # Construct the path to the image relative to the current script
            icon_path = os.path.join(current_dir, "assets", "Boo3.jpg")
            
            # Open the image
            pil_img = Image.open(icon_path)
            
            # Create a temporary ICO file with multiple sizes
            temp_ico = os.path.join(current_dir, "assets", "temp_icon.ico")
            
            # Save with multiple sizes for better quality
            pil_img.save(temp_ico, format="ICO", sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128)])
            
            # Set as window icon
            self.wm_iconbitmap(temp_ico)
            
        except Exception as e:
            print(f"Could not load icon: {e}")

                
        
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
            "start_precursor_per_protein": 1,
            "pulse_precursor_per_protein": 1,
            "precursor_ratios_per_protein": 1,
            "directLFQ_ions_per_protein": 1,
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
        self.meta_data = pd.DataFrame(columns=['Run', 'Sample'])
        
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
            try:
                # Import your main processing module
                from stackedLFQ.pipeline import Pipeline as pipeline
                
                path = self.config_data["folder_path"]
                pipeline = pipeline(path = path,  metadata_file='meta.csv')
               
                pipeline.execute_pipeline()
                
                messagebox.showinfo("Success", "Analysis completed successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred during analysis: {str(e)}")
        else:
            if self.current_page < (len(self.pages) - 1):
                self.show_frame(self.current_page + 1)
            
    def previous_page(self):
        if self.current_page > 0:
            self.show_frame(self.current_page - 1)
            
    # def save_config(self):
    #     if self.config_data["folder_path"]:
    #         config_file = os.path.join(self.config_data["folder_path"], "params.json")
    #         if os.path.exists(config_file):
    #             overwrite = messagebox.askyesno("File Exists", f"The file '{config_file}' already exists. Do you want to overwrite it?")
    #             if not overwrite:
    #                 return
                
    #         # Save config file
    #         with open(config_file, "w") as f:
    #             json.dump(self.config_data, f, indent=4)
                
    #         # Save metadata
    #         self.save_metadata()
            
    #         messagebox.showinfo("Success", f"Config file saved to {config_file}")
    #     else:
    #         messagebox.showwarning("Warning", "Your TSV file is not located in an accessible folder!")
    
    def save_config(self):
        if self.config_data["folder_path"]:
            # Create a copy of config_data to modify
            config_to_save = copy.deepcopy(self.config_data)
            
            # List of keys that should be integers
            int_keys = [
                "start_precursor_per_protein",
                "pulse_precursor_per_protein", 
                "precursor_ratios_per_protein",
                "directLFQ_ions_per_protein",
                "No_of_cores_dlfq"
            ]
            
            # Convert float values to integers
            for key in int_keys:
                if key in config_to_save:
                    config_to_save[key] = int(float(config_to_save[key]))
            
            # Save the modified config
            config_file = os.path.join(self.config_data["folder_path"], "params.json")
            if os.path.exists(config_file):
                overwrite = messagebox.askyesno("File Exists", 
                    f"The file '{config_file}' already exists. Do you want to overwrite it?")
                if not overwrite:
                    return
                    
            with open(config_file, "w") as f:
                json.dump(config_to_save, f, indent=4)
                
            messagebox.showinfo("Success", f"Config file saved to {config_file}")
        else:
            messagebox.showwarning("Warning", "Your TSV file is not located in an accessible folder!")

    def save_metadata(self):
        if self.config_data["folder_path"]:
            # Save to CSV
            metadata_file = os.path.join(self.config_data["folder_path"], "meta.csv")
            if os.path.exists(metadata_file):
                overwrite = messagebox.askyesno("File Exists", 
                    f"The file '{metadata_file}' already exists. Do you want to overwrite it?")
                if not overwrite:
                    return
                    
            # Save the metadata DataFrame directly
            self.meta_data.to_csv(metadata_file, index=False)
            messagebox.showinfo("Success", f"Metadata saved to {metadata_file}")
        else:
            messagebox.showwarning("Warning", "Please select a valid folder first!")
            
            
if __name__ == "__main__":
    app = App()
    app.mainloop()