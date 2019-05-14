/* ham.sv
 * A quick and dirty Hamming encoding bit vector corrector module. We will use
 * this as an example input to the sv2v testing tool.
 *
 * Author: Edric Kusuma
 *****************************************************************************/
`default_nettype none

module hamFix(
    input logic clock,          // posedge
    input logic [15:1] ham,     // 15-bit hamming encoding bit vector
    output logic [15:1] fixed); // the corrected bit vector

    logic [15:1] fixedAsync;
    logic p1, p2, p4, p8;
    logic [3:0] syndrome;
    assign p1 = ham[1];
    assign p2 = ham[2];
    assign p4 = ham[4];
    assign p8 = ham[8];
    assign syndrome = {p8, p4, p2, p1};

    always_comb begin
        fixedAsync = ham;
        if (syndrome != 4'b0000)                    // Errors to fix
            fixedAsync[syndrome] = ~ham[syndrome];  // Flip bit
    end

    always_ff @(posedge clock)
        fixed <= fixedAsync;

endmodule: hamFix
