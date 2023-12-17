from voicebox.effects.chain import *
from voicebox.effects.dc_offset import *
from voicebox.effects.delay import *
from voicebox.effects.distortion import *
from voicebox.effects.effect import Effects
from voicebox.effects.eq import *
from voicebox.effects.flanger import *
from voicebox.effects.glitch import *
from voicebox.effects.modulation import *
from voicebox.effects.normalize import *
from voicebox.effects.pedalboard import *
from voicebox.effects.vocoder import *


def default_effects() -> Effects:
    """Returns the default effects list, which is just ``[Normalize()]``."""
    return [Normalize()]
