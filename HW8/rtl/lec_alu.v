// lec_alu.v -- miter for combinational equivalence checking (LEC)
module lec_alu (
    input  wire [7:0] a,
    input  wire [7:0] b,
    input  wire [2:0] op,
    output wire       mismatch
);
    wire [7:0] y_impl, y_ref;

    alu     u_impl (.a(a), .b(b), .op(op), .y(y_impl));
    alu_ref u_ref  (.a(a), .b(b), .op(op), .y(y_ref));

    assign mismatch = (y_impl !== y_ref);
endmodule
