from .filesystem import FilesystemResolver
from .tank_ import TankResolver


registered = {'filesystem': FilesystemResolver,
              'tank': TankResolver}
