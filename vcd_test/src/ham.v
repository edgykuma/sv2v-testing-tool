module hamFix(clock, ham, fixed);
    input  clock;
    input  [15:1] ham;
    output [15:1] fixed;

    reg [15:1] fixedAsync, fixed_r;
    assign fixed = fixed_r;
    wire p1, p2, p3, p4;
    wire [3:0] parity;
    assign parity = {p4, p3, p2, p1};
    assign p1 = ham[1] ^ ham[3] ^ ham[5] ^ ham[7] ^ ham[9] ^ ham[11] ^ ham[13] ^
                ham[15];
    assign p2 = ham[2] ^ ham[3] ^ ham[6] ^ ham[7] ^ ham[10] ^ ham[11] ^
                ham[14] ^ ham[15];
    assign p3 = ham[4] ^ ham[5] ^ ham[6] ^ ham[7] ^ ham[12] ^ ham[13] ^
                ham[14] ^ ham[15];
    assign p4 = ham[8] ^ ham[9] ^ ham[10] ^ ham[11] ^ ham[12] ^ ham[13] ^
                ham[14] ^ ham[15];

    always @* begin
        fixedAsync = ham;
        if (parity != 4'b0000)                  // Errors to fix
            fixedAsync[parity] = ~ham[parity];  // Flip bit
    end

    always @(posedge clock) begin
        fixed_r <= fixedAsync;
    end

endmodule
