import unittest

from parameterized import parameterized

from voicebox.voiceboxes.queue import NotFinished, Queue


class QueueTest(unittest.TestCase):
    def test_join_with_timeout(self):
        queue = Queue()
        queue.put(1)

        with self.assertRaises(NotFinished):
            queue.join(timeout=0.1)

        queue.get()
        queue.task_done()
        queue.join(timeout=0.1)

    @parameterized.expand([0, -1])
    def test_join_with_non_negative_timeout_raises_ValueError(
        self,
        timeout: float,
    ):
        queue = Queue()

        with self.assertRaises(ValueError):
            queue.join(timeout=timeout)
