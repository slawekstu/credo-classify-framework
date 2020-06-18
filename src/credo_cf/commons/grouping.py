from typing import List, Dict, Any, Callable, Optional, Tuple

from credo_cf.commons.consts import DEVICE_ID, TIMESTAMP, CLASSIFIED, CLASS_ARTIFACT
from credo_cf.commons.utils import get_and_set, get_resolution_key


GroupFunc = Callable[[Any, Dict[Any, List[Any]]], Optional[Any]]


def group_by_lambda(array: List[dict], func: GroupFunc) -> Dict[Any, List[dict]]:
    """
    Convert list of objects to dict of list of object when key of dict is generated by func.

    Example::

      grouped = group_by_lambda(detections, lambda x: x.get(DEVICE_ID))

    :param array: list of objects to group
    :param func: give object as param and return key or None, when key is None then object will be excluded

    The ``func(obj, ret)`` callback provided as arg:

      Args:
        * ``obj``: next element from ``array``
        * ``ret``: dictionary of just grouped objects

      Return effect:
        * ``None``: object will not be added anywhere
        * *some value* : object will be append to array in *some value* key

    Note: there are some wrappers for this functions like
    ``group_by_device_id()``,
    ``group_by_timestamp_division()``,
    ``group_by_timestamp_division()``,
    ``group_by_resolution()``.

    :return: dict of list of object
    """
    ret = {}
    for o in array:
        key = func(o, ret)
        if key is None:
            continue
        os = get_and_set(ret, key, [])
        os.append(o)
    return ret


def exclude_artifacts(detection: dict):
    """
    Exclusion classified as artifact.
    :param detection: detection
    :return: detection['classified'] == 'artifact'
    """
    return detection.get(CLASSIFIED) == CLASS_ARTIFACT


def group_by_device_id(detections: List[dict]) -> Dict[int, List[dict]]:
    """
    Group detections by device_id field. The key of group is ``device_id``.

    Note: it is wrapper on ``group_by_lambda()``.
    :param detections: list of detections
    :return: detections grouped by device_id
    """
    return group_by_lambda(detections, lambda x, y: x.get(DEVICE_ID))


def group_by_timestamp_division(detections: List[dict], division: int = 1) -> Dict[int, List[dict]]:
    """
    Group detections by timestamp divided. The key of group is ``timestamp`` integer divided by ``division``.

    Note: it is wrapper on ``group_by_lambda()``.
    :param detections: list of ungrouped detections
    :param division: timestamp window do divide detections

    Note: when ``division=1`` then detection will be grouped by detections on the same original image frame.

    :return: detection grouped by timestamp integer divided by division param
    """
    return group_by_lambda(detections, lambda x, y: x.get(TIMESTAMP) // division)


def group_by_resolution(detections: List[dict]) -> Dict[Tuple[int, int], List[dict]]:
    """
    Group detections by resolution of original image frame.
    The key of group is tuple of (width, height) of original image frame.

    Note: it is wrapper on ``group_by_lambda()``.
    :param detections: list of ungrouped detections
    :return: detection grouped by resolution of original image frame.
    """
    return group_by_lambda(detections, lambda x, y: get_resolution_key(x))


def sort_by_field(detections: List[dict], field: str) -> List[dict]:
    """
    Sort detections by field.
    :param detections: list of detections
    :param field: field for sort by
    :return: list of detections sorted by field
    """
    return sorted(detections, key=lambda i: i[field])
