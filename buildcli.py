#!/usr/bin/env python
import os
import argparse
import glob
import subprocess
import sys

# Ensure snek.py is in the thirdparty/snek directory
snek_script = 'thirdparty/snek/snek.py'

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

required_packages = [
    'gcc',
    'nasm',
    'qemu-system-x86',
    'python3'
]

def install_packages():
    print("Installing required packages...")
    if sys.platform.startswith("linux"):
        package_manager = "apt-get" if os.path.exists("/usr/bin/apt-get") else "yum"
        subprocess.check_call(['sudo', package_manager, 'update'])
        subprocess.check_call(['sudo', package_manager, 'install', '-y'] + required_packages)
    elif sys.platform == "darwin":
        subprocess.check_call(['brew', 'install'] + required_packages)
    else:
        print("Unsupported OS. Please install the required packages manually.")
        sys.exit(1)

def build_py():
    for i in initial_py_files:
        output = i.replace('src', 'build')
        output = output.replace('.py', '.c')

        d = "build"

        if not os.path.exists(d):
            os.makedirs(d)

        os.system(f'python {snek_script} {i} {output}')

def build_c():
    for c_file in initial_c_files:
        command = "gcc "

        for flag in gcc_flags:
            command += flag + " "

        command += f"{c_file} -c -o {c_file + '.o'}"

        print(f"Compiling {c_file}")

        os.system(command)

def build_asm():
    for asm_file in initial_asm_files:
        command = f"nasm -felf64 {asm_file} -o build/{os.path.basename(asm_file + '.o')}"

        print(command)
        print(f"Assembling {asm_file}")

        os.system(command)

def link():
    object_files = [f'build/{os.path.basename(file + ".o")}' for file in initial_c_files + initial_asm_files]

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

def main():
    parser = argparse.ArgumentParser(description="Build System for Johnny OS")
    parser.add_argument('command', choices=['build', 'clean', 'run', 'build_run', 'install'], help="Command to execute")

    args = parser.parse_args()

    if args.command == 'install':
        install_packages()
    elif args.command == 'build':
        build_py()
        build_c()
        build_asm()
        link()
    elif args.command == 'clean':
        clean()
    elif args.command == 'run':
        run()
    elif args.command == 'build_run':
        build_py()
        build_c()
        build_asm()
        link()
        run()

if __name__ == "__main__":
    main()
