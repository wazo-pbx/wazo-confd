#!/bin/sh
PYTHONPATH=..:../xivo_recording:../../xivo-dao/xivo-dao lettuce features/queues.feature
