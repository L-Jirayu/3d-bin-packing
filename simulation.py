from py3dbp import Packer, Bin, Item, Painter
import time, copy


start = time.time()

# === CONFIG: Real Parcel Box Sizes (cm) ===
available_box_sizes = [
    (14, 20, 6),   # A
    (17, 25, 9),   # B
    (20, 30, 11),  # C
    (22, 35, 14),  # D
    (24, 40, 17),  # E
    (30, 45, 20),  # F
    (31, 36, 26),  # G
    (40, 45, 34),  # H
    (45, 55, 40),  # I

    (45, 45, 30),  # I
]

# === ITEMS ===
items_data = [
    ('MiniPerfume', 'cube', (10, 15, 21), '#FFC0CB'),
    ('MiniSerum', 'cube', (12, 12, 12), '#E6E6FA'),

    ('Soap-Bar', 'cube', (12, 12, 12), '#FFFFFF'),
    ('LipBalm', 'cube', (12, 12, 12), '#FFB6C1'),

    ('EyeCream', 'cube', (12, 12, 12), '#F5DEB3'),
    ('SampleToner', 'cube', (10, 15, 21), "#000000"),
    ('MiniPerfume', 'cube', (12, 12, 12), '#FFC0CB'),
    ('MiniSerum', 'cube', (12, 12, 12), '#E6E6FA'),
    ('LipBalm', 'cube', (12, 12, 12), '#FFB6C1'),
    ('EyeCream', 'cube', (14, 9.75, 6), '#F5DEB3'),

    ('MiniPerfume', 'cube', (12, 12, 12), '#FFC0CB'),
    ('MiniSerum', 'cube', (10, 15, 21), '#E6E6FA'),
    ('Soap-Bar', 'cube', (17, 25, 9), '#FFFFFF'),
    ('LipBalm', 'cube', (10, 15, 21), '#FFB6C1'),
    ('EyeCream', 'cube', (12, 12, 12), '#F5DEB3'),
    # ('SampleToner', 'cube', (15, 15, 15), '#D8BFD8'),
    # ('MiniPerfume', 'cube', (10, 15, 21), '#FFC0CB'),
    # ('MiniSerum', 'cube', (10, 15, 21), '#E6E6FA'),
    # ('LipBalm', 'cube', (12, 12, 12), '#FFB6C1'),
    # ('EyeCream', 'cube', (8, 8, 27), '#F5DEB3'),
]

# === เตรียม Items ===
all_items = []
for i, (partno, shape, size, color) in enumerate(items_data):
    all_items.append(Item(
        partno=f"{partno}-{i+1}", name='box', typeof=shape,
        WHD=size, weight=1, level=1, loadbear=100,
        updown=True, color=color
    ))

# === Optimization Step: กรองกล่องที่ไม่เหมาะสมออกก่อน ===
total_volume = sum(i.width * i.height * i.depth for i in all_items)
volume_threshold = 1.05  # เผื่อไว้ 5%
candidate_bins = [b for b in available_box_sizes if (b[0] * b[1] * b[2]) >= total_volume * volume_threshold]

# คำนวณน้ำหนักรวมจริง
total_weight = sum(i.weight for i in all_items) + 5  # เผื่อ buffer

# === Sorting Items ให้ง่ายต่อการจัดเรียง ===
all_items.sort(key=lambda x: x.width * x.height * x.depth, reverse=True)

packer = Packer()
selected_bin = None

# === ลอง pack เฉพาะกล่องที่ผ่านเกณฑ์ ===
for box_size in candidate_bins:
    temp_packer = Packer()
    test_bin = Bin("TestBin", box_size, total_weight, 0, 0)
    temp_packer.addBin(test_bin)

    # 🔁 แทนที่จะ addItem ทีละรอบ ให้ clone เข้าไป
    cloned_items = [copy.deepcopy(item) for item in all_items]
    for item in cloned_items:
        temp_packer.addItem(item)

    temp_packer.pack(
        bigger_first=True,
        distribute_items=False,
        fix_point=True,
        check_stable=True,
        support_surface_ratio=0.3,
        number_of_decimals=0
    )

    result_bin = temp_packer.bins[0]
    if not result_bin.unfitted_items:
        packer.addBin(result_bin)
        selected_bin = box_size
        break

# === ถ้าไม่มี bin ไหนใส่ได้หมด → ส่ง Trollor ===
if not selected_bin:
    trollor = Bin('Trollor', (60, 60, 60), total_weight, 0, 0)
    for item in all_items:
        trollor.putItem(item, pivot=(0, 0, 0))
    packer.addBin(trollor)

# === รายงานผล ===
print("\n== Packing Summary ==")
for b in packer.bins:
    volume = b.width * b.height * b.depth
    used_volume = sum(i.width * i.height * i.depth for i in b.items)
    try:
        b.gravity = packer.gravityCenter(b)
    except ZeroDivisionError:
        b.gravity = (0, 0, 0)

    print(f"\n=== BIN: {b.partno} ===")
    print(f"Size: {b.width}x{b.height}x{b.depth}")
    print(f"Utilization: {round(used_volume / volume * 100, 2)}%")
    print("Gravity Center:", b.gravity)

    print(">> FITTED ITEMS:")
    for item in b.items:
        print(f"  - {item.partno} | Pos: {item.position} | Size: {item.width}x{item.height}x{item.depth} | Color: {item.color}")

    if b.unfitted_items:
        print(">> UNFITTED ITEMS:")
        for item in b.unfitted_items:
            print(f"  - {item.partno} | Size: {item.width}x{item.height}x{item.depth}")

    fig = Painter(b).plotBoxAndItems(title=b.partno, alpha=0.7, write_num=False)
    fig.show()

print("\nTotal Time: {:.2f} seconds".format(time.time() - start))
