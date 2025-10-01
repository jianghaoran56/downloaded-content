import json
import os
import sys
from typing import Dict, List


def _resource_path_windows(src: str) -> str:
    # 兼容PyInstaller单文件模式的数据目录
    try:
        base_path = sys._MEIPASS  # type: ignore
        return os.path.join(base_path, src)
    except Exception:
        pass
    return src


def _load_units_json() -> Dict:
    # 尝试PyInstaller打包的数据路径
    candidate_paths = [
        _resource_path_windows(os.path.join("converter", "units.json")),
        _resource_path_windows("units.json"),
        os.path.join(os.path.dirname(__file__), "units.json"),
    ]
    for p in candidate_paths:
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f:
                return json.load(f)
    raise FileNotFoundError("未找到单位定义文件 units.json")


class UnitRegistry:
    def __init__(self):
        self._data = _load_units_json()

    def get_categories(self) -> List[str]:
        return list(self._data.keys())

    def get_units(self, category: str) -> List[str]:
        cat = self._data.get(category, {})
        if category == "temperature":
            return cat.get("units", [])
        units = cat.get("units", {})
        return list(units.keys())

    def get_category(self, category: str) -> Dict:
        return self._data[category]


class Converter:
    def __init__(self, registry: UnitRegistry):
        self.registry = registry

    def convert(self, category: str, value: float, from_unit: str, to_unit: str) -> float:
        if category == "temperature":
            return self._convert_temperature(value, from_unit, to_unit)
        cat = self.registry.get_category(category)
        base = cat.get("base")
        units = cat.get("units", {})
        if from_unit not in units or to_unit not in units:
            raise ValueError("所选单位不在该类别中")
        # 线性单位：先归一到基准，再转换到目标
        to_base = value * units[from_unit]
        return to_base / units[to_unit]

    @staticmethod
    def _convert_temperature(value: float, from_unit: str, to_unit: str) -> float:
        # 统一转换到摄氏度，再转换到目标
        def to_celsius(v: float, u: str) -> float:
            u = u.lower()
            if u in ("c", "celsius", "摄氏度"):
                return v
            if u in ("f", "fahrenheit", "华氏度"):
                return (v - 32) * 5.0 / 9.0
            if u in ("k", "kelvin", "开尔文"):
                return v - 273.15
            if u in ("r", "rankine", "兰氏度"):
                return (v - 491.67) * 5.0 / 9.0
            raise ValueError("不支持的温度单位")

        def from_celsius(c: float, u: str) -> float:
            u = u.lower()
            if u in ("c", "celsius", "摄氏度"):
                return c
            if u in ("f", "fahrenheit", "华氏度"):
                return c * 9.0 / 5.0 + 32
            if u in ("k", "kelvin", "开尔文"):
                return c + 273.15
            if u in ("r", "rankine", "兰氏度"):
                return (c + 273.15) * 9.0 / 5.0
            raise ValueError("不支持的温度单位")

        c = to_celsius(value, from_unit)
        return from_celsius(c, to_unit)