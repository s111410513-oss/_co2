// alu_ref.v -- independently coded golden model used for equivalence checking
// (same function, different coding style: shift/add built from explicit logic)
module alu_ref #(
    parameter W = 8
) (
    input  wire [W-1:0] a,
    input  wire [W-1:0] b,
    input  wire [2:0]   op,
    output reg  [W-1:0] y
);
    reg [W:0] sum;
    reg [W:0] dif;
    integer   i;

    always @* begin
        sum = {1'b0, a} + {1'b0, b};
        dif = {1'b0, a} - {1'b0, b};
        y   = {W{1'b0}};
        case (op)
            3'd0: for (i = 0; i < W; i = i + 1) y[i] = sum[i];
            3'd1: for (i = 0; i < W; i = i + 1) y[i] = dif[i];
            3'd2: y = ~(~a | ~b);                  // AND via De Morgan
            3'd3: y = ~(~a & ~b);                  // OR  via De Morgan
            3'd4: y = (a | b) & ~(a & b);          // XOR via AOI
            3'd5: y = a << b[2:0];
            3'd6: y = a >> b[2:0];
            default: y = {W{1'b0}};
        endcase
    end
endmodule
