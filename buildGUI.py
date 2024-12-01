#!/usr/bin/env python
import os
import sys
import glob
import tkinter as tk
from tkinter import messagebox, filedialog

# Gather initial files in src directory
initial_py_files = glob.glob('src/*.py')
initial_asm_files = glob.glob('src/*.asm')
initial_c_files = glob.glob('build/*.c')

gcc_flags = [
    '-O2',
    '-Wall',
    '-I.',
    '-std=gnu11',
    '-ffreestanding',
    '-fno-stack-protector',
    '-fno-pic',
    '-mabi=sysv',
    '-mno-80387',
    '-mno-mmx',
    '-mno-3dnow',
    '-mno-sse',
    '-mno-sse2',
    '-mno-red-zone',
    '-mcmodel=kernel',
]

ld_flags = [
    '-Tsrc/linker.ld',
    '-nostdlib',
    '-zmax-page-size=0x1000',
    '-static'
]

py_files = initial_py_files[:]
asm_files = initial_asm_files[:]
c_files = initial_c_files[:]

def build_py():
    for i in py_files:
        output = i.replace('src', 'build')
        output = output.replace('.py', '.c')

        d = "build"

        if not os.path.exists(d):
            os.makedirs(d)

        os.system(f'thirdparty/snek/snek.py {i} {output}')

def build_c():
    for c_file in c_files:
        command = "gcc "

        for flag in gcc_flags:
            command += flag + " "

        command += f"{c_file} -c -o {c_file + '.o'}"

        print(f"Compiling {c_file}")

        os.system(command)

def build_asm():
    for asm_file in asm_files:
        command = f"nasm -felf64 {asm_file} -o build/{os.path.basename(asm_file + '.o')}"

        print(command)
        print(f"Assembling {asm_file}")

        os.system(command)

def link():
    object_files = [f'build/{os.path.basename(file + ".o")}' for file in c_files + asm_files]

    command = "ld "

    for flag in ld_flags:
        command += flag + " "

    command += " ".join(object_files) + " -o kernel.elf"

    print(command)
    print(f"Linking kernel.elf")

    os.system(command)

def run():
    os.system("./scripts/make_image.py")
    os.system("qemu-system-x86_64 -M q35 -m 2G -cdrom pyOS.iso")

def clean():
    os.system("rm -rf build kernel.elf pyOS.iso")

def build():
    if var_py.get():
        build_py()
    if var_c.get():
        build_c()
    if var_asm.get():
        build_asm()
    if var_link.get():
        link()

def build_and_run():
    build()
    if var_run.get():
        run()

def add_py_file():
    file_path = filedialog.askopenfilename(filetypes=[("Python Files", "*.py")])
    if file_path:
        py_files.append(file_path)
        py_listbox.insert(tk.END, file_path)

def add_c_file():
    file_path = filedialog.askopenfilename(filetypes=[("C Files", "*.c")])
    if file_path:
        c_files.append(file_path)
        c_listbox.insert(tk.END, file_path)

def add_asm_file():
    file_path = filedialog.askopenfilename(filetypes=[("Assembly Files", "*.asm")])
    if file_path:
        asm_files.append(file_path)
        asm_listbox.insert(tk.END, file_path)

# GUI Setup
root = tk.Tk()
root.title("BUild JohnnyOS")

frame = tk.Frame(root)
frame.pack(pady=10)
root.resizable(False, False)

# Checkboxes
var_py = tk.BooleanVar()
var_c = tk.BooleanVar()
var_asm = tk.BooleanVar()
var_link = tk.BooleanVar()
var_run = tk.BooleanVar()

py_check = tk.Checkbutton(frame, text="Build Python", variable=var_py)
py_check.grid(row=0, column=0, sticky='w')

c_check = tk.Checkbutton(frame, text="Build C", variable=var_c)
c_check.grid(row=1, column=0, sticky='w')

asm_check = tk.Checkbutton(frame, text="Build ASM", variable=var_asm)
asm_check.grid(row=2, column=0, sticky='w')

link_check = tk.Checkbutton(frame, text="Link", variable=var_link)
link_check.grid(row=3, column=0, sticky='w')

run_check = tk.Checkbutton(frame, text="Run", variable=var_run)
run_check.grid(row=4, column=0, sticky='w')

# Listboxes for displaying files
py_listbox = tk.Listbox(frame, height=5)
py_listbox.grid(row=0, column=1, padx=5)
for file in py_files:
    py_listbox.insert(tk.END, file)

c_listbox = tk.Listbox(frame, height=5)
c_listbox.grid(row=1, column=1, padx=5)
for file in c_files:
    c_listbox.insert(tk.END, file)

asm_listbox = tk.Listbox(frame, height=5)
asm_listbox.grid(row=2, column=1, padx=5)
for file in asm_files:
    asm_listbox.insert(tk.END, file)

# Buttons to add files
py_add_button = tk.Button(frame, text="Add Python File", command=add_py_file)
py_add_button.grid(row=0, column=2, padx=5)

c_add_button = tk.Button(frame, text="Add C File", command=add_c_file)
c_add_button.grid(row=1, column=2, padx=5)

asm_add_button = tk.Button(frame, text="Add ASM File", command=add_asm_file)
asm_add_button.grid(row=2, column=2, padx=5)

# Control buttons
build_button = tk.Button(root, text="Build", command=build)
build_button.pack(pady=5)

build_run_button = tk.Button(root, text="Build and Run", command=build_and_run)
build_run_button.pack(pady=5)

clean_button = tk.Button(root, text="Clean", command=clean)
clean_button.pack(pady=5)

# Run the GUI
root.mainloop()
