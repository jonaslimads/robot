"""
These are global queues, which are used to feed data from one endpoint/feature to another in an asynchronous fashion.

Local queues should be defined within their classes/modules.
"""

from tornado.queues import Queue, QueueFull

from mind import get_logger
from mind.models import Device, Packet


logger = get_logger(__name__)

camera_queue: Queue = Queue(maxsize=20)

microphone_queue: Queue = Queue(maxsize=20)

audio_transcriber_queue: Queue = Queue(maxsize=20)


def put_packet_to_queue(packet: Packet) -> None:
    try:
        get_device_queue(packet.device.type).put_nowait(packet)
    except QueueFull as e:
        logger.warning(f"{packet.device.type}'s queue is full")
    except ValueError as e:
        logger.error(e)


def get_device_queue(device_type: Device.Type) -> Queue:
    if device_type == Device.Type.CAMERA:
        return camera_queue

    if device_type == Device.Type.MICROPHONE:
        return microphone_queue

    raise ValueError(f"{device_type}'s queue not found")
