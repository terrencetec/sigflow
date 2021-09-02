
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
        self.blocks = blocks

    def add_edge(self, u, v, portu=0, portv=0):
        """Add a directed edge to the system's graph from node u's portu to
        node v's portv.

        Parameters
        """
        # 

        self._succ[u] = {portu: (v, portv)}
        self._pred[v] = {portv: (u, portu)}


    def clear_edges(self):
        """Clear all the connections in the system."""
        self.edge_table.clear()

    def __str__(self):
        """Description of the system in string."""
        seq = ["ID\tType\tLabel"]
        for i, block in enumerate(self.blocks):
            tmp = "\t".join(i, block.__class__.__name__, block.label)
            seq.append(tmp)
        return "\n".join(seq)

    @property
    def blocks(self):
        """blocks in the system."""
        return self._blocks

    @blocks.setter
    def blocks(self, blocks):
        """block setter."""
        if isinstance(blocks, Block):
            blocks = list(blocks)
        if isinstance(blocks, list):
            _blocks = [block for block in blocks if isinstance(block, Block)]
            if len(blocks) != len(_blocks):
                raise TypeError("blocks must be a list of Block objects")
            self._blocks = blocks

