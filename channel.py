import sys, os, subprocess
from traceback import format_exc
import tkinter as tk
from tkinter import ttk, messagebox

class ChannelWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Blocked Channel Flow Calculator")
        self.root.geometry("400x450")
        
        # Initialize parameters
        self.params = {
            "inlet_velocity": 10,  # Скорость на входе в м/с
            "end_time": 500,       # Конечное время расчета
            "write_interval": 50,  # Интервал записи кадров
            "purge_write": 100     # Максимальное количество сохраняемых кадров
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
        self.status_label.grid(row=5, column=0, columnspan=2, pady=10)
        
    def create_parameter_inputs(self, parent):
        # Inlet velocity input
        ttk.Label(parent, text="Inlet Velocity (m/s):").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.velocity_var = tk.DoubleVar(value=self.params["inlet_velocity"])
        self.velocity_input = ttk.Spinbox(parent, from_=0.1, to=100.0, increment=0.1, 
                                        textvariable=self.velocity_var)
        self.velocity_input.grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # End time input
        ttk.Label(parent, text="End Time (s):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.end_time_var = tk.IntVar(value=self.params["end_time"])
        self.end_time_input = ttk.Spinbox(parent, from_=100, to=1000, 
                                        textvariable=self.end_time_var)
        self.end_time_input.grid(row=1, column=1, sticky=tk.W, pady=5)

        # Write interval input
        ttk.Label(parent, text="Write Interval (s):").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.write_interval_var = tk.IntVar(value=self.params["write_interval"])
        self.write_interval_input = ttk.Spinbox(parent, from_=1, to=100, 
                                              textvariable=self.write_interval_var)
        self.write_interval_input.grid(row=2, column=1, sticky=tk.W, pady=5)

        # Purge write input
        ttk.Label(parent, text="Max Frames to Keep:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.purge_write_var = tk.IntVar(value=self.params["purge_write"])
        self.purge_write_input = ttk.Spinbox(parent, from_=1, to=1000, 
                                           textvariable=self.purge_write_var)
        self.purge_write_input.grid(row=3, column=1, sticky=tk.W, pady=5)
        
    def create_control_buttons(self, parent):
        # Buttons frame
        buttons_frame = ttk.Frame(parent)
        buttons_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
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
        self.params["inlet_velocity"] = self.velocity_var.get()
        self.params["end_time"] = self.end_time_var.get()
        self.params["write_interval"] = self.write_interval_var.get()
        self.params["purge_write"] = self.purge_write_var.get()
    
    def clean(self):
        try:
            subprocess.Popen("blockedChannel/Clean.sh".split())
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
    base_dir = "blockedChannel"
    
    try:
        # 1. Изменяем файл 0/U
        u_file = base_dir + "/0/U"
        if os.path.exists(u_file):
            with open(u_file, 'r') as f:
                lines = f.readlines()
            
            # Создаем новое значение скорости
            velocity_value = f"({params['inlet_velocity']} 0 0)"
            
            # Обновляем internalField
            for i in range(len(lines)):
                if "internalField" in lines[i]:
                    lines[i] = f"internalField   uniform {velocity_value};\n"
                # Обновляем значение для inlet
                elif "inlet" in lines[i] and "{" in lines[i+1]:
                    # Ищем строку с value
                    for j in range(i, len(lines)):
                        if "value" in lines[j]:
                            lines[j] = f"        value           uniform {velocity_value};\n"
                            break
            
            with open(u_file, 'w') as f:
                f.writelines(lines)
        else:
            print(f"Файл {u_file} не найден!")
            return False

        # 2. Создаем файл constant/alpha.volume
        alpha_file = base_dir + "/constant/alpha.volume"
        alpha_content = """/*--------------------------------*- C++ -*----------------------------------*\\
  =========                 |
  \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\\\    /   O peration     | Website:  https://openfoam.org
    \\\\  /    A nd           | Version:  12
     \\\\/     M anipulation  |
\\*---------------------------------------------------------------------------*/
FoamFile
{
    format      ascii;
    class       volScalarField;
    location    "constant";
    object      alpha.volume;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [0 0 0 0 0 0 0];

internalField   uniform 1;

boundaryField
{
    inlet
    {
        type            fixedValue;
        value           $internalField;
    }
    outlet
    {
        type            zeroGradient;
    }
    walls
    {
        type            zeroGradient;
    }
    frontAndBack
    {
        type            empty;
    }
}

// ************************************************************************* //
"""
        # Создаем директорию constant, если её нет
        os.makedirs(os.path.dirname(alpha_file), exist_ok=True)
        
        # Записываем файл
        with open(alpha_file, 'w') as f:
            f.write(alpha_content)

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
    work_dir = os.curdir + "/blockedChannel"
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
    app = ChannelWindow(root)
    root.mainloop() 