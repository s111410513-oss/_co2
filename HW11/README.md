# HW11：nand2tetris 虛擬機翻譯器（VM Translator）

## 作業介紹

本專案使用 Python 撰寫 nand2tetris 虛擬機翻譯器，將 VM（Virtual Machine）指令轉換成 Hack Assembly 組合語言，輸出為 `.asm` 檔案。

## 檔案說明

| 檔案 | 說明 |
|---|---|
| `VMTranslator.py` | 虛擬機翻譯器主程式 |
| `README.md` | 作業說明文件 |

## 功能

目前程式支援以下 VM 指令：

### 1. 算術與邏輯運算
- `add`、`sub`
- `neg`
- `eq`、`gt`、`lt`
- `and`、`or`、`not`

### 2. 記憶體存取
- `push`
- `pop`
- 支援 `constant`、`local`、`argument`、`this`、`that`、`temp`、`pointer`、`static` 等 segment。

### 3. 程式流程控制
- `label`
- `goto`
- `if-goto`

### 4. 函數呼叫
- `function`
- `call`
- `return`

### 5. Bootstrap 初始化
當輸入資料夾時，程式會初始化堆疊指標（SP = 256），並呼叫 `Sys.init`。

## 執行環境

- Python 3
- 不需要安裝額外的 Python 套件

## 使用方法

### 翻譯單一 VM 檔案

在命令提示字元或 PowerShell 執行：

```bash
python VMTranslator.py 路徑/檔案.vm
```

例如：

```bash
python VMTranslator.py SimpleAdd.vm
```

程式會在同一個位置產生 `SimpleAdd.asm`。

### 翻譯整個資料夾

```bash
python VMTranslator.py 路徑/資料夾
```

程式會讀取資料夾內所有 `.vm` 檔案，依檔名排序後合併輸出為同名的 `.asm` 檔案。

資料夾模式會執行 Bootstrap 初始化，因此多檔案程式應包含定義 `Sys.init` 的 VM 程式。

## 測試範例

建立 `SimpleAdd.vm`，內容如下：

```text
push constant 7
push constant 8
add
```

執行：

```bash
python VMTranslator.py SimpleAdd.vm
```

成功後會產生 `SimpleAdd.asm`，可使用 nand2tetris 的 Hack CPU Emulator 或相關工具進一步測試。

## 注意事項

- 單一檔案模式不會自動執行 Bootstrap 初始化。
- 資料夾模式會自動呼叫 `Sys.init`。
- 請確認輸入路徑正確，且資料夾內含有 VM 檔案。
- 建議使用 nand2tetris 官方 Project 7、Project 8 測試案例驗證輸出結果。
