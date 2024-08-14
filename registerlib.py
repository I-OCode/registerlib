# registerlib - A library to manipulate Roblox <Circuit Maker 2> registers.
#
# Data is seperated into three sections via question marks:
# <block data>?<connection data>?<Im not sure whats put here, prob custom blocks>?
#
#
# Block data is comprised of blocks, like so:
# <block type>,<state (on/off)>,<pos-x>,<pos-y>,<pos-z>,<config options seperated by plus signs>
#
# Multiple blocks are seperated by semicolons.
#
#
# Connection data is comprised of connections, like so:
# <from>,<to>
#
# <from> and <to> are indexes into the block data, which start at index 1
# Multiple connections are seperated by semicolons.
#

import enum

# First element is block type,
# second element is "default state."
class BlockType (enum.Enum):
    NOR           = (0, 1)
    AND           = (1, 0)
    OR            = (2, 0)
    XOR           = (3, 0)
    Button        = (4, 0)
    Flip_flop_OFF = (5, 0)
    Flip_flop_ON  = (5, 1)
    LED           = (6, 0)
    Sound         = (7, 0)
    Conductor     = (8, 0)
    MysteriousOR  = (9, 0)
    NAND          = (10, 1)
    XNOR          = (11, 1)
    Random        = (12, 1)
    Text          = (13, 0)
    Tile          = (14, 0)
    Node          = (15, 0)
    Delay         = (16, 0)
    Antenna       = (17, 0)
    ConductorV2   = (18, 0)
    LEDMixer      = (19, 0)

# Enumeration of the different instruments
# in a sound block's configuration.
class SoundInstrumentType:
    Sine     = 0
    Square   = 1
    Triangle = 2
    Sawtooth = 3

# The main class for manipulating registers.
class Register:
    blocks = []
    connections = []

    def __init__ (self):
        pass

    # Add a block to the register.
    #
    # blockType - `BlockType` object representing the type of the block.
    # position - Position of the block represented by a 3-element tuple. (x, y, and z)
    # on - Determines whether the block should be on or off.
    # properties - A list of numbers that is used in the configuration of a block. Use `SoundInstrumentType` for instruments in sound blocks.
    #
    # Returns: An ID representing the newly created block.
    def add_block (self, blockType, position, on=None, properties=[]) -> int:
        if on == None:
            on = isOnByDefault(blockType)

        if blockType == BlockType.Flip_flop_OFF:
            self.blocks.append((blockType.value[0], int(on), *position, "0+0"))
        elif blockType == BlockType.Flip_flop_ON:
            self.blocks.append((blockType.value[0], int(on), *position, "2+0"))
        else:
            self.blocks.append((blockType.value[0], int(on), *position, "+".join(list(map(str, properties)))))

        return len(self.blocks) - 1

    # Add a connection to the register.
    #
    # fromID - The ID of the block that the connection should connect from.
    # toID - The ID of the block that the connection should connect to.
    #
    # Returns: An ID representing the newly created connection.
    def add_connection (self, fromID, toID) -> int:
        self.connections.append((fromID, toID))
        return len(self.blocks) - 1

    # Remove a block from the register.
    #
    # blockID - The ID of the block to remove.
    def remove_block (self, blockID) -> None:
        del self.blocks[blockID]

    # Remove a connection from the register.
    #
    # connectionID - The ID of the connection to remove.
    def remove_connection (self, connectionID) -> None:
        del self.blocks[connectionID]

    # Clears all blocks and connections from the register.
    def clear (self) -> None:
        self.blocks.clear()
        self.connections.clear()

    # Converts internal data to serialized data to be used in
    # the main game.
    def serialize (self) -> None:
        output = ""

        for block in self.blocks:
            output += ",".join(list(map(str, block))) + ";"

        if output[-1] == ";":
            output = output[:-1] + "?"

        for connection in self.connections:
            output += ",".join(list(map(lambda x: str(x+1), connection))) + ";"

        if output[-1] == ";":
            output = output[:-1] + "?"

        return output + "?"

# Checks whether a block is on by default.
#
# blockType - The block to check.
def isOnByDefault (blockType) -> bool:
    return bool(blockType.value[1])
