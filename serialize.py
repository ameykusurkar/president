from typing import Union, Iterable, Any

def serialize_iterable(items: Iterable) -> list[Any]:
    serialized = []
    for item in items:
        serial_attr = getattr(item, "serialize", None)
        if serial_attr and callable(serial_attr):
            serialized.append(item.serialize())
        else:
            serialized.append(repr(item))
    return serialized
