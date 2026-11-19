"use strict";

const test = require("node:test");
const assert = require("node:assert/strict");
const { translateText } = require("../VMTranslator");

test("算術指令會產生 Hack Assembly", () => {
  const assembly = translateText("push constant 7\npush constant 8\nadd");
  assert.match(assembly, /M=D\+M/);
});

test("比較指令會產生 true 與 false 分支", () => {
  const assembly = translateText("push constant 3\npush constant 2\ngt");
  assert.match(assembly, /CMP_TRUE/);
  assert.match(assembly, /CMP_FALSE/);
});

test("記憶體存取支援 local 與 temp", () => {
  const assembly = translateText("push local 2\npop temp 3");
  assert.match(assembly, /@LCL/);
  assert.match(assembly, /@8/);
});

test("流程控制標籤會加入檔案名稱作用域", () => {
  const assembly = translateText("label LOOP\ngoto LOOP", "Main.vm");
  assert.match(assembly, /\(Main\$LOOP\)/);
  assert.match(assembly, /@Main\$LOOP/);
});

test("function、call、return 會產生函式呼叫框架", () => {
  const assembly = translateText(
    "function Simple.add 2\ncall Simple.add 2\nreturn",
    "Main.vm"
  );
  assert.match(assembly, /\(Simple\.add\)/);
  assert.match(assembly, /Simple\.add\$ret\.0/);
  assert.match(assembly, /@R14/);
});

test("非法的 pop constant 會回報錯誤行號", () => {
  assert.throws(
    () => translateText("push constant 1\npop constant 0", "Bad.vm"),
    /Bad\.vm 第 2 行：不允許 pop constant/
  );
});
