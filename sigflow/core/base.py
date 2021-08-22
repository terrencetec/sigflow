from sigflow import Block

class System:
    """A generic system class that connect blocks.

    Attributes
    ----------
    
    """
    def __init__(self, blocks):
        """Constructor.

        Parameters
        ----------
        blocks : Block or list of Block.
            The block to be included in the system.
        """
        self.blocks = _blocks

    
    @property
    def blocks(self):
        """blocks in the system."""
        return self._blocks

    @blocks.setter
    def blocks(self, blocks):
        """block setter."""
        if isinstance(blocks, list):
            _blocks = [block for block in blocks if isinstance(block, Block)]
            if len(blocks) != len(_blocks):
                raise TypeError("blocks must be a list of Block objects")
        elif not isinstance(blocks, Block):
            raise TypeError("blocks must be of Block object")
        self._blocks = blocks

