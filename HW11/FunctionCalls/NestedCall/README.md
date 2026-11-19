# NestedCall 範例

此資料夾展示跨 VM 函式呼叫與遞迴呼叫。

- `Sys.vm`：程式入口，負責呼叫 `Main.fibonacci`。
- `Main.vm`：以遞迴方式計算 Fibonacci 數列。

使用整個資料夾作為翻譯器輸入時，會自動加入 Bootstrap，並依檔名順序合併 VM 檔案。
