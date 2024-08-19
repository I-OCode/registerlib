# registerlib - A library to manipulate Roblox <Circuit Maker 2> registers.
#
# Data is seperated into four sections via question marks:
# <block data>?<connection data>?<building data>?<text data>
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
# TODO: Describe and implement building data and text data

import enum

__author__ = "I/O Code"
__version__ = "v0.2"

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

    def __init__ (self, data=""):
        if not data:
            pass

        blocks, connections, buildings, textData = data.split("?")

        blocks = blocks.split(";")
        connections = connections.split(";")

        for block in blocks:
            elements = block.split(",")

            n1v = int(elements[0])
            try:
                n1 = BlockType((n1v, 0))
            except ValueError:
                n1 = BlockType((n1v, 1))

            n2 = bool(int(elements[1]))
            n3 = tuple(map(float, elements[2:5]))
            if elements[5]:
                n4 = list(map(float, elements[5].split("+")))
            else:
                n4 = []

            self.add_block(n1, n3, on=n2, properties=n4)

        for connection in connections:
            elements = connection.split(",")

            n1 = int(elements[0]) - 1
            n2 = int(elements[1]) - 1

            self.add_connection(n1, n2)

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
            self.blocks.append([blockType, on, position, [0, 0], []])
        elif blockType == BlockType.Flip_flop_ON:
            self.blocks.append([blockType, on, position, [2, 0], []])
        else:
            self.blocks.append([blockType, on, position, properties, []])

        return len(self.blocks) - 1

    # Add a connection to the register.
    #
    # fromID - The ID of the block that the connection should connect from.
    # toID - The ID of the block that the connection should connect to.
    #
    # Returns: An ID representing the newly created connection.
    def add_connection (self, fromID, toID) -> int:
        self.connections.append([fromID, toID])
        ID = len(self.connections) - 1

        self.blocks[fromID][4].append(ID)
        self.blocks[toID][4].append(ID)

        return ID

    # Get a dictionary of the form
    #   {
    #      "type": BlockType,
    #      "position": tuple[int, int, int],
    #      "on": bool,
    #      "properties": list[float],
    #      "connections": list[int]
    #   }
    #
    # describing the data of a block.
    # Note: "connections" is a list of connection IDs.
    #
    # blockID - The ID of the block to inspect.
    def get_block (self, blockID) -> dict:
        block = self.blocks[blockID]

        return {
            "type": block[0],
            "on": block[1],
            "position": block[2],
            "properties": block[3],
            "connections": block[4]
        }

    # Get a dictionary of the form
    #   {
    #      "fromID": int,
    #      "toID": int
    #   }
    #
    # describing the data of a connection.
    #
    # connectionID - The ID of the connection to inspect.
    def get_connection (self, connectionID) -> dict:
        connection = self.connections[connectionID]

        return {
            "fromID": connection[0],
            "toID": connection[1]
        }

    # Change type, position, state, and properties (but not connections)
    # of an existing block.
    #
    # blockID - The ID of the block to transmogrify.
    def transmogrify_block (self, blockID, blockType, position, on=None, properties=[]) -> None:
        if on == None:
            on = isOnByDefault(blockType)

        self.blocks[blockID][0] = blockType
        self.blocks[blockID][1] = on
        self.blocks[blockID][2] = position

        if blockType == BlockType.Flip_flop_OFF:
            self.blocks[blockID][3] = [0, 0]
        elif blockType == BlockType.Flip_flop_ON:
            self.blocks[blockID][3] = [2, 0]
        else:
            self.blocks[blockID][3] = properties

    # Change where an existing connection connects to and from.
    #
    # connectionID - The ID of the connection to transmogrify.
    def transmogrify_connection (self, connectionID, fromID, toID) -> None:
        self.connections[connectionID][0] = fromID
        self.connections[connectionID][1] = toID

    # Get the number of blocks in the register.
    def num_blocks (self) -> int:
        return len(self.blocks)

    # Get the number of connections in the register.
    def num_connections (self) -> int:
        return len(self.connections)

    # Converts internal data to serialized data to be used in
    # the main game.
    def serialize (self) -> None:
        output = ""

        for block in self.blocks:
            n1 = block[0].value[0]
            n2 = int(block[1])
            n3, n4, n5 = block[2]
            n6 = "+".join(map(str, block[3]))

            n = ",".join(map(str, (n1, n2, n3, n4, n5, n6)))
            output += n + ";"

        if output[-1] == ";":
            output = output[:-1] + "?"

        for connection in self.connections:
            n1 = connection[0] + 1
            n2 = connection[1] + 1

            n = str(n1) + "," + str(n2)            
            output += n + ";"

        if output[-1] == ";":
            output = output[:-1] + "?"

        return output + "?"

# Checks whether a block is on by default.
#
# blockType - The block to check.
def isOnByDefault (blockType) -> bool:
    return bool(blockType.value[1])
