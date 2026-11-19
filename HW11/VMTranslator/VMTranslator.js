#!/usr/bin/env node
"use strict";

const fs = require("node:fs");
const path = require("node:path");

const ARITHMETIC = new Set([
  "add", "sub", "neg", "eq", "gt", "lt", "and", "or", "not"
]);
const SEGMENTS = {
  local: "LCL",
  argument: "ARG",
  this: "THIS",
  that: "THAT"
};
const VALID_SEGMENTS = new Set([
  "constant", "local", "argument", "this", "that",
  "temp", "pointer", "static"
]);

class CodeWriter {
  constructor() {
    this.lines = [];
    this.labelCount = 0;
    this.returnCount = 0;
    this.currentFile = "Main";
    this.currentFunction = "";
  }

  write(line) {
    this.lines.push(line);
  }

  comment(line) {
    this.write("// " + line);
  }

  setFileName(fileName) {
    this.currentFile = path.basename(fileName, path.extname(fileName));
    this.currentFunction = "";
  }

  uniqueLabel(prefix) {
    const label = prefix + this.labelCount;
    this.labelCount += 1;
    return label;
  }

  pushD() {
    this.write("@SP");
    this.write("A=M");
    this.write("M=D");
    this.write("@SP");
    this.write("M=M+1");
  }

  writeInit() {
    this.comment("Bootstrap code");
    this.write("@256");
    this.write("D=A");
    this.write("@SP");
    this.write("M=D");
    this.writeCall("Sys.init", 0);
  }

  writeArithmetic(command) {
    this.comment(command);

    if (["add", "sub", "and", "or"].includes(command)) {
      this.write("@SP");
      this.write("AM=M-1");
      this.write("D=M");
      this.write("A=A-1");
      const operation = {
        add: "M=D+M",
        sub: "M=M-D",
        and: "M=D&M",
        or: "M=D|M"
      };
      this.write(operation[command]);
      return;
    }

    if (command === "neg" || command === "not") {
      this.write("@SP");
      this.write("A=M-1");
      this.write(command === "neg" ? "M=-M" : "M=!M");
      return;
    }

    if (command === "eq") {
      const yes = this.uniqueLabel("EQ_TRUE");
      const end = this.uniqueLabel("EQ_END");
      this.write("@SP");
      this.write("AM=M-1");
      this.write("D=M");
      this.write("A=A-1");
      this.write("D=M-D");
      this.write("@" + yes);
      this.write("D;JEQ");
      this.write("@SP");
      this.write("A=M-1");
      this.write("M=0");
      this.write("@" + end);
      this.write("0;JMP");
      this.write("(" + yes + ")");
      this.write("@SP");
      this.write("A=M-1");
      this.write("M=-1");
      this.write("(" + end + ")");
      return;
    }

    if (command === "gt" || command === "lt") {
      this.writeSignedComparison(command);
    }
  }

  writeSignedComparison(command) {
    const xNegative = this.uniqueLabel("X_NEG");
    const sameSign = this.uniqueLabel("SAME_SIGN");
    const yes = this.uniqueLabel("CMP_TRUE");
    const no = this.uniqueLabel("CMP_FALSE");
    const end = this.uniqueLabel("CMP_END");

    this.write("@SP");
    this.write("AM=M-1");
    this.write("D=M");
    this.write("@R13");
    this.write("M=D");
    this.write("@SP");
    this.write("A=M-1");
    this.write("D=M");
    this.write("@" + xNegative);
    this.write("D;JLT");

    this.write("@R13");
    this.write("D=M");
    this.write("@" + sameSign);
    this.write("D;JGE");
    this.write(command === "gt" ? "@" + yes : "@" + no);
    this.write("0;JMP");

    this.write("(" + xNegative + ")");
    this.write("@R13");
    this.write("D=M");
    this.write("@" + sameSign);
    this.write("D;JLT");
    this.write(command === "gt" ? "@" + no : "@" + yes);
    this.write("0;JMP");

    this.write("(" + sameSign + ")");
    this.write("@SP");
    this.write("A=M-1");
    this.write("D=M");
    this.write("@R13");
    this.write("D=D-M");
    this.write("@" + yes);
    this.write("D;" + (command === "gt" ? "JGT" : "JLT"));
    this.write("@" + no);
    this.write("0;JMP");

    this.write("(" + yes + ")");
    this.write("@SP");
    this.write("A=M-1");
    this.write("M=-1");
    this.write("@" + end);
    this.write("0;JMP");
    this.write("(" + no + ")");
    this.write("@SP");
    this.write("A=M-1");
    this.write("M=0");
    this.write("(" + end + ")");
  }

  validateSegment(command, segment, index) {
    if (!VALID_SEGMENTS.has(segment)) {
      throw new Error("不支援的 segment: " + segment);
    }
    if (!Number.isInteger(index) || index < 0) {
      throw new Error("index 必須是 0 或正整數");
    }
    if (segment === "temp" && index > 7) {
      throw new Error("temp index 必須介於 0 到 7");
    }
    if (segment === "pointer" && index > 1) {
      throw new Error("pointer index 只能是 0 或 1");
    }
    if (command === "pop" && segment === "constant") {
      throw new Error("不允許 pop constant");
    }
  }

  writePushPop(command, segment, index) {
    this.validateSegment(command, segment, index);
    this.comment(command + " " + segment + " " + index);

    if (command === "push") {
      if (segment === "constant") {
        this.write("@" + index);
        this.write("D=A");
      } else if (SEGMENTS[segment]) {
        this.write("@" + index);
        this.write("D=A");
        this.write("@" + SEGMENTS[segment]);
        this.write("A=D+M");
        this.write("D=M");
      } else if (segment === "temp") {
        this.write("@" + (5 + index));
        this.write("D=M");
      } else if (segment === "pointer") {
        this.write(index === 0 ? "@THIS" : "@THAT");
        this.write("D=M");
      } else {
        this.write("@" + this.currentFile + "." + index);
        this.write("D=M");
      }
      this.pushD();
      return;
    }

    if (SEGMENTS[segment]) {
      this.write("@" + index);
      this.write("D=A");
      this.write("@" + SEGMENTS[segment]);
      this.write("D=D+M");
    } else if (segment === "temp") {
      this.write("@" + (5 + index));
      this.write("D=A");
    } else if (segment === "pointer") {
      this.write(index === 0 ? "@THIS" : "@THAT");
      this.write("D=A");
    } else {
      this.write("@" + this.currentFile + "." + index);
      this.write("D=A");
    }

    this.write("@R13");
    this.write("M=D");
    this.write("@SP");
    this.write("AM=M-1");
    this.write("D=M");
    this.write("@R13");
    this.write("A=M");
    this.write("M=D");
  }

  scopedLabel(label) {
    return (this.currentFunction || this.currentFile) + "$" + label;
  }

  writeLabel(label) {
    this.comment("label " + label);
    this.write("(" + this.scopedLabel(label) + ")");
  }

  writeGoto(label) {
    this.comment("goto " + label);
    this.write("@" + this.scopedLabel(label));
    this.write("0;JMP");
  }

  writeIf(label) {
    this.comment("if-goto " + label);
    this.write("@SP");
    this.write("AM=M-1");
    this.write("D=M");
    this.write("@" + this.scopedLabel(label));
    this.write("D;JNE");
  }

  writeFunction(name, localCount) {
    if (!Number.isInteger(localCount) || localCount < 0) {
      throw new Error("function local 數量不可小於 0");
    }
    this.currentFunction = name;
    this.comment("function " + name + " " + localCount);
    this.write("(" + name + ")");
    for (let i = 0; i < localCount; i += 1) {
      this.write("@0");
      this.write("D=A");
      this.pushD();
    }
  }

  writeCall(name, argumentCount) {
    if (!Number.isInteger(argumentCount) || argumentCount < 0) {
      throw new Error("call argument 數量不可小於 0");
    }
    const returnLabel = name + "$ret." + this.returnCount;
    this.returnCount += 1;
    this.comment("call " + name + " " + argumentCount);

    this.write("@" + returnLabel);
    this.write("D=A");
    this.pushD();

    for (const segment of ["LCL", "ARG", "THIS", "THAT"]) {
      this.write("@" + segment);
      this.write("D=M");
      this.pushD();
    }

    this.write("@SP");
    this.write("D=M");
    this.write("@5");
    this.write("D=D-A");
    this.write("@" + argumentCount);
    this.write("D=D-A");
    this.write("@ARG");
    this.write("M=D");

    this.write("@SP");
    this.write("D=M");
    this.write("@LCL");
    this.write("M=D");
    this.write("@" + name);
    this.write("0;JMP");
    this.write("(" + returnLabel + ")");
  }

  writeReturn() {
    this.comment("return");
    this.write("@LCL");
    this.write("D=M");
    this.write("@R13");
    this.write("M=D");
    this.write("@5");
    this.write("A=D-A");
    this.write("D=M");
    this.write("@R14");
    this.write("M=D");

    this.write("@SP");
    this.write("AM=M-1");
    this.write("D=M");
    this.write("@ARG");
    this.write("A=M");
    this.write("M=D");
    this.write("@ARG");
    this.write("D=M+1");
    this.write("@SP");
    this.write("M=D");

    for (const segment of ["THAT", "THIS", "ARG", "LCL"]) {
      this.write("@R13");
      this.write("AM=M-1");
      this.write("D=M");
      this.write("@" + segment);
      this.write("M=D");
    }

    this.write("@R14");
    this.write("A=M");
    this.write("0;JMP");
  }

  toString() {
    return this.lines.join("\n") + "\n";
  }
}

function parseLine(line) {
  return line.split("//", 1)[0].trim().split(/\s+/).filter(Boolean);
}

function translateText(source, fileName = "Main.vm", writer = new CodeWriter()) {
  writer.setFileName(fileName);
  const lines = source.split(/\r?\n/);

  lines.forEach((rawLine, index) => {
    const command = parseLine(rawLine);
    if (command.length === 0) return;

    const [operation, ...args] = command;
    try {
      if (ARITHMETIC.has(operation)) {
        if (args.length !== 0) throw new Error("算術指令不應有參數");
        writer.writeArithmetic(operation);
      } else if (operation === "push" || operation === "pop") {
        if (args.length !== 2) throw new Error("格式應為：push/pop segment index");
        const number = Number(args[1]);
        if (!/^\d+$/.test(args[1])) throw new Error("index 必須是整數");
        writer.writePushPop(operation, args[0], number);
      } else if (["label", "goto", "if-goto"].includes(operation)) {
        if (args.length !== 1) throw new Error("流程控制指令格式錯誤");
        if (operation === "label") writer.writeLabel(args[0]);
        if (operation === "goto") writer.writeGoto(args[0]);
        if (operation === "if-goto") writer.writeIf(args[0]);
      } else if (operation === "function" || operation === "call") {
        if (args.length !== 2 || !/^\d+$/.test(args[1])) {
          throw new Error(operation + " 格式應為：指令 name 數量");
        }
        const count = Number(args[1]);
        if (operation === "function") writer.writeFunction(args[0], count);
        else writer.writeCall(args[0], count);
      } else if (operation === "return") {
        if (args.length !== 0) throw new Error("return 不應有參數");
        writer.writeReturn();
      } else {
        throw new Error("未知的 VM 指令：" + operation);
      }
    } catch (error) {
      throw new Error(fileName + " 第 " + (index + 1) + " 行：" + error.message);
    }
  });

  return writer.toString();
}

function translate(inputPath) {
  const absolutePath = path.resolve(inputPath);
  const stats = fs.statSync(absolutePath);
  const writer = new CodeWriter();
  let outputPath;

  if (stats.isDirectory()) {
    const vmFiles = fs.readdirSync(absolutePath)
      .filter((name) => name.toLowerCase().endsWith(".vm"))
      .sort();
    if (vmFiles.length === 0) throw new Error("資料夾內找不到 .vm 檔案");

    outputPath = path.join(absolutePath, path.basename(absolutePath) + ".asm");
    writer.writeInit();
    for (const name of vmFiles) {
      writer.comment("File: " + name);
      translateText(fs.readFileSync(path.join(absolutePath, name), "utf8"), name, writer);
    }
  } else {
    if (!absolutePath.toLowerCase().endsWith(".vm")) {
      throw new Error("請輸入 .vm 檔案或資料夾");
    }
    outputPath = absolutePath.replace(/\.vm$/i, ".asm");
    translateText(fs.readFileSync(absolutePath, "utf8"), path.basename(absolutePath), writer);
  }

  fs.writeFileSync(outputPath, writer.toString(), "utf8");
  return outputPath;
}

if (require.main === module) {
  const input = process.argv[2];
  if (!input || process.argv.length !== 3) {
    console.log("使用方式：");
    console.log("node VMTranslator.js 檔案.vm");
    console.log("node VMTranslator.js 資料夾");
    process.exit(1);
  }

  try {
    const output = translate(input);
    console.log("VM 轉換完成！");
    console.log("輸出檔案：" + output);
  } catch (error) {
    console.error("錯誤：" + error.message);
    process.exit(1);
  }
}

module.exports = { CodeWriter, translate, translateText };
