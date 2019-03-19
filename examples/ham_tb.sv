/* ham_tb.sv
 * The testbench for the hamFix module. Can be used to verify the behavior of
 * both the SystemVerilog and Verilog descriptions. Because this TB is written
 * in SystemVerilog, it will have to be compiled as such (i.e. using the
 * `-sverilog` flag in VCS).
 *
 * This code is property of Carnegie Mellon University's 18341 course.
 *
 * Author: Edric Kusuma
 *****************************************************************************/
`default_nettype none

module hamFix_test;
    logic clock, hasErrors;
    logic [15:1] ham, fixed, enc;
    logic [12:1] i;

    hamFix DUT(.*);

    initial begin
        clock = 0;
        forever #5 clock = ~clock;
    end

    function logic [15:1] hamEncode(
        input logic [11:1] data
    );
        logic p1, p2, p4, p8;
        logic [15:1] encoded;

        p1 = data[1] ^ data[2] ^ data[4] ^ data[5] ^ data[7] ^
             data[9] ^ data[11];
        p2 = data[1] ^ data[3] ^ data[4] ^ data[6] ^ data[7] ^
             data[10] ^ data[11];
        p4 = data[2] ^ data[3] ^ data[4] ^ data[8] ^ data[9] ^
             data[10] ^ data[11];
        p8 = data[5] ^ data[6] ^ data[7] ^ data[8] ^ data[9] ^
             data[10] ^ data[11];

        encoded[1] = p1;
        encoded[2] = p2;
        encoded[3] = data[1];
        encoded[4] = p4;
        encoded[5] = data[2];
        encoded[6] = data[3];
        encoded[7] = data[4];
        encoded[8] = p8;
        encoded[9] = data[5];
        encoded[10] = data[6];
        encoded[11] = data[7];
        encoded[12] = data[8];
        encoded[13] = data[9];
        encoded[14] = data[10];
        encoded[15] = data[11];

        return encoded;

    endfunction

    function logic [15:1] hamDecode (
        input logic [15:1] ham
    );
        logic [15:1] fixed;
        logic p1, p2, p3, p4;
        logic [3:0] parity = {p4, p3, p2, p1};

        p1 = ham[1] ^ ham[3] ^ ham[5] ^ ham[7] ^ ham[9] ^ ham[11] ^
             ham[13] ^ ham[15];
        p2 = ham[2] ^ ham[3] ^ ham[6] ^ ham[7] ^ ham[10] ^ ham[11] ^
             ham[14] ^ ham[15];
        p3 = ham[4] ^ ham[5] ^ ham[6] ^ ham[7] ^ ham[12] ^ ham[13] ^
             ham[14] ^ ham[15];
        p4 = ham[8] ^ ham[9] ^ ham[10] ^ ham[11] ^ ham[12] ^ ham[13] ^
             ham[14] ^ ham[15];

        fixed = ham;
        if (parity != 4'b0000)
            fixed[parity] = ~ham[parity];

        return fixed;

    endfunction

    initial begin
        hasErrors = 0;
        @(posedge clock);
        for (i = 12'd0; i < 12'b1000_0000_0000; i++) begin
            enc = hamEncode(i[11:1]);
            ham <= enc;
            @(posedge clock);
            // Delay of 1 to allow signals to settle
            #1 assert (fixed == hamDecode(enc)) else begin
                $error("Error: expected(%b) actual(%b) for input(%b)",
                    hamDecode(enc), fixed, enc);
                hasErrors = 1;
            end
        end

        @(posedge clock);
        if (!hasErrors)
            $display("All tests passed!");
        #10 $finish;
    end

endmodule: hamFix_test
