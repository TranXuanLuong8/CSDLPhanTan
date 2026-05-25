class Network:
    def __init__(self):
        self.nodes = {}
        self.partitions = None
        self.dropped = []

    def register(self, node_id, node):
        self.nodes[node_id] = node

    def set_partitions(self, partitions):
        # partitions: list of sets of node_ids
        self.partitions = [set(p) for p in partitions]

    def clear_partitions(self):
        self.partitions = None

    def can_reach(self, from_id, to_id):
        if self.partitions is None:
            return True
        for part in self.partitions:
            if from_id in part and to_id in part:
                return True
        return False

    def send(self, from_id, to_id, message):
        if to_id not in self.nodes:
            raise KeyError(f"Unknown node: {to_id}")
        if not self.can_reach(from_id, to_id):
            self.dropped.append((from_id, to_id, message))
            return False
        self.nodes[to_id].on_message(message, from_id)
        return True

    def request_state(self, from_id, to_id, tx_id):
        if to_id not in self.nodes:
            return None
        if not self.can_reach(from_id, to_id):
            return None
        return self.nodes[to_id].get_state(tx_id)

    def reachable_nodes(self, from_id, candidates):
        return [n for n in candidates if self.can_reach(from_id, n)]
