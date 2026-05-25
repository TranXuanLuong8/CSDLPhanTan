STATE_INIT = "INIT"
STATE_WAIT = "WAIT"
STATE_PRE_COMMIT = "PRE_COMMIT"
STATE_COMMIT = "COMMIT"
STATE_ABORT = "ABORT"


class Coordinator:
    def __init__(self, node_id, network, participant_ids):
        self.node_id = node_id
        self.network = network
        self.participant_ids = list(participant_ids)
        self.state = STATE_INIT
        self.tx_id = None
        self.reservations = []
        self.votes = {}
        self.acks = {}
        self.log = []

    def on_message(self, message, from_id):
        msg_type = message["type"]
        if msg_type in ("VOTE_COMMIT", "VOTE_ABORT"):
            self._on_vote(message, from_id)
        elif msg_type == "ACK":
            self._on_ack(message, from_id)
        elif msg_type == "STATE_RESP":
            pass
        else:
            raise ValueError(f"Unknown message type: {msg_type}")

    def start_transaction(self, tx_id, reservations):
        self.tx_id = tx_id
        self.reservations = list(reservations)
        self.votes = {}
        self.acks = {}
        self.state = STATE_WAIT
        self.log.append((self.tx_id, self.state))

    def send_vote_req(self):
        for pid in self.participant_ids:
            self.network.send(self.node_id, pid, {
                "type": "VOTE_REQ",
                "tx_id": self.tx_id,
                "reservations": self.reservations,
            })

    def _on_vote(self, message, from_id):
        self.votes[from_id] = message["type"]

    def can_pre_commit(self):
        if len(self.votes) != len(self.participant_ids):
            return False
        return all(v == "VOTE_COMMIT" for v in self.votes.values())

    def send_pre_commit(self):
        if not self.can_pre_commit():
            self.state = STATE_ABORT
            self.log.append((self.tx_id, self.state))
            self._broadcast_abort()
            return False
        self.state = STATE_PRE_COMMIT
        self.log.append((self.tx_id, self.state))
        for pid in self.participant_ids:
            self.network.send(self.node_id, pid, {
                "type": "PRE_COMMIT",
                "tx_id": self.tx_id,
            })
        return True

    def _on_ack(self, message, from_id):
        self.acks[from_id] = True

    def can_commit(self):
        return len(self.acks) == len(self.participant_ids)

    def send_commit(self):
        if not self.can_commit():
            return False
        self.state = STATE_COMMIT
        self.log.append((self.tx_id, self.state))
        for pid in self.participant_ids:
            self.network.send(self.node_id, pid, {
                "type": "COMMIT",
                "tx_id": self.tx_id,
            })
        return True

    def _broadcast_abort(self):
        for pid in self.participant_ids:
            self.network.send(self.node_id, pid, {
                "type": "ABORT",
                "tx_id": self.tx_id,
            })

    def snapshot(self):
        return {
            "node": self.node_id,
            "state": self.state,
            "log": list(self.log),
        }
