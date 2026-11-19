# HW11 — nand2tetris VM Translator

本作業參考 [ChunYang0808/_co 的第 08 章專案](https://github.com/ChunYang0808/_co/tree/main/08) 的資料夾規劃方式，將 VM Translator、Program Flow、Function Calls、測試與範例分開管理。

本版本使用 **JavaScript（Node.js）** 撰寫，不需要安裝 Python 或第三方 npm 套件。

## 專案結構

```text
HW11/
├── ProgramFlow/
│   ├── BasicLoop/
│   │   └── BasicLoop.vm
│   └── FibonacciSeries/
│       └── FibonacciSeries.vm
├── FunctionCalls/
│   ├── SimpleFunction/
│   │   └── SimpleFunction.vm
│   └── NestedCall/
│       ├── Main.vm
│       ├── Sys.vm
│       └── README.md
├── VMTranslator/
│   ├── VMTranslator.js
│   ├── package.json
│   ├── .gitignore
│   └── tests/
│       └── VMTranslator.test.js
└── README.md
```

## 支援功能

### Project 7：堆疊與記憶體操作

- 算術／邏輯：`add`、`sub`、`neg`、`eq`、`gt`、`lt`、`and`、`or`、`not`
- 記憶體存取：`push`、`pop`
- Segment：`constant`、`local`、`argument`、`this`、`that`、`temp`、`pointer`、`static`

### Project 8：流程控制與函式呼叫

- 流程控制：`label`、`goto`、`if-goto`
- 函式：`function`、`call`、`return`
- 資料夾模式自動加入 Bootstrap：設定 `SP = 256` 並呼叫 `Sys.init`
- `gt`、`lt` 會先處理不同正負號的情況，避免 16-bit signed subtraction overflow 影響比較結果。

## 執行環境

- Node.js 18 以上
- 不需要額外安裝套件

## 使用方式

先開啟終端機，切換到 `HW11/VMTranslator`：

```bash
cd HW11/VMTranslator
```

### 執行測試

```bash
npm test
```

### 翻譯單一 VM 檔案

```bash
node VMTranslator.js ../ProgramFlow/BasicLoop/BasicLoop.vm
```

會在 VM 檔案旁產生同名的 `.asm` 檔案。單檔模式不會自動加入 Bootstrap。

### 翻譯整個資料夾

```bash
node VMTranslator.js ../FunctionCalls/NestedCall
```

會讀取資料夾內所有 `.vm` 檔案，依檔名排序合併，並產生 `NestedCall.asm`。資料夾模式會加入 Bootstrap，因此需要有 `Sys.init` 作為入口函式。

## 測試

測試使用 Node.js 內建的 `node:test`，不需要安裝 Mocha、Jest 等套件。測試涵蓋算術指令、比較指令、記憶體存取、流程標籤、函式呼叫與錯誤訊息。

> 單元測試只確認翻譯器產生的組合語言內容與錯誤處理；要驗證最終執行結果，仍建議使用 nand2tetris CPU Emulator 執行官方測試腳本。

## 參考資料

- [參考專案：ChunYang0808/_co — 08](https://github.com/ChunYang0808/_co/tree/main/08)
- [nand2tetris 官方網站](https://www.nand2tetris.org/)
- [Node.js 官方文件](https://nodejs.org/docs/latest/api/)
