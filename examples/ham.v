/* ham.v
 * The (hand-transpiled) Verilog equivalent to the SystemVerilog hamFix module.
 *
 * Author: Edric Kusuma
 *****************************************************************************/
module hamFix(clock, ham, fixed);
    input  clock;
    input  [15:1] ham;
    output [15:1] fixed;

    reg [15:1] fixedAsync, fixed_r;
    assign fixed = fixed_r;
    wire p1, p2, p4, p8;
    wire [3:0] syndrome;
    assign syndrome = {p8, p4, p2, p1};
    assign p1 = ham[1];
    assign p2 = ham[2];
    assign p4 = ham[4];
    assign p8 = ham[8];

    always @* begin                 // always_comb
        fixedAsync = ham;
        if (syndrome != 4'b0000)                    // Errors to fix
            fixedAsync[syndrome] = ~ham[syndrome];  // Flip bit
    end

    always @(posedge clock) begin   // always_ff
        fixed_r <= fixedAsync;
    end

endmodule
