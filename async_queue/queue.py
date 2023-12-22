from __future__ import annotations

import asyncio
import logging
from typing import Any, Callable, Coroutine, Self


TaskDefinition = tuple[Callable[..., Coroutine[Any, Any, None]], list[Any], dict[str, Any]]


class Queue:
    def __init__(
        self: Self,
        producer_definitions: list[TaskDefinition],
        consumer_definitions: list[TaskDefinition],
    ) -> None:
        self.__producer_definitions = producer_definitions
        self.__consumer_definitions = consumer_definitions

        self.__queue: asyncio.Queue[str] = asyncio.Queue()

    async def start(self: Self) -> None:
        self.__init_tasks()

        while self.__tasks:
            done, _ = await asyncio.wait(
                self.__tasks.keys(),
                return_when=asyncio.FIRST_EXCEPTION,
                timeout=5,
            )

            self.__rerun_failed_tasks(done)
            if all(producer.done() for producer in self.__producers):
                break

        # wait for the remaining tasks to be processed
        await self.__queue.join()

        # cancel the consumers, which are now idle
        for c in self.__consumers:
            c.cancel()

    def __create_tasks(self: Self, task_definitions: list[TaskDefinition]) -> dict[asyncio.Task, TaskDefinition]:
        return {
            asyncio.create_task(coro(self.__queue, *args, **kwargs)): (coro, args, kwargs)
            for coro, args, kwargs in task_definitions
        }

    def __init_tasks(self: Self) -> None:
        self.__producers = self.__create_tasks(self.__producer_definitions)
        self.__consumers = self.__create_tasks(self.__consumer_definitions)

        self.__tasks = self.__producers.copy()
        self.__tasks.update(self.__consumers)

    def __rerun_failed_tasks(self: Self, done: set[asyncio.Task]) -> None:
        for task in done:
            if task.exception() is None:
                continue

            stacktrace_string = "\n".join(list(map(str, task.get_stack())))
            logging.error(f"Task exited with exception:\n{stacktrace_string}\n{task.exception()}")
            logging.info("Rescheduling the task\n")

            self.__rerun_task(task)

    def __rerun_task(self: Self, task: asyncio.Task) -> None:
        coro, args, kwargs = self.__tasks.pop(task)
        new_task = asyncio.create_task(coro(self.__queue, *args, **kwargs))

        def update_task(d: dict[asyncio.Task, TaskDefinition]) -> None:
            d.pop(task)
            d[new_task] = coro, args, kwargs

        self.__tasks[new_task] = coro, args, kwargs
        if task in self.__producers:
            update_task(self.__producers)
        elif task in self.__consumers:
            update_task(self.__consumers)
