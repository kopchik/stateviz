#!/usr/bin/env python

from __future__ import annotations

class Node:
    def __init__(self, f):
        self.f = f


"""
TODO:
- indicate loops
- indicate unvisited nodes
"""


class Then(Node):
    def __init__(self, f, next):
        self.f = f
        self.next = next

    def resolve(self, d):
        self.next = d[self.next]
        self.next.resolve(d)

    def run(self, *args):
        result = self.f(*args)
        return self.next.run(result)

    def __repr__(self):
        return f"{self.f.__name__}({self.next})"


class End(Node):
    def __init__(self, f):
        self.f = f

    def resolve(self, d):
        pass

    def run(self, *args):
        return self.f(*args)

    def __repr__(self):
        return f"{self.f.__name__}"


def get_wrapper(Cls, nodes, *args, **kwargs):
    def wrap(f):
        nodes[f.__name__] = Cls(f, *args, **kwargs)
        return f

    return wrap


class State:
    def __init__(self):
        self._root = None
        self._start_name = None
        self._nodes = {}

    def start(self, f):
        self._start_name = f.__name__
        return f

    def then(self, *args, **kwargs):
        return get_wrapper(Then, self._nodes, *args, **kwargs)

    def end(self):
        return get_wrapper(End, self._nodes)

    def resolve(self):
        root = self._nodes[self._start_name]
        root.resolve(self._nodes)
        self._root = root

    def run(self, *args, **kwargs):
        return self._root.run(*args, **kwargs)


state = State()


@state.start
@state.then("second")
def start(arg) -> str:
    return f"Pass {arg} to second stage"


@state.then("end")
def second(arg) -> str:
    print("got from previous stage:", arg)
    return "pass to end"


@state.end()
def end(arg: str) -> str:
    print(f"passed to end: {arg}")
    return arg


state.resolve()
print(state._root)
state.run('XOXOXO')
