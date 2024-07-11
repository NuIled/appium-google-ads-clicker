import os
import subprocess

def install_requirements():
    # Install necessary packages
    subprocess.check_call(['pip', 'install', '-r', 'req.txt'])

if __name__ == '__main__':
    install_requirements()
