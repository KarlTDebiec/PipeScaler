"""
I have an iterable whose elements are dictionaries with a consistent set of keys.
I'd like to use itertools.tee to create a set of iterators that provide the values for
each key.
I'd like the name and number of keys to be arbitrary, and for that reason would like to
construct the iterators within a for loop.
I've found that I obtain different results when generating the iterators in a for loop
than I do when I generate them explicitly.
"""
from itertools import tee


def get_generators_explicitly(elements):
    tees = list(tee(elements))
    yat = {}
    yat["a"] = (elem["a"] for elem in tees[0])
    yat["b"] = (elem["b"] for elem in tees[1])
    return yat


def get_generators_using_a_for_loop(elements):
    tees = list(tee(elements))
    yat = {}
    for i, key in enumerate(["a", "b"]):
        yat[key] = (elem[key] for elem in tees[i])
    return yat


def get_generators_using_a_for_loop_with_eval(elements):
    tees = list(tee(elements))
    yat = {}
    for i, key in enumerate(["a", "b"]):
        yat[key] = eval(f"(elem['{key}'] for elem in tees[{i}])")
    return yat

if __name__ == "__main__":
    elements = [
        {
            "a": "elements[0]['a']",
            "b": "elements[0]['b']",
        },
        {
            "a": "elements[1]['a']",
            "b": "elements[1]['b']",
        },
        {
            "a": "elements[2]['a']",
            "b": "elements[2]['b']",
        },
    ]

    print("Result of get_generators_explicitly:")
    generators_explicitly = get_generators_explicitly(elements)
    print(generators_explicitly)
    for item in generators_explicitly["a"]:
        print(item)
    for item in generators_explicitly["b"]:
        print(item)

    print("Result of get_generators_using_a_for_loop:")
    generators_from_for_loop = get_generators_using_a_for_loop(elements)
    print(generators_from_for_loop)
    for item in generators_from_for_loop["a"]:
        print(item)
    for item in generators_from_for_loop["b"]:
        print(item)

    print("Result of get_generators_using_a_for_loop_with_eval:")
    generators_from_for_loop_with_eval = get_generators_using_a_for_loop_with_eval(elements)
    print(generators_from_for_loop_with_eval)
    for item in generators_from_for_loop_with_eval["a"]:
        print(item)
    for item in generators_from_for_loop_with_eval["b"]:
        print(item)
