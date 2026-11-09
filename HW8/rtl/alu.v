// alu.v -- 8-bit combinational ALU (demo design for the EDA flow)
module alu #(
    parameter W = 8
) (
    input  wire [W-1:0] a,
    input  wire [W-1:0] b,
    input  wire [2:0]   op,
    output reg  [W-1:0] y
);
    always @* begin
        case (op)
            3'd0: y = a + b;          // ADD
            3'd1: y = a - b;          // SUB
            3'd2: y = a & b;          // AND
            3'd3: y = a | b;          // OR
            3'd4: y = a ^ b;          // XOR
            3'd5: y = a << b[2:0];    // SHL
            3'd6: y = a >> b[2:0];    // SHR
            default: y = {W{1'b0}};   // NOP
        endcase
    end
endmodule
