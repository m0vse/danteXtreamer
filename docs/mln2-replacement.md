# Yamaha MLN2 replacement target

## Product intent

`danteXtreamer` is intended to replace the MLN2 card inside both:

- Yamaha 01X digital mixing studio;
- Yamaha i88X audio interface.

The original MLN2/mLAN network function is replaced by the A203's
XDante/AES67 network endpoint. The Yamaha device should continue to exchange
audio and required control/clock state through its internal card interface,
without depending on a Windows PC to transport network audio.

This intent comes from the project requirements. The supplied A203 manual does
not mention Yamaha, MLN2, 01X, or i88X and does not establish compatibility.

Local Yamaha 01X and i88X service manuals are available under the ignored
`vendor/yamaha/` tree and are recorded by hash in `provenance.md`. Their presence
supports engineering reference work but does not grant redistribution rights.

## Compatibility boundary

```text
Yamaha host
  power, reset, clocks, audio lanes, mute/status, control, mechanics
        |
MLN2 compatibility layer
  host protection, level/timing adaptation, lane mapping, startup behavior
        |
A203 serial-audio/control/network integration
        |
XDante/AES67 Ethernet
```

The replacement must be evaluated across five independent dimensions:

1. **Mechanical:** connector position, card outline, mounting holes, keep-outs,
   cable access, airflow, and serviceability.
2. **Electrical:** rails, current/inrush, logic levels, pin direction, pulls,
   reset sequencing, unpowered behavior, and fault containment.
3. **Audio/clock:** lane and slot order, sample format, clock master/slave role,
   supported rates, mute transitions, latency, and loss-of-lock behavior.
4. **Host control:** any presence detection, identification, startup handshake,
   register traffic, MIDI/control traffic, firmware/version expectation, and
   recovery behavior required by the Yamaha host.
5. **Network function:** stable XDante/AES67 transmit/receive operation with the
   Yamaha channels mapped predictably.

## Two target profiles

The 01X and i88X are separate target profiles. The project should share a PCB
and firmware where measurements prove that is safe, but must permit different:

- connector or harness population;
- power/reset straps;
- audio lane/slot maps and channel counts;
- clock configuration;
- host identification/startup behavior;
- test expectations and product labels.

No signal should be assumed identical merely because both devices use an MLN2
card. A support claim requires the target-specific test matrix to pass in the
actual device.

## Characterisation before connection

1. Photograph and dimension the original card, host bay, connector, mounting,
   shields, cables, and component keep-outs for both products.
2. Use both local service manuals as references and build connector/pin tables
   from documentation plus continuity measurements. Record confidence and
   source for every pin.
3. With the original MLN2 installed, passively capture rails, reset, clocks,
   mute/status, and startup activity. Do not drive an unknown host signal.
4. Use deterministic audio patterns to derive lane, slot, direction, and channel
   mapping at each supported rate.
5. Compare 01X and i88X results before freezing a common carrier.

## Staged definition of done

### Characterisation milestone

- complete mechanical and connector records for both devices;
- voltage/direction/startup evidence for every used host pin;
- confirmed audio/clock maps and a list of unresolved signals;
- a safe bench adapter or interposer for prototype testing.

### First installed audio milestone

- prototype fits and powers safely in one target device;
- Yamaha host starts normally and reports no new card/interface fault;
- one deterministic bidirectional 48 kHz/24-bit channel group passes between
  the Yamaha host and a reference XDante/AES67 endpoint;
- startup, stop, network loss, clock loss, and recovery cause no unsafe drive or
  damaging contention;
- measurements and firmware/hardware versions are reproducible.

### Replacement milestone

- full intended channel mapping and supported rates pass on both 01X and i88X;
- mechanical closure, thermal behavior, EMC/pre-compliance, and long-run audio
  stability pass;
- any target-specific assembly/firmware configuration is unmistakable;
- USB compatibility, if enabled, cannot interfere with native A203 operation.
