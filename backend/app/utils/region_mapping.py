"""
地区编码与名称映射工具
"""

# 省份映射表
PROVINCES = {
    '110000': '北京市',
    '120000': '天津市',
    '130000': '河北省',
    '140000': '山西省',
    '150000': '内蒙古自治区',
    '210000': '辽宁省',
    '220000': '吉林省',
    '230000': '黑龙江省',
    '310000': '上海市',
    '320000': '江苏省',
    '330000': '浙江省',
    '340000': '安徽省',
    '350000': '福建省',
    '360000': '江西省',
    '370000': '山东省',
    '410000': '河南省',
    '420000': '湖北省',
    '430000': '湖南省',
    '440000': '广东省',
    '450000': '广西壮族自治区',
    '460000': '海南省',
    '500000': '重庆市',
    '510000': '四川省',
    '520000': '贵州省',
    '530000': '云南省',
    '540000': '西藏自治区',
    '610000': '陕西省',
    '620000': '甘肃省',
    '630000': '青海省',
    '640000': '宁夏回族自治区',
    '650000': '新疆维吾尔自治区',
    '710000': '台湾省',
    '810000': '香港特别行政区',
    '820000': '澳门特别行政区'
}

# 城市映射表（部分主要城市）
CITIES = {
    '330100': '杭州市',
    '330200': '宁波市',
    '330300': '温州市',
    '330400': '嘉兴市',
    '330500': '湖州市',
    '330600': '绍兴市',
    '330700': '金华市',
    '330800': '衢州市',
    '330900': '舟山市',
    '331000': '台州市',
    '331100': '丽水市',
    '320100': '南京市',
    '320200': '无锡市',
    '320300': '徐州市',
    '320400': '常州市',
    '320500': '苏州市',
    '320600': '南通市',
    '320700': '连云港市',
    '320800': '淮安市',
    '320900': '盐城市',
    '321000': '扬州市',
    '321100': '镇江市',
    '321200': '泰州市',
    '321300': '宿迁市'
}

# 区县映射表（部分主要区县）
DISTRICTS = {
    '330110': '余杭区',
    '330111': '建德市',
    '330112': '桐庐县',
    '330113': '淳安县',
    '330114': '临安区',
    '330101': '上城区',
    '330102': '下城区',
    '330103': '江干区',
    '330104': '拱墅区',
    '330105': '西湖区',
    '330106': '滨江区',
    '330107': '萧山区',
    '330108': '余杭区',
    '330109': '富阳区'
}


def get_region_name(region_code: str) -> str:
    """
    根据地区编码获取地区名称

    Args:
        region_code: 地区编码字符串

    Returns:
        地区名称，如果未找到则返回原编码
    """
    if not region_code:
        return ""

    # 首先尝试完整匹配
    if region_code in DISTRICTS:
        return DISTRICTS[region_code]
    if region_code in CITIES:
        return CITIES[region_code]
    if region_code in PROVINCES:
        return PROVINCES[region_code]

    # 如果是6位编码，尝试匹配省市
    if len(region_code) == 6:
        province_code = region_code[:2] + '0000'
        city_code = region_code[:4] + '00'

        if province_code in PROVINCES:
            province_name = PROVINCES[province_code]
            if city_code in CITIES:
                return CITIES[city_code]
            return province_name

    # 如果找不到，返回原编码
    return region_code


def resolve_region_from_codes(province_code: str = None, city_code: str = None, district_code: str = None) -> str:
    """
    根据省市县编码组合解析完整地区名称

    Args:
        province_code: 省份编码
        city_code: 城市编码
        district_code: 区县编码

    Returns:
        完整的地区名称字符串，如：浙江省 杭州市 余杭区
    """
    parts = []

    if province_code:
        province_name = get_region_name(province_code)
        if province_name and province_name != province_code:
            parts.append(province_name)
        elif province_code not in ['', '0', '00', '000', '0000', '00000', '000000']:
            parts.append(province_code)

    if city_code:
        city_name = get_region_name(city_code)
        if city_name and city_name != city_code:
            parts.append(city_name)
        elif city_code not in ['', '0', '00', '000', '0000', '00000', '000000']:
            parts.append(city_code)

    if district_code:
        district_name = get_region_name(district_code)
        if district_name and district_name != district_code:
            parts.append(district_name)
        elif district_code not in ['', '0', '00', '000', '0000', '00000', '000000']:
            parts.append(district_code)

    return ' '.join(parts) if parts else "全国"


if __name__ == "__main__":
    # 测试用例
    print("测试地区编码映射:")
    print(f"330000 -> {get_region_name('330000')}")
    print(f"330100 -> {get_region_name('330100')}")
    print(f"330110 -> {get_region_name('330110')}")

    print("\n测试地区组合解析:")
    print(f"浙江+杭州+余杭 -> {resolve_region_from_codes('330000', '330100', '330110')}")
    print(f"浙江+杭州 -> {resolve_region_from_codes('330000', '330100')}")
    print(f"浙江 -> {resolve_region_from_codes('330000')}")