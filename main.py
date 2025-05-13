import sys, os, subprocess
from traceback import format_exc
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QSpinBox
from PyQt5.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Temperature Mixing Calculator")
        self.setMinimumSize(400, 300)
        
        # Initialize parameters
        self.params = {
            "hot": 305,
            "cold": 295,
            "square": 100
        }
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create parameter input fields
        self.create_parameter_inputs(layout)
        
        # Create control buttons
        self.create_control_buttons(layout)
        
        # Status label
        self.status_label = QLabel("Ready")
        layout.addWidget(self.status_label)
        
    def create_parameter_inputs(self, layout):
        # Hot temperature input
        hot_layout = QHBoxLayout()
        hot_label = QLabel("Hot Temperature (K):")
        self.hot_input = QSpinBox()
        self.hot_input.setRange(273, 500)
        self.hot_input.setValue(self.params["hot"])
        hot_layout.addWidget(hot_label)
        hot_layout.addWidget(self.hot_input)
        layout.addLayout(hot_layout)
        
        # Cold temperature input
        cold_layout = QHBoxLayout()
        cold_label = QLabel("Cold Temperature (K):")
        self.cold_input = QSpinBox()
        self.cold_input.setRange(273, 500)
        self.cold_input.setValue(self.params["cold"])
        cold_layout.addWidget(cold_label)
        cold_layout.addWidget(self.cold_input)
        layout.addLayout(cold_layout)
        
        # Square size input
        square_layout = QHBoxLayout()
        square_label = QLabel("Square Size (mm):")
        self.square_input = QSpinBox()
        self.square_input.setRange(10, 1000)
        self.square_input.setValue(self.params["square"])
        square_layout.addWidget(square_label)
        square_layout.addWidget(self.square_input)
        layout.addLayout(square_layout)
        
    def create_control_buttons(self, layout):
        # Buttons layout
        buttons_layout = QHBoxLayout()
        
        # Clean button
        clean_btn = QPushButton("Clean")
        clean_btn.clicked.connect(self.clean)
        buttons_layout.addWidget(clean_btn)
        
        # Write button
        write_btn = QPushButton("Write Files")
        write_btn.clicked.connect(self.write_files)
        buttons_layout.addWidget(write_btn)
        
        # Run button
        run_btn = QPushButton("Run Solution")
        run_btn.clicked.connect(self.run_solution)
        buttons_layout.addWidget(run_btn)
        
        layout.addLayout(buttons_layout)
    
    def update_params(self):
        self.params["hot"] = self.hot_input.value()
        self.params["cold"] = self.cold_input.value()
        self.params["square"] = self.square_input.value()
    
    def clean(self):
        try:
            subprocess.Popen("buoyantCavity/Clean.sh".split())
            self.status_label.setText("Cleaned successfully")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to clean: {str(e)}")
    
    def write_files(self):
        try:
            self.update_params()
            if write_files(self.params):
                self.status_label.setText("Files written successfully")
            else:
                QMessageBox.warning(self, "Warning", "Failed to write files")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to write files: {str(e)}")
    
    def run_solution(self):
        try:
            run_solution()
            self.status_label.setText("Solution completed")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to run solution: {str(e)}")

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
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())