from py3dbp import Packer, Bin, Item
import copy

#depth = length
def do_packing(skus):
    # skus: list of dict, แต่ละ dict มี 'dimension': {width, length, height} และ 'name'
    # แปลงข้อมูลเป็น py3dbp.Item
    all_items = []
    for i, sku in enumerate(skus):
        dim = sku['dimension']
        # py3dbp ใช้ width, height, depth
        width = dim['width']
        height = dim['height']
        depth = dim['depth']
        name = sku.get('name') or f"Item-{i+1}"

        all_items.append(Item(
            partno=f"{name}-{i+1}",
            name=name,
            typeof='cube',
            WHD=(width, height, depth),
            weight=1,
            level=1,
            loadbear=100,
            updown=True,
            color="#CCCCCC"
        ))

    # === CONFIG กล่องเหมือนเดิม
    available_box_sizes = [
        (14, 20, 6),
        (17, 25, 9),
        (20, 30, 11),
        (22, 35, 14),
        (24, 40, 17),
        (30, 45, 20),
        (31, 36, 26),
        (40, 45, 34),
        (45, 55, 40),
        (45, 45, 30),
    ]

    # กรองกล่องตามปริมาตรรวม
    total_volume = sum(i.width * i.height * i.depth for i in all_items)
    volume_threshold = 1.05
    candidate_bins = [b for b in available_box_sizes if (b[0]*b[1]*b[2]) >= total_volume * volume_threshold]

    total_weight = sum(i.weight for i in all_items) + 5

    all_items.sort(key=lambda x: x.width * x.height * x.depth, reverse=True)

    packer = Packer()
    selected_bin = None

    for box_size in candidate_bins:
        temp_packer = Packer()
        test_bin = Bin("TestBin", box_size, total_weight, 0, 0)
        temp_packer.addBin(test_bin)

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

    if not selected_bin:
        trollor = Bin('Trollor', (60, 60, 60), total_weight, 0, 0)
        for item in all_items:
            trollor.putItem(item, pivot=(0, 0, 0))
        packer.addBin(trollor)

    # สร้างผลลัพธ์สรุปเป็น dict (ไม่ plot)
    res_bins = []
    for b in packer.bins:
        used_volume = sum(i.width * i.height * i.depth for i in b.items)
        total_vol = b.width * b.height * b.depth
        bin_info = {
            "partno": b.partno,
            "size": {
                "width": b.width, 
                "height": b.height,
                "depth": b.depth}, 
                
        }
        res_bins.append(bin_info)

    return {"bins": res_bins}
