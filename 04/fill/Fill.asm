// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// 初始化：設定螢幕起點 (RAM[16] = 16384)
@16384
D=A
@16
M=D

// 初始化：設定螢幕大小為 8192 字組 (RAM[17] = 8192)
@8192
D=A
@17
M=D

// 初始化：偏移計數器歸零 (RAM[18] = 0)
@18
M=0

// 檢查是否已畫完全部 8192 個字組，畫完就跳到行號 36 重設
@18
D=M
@17
D=D-M
@36
D;JEQ

// 讀取鍵盤狀態：若沒按鍵 (等於0) 跳到行號 27 塗白
@24576
D=M
@27
D;JEQ

// 塗黑：把目前像素位址填入 -1，完成後跳到行號 32
@16
D=M
@18
A=D+M
M=-1
@32
0;JMP

// 塗白：把目前像素位址填入 0
@16
D=M
@18
A=D+M
M=0

// 計數器加 1，並跳回行號 10 處理下一個像素字組
@18
M=M+1
@10
0;JMP

// 螢幕整面更新完畢，跳回開頭 (行號 0) 重新監聽
@0
0;JMP
