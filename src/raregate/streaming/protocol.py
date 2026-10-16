"""Fixed protocol arithmetic and byte layouts. Standard library only."""

import struct
from dataclasses import dataclass

VERSION = 1
TOKEN = b"LT0051-FIXTURE!!"
MAGIC = b"LTS0051\x00"
SLOTS = 64
CONTROL_BYTES = 4096
SLOT_BYTES = 128
SHARED_BYTES = CONTROL_BYTES + SLOTS * SLOT_BYTES
MAX_U64 = (1 << 64) - 1
DESCRIPTOR = struct.Struct("<HHIQIIQQ16s8s")
METADATA = struct.Struct("<QQ48s")
TIMEOUT_NS = 1_000_000
LATE_NS = 2_000_000


def require(condition, message):
    if not condition:
        raise ValueError(message)


def uint(value, bits=64):
    require(type(value) is int and 0 <= value < 1 << bits, "Unsigned overflow/type")
    return value


def position(k):
    uint(k)
    segment, offset = divmod(k % 384, 128)
    return (0, 448, 896)[segment] + offset


def approved(pos):
    return type(pos) is int and any(
        a <= pos <= b for a, b in ((0, 127), (448, 575), (896, 1023))
    )


@dataclass(frozen=True)
class Descriptor:
    run: int
    presentation: int
    prefix: int
    intended: int
    submission: int
    token: bytes = TOKEN

    def encode(self):
        uint(self.run, 32)
        uint(self.presentation)
        uint(self.prefix, 32)
        require(approved(self.prefix), "Unapproved symbolic position")
        uint(self.intended)
        uint(self.submission)
        require(self.submission >= self.intended, "Submission precedes intended offer")
        require(self.token == TOKEN, "Only the fixture routing token is supported")
        return DESCRIPTOR.pack(
            VERSION,
            0,
            self.run,
            self.presentation,
            self.prefix,
            0,
            self.intended,
            self.submission,
            self.token,
            bytes(8),
        )

    @classmethod
    def decode(cls, blob):
        require(len(blob) == 64, "Descriptor is64bytes")
        v, flags, run, k, pos, reserved, intended, submission, token, tail = (
            DESCRIPTOR.unpack(blob)
        )
        require(
            v == VERSION and flags == reserved == 0 and tail == bytes(8),
            "Version/reserved fields",
        )
        result = cls(run, k, pos, intended, submission, token)
        result.encode()
        return result


def metadata(admission, sequence):
    return METADATA.pack(uint(admission), uint(sequence), bytes(48))


def read_metadata(blob):
    require(len(blob) == 64, "Metadata is64bytes")
    admission, sequence, reserved = METADATA.unpack(blob)
    require(reserved == bytes(48), "Slot metadata reserved bytes")
    return admission, sequence


class Scheduler:
    """One wake samples due offers, without constructing an arrival vector."""

    def __init__(self, t0, count=768, rate=500):
        uint(t0)
        require(type(count) is int and 1 <= count <= 768, "Bounded presentation count")
        require(type(rate) is int and 1 <= rate <= 1_000_000, "Integer rate")
        self.t0, self.count, self.rate, self.k = t0, count, rate, 0
        uint(self.horizon)

    def intended(self, k):
        require(0 <= k < self.count, "Presentation index")
        return self.t0 + k * 1_000_000_000 // self.rate

    @property
    def horizon(self):
        return self.t0 + self.count * 1_000_000_000 // self.rate

    def wake(self, now, emit):
        """emit(k,intended,action); attempts are decisions, never feedback paced."""
        uint(now)
        attempts = 0
        while self.k < self.count and self.intended(self.k) <= now:
            k, intended = self.k, self.intended(self.k)
            self.k += 1
            if now >= self.horizon:
                action = "missed_horizon"
            elif now - intended > LATE_NS:
                action = "missed_late"
            elif attempts >= 4:
                action = "missed_catchup_cap"
            else:
                action = "attempt"
                attempts += 1
            emit(k, intended, action)
        return None if self.k == self.count else self.intended(self.k)
