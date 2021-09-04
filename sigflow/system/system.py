from sigflow.blocks import Block
from sigflow.core.utils import to_list


class System:
    """A generic system class that connect blocks.

    Attributes
    ----------
    blocks : list of Block objects
        System's blocks which connect to each other.
    fs : int or float
        Sampling frequency of the system.
        For z-transform usage.
    """
    def __init__(self, blocks=None):
        """Constructor.

        Parameters
        ----------
        blocks : Block or iterable of Block objects.
            The block to be included in the system.
        """
        if blocks is None:
            blocks = []
        ids = range(len(blocks))
        self.blocks = dict(enumerate(blocks))
        self._ids = dict(zip(blocks, ids))
        self._inout = False # indicate if find_inout is run.
        self._succ = {}.fromkeys(ids, {})
        self._pred = {}.fromkeys(ids, {})

    def add_blocks(self, blocks):
        """Add blocks to the system

        Parameters
        ----------
        blocks : Block or iterable of Block objects.
            The block to add in the system.
        """
        if len(self.blocks) == 0:
            id_start = 0
        else:
            last_id = max(self.blocks)
            id_start = last_id + 1
        blocks = to_list(blocks, types=Block)
        new_ids = range(id_start, id_start+len(blocks))
        self.blocks = {**self.blocks, **dict(zip(new_ids, blocks))}
        self._ids = {**self._ids, **dict(zip(blocks, new_ids))}
        self._succ = {**self._succ, **dict(zip(new_ids, [{}]*len(new_ids)))}
        self._pred = {**self._pred, ** dict(zip(new_ids, [{}]*len(new_ids)))}


    def add_edge(self, edge_from, edge_to, from_port=0, to_port=0):
        """Add a directed connection from block out_edge to in_edge.

        Parameters
        ----------
        edge_from : Block or block_id
            The block to connect from.
        edge_to : Block or block_id
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
        edge_from_exist = (edge_from in self.blocks.values()
                           or edge_from in self.blocks)
        edge_to_exist = (edge_to in self.blocks.values()
                         or edge_to in self.blocks)
        if not edge_from_exist:
            raise ValueError("edge_from not in system's blocks")
        if not edge_to_exist:
            raise ValueError("edge_to not in system's blocks")

        if isinstance(edge_from, Block):
            from_id = self._ids[edge_from]
        else:
            from_id = edge_from
        if isinstance(edge_to, Block):
            to_id = self._ids[edge_to]
        else:
            to_id = edge_to

        # add edge
        if to_id in self._succ[from_id]:
            self._succ[from_id][to_id].update({from_port: to_port})
        else:
            self._succ[from_id] = {to_id: {from_port: to_port}}

        if from_id in self._pred[to_id]:
            self._pred[to_id][from_id].update({from_port: to_port})
        else:
            self._pred[to_id] = {from_id: {from_port: to_port}}
        self._inout = False

    def remove_edge(self, edge_from, edge_to, from_port=0, to_port=0):
        """Remove the given edge from the system.

        Parameters
        ----------
        edge_from : Block or block_id
            The block to connect from.
        edge_to : Block or block_id
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
        if isinstance(edge_from, Block):
            from_id = self._ids[edge_from]
        else:
            from_id = edge_from
        if isinstance(edge_to, Block):
            to_id = self._ids[edge_to]
        else:
            to_id = edge_to
        del self._succ[from_id][to_id][from_port]
        del self._pred[to_id][from_id][from_port]
        self._inout = False

    def clear_edges(self):
        """Clear all the connections in the system."""
        ids = range(len(self.blocks))
        self._succ = {}.fromkeys(ids, {})
        self._pred = {}.fromkeys(ids, {})
        self._inout = False

    def remove_blocks(self, blocks):
        """Remove blocks from the system.

        Parameters
        ----------
        blocks : Block or list of Block
            Blocks to remove from the system.
        """
        blocks = to_list(blocks, types=Block)
        for delete in blocks:
            try:
                del_id = self._ids.pop(delete)
            except KeyError:
                raise ValueError("block not in the system")

            del self.blocks[del_id]
            for dictionary in [self._succ, self._pred]:
                del dictionary[del_id]
                for key in dictionary:
                    if del_id in dictionary[key]:
                        del dictionary[key][del_id]
        self._inout = False

    def remove_by_id(self, block_id):
        """Remove blocks from the system.

        Parameters
        ----------
        block_id : int or list of int
            ID of the blocks to remove from the system.
        """
        blocks_id = to_list(block_id, int)
        for del_id in blocks_id:
            delete = self.blocks.pop(del_id)
            del self._ids[delete]
            for dictionary in [self._succ, self._pred]:
                del dictionary[del_id]
                for key in dictionary:
                    if del_id in dictionary[key]:
                        del dictionary[key][del_id]
        self._inout = False

    def _find_inout(self):
        # find ending blocks
        if self._inout is False:
            starting_blocks = []
            ending_blocks = []
            for stat, table in zip([starting_blocks, ending_blocks],
                                   [self._pred, self._succ]):
                for block_id in table:
                    if len(table[block_id]) == 0:
                        stat.append(block_id)
            self.inputs = starting_blocks
            self.outputs = ending_blocks
            self._inout = True

    def __call__(self, inputs):
        """Traverse the system once.

        Parameters
        ----------
        inputs : dict
            Block objects as keys,
            float, int or array as value for system inputs.
        """
        if not isinstance(inputs, dict):
            raise TypeError("inputs must be a dict, not %s"\
                            % type(inputs).__name__)
        for key in inputs:
            if isinstance(key, Block):
                try:
                    block_id = self._ids[key]
                except KeyError:
                    raise ValueError(key, "doesn't exist in the system")
                self.blocks[block_id].inputs = inputs[key]
            if isinstance(key, int):
                try:
                    self.blocks[key].inputs = inputs[key]
                except KeyError:
                    raise ValueError("ID %d doesn't exist in the system"%key)

        self._find_inout()
        visited = {}.fromkeys(self.blocks.keys(), False)
        # block waiting to process in breadth first search method,
        # may have duplicates
        queue = [block_id for block_id in self.inputs]

        # pending output data to be set with inputs
        pending = {}

        while len(queue):
            current_id = queue.pop(0)
            if visited[current_id] is False:
                visited[current_id] = True
                current_block = self.blocks[current_id]
                # setting predessors output as successor's input
                if current_id in pending:
                    if current_block.ninput > 1:
                        current_block.inputs = pending[current_id]
                    else:
                        current_block.inputs = pending[current_id][0]

                # process input to output
                tmp_output = current_block.output

                # a nested dict of target blocks
                table = self._succ[current_id]
                for target_id in table:
                    queue.append(target_id)    # add blocks to be run
                    if target_id not in pending:
                        n = self.blocks[target_id].ninput
                        pending.update({target_id: [0]*n})

                    for from_port in table[target_id]:
                        to = table[target_id][from_port]
                        if current_block.noutput > 1:
                            pending[target_id][to] = tmp_output[from_port]
                        else:
                            pending[target][to] = tmp_output
        values = [self.blocks[block_id].output for block_id in self.outputs]
        res = dict(zip(self.outputs, values))
        return res

    def __str__(self):
        """Description of the system in string."""
        seq = ["{:<6s} {:<14s} {:s}".format("ID", "type", "label")]
        for i, block in self.blocks.items():
            tmp = "{:<6s} {:<14s} {:s}".format(i,
                                               block.__class__.__name__,
                                               str(block.label))
            seq.append(tmp)
        seq.append("\nConnections:")
        seq.append("from_id\tto_id\tfrom_port\tto_port")
        seq.append(str(self._succ))
        return "\n".join(seq)

    @property
    def blocks(self):
        """blocks in the system and their corresponding id."""
        if self._blocks is None:
            raise ValueError("self.blocks is not set, please add blocks"
                             " before using the system")
        return self._blocks

    @blocks.setter
    def blocks(self, blocks):
        """block setter."""
        if isinstance(blocks, dict):
            for block in blocks.values():
                if not isinstance(block, Block):
                    raise TypeError("System.blocks dict's value must be Block\
                                    objects, not %s"%type(block).__name__)
            self._blocks = blocks
        else:
            raise TypeError("blocks must be of type dict, not %s"\
                             % type(blocks).__name__)


