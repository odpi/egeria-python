import subprocess

startup_scripts = ["config_cocoMDS1.py", "config_cocoMDS2.py",
                   "config_cocoMDS3.py", "config_cocoMDS4.py",
                   "config_cocoMDS5.py", "config_cocoMDSx.py",
                   "config_cocoView1.py", "config_exchangeDL01.py",
                   "config_monitorDev01.py", "config_monitorGov01.py"]
for script in startup_scripts:
    subprocess.call(["python",script])