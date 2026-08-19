# EasyEDA hardware source

The first generated EasyEDA Standard JSON attempt has been withdrawn. It used
inline generated symbols and produced an unacceptable schematic layout. Do not
use commit `e01c839` as an electrical-design source.

The replacement must be drafted as a native EasyEDA Pro project using reusable
devices from EasyEDA libraries:

- place normal components by their EasyEDA/LCSC library device identifiers;
- use the existing AudioXtreamer KEL connector device through the Eagle library
  import under `library-import/`;
- use an EasyEDA library Mini-PCI device for the A203 socket, initially
  `C9900276972` or `C9900177431`, after footprint/height verification;
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

The next schematic revision must be reviewed visually in EasyEDA Pro and pass
ERC before it is committed as the project schematic.
