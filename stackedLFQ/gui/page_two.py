import tkinter as tk

class PageTwo(tk.Frame):
    def __init__(self, controller):
        super().__init__(controller.container)  
        self.controller = controller
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Data Filters
        tk.Label(self, text="Data Filters", bg="lightblue").grid(row=0, column=0, columnspan=2, pady=20)
        
        tk.Label(self, text="Global.PG.Q.Value <:").grid(row=1, column=0, padx=10, pady=5)
        tk.Label(self, text="Channel.Q.Value <:").grid(row=2, column=0, padx=10, pady=5)
        tk.Label(self, text="Precursor.Charge >:").grid(row=3, column=0, padx=10, pady=5)
        
        self.global_pg_q_value_var = tk.StringVar(value=0.01)
        self.global_pg_q_value_var.trace_add("write", self.update_config)
        self.channel_q_value_var= tk.StringVar(value=0.03)
        self.channel_q_value_var.trace_add("write", self.update_config)
        self.precursor_charge_var = tk.StringVar(value=1)
        self.precursor_charge_var.trace_add("write", self.update_config)
        
        self.global_pg_q_value_entry = tk.Entry(self, textvariable=self.global_pg_q_value_var, validate="key", validatecommand=(self.register(self.validate_decimal), "%P"))
        self.channel_q_value_entry = tk.Entry(self, textvariable=self.channel_q_value_var, validate="key", validatecommand=(self.register(self.validate_decimal), "%P"))
        self.precursor_charge_entry = tk.Entry(self, textvariable=self.precursor_charge_var, validate="key", validatecommand=(self.register(self.validate_decimal), "%P"))
        
        self.global_pg_q_value_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        self.channel_q_value_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        self.precursor_charge_entry.grid(row=3, column=1, padx=5, pady=5, sticky="w")
        
        
        
        # stackedLFQ Settings
        tk.Label(self, text="stackedLFQ Settings", bg="lightblue").grid(row=4, column=0, columnspan=2, pady=20)
        
        tk.Label(self, text="Precursor per ProteinGroup Starting Channel:").grid(row=5, column=0, padx=10, pady=5)
        tk.Label(self, text="Precursors per ProteinGroup Pulse Channel:").grid(row=6, column=0, padx=10, pady=5)
        tk.Label(self, text="Number of Precursor Ratios per ProteinGroup:").grid(row=7, column=0, padx=10, pady=5)
        
        self.precursor_starting_channel_var = tk.StringVar(value=2)
        self.precursor_starting_channel_var.trace_add("write", self.update_config)
        self.precursor_pulse_channel_var = tk.StringVar(value=2)
        self.precursor_pulse_channel_var.trace_add("write", self.update_config)
        self.precursor_ratios_var = tk.StringVar(value=2)
        self.precursor_ratios_var.trace_add("write", self.update_config)
        
        self.precursor_starting_channel_entry = tk.Entry(self, textvariable=self.precursor_starting_channel_var, validate="key", validatecommand=(self.register(self.validate_decimal), "%P"))
        self.precursor_pulse_channel_entry = tk.Entry(self, textvariable=self.precursor_pulse_channel_var, validate="key", validatecommand=(self.register(self.validate_decimal), "%P"))
        self.precursor_ratios_entry = tk.Entry(self, textvariable=self.precursor_ratios_var, validate="key", validatecommand=(self.register(self.validate_decimal), "%P"))
        
        self.precursor_starting_channel_entry.grid(row=5, column=1, padx=5, pady=5, sticky="w")
        self.precursor_pulse_channel_entry.grid(row=6, column=1, padx=5, pady=5, sticky="w")
        self.precursor_ratios_entry.grid(row=7, column=1, padx=5, pady=5, sticky="w")
        
        
        
        # directLFQ Settings
        tk.Label(self, text="directLFQ Settings", bg="lightblue").grid(row=8, column=0, columnspan=2, pady=20)
        
        tk.Label(self, text="directLFQ Ions per Protein:").grid(row=9, column=0, padx=10, pady=5)
        tk.Label(self, text="directLFQ Number Cores:").grid(row=10, column=0, padx=10, pady=5)
        
        self.dlfq_ions_var = tk.StringVar(value=3)
        self.dlfq_ions_var.trace_add("write", self.update_config)
        self.dlfq_num_cores_var = tk.StringVar(value=8)
        self.dlfq_num_cores_var.trace_add("write", self.update_config)
        
        self.dlfq_ions_entry = tk.Entry(self, textvariable=self.dlfq_ions_var, validate="key", validatecommand=(self.register(self.validate_decimal), "%P"))
        self.dlfq_num_cores_entry = tk.Entry(self, textvariable=self.dlfq_num_cores_var, validate="key", validatecommand=(self.register(self.validate_decimal), "%P"))
        
        self.dlfq_ions_entry.grid(row=9, column=1, padx=5, pady=5, sticky="w")
        self.dlfq_num_cores_entry.grid(row=10, column=1, padx=5, pady=5, sticky="w")
        
        
        
        
        
        
    def validate_decimal(self, value):
        """Allow only numbers and at most one decimal point."""
        return value == "" or value.replace(".", "", 1).isdigit()    
    
    # def update_config(self, *args):
    #     try:
    #         self.controller.config_data["filters"]["Global.PG.Q.Value"] = float(self.global_pg_q_value_var.get().strip())
    #         self.controller.config_data["filters"]["Channel.Q.Value"] = float(self.channel_q_value_var.get().strip())
    #         self.controller.config_data["filters"]["Precursor.Charge"] = float(self.precursor_charge_var.get().strip())
    #         self.controller.config_data["start_precursor_per_protein"] = float(self.precursor_starting_channel_var.get().strip())
    #         self.controller.config_data["pulse_precursor_per_protein"] = float(self.precursor_pulse_channel_var.get().strip())
    #         self.controller.config_data["precursor_ratios_per_protein"] = float(self.precursor_ratios_var.get().strip())
    #         self.controller.config_data["directLFQ_ions_per_protein"] = float(self.dlfq_ions_var.get().strip())
    #         self.controller.config_data["No_of_cores_dlfq"] = float(self.dlfq_num_cores_var.get().strip())
    #     except ValueError:
    #         pass
    def update_config(self, *args):
        try:
            # Save float values for these parameters
            self.controller.config_data["filters"]["Global.PG.Q.Value"] = float(self.global_pg_q_value_var.get().strip())
            self.controller.config_data["filters"]["Channel.Q.Value"] = float(self.channel_q_value_var.get().strip())
            self.controller.config_data["filters"]["Precursor.Charge"] = int(self.precursor_charge_var.get().strip())
            
            # Save integer values for these parameters
            self.controller.config_data["start_precursor_per_protein"] = int(float(self.precursor_starting_channel_var.get().strip()))
            self.controller.config_data["pulse_precursor_per_protein"] = int(float(self.precursor_pulse_channel_var.get().strip()))
            self.controller.config_data["precursor_ratios_per_protein"] = int(float(self.precursor_ratios_var.get().strip()))
            self.controller.config_data["directLFQ_ions_per_protein"] = int(float(self.dlfq_ions_var.get().strip()))
            self.controller.config_data["No_of_cores_dlfq"] = int(float(self.dlfq_num_cores_var.get().strip()))
        except ValueError:
            pass
        #print(self.controller.config_data) # FOR DEBUGGING - CAN BE REMOVED
        