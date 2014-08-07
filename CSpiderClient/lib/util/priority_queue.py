#!/usr/bin/env python
#coding=UTF-8
'''
    Created on 2013-11-23
    @author: devin
    @desc:
        priority queue
'''
import itertools
from heapq import *

class PriorityQueue:
    def __init__(self):
        self.pq = []                         # list of entries arranged in a heap
        self.entry_finder = {}               # mapping of tasks to entries
        self.REMOVED = '<removed-task>'      # placeholder for a removed task
        self.counter = itertools.count()     # unique sequence count

    def add_task(self, task, priority = 0):
        '''
            Add a new task or update the priority of an existing task.
        '''
        if task in self.entry_finder:
            self.remove_task(task)
        count = next(self.counter)
        entry = [priority, count, task]
        self.entry_finder[task] = entry
        heappush(self.pq, entry)
    
    def update_task(self, task, priority = 0):
        self.add_task(task, priority)

    def remove_task(self, task):
        '''
            Mark an existing task as REMOVED.  Raise KeyError if not found.
        '''
        if task not in self.entry_finder:
            return
        entry = self.entry_finder.pop(task)
        entry[-1] = self.REMOVED

    def pop_task(self):
        '''
            Remove and return the lowest priority task. Raise KeyError if empty.
        '''
        while self.pq:
            priority, count, task = heappop(self.pq)
            if task is not self.REMOVED:
                del self.entry_finder[task]
                return task, priority

        return None

    def __len__(self):
        return len(self.entry_finder)


if __name__ == "__main__":
    queue = PriorityQueue()
    queue.add_task("write code", 5)
    queue.add_task("release product", 7)
    queue.add_task("wirte spec", 1)
    queue.add_task("create tests", 3)

    print queue.pop_task()
    
    queue.remove_task("create tests")
    queue.update_task("release product", 4)
    print queue.pop_task()

