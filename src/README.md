# Source layout

Implementation begins only after the Yamaha 01X/i88X MLN2 boundaries, target
controller, and A203 control interface are confirmed.

- `control/` holds hardware-independent A203 control abstractions and protocol
  tests based on authorised documentation.
- `platform/` holds board/MCU/OS-specific UART, SPI, I2C, GPIO, timing, and
  storage adapters, including explicit 01X and i88X target profiles.
- `usb-bridge/` holds optional AudioXtreamer host-protocol compatibility and
  must remain independent of core A203 integration.

Serial-audio processing logic may later live in a technology-specific sibling
tree (for example `firmware/`, `dsp/`, or `fpga/`) once measurements justify the
choice. No legacy FPGA tree is pre-created or imported.
