# Hardware-in-the-loop validation

The first test suite will cover:

1. current-limited power and reset behavior;
2. MCLK/SCLK/LRCLK/MUTE capture and lock transition;
3. read-only identity/status through the confirmed control interface;
4. deterministic impulse/channel-ID mapping in both directions;
5. XDante/AES67 interoperability at 48 kHz/24-bit;
6. a 30-minute discontinuity/sample-slip baseline.

Raw packet traces, logic-analyser captures, and device dumps belong under the
ignored `captures/` tree unless sanitised and cleared for redistribution.
