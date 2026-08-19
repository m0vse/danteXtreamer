# EasyEDA hardware source

The first generated EasyEDA Standard JSON attempt has been withdrawn. It used
inline generated symbols and produced an unacceptable schematic layout. Do not
use commit `e01c839` as an electrical-design source.

The replacement must be drafted as a native EasyEDA Pro project using reusable
devices from EasyEDA libraries:

- place normal components by their EasyEDA/LCSC library device identifiers;
- use the existing AudioXtreamer KEL connector device through the Eagle library
  import under `library-import/`;
- use the EasyEDA/LCSC `MINI_PCI-124P` device `C9900003781` for the A203
  socket. It has contacts 1–124 and two mechanical latch pads numbered 0;
- do not use exploded, inline, or generator-created schematic symbols;
- use conventional wires, buses, power ports, and hierarchical/net ports rather
  than attaching a visible net label to every device pin.

## Yamaha connector library

The original AudioXtreamer Eagle schematic embeds a complete two-gate device
for KEL `8831E-100-170L`, including its footprint and 102 pin/pad mappings (100
contacts plus two shell pads). `library-import/KEL_8831E-100-170L.lbr` extracts
that existing library without changing its geometry.

EasyEDA Pro supports direct Eagle library import. Use **File > Import > EAGLE**,
select library extraction, and save the resulting device in the EasyEDA project
or personal library. See `library-import/README.md` for verification notes.

Regenerate the import file from the local AudioXtreamer checkout with:

```powershell
.\tools\extract-kel-eagle-library.ps1
```

The schematic must be reviewed visually in EasyEDA Pro and pass ERC before it
is treated as fabrication-ready or used to update a PCB.

## A203 socket library

`library-import/EasyEDA-C9900003781.json` is an unmodified EasyEDA Pro library
search response captured on 2026-08-19. The selected device UUID is
`b3cf1af8fca444479b33a1f2f2fb2aaa`; its symbol and footprint UUIDs are
`26c64d2176bc4ad9b45b12f2a7fa9e5b` and
`d106f2bbecb5493b8c11bc4fd67a281e`. The snapshot is retained because the part
is available through the online EasyEDA/LCSC library but not the installed
offline `easyeda-std.elib` database.

The footprint is suitable for schematic development, but physical connector
height, keying, latch geometry, and the A203 mating datum still require a
measurement against the module before fabrication.
