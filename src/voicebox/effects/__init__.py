from voicebox.effects.chain import *
from voicebox.effects.dc_offset import *
from voicebox.effects.effect import *
from voicebox.effects.eq import *
from voicebox.effects.flanger import *
from voicebox.effects.glitch import *
from voicebox.effects.ring_mod import *
from voicebox.effects.normalize import *
from voicebox.effects.pedalboard import *
from voicebox.effects.tail import *
from voicebox.effects.vocoder import *


def default_effects() -> Effects:
    """Returns the default effects list, which is just ``[Normalize()]``."""
    return [Normalize()]
