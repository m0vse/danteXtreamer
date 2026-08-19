# Hardware-in-the-loop validation

The first test suite will cover:

1. passive MLN2 connector, power, reset/startup, clock, and lane
   characterisation in both Yamaha 01X and i88X;
2. current-limited replacement power and reset behavior outside the host;
3. MCLK/SCLK/LRCLK/MUTE capture and lock transition;
4. read-only identity/status through the confirmed control interface;
5. safe fit/startup in the selected first Yamaha target;
6. deterministic Yamaha channel-ID mapping in both directions;
7. XDante/AES67 interoperability at 48 kHz/24-bit;
8. a 30-minute discontinuity/sample-slip baseline;
9. repetition of the target-specific compatibility matrix on the other Yamaha
   device before both are declared supported.

Raw packet traces, logic-analyser captures, and device dumps belong under the
ignored `captures/` tree unless sanitised and cleared for redistribution.
