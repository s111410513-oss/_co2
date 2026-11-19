import os
import sys


class Parser:
    """讀取 VM 檔案，移除註解與空白行。"""

    def __init__(self, filename):
        self.filename = filename
        self.commands = []
        with open(filename, "r", encoding="utf-8") as file:
            for line_number, line in enumerate(file, 1):
                line = line.split("//", 1)[0].strip()
                if line:
                    self.commands.append((line_number, line.split()))
        self.index = 0

    def has_more_commands(self):
        return self.index < len(self.commands)

    def advance(self):
        line_number, command = self.commands[self.index]
        self.index += 1
        return line_number, command


class CodeWriter:
    """將 VM 指令轉成 Hack Assembly。"""

    ARITHMETIC = {
        "add", "sub", "neg", "eq", "gt", "lt",
        "and", "or", "not"
    }
    SEGMENTS = {
        "local": "LCL",
        "argument": "ARG",
        "this": "THIS",
        "that": "THAT"
    }

    def __init__(self, filename):
        self.file = open(filename, "w", encoding="utf-8")
        self.label_count = 0
        self.return_count = 0
        self.current_file = ""
        self.current_function = ""

    def write(self, code):
        self.file.write(code + "\n")

    def write_comment(self, comment):
        self.write("// " + comment)

    def set_file_name(self, filename):
        self.current_file = os.path.splitext(os.path.basename(filename))[0]
        self.current_function = ""

    def push_d(self):
        self.write("@SP")
        self.write("A=M")
        self.write("M=D")
        self.write("@SP")
        self.write("M=M+1")

    def write_init(self):
        self.write_comment("Bootstrap: initialize stack and call Sys.init")
        self.write("@256")
        self.write("D=A")
        self.write("@SP")
        self.write("M=D")
        self.write_call("Sys.init", 0)

    def write_arithmetic(self, command):
        self.write_comment(command)

        if command in ("add", "sub", "and", "or"):
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

        elif command in ("neg", "not"):
            self.write("@SP")
            self.write("A=M-1")
            self.write("M=-M" if command == "neg" else "M=!M")

        elif command == "eq":
            true_label = self.unique_label("TRUE")
            end_label = self.unique_label("END")
            self.write("@SP")
            self.write("AM=M-1")
            self.write("D=M")
            self.write("A=A-1")
            self.write("D=M-D")
            self.write("@" + true_label)
            self.write("D;JEQ")
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

        elif command in ("gt", "lt"):
            self.write_signed_comparison(command)

    def unique_label(self, prefix):
        label = prefix + str(self.label_count)
        self.label_count += 1
        return label

    def write_signed_comparison(self, command):
        """
        比較 x 與 y。不能只計算 x-y 後判斷正負，因為 16-bit
        signed 整數相減可能溢位。先比較正負號，只有同號時才相減。
        """
        x_negative = self.unique_label("X_NEG")
        same_sign = self.unique_label("SAME_SIGN")
        true_label = self.unique_label("CMP_TRUE")
        false_label = self.unique_label("CMP_FALSE")
        end_label = self.unique_label("CMP_END")

        self.write("@SP")
        self.write("AM=M-1")
        self.write("D=M")
        self.write("@R13")
        self.write("M=D")             # R13 = y
        self.write("@SP")
        self.write("A=M-1")
        self.write("D=M")             # D = x
        self.write("@" + x_negative)
        self.write("D;JLT")           # x < 0

        # x >= 0：若 y < 0，gt 為真、lt 為假。
        self.write("@R13")
        self.write("D=M")
        self.write("@" + same_sign)
        self.write("D;JGE")           # y >= 0，兩者同號
        if command == "gt":
            self.write("@" + true_label)
        else:
            self.write("@" + false_label)
        self.write("0;JMP")

        # x < 0：若 y >= 0，gt 為假、lt 為真。
        self.write("(" + x_negative + ")")
        self.write("@R13")
        self.write("D=M")
        self.write("@" + same_sign)
        self.write("D;JLT")           # y < 0，兩者同號
        if command == "gt":
            self.write("@" + false_label)
        else:
            self.write("@" + true_label)
        self.write("0;JMP")

        # 同號時 x-y 不會發生 signed overflow。
        self.write("(" + same_sign + ")")
        self.write("@SP")
        self.write("A=M-1")
        self.write("D=M")
        self.write("@R13")
        self.write("D=D-M")           # D = x-y
        self.write("@" + true_label)
        self.write("D;" + ("JGT" if command == "gt" else "JLT"))
        self.write("@" + false_label)
        self.write("0;JMP")

        self.write("(" + true_label + ")")
        self.write("@SP")
        self.write("A=M-1")
        self.write("M=-1")
        self.write("@" + end_label)
        self.write("0;JMP")
        self.write("(" + false_label + ")")
        self.write("@SP")
        self.write("A=M-1")
        self.write("M=0")
        self.write("(" + end_label + ")")

    def check_index(self, segment, index, command):
        if index < 0:
            raise ValueError("segment index 不可小於 0")
        if segment == "temp" and index > 7:
            raise ValueError("temp index 必須介於 0 到 7")
        if segment == "pointer" and index not in (0, 1):
            raise ValueError("pointer index 只能是 0 或 1")
        if segment == "constant" and command == "pop":
            raise ValueError("不允許 pop constant")
        if segment not in (
            "constant", "local", "argument", "this", "that",
            "temp", "pointer", "static"
        ):
            raise ValueError("不支援的 segment: " + segment)

    def write_push_pop(self, command, segment, index):
        self.check_index(segment, index, command)
        self.write_comment(command + " " + segment + " " + str(index))

        if command == "push":
            if segment == "constant":
                self.write("@" + str(index))
                self.write("D=A")
            elif segment in self.SEGMENTS:
                self.write("@" + str(index))
                self.write("D=A")
                self.write("@" + self.SEGMENTS[segment])
                self.write("A=D+M")
                self.write("D=M")
            elif segment == "temp":
                self.write("@" + str(5 + index))
                self.write("D=M")
            elif segment == "pointer":
                self.write("@THIS" if index == 0 else "@THAT")
                self.write("D=M")
            else:
                self.write("@" + self.current_file + "." + str(index))
                self.write("D=M")
            self.push_d()

        elif command == "pop":
            if segment in self.SEGMENTS:
                self.write("@" + str(index))
                self.write("D=A")
                self.write("@" + self.SEGMENTS[segment])
                self.write("D=D+M")
            elif segment == "temp":
                self.write("@" + str(5 + index))
                self.write("D=A")
            elif segment == "pointer":
                self.write("@THIS" if index == 0 else "@THAT")
                self.write("D=A")
            else:
                self.write("@" + self.current_file + "." + str(index))
                self.write("D=A")

            self.write("@R13")
            self.write("M=D")
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
        self.write_comment("label " + label)
        self.write("(" + self.scoped_label(label) + ")")

    def write_goto(self, label):
        self.write_comment("goto " + label)
        self.write("@" + self.scoped_label(label))
        self.write("0;JMP")

    def write_if(self, label):
        self.write_comment("if-goto " + label)
        self.write("@SP")
        self.write("AM=M-1")
        self.write("D=M")
        self.write("@" + self.scoped_label(label))
        self.write("D;JNE")

    def write_function(self, name, num_vars):
        if num_vars < 0:
            raise ValueError("function local 數量不可小於 0")
        self.current_function = name
        self.write_comment("function " + name + " " + str(num_vars))
        self.write("(" + name + ")")
        for _ in range(num_vars):
            self.write("@0")
            self.write("D=A")
            self.push_d()

    def write_call(self, name, num_args):
        if num_args < 0:
            raise ValueError("call argument 數量不可小於 0")
        return_label = name + "$ret." + str(self.return_count)
        self.return_count += 1
        self.write_comment("call " + name + " " + str(num_args))

        self.write("@" + return_label)
        self.write("D=A")
        self.push_d()

        for segment in ("LCL", "ARG", "THIS", "THAT"):
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
        self.write_comment("return")
        self.write("@LCL")
        self.write("D=M")
        self.write("@R13")
        self.write("M=D")             # FRAME = LCL

        self.write("@5")
        self.write("A=D-A")
        self.write("D=M")
        self.write("@R14")
        self.write("M=D")             # RET = *(FRAME-5)

        self.write("@SP")
        self.write("AM=M-1")
        self.write("D=M")
        self.write("@ARG")
        self.write("A=M")
        self.write("M=D")             # *ARG = pop()

        self.write("@ARG")
        self.write("D=M+1")
        self.write("@SP")
        self.write("M=D")             # SP = ARG+1

        for segment in ("THAT", "THIS", "ARG", "LCL"):
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
    path = os.path.abspath(path)

    if os.path.isdir(path):
        vm_files = [
            os.path.join(path, name)
            for name in sorted(os.listdir(path))
            if name.lower().endswith(".vm")
        ]
        output_file = os.path.join(
            path, os.path.basename(path) + ".asm"
        )
        bootstrap = True
    else:
        if not path.lower().endswith(".vm"):
            raise ValueError("請輸入 .vm 檔案或資料夾")
        vm_files = [path]
        output_file = os.path.splitext(path)[0] + ".asm"
        bootstrap = False

    if not vm_files:
        raise ValueError("找不到 VM 檔案")

    writer = CodeWriter(output_file)
    try:
        if bootstrap:
            writer.write_init()

        for filename in vm_files:
            writer.set_file_name(filename)
            writer.write_comment("File: " + os.path.basename(filename))
            parser = Parser(filename)

            while parser.has_more_commands():
                line_number, command = parser.advance()
                cmd = command[0]
                try:
                    if cmd in writer.ARITHMETIC:
                        if len(command) != 1:
                            raise ValueError("算術指令不應有參數")
                        writer.write_arithmetic(cmd)
                    elif cmd in ("push", "pop"):
                        if len(command) != 3:
                            raise ValueError("push/pop 格式應為：指令 segment index")
                        writer.write_push_pop(cmd, command[1], int(command[2]))
                    elif cmd in ("label", "goto", "if-goto"):
                        if len(command) != 2:
                            raise ValueError("流程控制指令格式錯誤")
                        if cmd == "label":
                            writer.write_label(command[1])
                        elif cmd == "goto":
                            writer.write_goto(command[1])
                        else:
                            writer.write_if(command[1])
                    elif cmd == "function":
                        if len(command) != 3:
                            raise ValueError("function 格式應為：function name nVars")
                        writer.write_function(command[1], int(command[2]))
                    elif cmd == "call":
                        if len(command) != 3:
                            raise ValueError("call 格式應為：call name nArgs")
                        writer.write_call(command[1], int(command[2]))
                    elif cmd == "return":
                        if len(command) != 1:
                            raise ValueError("return 不應有參數")
                        writer.write_return()
                    else:
                        raise ValueError("未知的 VM 指令：" + cmd)
                except (ValueError, IndexError) as error:
                    raise ValueError(
                        "{} 第 {} 行：{}".format(filename, line_number, error)
                    )
    finally:
        writer.close()

    print("VM 轉換完成！")
    print("輸出檔案：" + output_file)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("使用方式：")
        print("python VMTranslator.py 檔案.vm")
        print("python VMTranslator.py 資料夾")
        sys.exit(1)

    try:
        translate(sys.argv[1])
    except (OSError, ValueError) as error:
        print("錯誤：" + str(error))
        sys.exit(1)
