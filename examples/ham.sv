/* ham.sv
 * A quick and dirty Hamming encoding bit vector corrector module. Used as a
 * part of an 18341 homework, which we will use as an example input to the sv2v
 * testing suite.
 *
 * This code is property of Carnegie Mellon University's 18341 course.
 *
 * Author: Edric Kusuma
 *****************************************************************************/
`default_nettype none

module hamFix(
    input logic clock,          // posedge
    input logic [15:1] ham,     // 15-bit hamming encoding bit vector
    output logic [15:1] fixed); // the corrected bit vector

    logic [15:1] fixedAsync;
    logic p1, p2, p3, p4;
    logic [3:0] parity;
    assign parity = {p4, p3, p2, p1};
    assign p1 = ham[1] ^ ham[3] ^ ham[5] ^ ham[7] ^ ham[9] ^ ham[11] ^ ham[13] ^
                ham[15];
    assign p2 = ham[2] ^ ham[3] ^ ham[6] ^ ham[7] ^ ham[10] ^ ham[11] ^
                ham[14] ^ ham[15];
    assign p3 = ham[4] ^ ham[5] ^ ham[6] ^ ham[7] ^ ham[12] ^ ham[13] ^
                ham[14] ^ ham[15];
    assign p4 = ham[8] ^ ham[9] ^ ham[10] ^ ham[11] ^ ham[12] ^ ham[13] ^
                ham[14] ^ ham[15];

    always_comb begin
        fixedAsync = ham;
        if (parity != 4'b0000)                  // Errors to fix
            fixedAsync[parity] = ~ham[parity];  // Flip bit
    end

    always_ff @(posedge clock)
        fixed <= fixedAsync;

endmodule: hamFix
