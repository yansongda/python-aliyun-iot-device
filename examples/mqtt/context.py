# -*- coding: utf-8 -*-

try:
    import aliyun_iot_device

except ImportError:
    import sys
    import os
    import inspect

    cmd_subfolder = os.path.realpath(
        os.path.abspath(
            os.path.join(
                os.path.split(
                    inspect.getfile(inspect.currentframe())
                )[0],
                "..",
                ".."
            )
        )
    )
    if cmd_subfolder not in sys.path:
        sys.path.insert(0, cmd_subfolder)

    import aliyun_iot_device