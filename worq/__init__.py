# WorQ - asynchronous Python task queue.
#
# Copyright (c) 2012 Daniel Miller
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from __future__ import absolute_import
from urlparse import urlparse
from worq.core import DEFAULT, Broker
from worq.task import Task, TaskSet, TaskFailure, TaskSpace
from worq.memory import MemoryQueue, MemoryResults
from worq.redis import RedisQueue, RedisResults

BROKER_REGISTRY = {
    'memory': (MemoryQueue.factory, MemoryResults.factory),
    'redis': (RedisQueue, RedisResults),
}

def get_broker(url, *queues):
    """Create a new broker

    :param url: Message queue and result store URL (this convenience function
        uses the same URL to construct both).
    :param *queues: One or more queue names on which to expose or invoke tasks.
    """
    url_scheme = urlparse(url).scheme
    try:
        make_queue, make_results = BROKER_REGISTRY[url_scheme]
    except KeyError:
        raise ValueError('invalid broker URL: %s' % url)
    message_queue = make_queue(url, queues)
    result_store = make_results(url)
    return Broker(message_queue, result_store)

def queue(url, queue=DEFAULT, target=''):
    """Get a queue object for invoking remote tasks

    :param url: URL of the task queue.
    :param queue: The name of the queue on which tasks should be invoked.
        Queued tasks will be invoked iff there is a worker listening on the
        named queue. Default value: 'default'.
    :param target: Task namespace (similar to a python module) or name
        (similar to a python function). Default to the root namespace ('').
    :returns: An instance of worq.task.Queue.
    """
    broker = get_broker(url)
    return broker.queue(queue, target)
