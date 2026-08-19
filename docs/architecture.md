# Architecture baseline

## Scope and system boundary

The A203 terminates the XDante/AES67 network-audio function. The core product is
therefore a hardware integration around three boundaries:

1. **Network side:** the A203's Ethernet MAC/PHY-facing signals and the external
   network components required by the vendor's reference design.
2. **Audio side:** synchronous I2S/TDM data, word/bit/master clocks, and the mute
   indication between the A203 and the local audio subsystem.
3. **Control side:** reset plus a vendor-confirmed UART, SPI, I2C, or other
   configuration path.

There is no Windows streaming path in the core design. A desktop utility may
eventually configure or diagnose the product, but it would not carry the A203's
XDante/AES67 media stream.

## Logical components

### A203 carrier integration

The carrier supplies 3.3 V, grounding, reset, connector mechanics, and any
external Ethernet PHY/magnetics required by the confirmed reference design.
Power sequencing, rail current, reset timing, PHY choice, and strap requirements
remain blocking questions; the manual does not provide enough information for a
schematic freeze.

### Serial-audio adapter

The adapter converts the product's local audio representation to the A203's
serial-audio contract:

- 32-bit slots;
- 24-bit or 16-bit samples left-aligned and zero-padded;
- sampling on the rising SCLK edge and output changes on the falling edge;
- I2S or TDM4/8/16, with LRCLK edge polarity configurable somewhere outside the
  supplied manual.

The implementation technology is intentionally open. An audio DSP, MCU with
sufficient serial-audio peripherals, or FPGA may be appropriate after lane
mapping and clock-role measurements. The legacy Xilinx ISE/Spartan-6 design is
not inherited by default.

### Control adapter

All module control will sit behind a narrow interface such as discovery,
read-only status, configuration transaction, and reset. No register addresses
or packet formats from the BF01 examples are promoted into this interface until
Audiocom confirms that they apply to the A203 and may be used.

### Diagnostics and validation

Diagnostics should record configuration, clock role, sample rate, mute/lock
state, route identity, packet/network observations, channel map, error counters,
and run duration. Hardware captures and vendor dumps stay out of source control
when they contain proprietary material or device identifiers.

### USB bridge hardware provision

The carrier architecture includes a USB 2.0 High-Speed device path even though
its compatibility firmware may follow later. The board must reserve:

- a USB device connector, ESD protection, VBUS detection, and controlled-
  impedance D+/D- routing;
- a bridge processing footprint or module interface capable of sustained
  high-speed USB, multichannel serial audio, bounded buffering, and firmware
  update/debug;
- access to the confirmed A203 audio lanes and MCLK/SCLK/LRCLK so the bridge can
  share or measure the audio clock domain;
- independently controllable bridge power/reset so an unprogrammed or
  unpopulated bridge cannot load A203 signals or disturb native network audio;
- clock/audio/reset test points and enough non-volatile storage/RAM for the
  eventual implementation.

Exact silicon is not selected. A high-speed USB MCU, FPGA plus USB controller,
or similar solution remains valid if it meets the measured lane and clocking
needs. See `../hardware/usb-bridge-requirements.md`.

## Clocking model

The manual says the A203 has an onboard VCXO, always outputs MCLK, and can lock
its generated audio clocks to an external clock. It also discusses LRCLK_IN and
SCLK_IN, but the pin table names pin 68 `EXTERNL_CLK` and does not explicitly map
that pin to `SCLK_IN`. Until confirmed, the following are design constraints:

- treat the A203 as serial-audio clock master for initial bring-up;
- do not drive any clock input until its pin, voltage, and mode are confirmed;
- capture MCLK, SCLK, LRCLK, and MUTE together to establish actual phase and
  lock behavior;
- put sample-rate conversion or drift management at an explicit boundary if a
  later asynchronous source, including USB, cannot share the A203 clock.

## USB compatibility bridge

The bridge is included in the hardware plan but remains a peer of the local
audio subsystem, not the network transport:

```text
existing AudioXtreamer host software
        | custom USB/WinUSB stream
optional USB bridge (packing, buffering, clock-domain control)
        | A203 serial audio (I2S/TDM)
       A203
        | XDante/AES67 network
```

Compatibility firmware requires the missing legacy FX2 descriptors/firmware
behavior to be recovered or separately specified. The bridge must not copy the
legacy output-pacing scheme without solving its documented underrun/
resynchronization problems. Hardware may be fitted and safely held inactive
before that firmware exists. Details and gates are in `usb-bridge.md`.

## First integration milestone

**Goal:** prove one stable bidirectional A203 network-audio route at the manual's
clearly advertised 48 kHz, 24-bit operating point using a vendor-confirmed
serial-audio mode.

Entry criteria:

- confirmed carrier/reference schematic requirements and maximum 3.3 V load;
- confirmed PHY/network connection and reset/power sequence;
- confirmed A203 control interface and a safe way to select/read the test mode;
- confirmed serial-audio lane and channel ordering for the chosen mode.

Pass criteria:

- the module powers and resets without exceeding limits;
- clocks and MUTE/lock behavior match the confirmed configuration;
- a reference XDante/AES67 endpoint can send and receive the selected channels;
- an impulse/channel-ID pattern proves direction and channel order;
- a 30-minute run shows no audible discontinuity or observed sample slip;
- the exact hardware, firmware, configuration, PTP state, and measurements are
  recorded in a reproducible test report.

Scaling to 32x32, 96 kHz, additional modes, or enabling USB compatibility
firmware follows only after this baseline passes. USB-capable hardware may
already be present during the baseline but must remain electrically benign.
