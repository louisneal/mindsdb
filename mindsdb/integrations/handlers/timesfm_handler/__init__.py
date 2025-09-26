from mindsdb.integrations.libs.const import HANDLER_TYPE
from mindsdb.utilities import log
from .__about__ import __version__ as version, __description__ as description

logger = log.getLogger(__name__)

try:
    from .timesfm_handler import TimesfmHandler as Handler
    import_error = None
except Exception as e:
    Handler = None
    import_error = e

title = 'TimesFM'
name = 'timesfm'
type = HANDLER_TYPE.ML
icon_path = 'icon.png'
permanent = False

__all__ = [
    'Handler', 'version', 'name', 'type', 'title', 'description', 'import_error', 'icon_path'
]

