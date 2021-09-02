from sigflow.blocks import Block


class System:
    """A generic system class that connect blocks.

    Attributes
    ----------

    """
    def __init__(self, blocks, fs):
        """Constructor.

        Parameters
        ----------
        blocks : Block or list of Block.
            The block to be included in the system.
        """
        self.blocks = blocks
        self.fs = fs
        self._inout = False # indicate if find_inout is run.
        self._succ = {}.fromkeys(self.blocks, {})
        self._pred = {}.fromkeys(self.blocks, {})

    def add_blocks(self, blocks):
        """Add blocks to the system

        Parameters
        ----------
        blocks : Block or list of Block
            The block to add in the system.
        """
        if isinstance(blocks, list):
            self.blocks += blocks
            for blk in blocks:
                self._succ.update({blk: {}})
                self._pred.update({blk: {}})
        elif isinstance(blocks, Block):
            self.blocks.append(blocks)
            self._succ.update({blocks: {}})
            self._pred.update({blocks: {}})
        else:
            raise TypeError("blocks must be of type Block or list, not %s"%
                            type(blocks).__name__)

    def remove_blocks(self, blocks):
        """Remove blocks from the system.

        Parameters
        ----------
        blocks : Block or list of Block
            Blocks to remove from the system.
        """
        if not isinstance(blocks, list):
            blocks = [blocks]
        for delete in blocks:
            for dictionary in [self._succ, self._pred]:
                del dictionary[delete]
                for key in dictionary:
                    if delete in dictionary[key]:
                        del dictionary[key][delete]
        self._inout = False


    def add_edge(self, edge_from, edge_to, from_port=0, to_port=0):
        """Add a directed connection from block out_edge to in_edge.

        Parameters
        ----------
        edge_from : Block
            The block to connect from.
        edge_to : Block
            The block to connect to.
        from_port : int, optional
            The output port to connect from.
            out_port must be smaller tha noutput of the block.
            Defaults to 0.
        to_port : int, optional
            The input port to connect from.
            in_port must be smaller tha ninput of the block.
            Defaults to 0.
        """
        # error check, need to add
        if edge_from not in self.blocks:
            raise ValueError("edge_from not in system's blocks")
        if edge_to not in self.blocks:
            raise ValueError("edge_to not in system's blocks")

        # add edge
        if edge_to in self._succ[edge_from]:
            self._succ[edge_from][edge_to].update({from_port: to_port})
        else:
            self._succ[edge_from].update({edge_to: {from_port: to_port}})

        if edge_from in self._pred[edge_to]:
            self._pred[edge_to][edge_from].update({from_port: to_port})
        else:
            self._pred[edge_to].update({edge_from: {from_port: to_port}})
        self._inout = False

    def remove_edge(self, edge_from, edge_to, from_port=0, to_port=0):
        del self._succ[edge_from][edge_to][from_port]
        del self._pred[edge_to][edge_from][from_port]
        self._inout = False

    def clear_edges(self):
        """Clear all the connections in the system."""
        self._succ = {}.fromkeys(self.blocks, {})
        self._pred = {}.fromkeys(self.blocks, {})
        self._inout = False

    def _find_inout(self):
        # find ending blocks
        if self._inout is False:
            starting_blocks = []
            ending_blocks = []
            for stat, table in zip([starting_blocks, ending_blocks],
                                   [self._pred, self._succ]):
                for block in table:
                    if len(table[block]) == 0:
                        stat.append(block)
            self.inputs = starting_blocks
            self.outputs = ending_blocks
            self._inout = True

    def __call__(self, inputs):
        """Traverse the system once.

        Parameters
        ----------
        input_dict : dict
            Block objects as keys,
            float, int or array as value for system inputs.
        """
        for block in inputs:
            block.inputs = inputs[block]

        self._find_inout()
        visited = {}.fromkeys(self.blocks, False)
        # block waiting to process in breadth first search method,
        # may have duplicates
        queue = [block for block in self.inputs]

        # pending output data to be set with inputs
        pending = {}

        while len(queue):
            current_block = queue.pop(0)
            if visited[current_block] is False:
                visited[current_block] = True

                # setting predessors output as successor's input
                if current_block in pending:
                    if current_block.ninput > 1:
                        current_block.inputs = pending[current_block]
                    else:
                        current_block.inputs = pending[current_block][0]

                # process input to output
                tmp_output = current_block.output

                # a nested dict of target blocks
                table = self._succ[current_block]
                for target in table:
                    queue.append(target)    # add blocks to be run
                    if target not in pending:
                        pending.update({target: [0]*target.ninput})

                    for from_port in table[target]:
                        to = table[target][from_port]
                        if current_block.noutput > 1:
                            pending[target][to] = tmp_output[from_port]
                        else:
                            pending[target][to] = tmp_output
        return [block.output for block in self.outputs]

    def __str__(self):
        """Description of the system in string."""
        seq = ["ID\tType\t\tLabel"]
        seq.append("-"*len(seq[0]))
        for i, block in enumerate(self.blocks):
            tmp = "\t".join([str(i), block.__class__.__name__, block.label])
            seq.append(tmp)
        return "\n".join(seq)

    @property
    def blocks(self):
        """blocks in the system."""
        return self._blocks

    @blocks.setter
    def blocks(self, blocks):
        """block setter."""
        if blocks is None:
            self._blocks = None
        if isinstance(blocks, Block):
            blocks = list(blocks)
        if isinstance(blocks, list):
            _blocks = [block for block in blocks if isinstance(block, Block)]
            if len(blocks) != len(_blocks):
                raise TypeError("blocks must be a list of Block objects")
            self._blocks = blocks

