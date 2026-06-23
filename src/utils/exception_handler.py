"""异常处理工具类"""
import logging
import traceback
from exception import get_logger, show_error_dialog


def handle_exception(e: Exception, context: str = '',
                     show_dialog: bool = True) -> None:
    """统一处理异常：记录日志 + 可选弹窗"""
    tb = traceback.format_exc()
    msg = f'{context}: {e}' if context else str(e)
    try:
        get_logger().error('%s\n%s', msg, tb)
    except Exception as e_log:
        logging.error(f'异常日志记录失败: {e_log}')
    if show_dialog:
        show_error_dialog(msg)
