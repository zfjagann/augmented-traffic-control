#
#  Copyright (c) 2014, Facebook, Inc.
#  All rights reserved.
#
#  This source code is licensed under the BSD-style license found in the
#  LICENSE file in the root directory of this source tree. An additional grant
#  of patent rights can be found in the PATENTS file in the same directory.
#
#
import logging
import os
import sys

from atcd.AtcdDeviceTimeoutTask import AtcdDeviceTimeoutTask
from atcd.AtcdExabgpTask import AtcdExabgpTask
from atcd.AtcdThriftHandlerTask import AtcdNBServerTask
from atcd.AtcdThriftHandlerTask import AtcdThriftHandlerTask
from sparts.sparts import option
from sparts.vservice import VService


class AtcdVService(VService):

    TASKS = [
        AtcdNBServerTask,
        AtcdExabgpTask,
        AtcdThriftHandlerTask.factory(),
        AtcdDeviceTimeoutTask
    ]

    enable_exabgp = option(
        action='store_true',
        help='Enable Exabgp Task',
    )

    @classmethod
    def initFromOptions(cls, ns, name=None):
        """
        Override default static method to disable Exabgp if needed.
        We disable rather than enable in order to get options displayed
        when using -h.
        """
        if not ns.enable_exabgp:
            cls.TASKS.remove(AtcdExabgpTask)
        super(AtcdVService, cls).initFromOptions(ns, name)

    def initLogging(self):
        super(AtcdVService, self).initLogging()
        sh = logging.handlers.SysLogHandler(address=self._syslog_address())
        sh.setLevel(logging.DEBUG)
        self.logger.addHandler(sh)
        # Make sparts.tasks logging go to syslog
        sparts_tasks_logger = logging.getLogger('sparts.tasks')
        sparts_tasks_logger.addHandler(sh)

    def _syslog_address(self):
        address = None
        if sys.platform == 'linux2':
            address = '/dev/log'
        elif sys.platform == 'darwin':
            address = '/var/run/syslog'

        if address is None or not os.path.exists(address):
            address = ('localhost', 514)
        return address
