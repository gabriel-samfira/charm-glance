#!/usr/bin/env python3
#
# Copyright 2016 Canonical Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
import os

_path = os.path.dirname(os.path.realpath(__file__))
_parent = os.path.abspath(os.path.join(_path, ".."))
_hooks = os.path.abspath(os.path.join(_parent, "hooks"))


def _add_path(path):
    if path not in sys.path:
        sys.path.insert(1, path)


_add_path(_parent)
_add_path(_hooks)


from charmhelpers.core.hookenv import action_fail

from glance_utils import (
    pause_unit_helper,
    resume_unit_helper,
    register_configs,
)


def pause(args):
    """Pause all the Glance services.

    @raises Exception if any services fail to stop
    """
    pause_unit_helper(register_configs())


def resume(args):
    """Resume all the Glance services.

    @raises Exception if any services fail to start
    """
    resume_unit_helper(register_configs())


# A dictionary of all the defined actions to callables (which take
# parsed arguments).
ACTIONS = {"pause": pause, "resume": resume}


def main(args):
    action_name = os.path.basename(args[0])
    try:
        action = ACTIONS[action_name]
    except KeyError:
        return "Action %s undefined" % action_name
    else:
        try:
            action(args)
        except Exception as e:
            action_fail(str(e))


if __name__ == "__main__":
    sys.exit(main(sys.argv))
