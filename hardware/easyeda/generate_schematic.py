#!/usr/bin/env python3
"""Generate the preliminary danteXtreamer EasyEDA Standard schematic.

EasyEDA Pro can import the resulting multi-sheet JSON document.  Library data
for JLC/LCSC parts is downloaded from EasyEDA and embedded in the document, so
the imported symbols retain their supplier and footprint bindings.
"""

from __future__ import annotations

import csv
import gzip
import json
import re
import urllib.request
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
CACHE = HERE / ".cache"
OUTPUT = HERE / "danteXtreamer_revA_preliminary.json"
MANIFEST = HERE / "jlc-parts.csv"


PARTS = {
    "C39313": ("XC6SLX16-2FTG256C", "FPGA", "Extended", 1312),
    "C9926": ("CY7C68013A-100AXC", "optional USB 2.0 bridge", "Extended", 662),
    "C165948": ("TYPE-C-31-M-12", "USB-C receptacle", "Extended", 418864),
    "C7519": ("USBLC6-2SC6", "USB ESD protection", "Basic", 38113),
    "C6478": ("AT24C128C-SSHM-T", "FX2LP boot EEPROM", "Extended", 43479),
    "C15643": ("X322524MSB4SI", "24 MHz FX2LP crystal", "Extended", 31675),
    "C82344": ("W25Q32JVSSIQ", "FPGA configuration flash", "Extended", 8276),
    "C43590": ("TPS62130RGTR", "3 A buck regulator", "Extended", 28008),
    "C133191": ("SMMS0420-2R2M", "2.2 uH buck inductor", "Extended", 9817),
    "C2869949": ("TPS7A2025PDBVR", "2.5 V auxiliary LDO", "Extended", 243),
    "C2149796": ("TPS22919DCKR", "USB-section load switch", "Extended", 45225),
    "C1852114": ("TLV803EA29DBZR", "reset supervisor", "Extended", 853),
    "C181295": ("TPS25942ARVCR", "host-input eFuse", "Extended", 3360),
    "C122228": ("INA180A1IDBVR", "host-current monitor", "Extended", 19773),
    "C500720": ("2512 20 mOhm 1%", "host-current shunt", "Extended", 3717),
    "C135822": ("74LVC1G157GW,125", "clock source selector", "Extended", 9597),
    "C113325": ("CDCLVC1102PWR", "clock fanout buffer", "Extended", 3520),
    "C282345": ("74LVC1G07GW,125", "open-drain reset driver", "Extended", 27968),
    "C23140": ("33R 0603 1%", "series termination", "Basic", 1000000),
    "C21189": ("0R 0603", "configuration link", "Basic", 1000000),
    "C25804": ("10k 0603 1%", "pull resistor", "Basic", 1000000),
    "C23186": ("5.1k 0603 1%", "USB-C CC resistor", "Basic", 1000000),
    "C4190": ("2.2k 0603 1%", "I2C pull-up", "Basic", 1000000),
    "C25803": ("100k 0603 1%", "feedback/pull resistor", "Basic", 1000000),
    "C25814": ("316k 0603 1%", "3.3 V feedback resistor", "Extended", 39327),
    "C23184": ("49.9k 0603 1%", "1.2 V feedback resistor", "Basic", 1000000),
    "C1525": ("100nF 0402", "decoupling capacitor", "Basic", 1000000),
    "C47339": ("470nF 0402", "FPGA decoupling capacitor", "Extended", 647270),
    "C15849": ("1uF 0603", "decoupling capacitor", "Basic", 1000000),
    "C1779": ("4.7uF 0805", "FPGA decoupling capacitor", "Basic", 1000000),
    "C15850": ("10uF 0805", "buck input capacitor", "Basic", 1000000),
    "C45783": ("22uF 0805", "buck output capacitor", "Basic", 1000000),
    "C48971041": ("100uF 10V polymer", "rail bulk capacitor", "Extended", 15653),
}


class Gids:
    def __init__(self) -> None:
        self.value = 1

    def new(self) -> str:
        value = f"ggeDX{self.value:07d}"
        self.value += 1
        return value


GID = Gids()


def load_lcsc(lcsc: str) -> dict:
    CACHE.mkdir(parents=True, exist_ok=True)
    cached = CACHE / f"{lcsc}.json"
    if cached.exists():
        payload = json.loads(cached.read_text(encoding="utf-8"))
    else:
        request = urllib.request.Request(
            f"https://easyeda.com/api/products/{lcsc}/components",
            headers={
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "Accept-Encoding": "gzip, deflate",
                "Referer": "https://easyeda.com/",
                "User-Agent": "Mozilla/5.0 Chrome/120.0 EasyEDA-import-generator",
            },
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            raw = response.read()
        if raw[:2] == b"\x1f\x8b":
            raw = gzip.decompress(raw)
        payload = json.loads(raw.decode("utf-8"))
        cached.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    if not payload.get("success"):
        raise RuntimeError(f"EasyEDA library lookup failed for {lcsc}: {payload}")
    return payload["result"]


def para_string(values: dict) -> str:
    return "`".join(str(item) for pair in values.items() for item in pair)


def replace_ids(shapes: list[str]) -> list[str]:
    mapping: dict[str, str] = {}

    def replacement(match: re.Match[str]) -> str:
        source = match.group(0)
        mapping.setdefault(source, GID.new())
        return mapping[source]

    return [re.sub(r"gge[A-Za-z0-9_-]+", replacement, shape) for shape in shapes]


def update_symbol_text(shape: str, pre: str, value: str) -> str:
    if not shape.startswith(("T~P~", "T~N~")):
        return shape
    fields = shape.split("~")
    try:
        index = fields.index("comment") + 1
    except ValueError:
        return shape
    fields[index] = pre if shape.startswith("T~P~") else value
    return "~".join(fields)


def pin_info(shape: str) -> tuple[str, str, float, float] | None:
    if not shape.startswith("P~"):
        return None
    segments = shape.split("^^")
    header = segments[0].split("~")
    detail = segments[3].split("~") if len(segments) > 3 else []
    if len(header) < 7:
        return None
    name = detail[4] if len(detail) > 4 else header[3]
    return header[3], name, float(header[4]), float(header[5])


class Sheet:
    def __init__(self, title: str, description: str = "") -> None:
        self.title = title
        self.description = description
        self.shape: list[str] = []

    def text(self, x: float, y: float, value: str, size: str = "9pt", color: str = "#000000") -> None:
        safe = value.replace("~", "-").replace("\n", " ")
        self.shape.append(
            f"T~L~{x}~{y}~0~{color}~Arial~{size}~~~~comment~{safe}~1~start~{GID.new()}~0~"
        )

    def label(self, x: float, y: float, net: str, color: str = "#0000FF") -> None:
        safe = net.replace("~", "-").replace(" ", "_")
        self.shape.append(
            f"N~{x}~{y}~0~{color}~{safe}~{GID.new()}~start~{x}~{y}~Arial~7pt~0"
        )

    def no_connect(self, x: float, y: float) -> None:
        self.shape.append(
            f"O~{x}~{y}~{GID.new()}~M-4 -4L4 4M4 -4L-4 4~#33cc33~0"
        )

    def lcsc(
        self,
        lcsc: str,
        pre: str,
        value: str,
        x: float,
        y: float,
        subpart: int | None = None,
    ) -> dict[str, list[tuple[float, float, str]]]:
        result = load_lcsc(lcsc)
        source = result["subparts"][subpart - 1]["dataStr"] if subpart else result["dataStr"]
        if isinstance(source, str):
            source = json.loads(source)
        head = source["head"]
        raw_shapes = source["shape"]
        source_x, source_y = float(head.get("x", 0)), float(head.get("y", 0))
        off_x, off_y = x - source_x, y - source_y
        rewritten = replace_ids(raw_shapes)
        rewritten = [update_symbol_text(item, pre, value) for item in rewritten]
        c_para = dict(head.get("c_para", {}))
        c_para.update({"pre": pre, "name": value, "Supplier Part": lcsc, "Supplier": "LCSC"})
        parent = (
            f"LIB~{off_x}~{off_y}~{para_string(c_para)}~0~{head.get('importFlag', 0)}~{GID.new()}~"
            f"{head.get('puuid', '')}~{head.get('uuid', result.get('uuid', ''))}~0~~yes~yes"
        )
        self.shape.append(parent + "#@$" + "#@$".join(rewritten))
        pins: dict[str, list[tuple[float, float, str]]] = defaultdict(list)
        for raw in raw_shapes:
            info = pin_info(raw)
            if info:
                number, name, px, py = info
                absolute = (px + off_x, py + off_y, name)
                pins[number].append(absolute)
                pins[name].append(absolute)
        return dict(pins)

    def custom_connector(
        self,
        pre: str,
        title: str,
        x: float,
        y: float,
        rows: list[tuple[int, str]],
    ) -> dict[int, tuple[float, float]]:
        children = [f"R~0~0~~~145~{len(rows) * 10 + 10}~#880000~1~0~#F6F6F6~{GID.new()}~0"]
        children.append(
            f"T~P~10~-15~0~#000080~Arial~9pt~~~~comment~{pre}~1~start~{GID.new()}~0~"
        )
        children.append(
            f"T~N~10~-5~0~#000080~Arial~7pt~~~~comment~{title}~1~start~{GID.new()}~0~"
        )
        points: dict[int, tuple[float, float]] = {}
        for index, (number, name) in enumerate(rows):
            py = 10 + index * 10
            points[number] = (x - 20, y + py)
            children.append(
                f"P~show~0~{number}~-20~{py}~180~{GID.new()}~0^^-20~{py}^^M -20 {py} h 20~#880000"
                f"^^1~4~{py + 3}~0~{name}~start~~~#0000FF^^1~-6~{py - 1}~0~{number}~end~~~#0000FF"
                f"^^0~-3~{py}^^0~M 0 {py - 3} L 3 {py} L 0 {py + 3}"
            )
        attributes = para_string(
            {
                "pre": pre,
                "name": title,
                "package": "PROVISIONAL_NO_FOOTPRINT",
                "Assembly": "DNI / customer supplied",
                "convert_to_pcb": "no",
                "add_into_bom": "no",
            }
        )
        self.shape.append(f"LIB~{x}~{y}~{attributes}~0~0~{GID.new()}~~~~0~~no~no#@$" + "#@$".join(children))
        return points

    def to_document(self) -> dict:
        data = {
            "head": {
                "docType": "1",
                "editorVersion": "6.5.23",
                "newgId": True,
                "c_para": {"project": "danteXtreamer", "revision": "Rev A preliminary"},
                "c_spiceCmd": None,
            },
            "canvas": "CA~1400~900~#FFFFFF~yes~#CCCCCC~5~1400~900~line~5~pixel~5~0~0",
            "shape": self.shape,
            "BBox": {"x": 0, "y": 0, "width": 1400, "height": 900},
            "colors": {},
        }
        return {
            "docType": "1",
            "title": self.title,
            "description": self.description,
            "dataStr": json.dumps(data, ensure_ascii=False, separators=(",", ":")),
        }


def read_csv(name: str) -> list[dict[str, str]]:
    with (ROOT / "hardware" / "interfaces" / name).open(encoding="utf-8", newline="") as source:
        return list(csv.DictReader(source))


def first_pin(pins: dict[str, list[tuple[float, float, str]]], key: str) -> tuple[float, float, str]:
    if key not in pins:
        raise KeyError(f"Pin {key!r} not found; available keys include {list(pins)[:20]}")
    return pins[key][0]


def label_all(sheet: Sheet, pins: dict[str, list[tuple[float, float, str]]], key: str, net: str) -> None:
    for px, py, _ in pins.get(key, []):
        sheet.label(px, py, net)


def two_pin(
    sheet: Sheet,
    lcsc: str,
    ref: str,
    value: str,
    x: float,
    y: float,
    net_1: str,
    net_2: str,
) -> None:
    pins = sheet.lcsc(lcsc, ref, value, x, y)
    label_all(sheet, pins, "1", net_1)
    label_all(sheet, pins, "2", net_2)


def overview_sheet() -> Sheet:
    sheet = Sheet("00 Overview and design holds", "Scope, assembly strategy, and unresolved vendor inputs")
    lines = [
        "danteXtreamer Rev A PRELIMINARY - Yamaha 01X/i88X MLN2 replacement",
        "Primary path: Yamaha serial audio/MIDI <-> Spartan-6 <-> Audiocom A203 Dante/AES67 module.",
        "Optional path: Cypress FX2LP USB 2.0 using the AudioXtreamer-compatible protocol; firmware may follow later.",
        "ASSEMBLY: J1 Yamaha KEL connector is DNI/customer supplied and intended for hand soldering.",
        "ASSEMBLY: X1 A203 124-pin 0.8 mm Mini-PCI socket may be consigned to JLC or hand fitted.",
        "MECHANICAL: 01X has ample height above the PCB; confirm socket keying, standoffs, insertion geometry, and i88X clearance.",
        "HOLD: Audiocom-approved Ethernet PHY/reference design is required; no PHY has been guessed.",
        "HOLD: measure Yamaha +5 V steady current, inrush, signal levels, clock ownership, and reset states.",
        "HOLD: obtain A203 current budget, reset timing, PHY timing/voltage, and TDM lane/control definitions.",
        "All JLC stock quantities in jlc-parts.csv are snapshots and must be rechecked when ordering.",
        "This source is intended for EasyEDA Pro: Import > EasyEDA Standard, then save as a local Pro project.",
        "NOT FABRICATION READY. Complete ERC, footprint verification, controlled-impedance design, and prototype review first.",
    ]
    for index, line in enumerate(lines):
        sheet.text(70, 80 + index * 42, line, "12pt" if index == 0 else "9pt", "#AA0000" if "HOLD:" in line or "NOT " in line else "#000000")
    return sheet


def connector_sheet(
    title: str,
    rows: list[dict[str, str]],
    number_key: str,
    signal_key: str,
    net_key: str,
    group_size: int,
    prefix: str,
    connector_title: str,
    net_resolver=None,
) -> Sheet:
    sheet = Sheet(title)
    sheet.text(50, 35, connector_title, "12pt")
    sheet.text(50, 55, "DNI/customer-supplied connector; symbol preserves every documented contact while the PCB footprint remains on hold.", "8pt", "#AA0000")
    grouped = [rows[index:index + group_size] for index in range(0, len(rows), group_size)]
    for part_index, group in enumerate(grouped, start=1):
        x = 70 + (part_index - 1) * 330
        y = 100
        connector_rows = [(int(row[number_key]), row[signal_key]) for row in group]
        points = sheet.custom_connector(f"{prefix}.{part_index}", connector_title, x, y, connector_rows)
        for row in group:
            number = int(row[number_key])
            net = (net_resolver(row) if net_resolver else row[net_key]).strip()
            px, py = points[number]
            if not net or net == "NC":
                sheet.no_connect(px, py)
            else:
                sheet.label(px, py, net)
    return sheet


def fpga_sheet(assignments: list[dict[str, str]]) -> Sheet:
    sheet = Sheet("03 FPGA, configuration and power", "XC6SLX16-2FTG256C partition and configuration")
    sheet.text(40, 30, "U1 XC6SLX16-2FTG256C (LCSC C39313) - all seven symbol units", "12pt")
    sheet.text(40, 50, "Bank assignment is provisional until ISE implementation and timing closure. M[1:0]=01 selects Master SPI.", "8pt", "#AA0000")
    by_ball = {row["ball"]: row["fpga_signal"] for row in assignments}
    positions = [(230, 270), (660, 270), (1060, 270), (230, 650), (620, 650), (910, 650), (1190, 650)]
    for subpart, (x, y) in enumerate(positions, start=1):
        pins = sheet.lcsc("C39313", f"U1.{subpart}", "XC6SLX16-2FTG256C", x, y, subpart=subpart)
        for ball, net in by_ball.items():
            if ball in pins:
                label_all(sheet, pins, ball, net)
        if subpart <= 4:
            for ball, net in {"C4": "+3V3_LOGIC", "T11": "+3V3_LOGIC", "N11": "GND"}.items():
                if ball in pins and ball not in by_ball:
                    label_all(sheet, pins, ball, net)
        if subpart == 5:
            config = {
                "T2": "FPGA_PROGRAM_N", "P13": "FPGA_DONE", "R3": "FPGA_INIT_N",
                "R11": "FPGA_CCLK", "P10": "FPGA_DIN", "T10": "FPGA_MOSI", "T3": "FPGA_CSO_N",
                "C14": "FPGA_TCK", "C12": "FPGA_TDI", "A15": "FPGA_TMS", "E14": "FPGA_TDO",
            }
            for ball, net in config.items():
                if ball in pins:
                    label_all(sheet, pins, ball, net)
        if subpart == 6:
            for key, locations in list(pins.items()):
                if not locations:
                    continue
                pin_name = locations[0][2]
                if pin_name == "VCCINT":
                    label_all(sheet, pins, key, "+1V2_FPGA")
                elif pin_name.startswith("VCC"):
                    label_all(sheet, pins, key, "+3V3_LOGIC")
        if subpart == 7:
            for key, locations in list(pins.items()):
                if locations and locations[0][2] == "GND":
                    label_all(sheet, pins, key, "GND")

    flash = sheet.lcsc("C82344", "U2", "W25Q32JVSSIQ", 1040, 90)
    flash_nets = {
        "1": "FPGA_CSO_N", "2": "FPGA_DIN", "3": "+3V3_LOGIC", "4": "GND",
        "5": "FPGA_MOSI", "6": "FPGA_CCLK", "7": "+3V3_LOGIC", "8": "+3V3_LOGIC",
    }
    for name, net in flash_nets.items():
        label_all(sheet, flash, name, net)
    sheet.text(970, 190, "Configuration flash wiring follows Spartan-6 Master SPI; verify symbol pin aliases during EasyEDA ERC.", "7pt")
    sheet.text(40, 830, "FPGA decoupling population is specified on the Power sheet from AMD UG393; do not reduce it from generic BGA practice.", "8pt", "#AA0000")
    return sheet


def usb_sheet(assignments: list[dict[str, str]]) -> Sheet:
    sheet = Sheet("04 Optional USB FX2LP", "Optional AudioXtreamer-compatible USB 2.0 hardware")
    sheet.text(40, 30, "Optional USB section - electrically isolatable and not required for the Yamaha-to-A203 path", "12pt")
    sheet.text(40, 50, "FX2LP is discontinued: C9926 was stocked at snapshot time, but buy-ahead and lifecycle risk remain.", "8pt", "#AA0000")
    fx = sheet.lcsc("C9926", "U3", "CY7C68013A-100AXC", 500, 390)

    exact = {
        "IFCLK": "USB_IFCLK", "RDY0/SLRD": "USB_SLRD_N", "RDY1/SLWR": "USB_SLWR_N",
        "CTL0/FLAGA": "USB_FLAGA", "CTL1/FLAGB": "USB_FLAGB", "CTL3": "USB_EZ_SOF",
        "PA0/INT0#": "USB_LSI_RDNCK", "PA1/INT1#": "USB_LSI_EN", "PA2/SLOE": "USB_SLOE_N",
        "PA4/FIFOADR0": "USB_FIFOADDR0", "PA5/FIFOADR1": "USB_FIFOADDR1", "PA6/PKTEND": "USB_PKTEND_N",
        "PA7/FLAGD/SLCS#": "USB_PA7_FLAGD", "PE5/INT6": "USB_EZ_INT", "PE4/RXD1OUT": "USB_EZ_BSY",
        "DPLUS": "USB_DP", "DMINUS": "USB_DM", "XTALIN": "USB_XTAL_IN", "XTALOUT": "USB_XTAL_OUT",
        "SDA": "USB_EEPROM_SDA", "SCL": "USB_EEPROM_SCL", "RESET#": "USB_RESET_N",
    }
    for name, net in exact.items():
        label_all(sheet, fx, name, net)
    for index in range(8):
        label_all(sheet, fx, f"PB{index}/FD[{index}]", f"USB_FD{index}")
        label_all(sheet, fx, f"PD{index}/FD[{index + 8}]", f"USB_FD{index + 8}")
        label_all(sheet, fx, f"PC{index}/GPIFADR{index}", f"USB_LSI_D{index}")
    for key, locations in list(fx.items()):
        if not locations:
            continue
        name = locations[0][2]
        if name in {"VCC", "AVCC"}:
            label_all(sheet, fx, key, "+3V3_USB")
        elif name in {"GND", "AGND"}:
            label_all(sheet, fx, key, "GND")

    usb = sheet.lcsc("C165948", "J2", "TYPE-C-31-M-12", 1050, 180)
    for key, locations in list(usb.items()):
        if not locations:
            continue
        name = locations[0][2].upper()
        if "VBUS" in name:
            label_all(sheet, usb, key, "USB_VBUS")
        elif name in {"GND", "SHELL"} or "GND" in name:
            label_all(sheet, usb, key, "GND")
        elif "CC1" in name or "CC2" in name:
            label_all(sheet, usb, key, f"USB_{name}")
        elif "D+" in name or name.startswith("DP"):
            label_all(sheet, usb, key, "USB_DP_RAW")
        elif "D-" in name or name.startswith("DN") or name.startswith("DM"):
            label_all(sheet, usb, key, "USB_DM_RAW")

    esd = sheet.lcsc("C7519", "U4", "USBLC6-2SC6", 850, 180)
    for number, net in {"1": "USB_DP_RAW", "6": "USB_DP", "3": "USB_DM_RAW", "4": "USB_DM", "2": "GND", "5": "USB_VBUS"}.items():
        label_all(sheet, esd, number, net)
    sheet.text(770, 275, "U4 sits between USB_DP/DM_RAW and USB_DP/DM; verify pad names and keep traces short.", "7pt")
    crystal = sheet.lcsc("C15643", "Y1", "24MHz", 840, 430)
    label_all(sheet, crystal, "OSC1", "USB_XTAL_IN")
    label_all(sheet, crystal, "OSC2", "USB_XTAL_OUT")
    label_all(sheet, crystal, "GND", "GND")
    eeprom = sheet.lcsc("C6478", "U5", "AT24C128C-SSHM-T", 1060, 480)
    for name, net in {"SDA": "USB_EEPROM_SDA", "SCL": "USB_EEPROM_SCL", "VCC": "+3V3_USB", "GND": "GND"}.items():
        label_all(sheet, eeprom, name, net)
    sheet.text(40, 820, "The GPIF/Slave-FIFO and LSI8 pin mapping follows the legacy ZTEX/AudioXtreamer reference; firmware timing is not yet proven.", "8pt", "#AA0000")
    return sheet


def power_sheet() -> Sheet:
    sheet = Sheet("05 Power entry and rails", "Protected host input and provisional point-of-load regulators")
    sheet.text(40, 30, "Power architecture - values are preliminary pending Yamaha and A203 current/inrush measurements", "12pt")
    sheet.text(40, 50, "Do not fit an eFuse current-limit resistor value until host measurements and thermal analysis are complete.", "8pt", "#AA0000")

    efuse = sheet.lcsc("C181295", "U6", "TPS25942ARVCR", 230, 200)
    for key, locations in list(efuse.items()):
        if not locations:
            continue
        name = locations[0][2].upper()
        if name.startswith("IN"):
            label_all(sheet, efuse, key, "HOST_5V")
        elif name.startswith("OUT"):
            label_all(sheet, efuse, key, "+5V_PROTECTED")
        elif "GND" in name:
            label_all(sheet, efuse, key, "GND")
        elif "ILIM" in name:
            label_all(sheet, efuse, key, "EFUSE_ILIM_TBD")
    shunt = sheet.lcsc("C500720", "R1", "20mR 1%", 450, 115)
    shunt_numbers = sorted({key for key in shunt if key.isdigit()}, key=int)
    if len(shunt_numbers) >= 2:
        label_all(sheet, shunt, shunt_numbers[0], "+5V_PROTECTED")
        label_all(sheet, shunt, shunt_numbers[1], "+5V_SENSED")
    monitor = sheet.lcsc("C122228", "U7", "INA180A1IDBVR", 600, 160)
    for name, net in {"IN+": "+5V_PROTECTED", "IN-": "+5V_SENSED", "VS": "+3V3_LOGIC", "GND": "GND", "OUT": "HOST_CURRENT_MON"}.items():
        label_all(sheet, monitor, name, net)

    rails = [
        ("U8", "+3V3_LOGIC", 200, 500, "C25814", "316k", "L1", "R10", "R11", "C10", "C11"),
        ("U9", "+3V3_A203", 650, 500, "C25814", "316k", "L2", "R12", "R13", "C12", "C13"),
        ("U10", "+1V2_FPGA", 1100, 500, "C23184", "49.9k", "L3", "R14", "R15", "C14", "C15"),
    ]
    for ref, rail, x, y, top_lcsc, top_value, inductor_ref, top_ref, bottom_ref, cin_ref, cout_ref in rails:
        regulator = sheet.lcsc("C43590", ref, "TPS62130RGTR", x, y)
        for key, locations in list(regulator.items()):
            if not locations:
                continue
            name = locations[0][2].upper()
            if name in {"AVIN", "PVIN"}:
                label_all(sheet, regulator, key, "+5V_SENSED")
            elif name == "SW":
                label_all(sheet, regulator, key, f"{rail}_SW")
            elif "GND" in name:
                label_all(sheet, regulator, key, "GND")
            elif name == "FB":
                label_all(sheet, regulator, key, f"{rail}_FB")
            elif name == "VOS":
                label_all(sheet, regulator, key, rail)
            elif name == "EN":
                label_all(sheet, regulator, key, "POWER_ENABLE")
        inductor = sheet.lcsc("C133191", inductor_ref, "2.2uH", x + 150, y)
        numbers = sorted({key for key in inductor if key.isdigit()}, key=int)
        if len(numbers) >= 2:
            label_all(sheet, inductor, numbers[0], f"{rail}_SW")
            label_all(sheet, inductor, numbers[1], rail)
        two_pin(sheet, top_lcsc, top_ref, top_value, x - 60, y + 145, rail, f"{rail}_FB")
        two_pin(sheet, "C25803", bottom_ref, "100k", x + 60, y + 145, f"{rail}_FB", "GND")
        two_pin(sheet, "C15850", cin_ref, "10uF", x - 60, y + 205, "+5V_SENSED", "GND")
        two_pin(sheet, "C45783", cout_ref, "22uF", x + 60, y + 205, rail, "GND")
        sheet.text(x - 100, y + 265, f"{rail}: 2.2uH, 10uF input, 22uF output; verify loop layout against TI datasheet.", "7pt")

    load = sheet.lcsc("C2149796", "U11", "TPS22919DCKR", 1050, 150)
    for key, locations in list(load.items()):
        if not locations:
            continue
        name = locations[0][2].upper()
        if name in {"VIN", "IN", "A"}:
            label_all(sheet, load, key, "+3V3_LOGIC")
        elif name in {"VOUT", "Y"}:
            label_all(sheet, load, key, "+3V3_USB")
        elif "GND" in name:
            label_all(sheet, load, key, "GND")
        elif name in {"ON", "EN"}:
            label_all(sheet, load, key, "USB_POWER_ENABLE")
    sheet.text(950, 285, "USB load switch keeps the optional USB section from back-powering the native audio path.", "7pt")

    sheet.text(40, 825, "The complete package-specific FPGA capacitor network is on sheet 06.", "8pt")
    return sheet


def fpga_decoupling_sheet() -> Sheet:
    sheet = Sheet("06 FPGA package decoupling", "XC6SLX16 FTG256 capacitor population from AMD UG393")
    sheet.text(40, 30, "Spartan-6 LX16 FTG256 minimum package decoupling population", "12pt")
    sheet.text(40, 50, "Populate and place by rail/bank exactly as grouped; layout and plane inductance still require PCB review.", "8pt", "#AA0000")
    groups = [
        ("VCCINT", "+1V2_FPGA", [("C1779", "4.7uF")] * 5 + [("C47339", "0.47uF")]),
        ("VCCAUX", "+3V3_LOGIC", [("C48971041", "100uF"), ("C1779", "4.7uF"), ("C47339", "0.47uF"), ("C47339", "0.47uF")]),
        ("VCCO bank 0", "+3V3_LOGIC", [("C48971041", "100uF"), ("C1779", "4.7uF"), ("C47339", "0.47uF")]),
        ("VCCO bank 1", "+3V3_LOGIC", [("C48971041", "100uF"), ("C1779", "4.7uF"), ("C47339", "0.47uF"), ("C47339", "0.47uF")]),
        ("VCCO bank 2", "+3V3_LOGIC", [("C48971041", "100uF"), ("C1779", "4.7uF"), ("C47339", "0.47uF")]),
        ("VCCO bank 3", "+3V3_LOGIC", [("C48971041", "100uF"), ("C1779", "4.7uF"), ("C47339", "0.47uF"), ("C47339", "0.47uF")]),
    ]
    capacitor = 100
    for group_index, (name, rail, population) in enumerate(groups):
        column = group_index % 3
        row = group_index // 3
        base_x = 130 + column * 430
        base_y = 120 + row * 380
        sheet.text(base_x - 70, base_y - 45, f"{name} ({rail})", "10pt")
        for item_index, (lcsc, value) in enumerate(population):
            x = base_x + (item_index % 2) * 170
            y = base_y + (item_index // 2) * 90
            two_pin(sheet, lcsc, f"C{capacitor}", value, x, y, rail, "GND")
            capacitor += 1
    sheet.text(40, 845, "Also place local 100nF capacitors at each non-FPGA IC supply group; those values remain candidates until the remaining sheets are completed.", "8pt")
    return sheet


def ethernet_hold_sheet(a203_rows: list[dict[str, str]]) -> Sheet:
    sheet = Sheet("07 Ethernet PHY design hold", "A203 Ethernet pins captured without inventing a PHY circuit")
    sheet.text(50, 40, "ETHERNET PHY DESIGN HOLD", "14pt", "#AA0000")
    sheet.text(50, 70, "The A203 manual names RGMII/MII/MDIO signals but does not provide a supported PHY, voltage standard, delays, straps, magnetics, or layout.", "9pt")
    sheet.text(50, 95, "Obtain Audiocom's carrier/reference design before selecting a JLC-stocked PHY. These nets intentionally terminate at this sheet boundary.", "9pt", "#AA0000")
    phy_rows = [row for row in a203_rows if row["owner"] == "ethernet_phy"]
    for index, row in enumerate(phy_rows):
        column = index // 12
        line = index % 12
        x = 100 + column * 360
        y = 170 + line * 42
        sheet.label(x, y, f"A203_{row['signal']}")
        sheet.text(x + 25, y - 3, f"X1 pin {row['pin']} {row['signal']} - {row['confidence']}", "7pt")
    sheet.text(50, 760, "Required before release: exact PHY part/revision, I/O voltage, RGMII delay ownership, clock mode, strap values, reset sequence, magnetics/RJ45, and PCB stack-up.", "8pt", "#AA0000")
    return sheet


def write_manifest() -> None:
    placed = {
        "C39313", "C9926", "C165948", "C7519", "C6478", "C15643", "C82344",
        "C43590", "C133191", "C2149796", "C181295", "C122228", "C500720",
        "C25803", "C25814", "C23184", "C47339", "C1779", "C15850", "C45783", "C48971041",
    }
    with MANIFEST.open("w", encoding="utf-8", newline="") as output:
        writer = csv.writer(output, lineterminator="\n")
        writer.writerow(["lcsc", "mpn_or_value", "purpose", "jlc_class", "stock_snapshot_2026-08-19", "schematic_state", "assembly_status"])
        for lcsc, (mpn, purpose, part_class, stock) in PARTS.items():
            state = "placed" if lcsc in placed else "candidate only"
            assembly = "fit by JLC; recheck stock before order" if lcsc in placed else "do not order until placed and reviewed"
            writer.writerow([lcsc, mpn, purpose, part_class, stock, state, assembly])
        writer.writerow(["N/A", "KEL 8831E-100-170L", "Yamaha MLN2 host connector", "not a JLC part", "user has stock", "connector symbol; footprint hold", "DNI; customer hand-fit"])
        writer.writerow(["TBD", "124-pin 0.8 mm Mini-PCI socket", "Audiocom A203 socket", "JLC candidates currently zero stock", 0, "connector symbol; footprint hold", "consign or hand-fit after key/footprint verification"])


def main() -> None:
    assignments = read_csv("fpga-pin-assignment.csv")
    yamaha = read_csv("yamaha-mln2-pin-matrix.csv")
    a203 = read_csv("a203-pin-matrix.csv")
    assignment_by_ball = {row["ball"]: row["fpga_signal"] for row in assignments}

    def a203_net(row: dict[str, str]) -> str:
        signal = row["signal"]
        if signal == "GND":
            return "GND"
        if signal == "3.3V":
            return "+3V3_A203"
        if row["fpga_ball"]:
            return assignment_by_ball[row["fpga_ball"]]
        if row["owner"] == "ethernet_phy":
            return f"A203_{signal}"
        if row["owner"] == "module_flash":
            return ""
        if row["owner"] == "reset_supervisor":
            return "A203_RESET_N"
        return f"A203_{signal}_TEST"

    sheets = [
        overview_sheet(),
        connector_sheet("01 Yamaha MLN2 interface", yamaha, "contact", "generic_signal", "design_net", 25, "J1", "KEL 8831E-100-170L Yamaha MLN2 connector"),
        connector_sheet("02 Audiocom A203 interface", a203, "pin", "signal", "signal", 31, "X1", "Audiocom A203 124-pin Mini-PCI socket", a203_net),
        fpga_sheet(assignments),
        usb_sheet(assignments),
        power_sheet(),
        fpga_decoupling_sheet(),
        ethernet_hold_sheet(a203),
    ]
    document = {
        "editorVersion": "6.5.23",
        "docType": "5",
        "title": "danteXtreamer Rev A preliminary",
        "description": "Preliminary Yamaha 01X/i88X MLN2 replacement using Audiocom A203, Spartan-6, and optional FX2LP USB",
        "schematics": [sheet.to_document() for sheet in sheets],
    }
    OUTPUT.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_manifest()
    print(f"Wrote {OUTPUT}")
    print(f"Wrote {MANIFEST}")


if __name__ == "__main__":
    main()
