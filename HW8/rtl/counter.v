// counter.v -- 8-bit up/down counter with load and zero flag
module counter #(
    parameter W = 8
) (
    input  wire         clk,
    input  wire         rst_n,   // asynchronous active-low reset
    input  wire         en,      // count enable
    input  wire         up,      // 1 = up, 0 = down
    input  wire         ld,      // synchronous load
    input  wire [W-1:0] load,
    output reg  [W-1:0] q,
    output wire         zero
);
    assign zero = (q == {W{1'b0}});

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n)     q <= {W{1'b0}};
        else if (ld)    q <= load;
        else if (en)    q <= up ? q + 1'b1 : q - 1'b1;
    end
endmodule
