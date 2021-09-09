import numpy as np

from sigflow.blocks import Block
from sigflow.core.utils import to_array

class System(Block):
    """A generic system class that connect blocks.

    Attributes
    ----------
    blocks : list of Block objects
        System's blocks which connect to each other.
    """
    def __init__(self, blocks=None, nin=0, nout=0):
        """Constructor.

        Parameters
        ----------
        blocks : Block or iterable of Block objects.
            The block to be included in the system.
        """
        if blocks is None:
            blocks = []

        ## node table
        blocks = to_array(blocks, Block)
        ids = range(len(blocks))
        self.blocks = dict(enumerate(blocks))
        self._ids = dict(zip(blocks, ids))

        ## adjacency list
        out_ports = [[{}]*block.noutput for block in blocks]
        self._succ = dict(zip(ids, out_ports))

        self._set = False # indicate if starting block is set.
        in_ports = [[0.]*block.ninput for block in blocks]
        self._pending = dict(zip(ids, in_ports))
        self.set_ninout(nin, nout)

    def set_ninout(self, ninput, noutput=0):
        """Set the input and output blocks of the system.
        System then behaves like a block, with definite input and output.

        Parameters
        ----------
        ninput : int
            number of input port of the system.
        output_blocks : int, optional
            number of output port of the system.
            Defaults to 0.
        """
        self.ninput = ninput
        self.noutput = noutput
        if ninput > 0:
            self._succ = {**self._succ, **{"input": [{}]*ninput}}
        if noutput > 0:
            self._pending = {**self._pending, **{"output": [{}]*noutput}}
        self._set = True

    def _i2o(self):
        """Method to convert the input signal to an output signal.

        Returns
        -------
        list
        """
        if not self._set:
            raise ValueError("self.input_blocks is not set."
                             "Set it by using self.set_blocks method.")
        ## for short hand
        inputs = self.inputs
        pending = self._pending
        visited = {}.fromkeys(self.blocks.keys(), False)
        ## block waiting to process in breadth first search method,
        ## may have duplicates
        queue = []
        ## reset to block input=list of zero if block mutated
        for ids, data in pending.items():
            if ids != "input" and ids != "output":
                length = self.blocks[ids].ninput
                if len(data) != length:
                    pending[ids] = [0.]*length
        ## setting input to the system to blocks' inputs
        for from_port in range(self.ninput):
            for target_id, to_port in self._succ["input"][from_port].items():
                queue.append(target_id)    # add blocks to be run
                pending[target_id][to_port] = self.inputs[from_port]


        while len(queue):
            current_id = queue.pop(0)
            if visited[current_id]:
                continue

            visited[current_id] = True
            current_block = self.blocks[current_id]

            ## setting predessors output as successor's input
            if current_block.ninput > 1:
                ## setting each element of the input as the same size
                tmp = np.broadcast(*pending[current_id])
                pending[current_id] = np.column_stack(tuple(tmp))
                current_block.inputs = pending[current_id]
            else:
                current_block.inputs = pending[current_id][0]
            ## process input to output
            tmp_output = current_block.output

            ports = self._succ[current_id] # nested dict of target blocks
            for from_port in range(len(ports)):
                ## caching data
                for target_id, to_port in ports[from_port].items():
                    if target_id != "output":
                        queue.append(target_id)    # add blocks to be run
                    pending[target_id][to_port] = tmp_output[from_port]
        if self.noutput > 0:
            res = pending["output"].copy()
        else:
            res = None
        return res

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
        blocks = to_array(blocks, types=Block)
        new_ids = range(id_start, id_start+len(blocks))
        out_ports = [[{}]*block.noutput for block in blocks]
        self.blocks = {**self.blocks,
                       **dict(zip(new_ids, blocks))}
        self._ids = {**self._ids,
                     **dict(zip(blocks, new_ids))}
        self._succ = {**self._succ,
                      **dict(zip(new_ids, out_ports))}
        in_ports = [[0.]*block.ninput for block in blocks]
        self._pending = {**self._pending,
                         **dict(zip(new_ids, in_ports))}

    def add_edge(self, edge_from, edge_to, from_port=0, to_port=0):
        """Add a directed connection from block out_edge to in_edge.

        Parameters
        ----------
        edge_from : Block object, block_id, or 'input'
            The block to connect from.
            'input' indicates system's input.
        edge_to : Block object, block_id, or 'output'
            The block to connect to.
            'output' indicates system's output
        from_port : int, optional
            The output port to connect from.
            out_port must be smaller than noutput of the block.
            Defaults to 0.
        to_port : int, optional
            The input port to connect from.
            in_port must be smaller than ninput of the block.
            Defaults to 0.
        """
        self._check_block_exists(edge_from)
        self._check_block_exists(edge_to)
        if isinstance(edge_from, Block):
            from_id = self._ids[edge_from]
        else:
            from_id = edge_from
        if isinstance(edge_to, Block):
            to_id = self._ids[edge_to]
        else:
            to_id = edge_to

        ## check valid port
        if from_id == "input":
            nport = self.ninput
        else:
            nport = self.blocks[from_id].ninput
        if from_port >= nport:
            raise ValueError("invalid from port {} for id:{}"
                             "".format(from_port, from_id))
        if to_id == "output":
            nport = self.noutput
        else:
            nport = self.blocks[to_id].ninput
        if to_port >= nport:
            raise ValueError("invalid to port {} for id:{}"
                             "".format(from_port, to_id))

        ## add edge
        target_dict = self._succ[from_id][from_port]
        self._succ[from_id][from_port] = {**target_dict, **{to_id: to_port}}

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
        del self._succ[from_id][from_port][to_id]

    def clear_edges(self):
        """Clear all the connections in the system."""
        succ = [(i, [{}]*block.noutput) for i, block in self.blocks.items()]
        self._succ = dict(succ)

    def remove_blocks(self, blocks):
        """Remove blocks from the system.

        Parameters
        ----------
        blocks : Block or list of Block
            Blocks to remove from the system.
        """
        blocks = to_array(blocks, types=Block)
        for delete in blocks:
            self._check_block_exists(delete)
            del_id = self._ids[delete]
            self._remove_block(del_id)

    def remove_by_id(self, block_id):
        """Remove blocks from the system.

        Parameters
        ----------
        block_id : int or list of int
            ID of the blocks to remove from the system.
        """
        blocks_id = to_array(block_id, np.integer)
        for del_id in blocks_id:
            self._check_block_exists(del_id)
            self._remove_block(del_id)

    def _remove_block(self, del_id):
        delete = self.blocks.pop(del_id)
        del self._ids[delete]
        del self._pending[del_id]

        for dictionary in [self._succ]:
            del dictionary[del_id]
            for key in dictionary:
                for port in range(len(dictionary[key])):
                    if del_id in dictionary[key][port]:
                        del dictionary[key][port][del_id]

    def _check_block_exists(self, block):
        """An internal method to check if block is in the system.

        Parameters
        ----------
        block : Block objects, or block_id
        """
        if isinstance(block, Block):
            if block not in self._ids:
                raise LookupError("{} doesn't exist in the system"
                                  "".format(block))
        elif isinstance(block, (int, np.integer)):
            if block not in self.blocks:
                raise LookupError("ID {:d} doesn't exist in the system"
                                  "".format(block))
        elif block != "input" and block != "output":
            print(block)
            raise TypeError("wrong type to call block")

    def connections(self):
        """Connections of blocks in the system."""
        seq = ["Connections:"]
        seq.append("from_id\tfrom_port\tto_id\tto_port")
        seq.append(str(self._succ))
        return "\n".join(seq)

    def __str__(self):
        """Description of the system in string."""
        seq = ["{:<6s} {:<14s} {:s}".format("ID", "type", "label")]
        for i, block in self.blocks.items():
            tmp = "{:<6d} {:<14s} {:s}".format(i,
                                               block.__class__.__name__,
                                               str(block.label))
            seq.append(tmp)
        seq = "\n".join(seq)
        seq += "\n" + self.connections()
        return seq

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
    @property
    def inputs(self):
        return self._inputs

    @inputs.setter
    def inputs(self, values):
        """inputs setter"""
        values = to_array(values, (np.integer, np.floating, np.ndarray))
        # print("inputs :", values)
        if len(values) != self.ninput:
            raise ValueError("expected input size of {} in axis 0, "
                             "got {} instead".format(self.ninput, len(values)))
        self._inputs = values
