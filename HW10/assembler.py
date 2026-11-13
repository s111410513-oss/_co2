# Nand2Tetris Hack Assembler
# 將 Hack Assembly (.asm) 轉換成 16 位元機器碼 (.hack)

# 預先定義的符號
symbol_table = {
    "SP": 0,
    "LCL": 1,
    "ARG": 2,
    "THIS": 3,
    "THAT": 4,
    "SCREEN": 16384,
    "KBD": 24576
}

# R0 到 R15
for i in range(16):
    symbol_table["R" + str(i)] = i


# comp 指令編碼
comp_table = {
    "0": "0101010",
    "1": "0111111",
    "-1": "0111010",
    "D": "0001100",
    "A": "0110000",
    "M": "1110000",
    "!D": "0001101",
    "!A": "0110001",
    "!M": "1110001",
    "-D": "0001111",
    "-A": "0110011",
    "-M": "1110011",
    "D+1": "0011111",
    "A+1": "0110111",
    "M+1": "1110111",
    "D-1": "0001110",
    "A-1": "0110010",
    "M-1": "1110010",
    "D+A": "0000010",
    "D+M": "1000010",
    "D-A": "0010011",
    "D-M": "1010011",
    "A-D": "0000111",
    "M-D": "1000111",
    "D&A": "0000000",
    "D&M": "1000000",
    "D|A": "0010101",
    "D|M": "1010101"
}

# dest 指令編碼
dest_table = {
    "": "000",
    "M": "001",
    "D": "010",
    "MD": "011",
    "A": "100",
    "AM": "101",
    "AD": "110",
    "AMD": "111"
}

# jump 指令編碼
jump_table = {
    "": "000",
    "JGT": "001",
    "JEQ": "010",
    "JGE": "011",
    "JLT": "100",
    "JNE": "101",
    "JLE": "110",
    "JMP": "111"
}


# 清除註解與空白
def clean_line(line):
    line = line.split("//")[0]
    return line.strip()


# 第一次掃描：找出標籤位址
def first_pass(lines):
    rom_address = 0

    for line in lines:
        line = clean_line(line)

        if line == "":
            continue

        if line.startswith("(") and line.endswith(")"):
            label = line[1:-1]
            symbol_table[label] = rom_address
        else:
            rom_address += 1


# 第二次掃描：將指令轉換成機器碼
def second_pass(lines):
    binary_code = []
    ram_address = 16

    for line in lines:
        line = clean_line(line)

        if line == "":
            continue

        # 標籤不會產生機器碼
        if line.startswith("(") and line.endswith(")"):
            continue

        # A 指令
        if line.startswith("@"):
            symbol = line[1:]

            if symbol.isdigit():
                address = int(symbol)
            else:
                if symbol not in symbol_table:
                    symbol_table[symbol] = ram_address
                    ram_address += 1

                address = symbol_table[symbol]

            binary = format(address, "016b")
            binary_code.append(binary)

        # C 指令
        else:
            dest = ""
            jump = ""

            if "=" in line:
                dest, line = line.split("=", 1)

            if ";" in line:
                comp, jump = line.split(";", 1)
            else:
                comp = line

            dest = dest.strip()
            comp = comp.strip()
            jump = jump.strip()

            binary = "111"
            binary += comp_table[comp]
            binary += dest_table[dest]
            binary += jump_table[jump]

            binary_code.append(binary)

    return binary_code


# 主程式：讀取 asm 並輸出 hack
def assemble(filename):
    with open(filename, "r", encoding="utf-8") as file:
        lines = file.readlines()

    # 第一次掃描
    first_pass(lines)

    # 第二次掃描
    binary_code = second_pass(lines)

    # 產生輸出檔名
    if filename.endswith(".asm"):
        output_file = filename[:-4] + ".hack"
    else:
        output_file = filename + ".hack"

    with open(output_file, "w", encoding="utf-8") as file:
        for code in binary_code:
            file.write(code + "\n")

    print("組譯完成！")
    print("輸出檔案：" + output_file)


# 執行組譯器（請將 Prog.asm 放在同一個資料夾）
assemble("Prog.asm")
