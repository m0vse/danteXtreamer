# EasyEDA schematic source

`danteXtreamer_revA_preliminary.json` is a generated, multi-sheet EasyEDA
Standard document intended for import into EasyEDA Pro 2.2.x. It embeds the
EasyEDA library symbols, LCSC identifiers, and PCB-package bindings for the
selected JLCPCB-assembly parts.

Import it using **EasyEDA Pro > File/Start page > Import > EasyEDA Standard**,
inspect all import warnings, run ERC, and then save it as a native local EasyEDA
Pro project. Do not order a PCB from this preliminary source.

The schematic deliberately treats the two module connectors differently from
ordinary JLC parts:

- `J1`, KEL `8831E-100-170L`, is marked DNI/customer supplied. The user has
  suitable Yamaha connectors and plans to hand-solder one.
- `X1`, the A203 124-pin 0.8 mm Mini-PCI socket, is also initially DNI. Matching
  JLC catalogue candidates had zero assembly stock on 2026-08-19. A verified
  socket may instead be consigned to JLC or fitted manually. Do not release its
  PCB footprint until keying, insertion height, retention, and chassis/module
  clearance have been checked. The 01X is known to have ample space above the
  PCB, so its socket height is not expected to be restrictive; the mating plane,
  standoff geometry, and i88X clearance still need verification.

The Ethernet page is intentionally a design hold. The A203 hardware manual
does not establish a supported PHY/reference design, PHY I/O voltage, RGMII
delay ownership, straps, magnetics, or layout. Selecting a plausible PHY would
therefore invent unsupported hardware behavior.

## Regeneration

Run:

```powershell
python hardware\easyeda\generate_schematic.py
```

The generator downloads current EasyEDA component-library records into the
ignored `hardware/easyeda/.cache/` directory and embeds them in the generated
JSON. `jlc-parts.csv` is an auditable selection/stock snapshot; recheck every
part in the JLC parts search immediately before ordering.

The generated source is preliminary in three distinct senses:

1. connector symbols preserve the complete pin matrices, but their production
   footprints are not released;
2. the USB block captures the proven legacy pin relationship but does not claim
   that new FX2LP firmware or FPGA timing is complete;
3. regulator topology and FPGA package decoupling are captured, while host and
   A203 current budgets, eFuse setting, clock conditioning, safe output-enable
   circuitry, and the Ethernet PHY still require measurements/vendor input.
