__all__ = ['NotFinished', 'Queue']

from queue import Queue as Queue_
from time import monotonic as time


class NotFinished(Exception):
    """Exception raised by Queue.join() when it times out."""


class Queue(Queue_):
    def join(self, timeout: float = None) -> None:
        """
        Blocks until all items in the Queue have been gotten and processed,
        or until ``timeout`` seconds have elapsed.

        The count of unfinished tasks goes up whenever an item is added to the
        queue. The count goes down whenever a consumer thread calls task_done()
        to indicate the item was retrieved and all work on it is complete.

        When the count of unfinished tasks drops to zero, join() unblocks.

        Args:
            timeout:
                An optional timeout in seconds to wait for unfinished tasks.
                If ``None`` (default), then there is no limit to the wait time.

        Raises:
            NotFinished:
                If ``timeout`` is not ``None`` and the timeout is reached
                before all tasks are finished.
        """

        if timeout is None:
            return super().join()
        elif timeout <= 0:
            raise ValueError(
                f'timeout must be a non-negative number; timeout={timeout}'
            )

        end_time = time() + timeout
        with self.all_tasks_done:
            while self.unfinished_tasks:
                remaining = end_time - time()
                if remaining <= 0.0:
                    raise NotFinished

                self.all_tasks_done.wait(remaining)
