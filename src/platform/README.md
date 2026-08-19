# Platform adapters

Reserved for target-specific power/reset GPIO, UART/SPI/I2C transport, monotonic
time, persistence, and diagnostics.

Keep platform APIs narrow enough that protocol tests can run without hardware.
Do not expose raw vendor SDK types in hardware-independent control code.
