// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)

// Mult.asm: R2 = R0 * R1 (重複累加法)

@2
M=0       // R2 歸零 (Result = 0)

// --- Loop 開頭 (ROM[2]) ---
@0
D=M
@14
D;JLE     // 若 R0 <= 0 則跳出迴圈至 ROM[14]

@1
D=M
@2
M=D+M     // R2 += R1 (累加)

@0
M=M-1     // R0 -= 1  (計數器減 1)

@2
0;JMP     // 跳回 Loop 開頭 (ROM[2])

// --- End (ROM[14]) ---
@14
0;JMP     // 無限迴圈結束 (Trap)
