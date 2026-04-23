"""Excel导出功能"""
from typing import List, Dict, Tuple


def export_to_excel(data: List[Dict], file_path: str) -> Tuple[bool, str]:
    """
    导出仿真数据到Excel。
    data: [{'t':..,'sv':..,'pv':..,'u':..,'d':..}, ...]
    """
    try:
        import openpyxl
    except ImportError:
        return False, '缺少openpyxl库，请运行: pip install openpyxl'

    try:
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = '仿真数据'
        headers = ['时间(s)', '设定值SV', '过程值PV', '控制量u', '干扰d']
        ws.append(headers)
        for row in data:
            ws.append([
                row.get('t', 0),
                row.get('sv', 0),
                row.get('pv', 0),
                row.get('u', 0),
                row.get('d', 0),
            ])
        # 设置列宽
        for col in ws.columns:
            ws.column_dimensions[col[0].column_letter].width = 15
        wb.save(file_path)
        return True, f'导出成功：{file_path}'
    except Exception as e:
        return False, f'导出失败：{e}'
