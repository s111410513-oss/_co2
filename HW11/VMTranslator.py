import os
import sys


class Parser:
    def __init__(self, filename):
        self.commands = []
        with open(filename, "r", encoding="utf-8") as file:
            for line in file:
                line = line.split("//")[0].strip()
                if line:
                    self.commands.append(line.split())
        self.index = 0

    def has_more_commands(self):
        return self.index < len(self.commands)

    def advance(self):
        command = self.commands[self.index]
        self.index += 1
        return command


class CodeWriter:
    def __init__(self, filename):
        self.file = open(filename, "w", encoding="utf-8")
        self.label_count = 0
        self.current_file = ""
        self.current_function = ""

    def write(self, code):
        self.file.write(code + "\n")

    def set_file_name(self, filename):
        self.current_file = os.path.splitext(os.path.basename(filename))[0]

    def write_init(self):
        self.write("@256")
        self.write("D=A")
        self.write("@SP")
        self.write("M=D")
        self.write_call("Sys.init", 0)

    def write_arithmetic(self, command):
        if command in ["add", "sub", "and", "or"]:
            self.write("@SP")
            self.write("AM=M-1")
            self.write("D=M")
            self.write("A=A-1")
            if command == "add":
                self.write("M=D+M")
            elif command == "sub":
                self.write("M=M-D")
            elif command == "and":
                self.write("M=D&M")
            else:
                self.write("M=D|M")

        elif command in ["neg", "not"]:
            self.write("@SP")
            self.write("A=M-1")
            self.write("M=-M" if command == "neg" else "M=!M")

        elif command in ["eq", "gt", "lt"]:
            true_label = "TRUE" + str(self.label_count)
            end_label = "END" + str(self.label_count)
            self.label_count += 1

            self.write("@SP")
            self.write("AM=M-1")
            self.write("D=M")
            self.write("A=A-1")
            self.write("D=M-D")
            self.write("@" + true_label)
            self.write({"eq": "D;JEQ", "gt": "D;JGT", "lt": "D;JLT"}[command])
            self.write("@SP")
            self.write("A=M-1")
            self.write("M=0")
            self.write("@" + end_label)
            self.write("0;JMP")
            self.write("(" + true_label + ")")
            self.write("@SP")
            self.write("A=M-1")
            self.write("M=-1")
            self.write("(" + end_label + ")")

    def write_push_pop(self, command, segment, index):
        if command == "push":
            if segment == "constant":
                self.write("@" + str(index))
                self.write("D=A")
            elif segment in ["local", "argument", "this", "that"]:
                base = {"local": "LCL", "argument": "ARG",
                        "this": "THIS", "that": "THAT"}[segment]
                self.write("@" + str(index))
                self.write("D=A")
                self.write("@" + base)
                self.write("A=D+M")
                self.write("D=M")
            elif segment == "temp":
                self.write("@" + str(5 + index))
                self.write("D=M")
            elif segment == "pointer":
                self.write("@THIS" if index == 0 else "@THAT")
                self.write("D=M")
            elif segment == "static":
                self.write("@" + self.current_file + "." + str(index))
                self.write("D=M")
            else:
                raise ValueError("不支援的 segment: " + segment)

            self.write("@SP")
            self.write("A=M")
            self.write("M=D")
            self.write("@SP")
            self.write("M=M+1")

        elif command == "pop":
            if segment in ["local", "argument", "this", "that"]:
                base = {"local": "LCL", "argument": "ARG",
                        "this": "THIS", "that": "THAT"}[segment]
                self.write("@" + str(index))
                self.write("D=A")
                self.write("@" + base)
                self.write("D=D+M")
                self.write("@R13")
                self.write("M=D")
            elif segment == "temp":
                self.write("@" + str(5 + index))
                self.write("D=A")
                self.write("@R13")
                self.write("M=D")
            elif segment == "pointer":
                self.write("@THIS" if index == 0 else "@THAT")
                self.write("D=A")
                self.write("@R13")
                self.write("M=D")
            elif segment == "static":
                self.write("@" + self.current_file + "." + str(index))
                self.write("D=A")
                self.write("@R13")
                self.write("M=D")
            else:
                raise ValueError("不支援的 segment: " + segment)

            self.write("@SP")
            self.write("AM=M-1")
            self.write("D=M")
            self.write("@R13")
            self.write("A=M")
            self.write("M=D")

    def scoped_label(self, label):
        scope = self.current_function if self.current_function else self.current_file
        return scope + "$" + label

    def write_label(self, label):
        self.write("(" + self.scoped_label(label) + ")")

    def write_goto(self, label):
        self.write("@" + self.scoped_label(label))
        self.write("0;JMP")

    def write_if(self, label):
        self.write("@SP")
        self.write("AM=M-1")
        self.write("D=M")
        self.write("@" + self.scoped_label(label))
        self.write("D;JNE")

    def write_function(self, name, num_vars):
        self.current_function = name
        self.write("(" + name + ")")
        for _ in range(num_vars):
            self.write("@0")
            self.write("D=A")
            self.push_d()

    def push_d(self):
        self.write("@SP")
        self.write("A=M")
        self.write("M=D")
        self.write("@SP")
        self.write("M=M+1")

    def write_call(self, name, num_args):
        return_label = "RETURN" + str(self.label_count)
        self.label_count += 1

        self.write("@" + return_label)
        self.write("D=A")
        self.push_d()

        for segment in ["LCL", "ARG", "THIS", "THAT"]:
            self.write("@" + segment)
            self.write("D=M")
            self.push_d()

        self.write("@SP")
        self.write("D=M")
        self.write("@5")
        self.write("D=D-A")
        self.write("@" + str(num_args))
        self.write("D=D-A")
        self.write("@ARG")
        self.write("M=D")

        self.write("@SP")
        self.write("D=M")
        self.write("@LCL")
        self.write("M=D")

        self.write("@" + name)
        self.write("0;JMP")
        self.write("(" + return_label + ")")

    def write_return(self):
        self.write("@LCL")
        self.write("D=M")
        self.write("@R13")
        self.write("M=D")

        self.write("@5")
        self.write("A=D-A")
        self.write("D=M")
        self.write("@R14")
        self.write("M=D")

        self.write("@SP")
        self.write("AM=M-1")
        self.write("D=M")
        self.write("@ARG")
        self.write("A=M")
        self.write("M=D")

        self.write("@ARG")
        self.write("D=M+1")
        self.write("@SP")
        self.write("M=D")

        for segment in ["THAT", "THIS", "ARG", "LCL"]:
            self.write("@R13")
            self.write("AM=M-1")
            self.write("D=M")
            self.write("@" + segment)
            self.write("M=D")

        self.write("@R14")
        self.write("A=M")
        self.write("0;JMP")

    def close(self):
        self.file.close()


def translate(path):
    if os.path.isdir(path):
        vm_files = [
            os.path.join(path, name)
            for name in sorted(os.listdir(path))
            if name.endswith(".vm")
        ]
        output_file = os.path.join(
            path, os.path.basename(os.path.abspath(path)) + ".asm"
        )
        bootstrap = True
    else:
        if not path.endswith(".vm"):
            print("請輸入 .vm 檔案或資料夾")
            return
        vm_files = [path]
        output_file = os.path.splitext(path)[0] + ".asm"
        bootstrap = False

    if not vm_files:
        print("找不到 VM 檔案")
        return

    writer = CodeWriter(output_file)
    try:
        if bootstrap:
            writer.write_init()

        for filename in vm_files:
            parser = Parser(filename)
            writer.set_file_name(filename)

            while parser.has_more_commands():
                command = parser.advance()
                cmd = command[0]

                if cmd in ["add", "sub", "neg", "eq", "gt", "lt",
                           "and", "or", "not"]:
                    writer.write_arithmetic(cmd)
                elif cmd in ["push", "pop"]:
                    writer.write_push_pop(cmd, command[1], int(command[2]))
                elif cmd == "label":
                    writer.write_label(command[1])
                elif cmd == "goto":
                    writer.write_goto(command[1])
                elif cmd == "if-goto":
                    writer.write_if(command[1])
                elif cmd == "function":
                    writer.write_function(command[1], int(command[2]))
                elif cmd == "call":
                    writer.write_call(command[1], int(command[2]))
                elif cmd == "return":
                    writer.write_return()
                else:
                    raise ValueError("未知的 VM 指令: " + " ".join(command))
    finally:
        writer.close()

    print("VM 轉換完成！")
    print("輸出檔案：" + output_file)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("使用方式：")
        print("python VMTranslator.py 檔案.vm")
        print("python VMTranslator.py 資料夾")
    else:
        translate(sys.argv[1])
