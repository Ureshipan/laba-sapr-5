import sys, os, subprocess
from traceback import format_exc
import tkinter as tk
from tkinter import ttk, messagebox

class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Temperature Mixing Calculator")
        self.root.geometry("400x450")  # Увеличиваем высоту окна
        
        # Initialize parameters
        self.params = {
            "hot": 305,
            "cold": 295,
            "square": 100,
            "end_time": 500,
            "write_interval": 50,
            "purge_write": 100  # Добавляем параметр для хранения количества кадров
        }
        
        # Create main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create parameter inputs
        self.create_parameter_inputs(main_frame)
        
        # Create control buttons
        self.create_control_buttons(main_frame)
        
        # Status label
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var)
        self.status_label.grid(row=7, column=0, columnspan=2, pady=10)
        
    def create_parameter_inputs(self, parent):
        # Hot temperature input
        ttk.Label(parent, text="Hot Temperature (K):").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.hot_var = tk.IntVar(value=self.params["hot"])
        self.hot_input = ttk.Spinbox(parent, from_=273, to=500, textvariable=self.hot_var)
        self.hot_input.grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # Cold temperature input
        ttk.Label(parent, text="Cold Temperature (K):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.cold_var = tk.IntVar(value=self.params["cold"])
        self.cold_input = ttk.Spinbox(parent, from_=273, to=500, textvariable=self.cold_var)
        self.cold_input.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # Square size input
        ttk.Label(parent, text="Square Size (mm):").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.square_var = tk.IntVar(value=self.params["square"])
        self.square_input = ttk.Spinbox(parent, from_=10, to=1000, textvariable=self.square_var)
        self.square_input.grid(row=2, column=1, sticky=tk.W, pady=5)

        # End time input
        ttk.Label(parent, text="End Time (s):").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.end_time_var = tk.IntVar(value=self.params["end_time"])
        self.end_time_input = ttk.Spinbox(parent, from_=100, to=1000, textvariable=self.end_time_var)
        self.end_time_input.grid(row=3, column=1, sticky=tk.W, pady=5)

        # Write interval input
        ttk.Label(parent, text="Write Interval (s):").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.write_interval_var = tk.IntVar(value=self.params["write_interval"])
        self.write_interval_input = ttk.Spinbox(parent, from_=1, to=100, textvariable=self.write_interval_var)
        self.write_interval_input.grid(row=4, column=1, sticky=tk.W, pady=5)

        # Purge write input
        ttk.Label(parent, text="Max Frames to Keep:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.purge_write_var = tk.IntVar(value=self.params["purge_write"])
        self.purge_write_input = ttk.Spinbox(parent, from_=1, to=1000, textvariable=self.purge_write_var)
        self.purge_write_input.grid(row=5, column=1, sticky=tk.W, pady=5)
        
    def create_control_buttons(self, parent):
        # Buttons frame
        buttons_frame = ttk.Frame(parent)
        buttons_frame.grid(row=6, column=0, columnspan=2, pady=10)
        
        # Clean button
        clean_btn = ttk.Button(buttons_frame, text="Clean", command=self.clean)
        clean_btn.pack(side=tk.LEFT, padx=5)
        
        # Write button
        write_btn = ttk.Button(buttons_frame, text="Write Files", command=self.write_files)
        write_btn.pack(side=tk.LEFT, padx=5)
        
        # Run button
        run_btn = ttk.Button(buttons_frame, text="Run Solution", command=self.run_solution)
        run_btn.pack(side=tk.LEFT, padx=5)
    
    def update_params(self):
        self.params["hot"] = self.hot_var.get()
        self.params["cold"] = self.cold_var.get()
        self.params["square"] = self.square_var.get()
        self.params["end_time"] = self.end_time_var.get()
        self.params["write_interval"] = self.write_interval_var.get()
        self.params["purge_write"] = self.purge_write_var.get()
    
    def clean(self):
        try:
            subprocess.Popen("buoyantCavity/Clean.sh".split())
            self.status_var.set("Cleaned successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to clean: {str(e)}")
    
    def write_files(self):
        try:
            self.update_params()
            if write_files(self.params):
                self.status_var.set("Files written successfully")
            else:
                messagebox.showwarning("Warning", "Failed to write files")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to write files: {str(e)}")
    
    def run_solution(self):
        try:
            run_solution()
            self.status_var.set("Solution completed")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to run solution: {str(e)}")

def write_files(params):
    base_dir = "buoyantCavity"
    
    try:
        # 1. Изменяем файл 0/T
        t_file = base_dir + "/0/T"
        if os.path.exists("base_files/" + t_file):
            with open("base_files/" + t_file, 'r') as f:
                lines = f.readlines()
            
            for i in range(len(lines)):
                lines[i] = lines[i].replace('{{hot}}', str(params['hot']))
                lines[i] = lines[i].replace('{{cold}}', str(params['cold']))
                lines[i] = lines[i].replace('{{uniform}}', str(round((params['hot'] + params['cold']) / 2)))
            
            with open(t_file, 'w') as f:
                f.writelines(lines)
        else:
            print(f"Файл {t_file} не найден!")
            return False

        # 2. Изменяем system/blockMeshDict
        block_mesh_file = base_dir + "/system/blockMeshDict"
        if os.path.exists(block_mesh_file):
            with open(block_mesh_file, 'r') as f:
                lines = f.readlines()
            
            if len(lines) > 16:  
                lines[16] = f"b {params['square']};\n"
            
            with open(block_mesh_file, 'w') as f:
                f.writelines(lines)
        else:
            print(f"Файл {block_mesh_file} не найден!")
            return False

        # 3. Изменяем system/controlDict
        control_dict_file = base_dir + "/system/controlDict"
        if os.path.exists(control_dict_file):
            with open(control_dict_file, 'r') as f:
                lines = f.readlines()
            
            for i in range(len(lines)):
                if "endTime" in lines[i]:
                    lines[i] = f"endTime         {params['end_time']};\n"
                elif "writeInterval" in lines[i]:
                    lines[i] = f"writeInterval   {params['write_interval']};\n"
                elif "purgeWrite" in lines[i]:
                    lines[i] = f"purgeWrite      {params['purge_write']};\n"
            
            with open(control_dict_file, 'w') as f:
                f.writelines(lines)
        else:
            print(f"Файл {control_dict_file} не найден!")
            return False

        return True

    except Exception as e:
        print(f"Ошибка: {e}")
        return False
    
def run_solution():
    work_dir = os.curdir + "/buoyantCavity"
    commands = [
        "blockMesh",
        "foamRun > log",
        "paraFoam"
    ]
    
    for cmd in commands:
        process = subprocess.Popen(
            cmd,
            cwd=work_dir,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        stdout, stderr = process.communicate()
        
        print(f"Command: {cmd}")
        print("STDOUT:", stdout)
        print("STDERR:", stderr)
        
        if process.returncode != 0:
            print(f"Error in command '{cmd}': Exit code {process.returncode}")
            break

if __name__ == '__main__':
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()