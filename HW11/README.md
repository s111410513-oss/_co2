# HW11：nand2tetris 虛擬機翻譯器（VM Translator）

## 專案簡介

本專案以 Python 3 實作 nand2tetris Project 7、Project 8 的 VM Translator，將一個或多個 `.vm` 檔案翻譯成 Hack Assembly（`.asm`）。

翻譯器採用 Parser 與 CodeWriter 分工：
- **Parser**：讀取 VM 檔案、移除註解與空白行，並保留行號以便指出錯誤位置。
- **CodeWriter**：依 VM 指令種類產生對應的 Hack Assembly。
- **translate()**：負責單檔／資料夾輸入、檔案排序、bootstrap 與錯誤處理。

## 檔案

| 檔案 | 用途 |
|---|---|
| `VMTranslator.py` | VM 翻譯器主程式 |
| `README.md` | 專案說明與執行方式 |

## 支援的 VM 指令

### 1. 算術與邏輯指令（Project 7）

`add`、`sub`、`neg`、`eq`、`gt`、`lt`、`and`、`or`、`not`

比較結果依 VM 規格使用 `-1` 表示 true、`0` 表示 false。

**重要改進：** `gt` 與 `lt` 不再單純以 16-bit 的 `x-y` 正負判斷。當兩個運算元符號不同時先依符號決定結果，只有同號時才相減，避免極端負數／正數相減造成 signed overflow 判斷錯誤。

### 2. 記憶體存取指令（Project 7）

支援 `push`、`pop`，以及以下 segment：

- `constant`
- `local`
- `argument`
- `this`
- `that`
- `temp`（index 0～7）
- `pointer`（index 0～1）
- `static`

`pop constant`、超出合法範圍的 temp/pointer index，以及負數 index 會回報錯誤。

### 3. 程式流程指令（Project 8）

- `label labelName`
- `goto labelName`
- `if-goto labelName`

標籤會依目前函式名稱加上作用域前綴；如果尚未進入函式，則使用目前 VM 檔案名稱作為作用域，避免不同函式或檔案的同名標籤互相衝突。

### 4. 函式呼叫指令（Project 8）

- `function functionName nVars`
- `call functionName nArgs`
- `return`

實作標準 VM 呼叫框架：保存 return address、LCL、ARG、THIS、THAT，設定新的 ARG/LCL；return 時將回傳值放回呼叫者的 ARG[0]，還原呼叫者環境並跳回 return address。

## Bootstrap 初始化

- **資料夾模式**：輸出檔案開頭會先設定 `SP = 256)，再執行 `call Sys.init 0`。
- **單一檔案模式**：不自動加入 bootstrap，方便執行 Project 7 的單檔測試。

資料夾模式適用於包含 `Sys.init` 的多檔 VM 專案。

## 執行環境

- Python 3.8 以上
- 不需要安裝第三方套件

## 使用方式

請在命令提示字元（CMD）或 PowerShell 中，切換到 `VMTranslator.py` 所在資料夾。

### 翻譯單一 VM 檔案

```bash
python VMTranslator.py SimpleAdd.vm
```

會在同一個資料夾產生 `SimpleAdd.asm`。

### 翻譯整個資料夾

```bash
python VMTranslator.py path/to/Program
```

程式會依檔名排序讀取資料夾內的 `.vm` 檔案，並產生 `Program/Program.asm`。

### 使用 nand2tetris Emulator 驗證

1. 使用 VMTranslator 產生 `.asm`。
2. 開啟 nand2tetris 的 **CPU Emulator**。
3. 載入對應的 `.tst` 測試腳本（測試腳本會載入產生的 `.asm`）。
4. 執行測試，確認結果與預期輸出一致。

請注意：**VM Emulator 執行的是原始 `.vm` 程式；CPU Emulator 才是用來驗證翻譯後 `.asm` 的工具。**

建議依序使用官方 Project 7、Project 8 測試案例：
- Project 7：SimpleAdd、StackTest、BasicTest、PointerTest、StaticTest
- Project 8：BasicLoop、FibonacciSeries、SimpleFunction、NestedCall、FibonacciElement、StaticsTest

## 錯誤處理

遇到不支援的 VM 指令、指令參數數量錯誤、非法 segment index 或無法讀取檔案時，程式會顯示錯誤訊息；VM 指令格式錯誤時也會指出來源檔案與行號，方便除錯。

## 參考資料

本實作參考以下公開專案的 VM 翻譯器設計與 nand2tetris Project 7/8 指令規格，並以 Python 重新實作：

- [ccc115a/co - nand2tetris/08](https://github.com/ccc115a/co/tree/main/nand2tetris/08)
- [ccc-js/hack-computer - lib/vm](https://github.com/ccc-js/hack-computer/tree/main/lib/vm)
- [Nand2Tetris 官方網站](https://www.nand2tetris.org/)

本專案不是上述專案的原始碼複製；程式碼以本作業的 Python 架構撰寫。
