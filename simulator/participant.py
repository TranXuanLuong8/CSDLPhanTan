import json

STATE_INIT = "INIT"
STATE_WAIT = "WAIT"
STATE_PRE_COMMIT = "PRE_COMMIT"
STATE_COMMIT = "COMMIT"
STATE_ABORT = "ABORT"


class Participant:
    def __init__(self, node_id, network, datastores, owned_resources, peer_ids, log_path=None):
        self.node_id = node_id
        self.network = network
        self.datastores = datastores
        self.owned_resources = set(owned_resources)
        self.peer_ids = list(peer_ids)
        self.state = STATE_INIT
        self.tx_id = None
        self.log = []
        self.pending_reservations = []
        self.log_path = log_path
        if self.log_path:
            self._load_log()

    def on_message(self, message, from_id):
        msg_type = message["type"]
        if msg_type == "VOTE_REQ":
            self._on_vote_req(message, from_id)
        elif msg_type == "PRE_COMMIT":
            self._on_pre_commit(message, from_id)
        elif msg_type == "COMMIT":
            self._on_commit(message, from_id)
        elif msg_type == "ABORT":
            self._on_abort(message, from_id)
        elif msg_type == "STATE_REQ":
            self._on_state_req(message, from_id)
        else:
            raise ValueError(f"Unknown message type: {msg_type}")

    def _on_vote_req(self, message, from_id):
        self.tx_id = message["tx_id"]
        self.pending_reservations = message["reservations"]
        self.state = STATE_WAIT
        self._append_log(self.state, reservations=self.pending_reservations)
        decision = self._can_commit()
        if decision:
            self.network.send(self.node_id, from_id, {
                "type": "VOTE_COMMIT",
                "tx_id": self.tx_id,
            })
        else:
            self.state = STATE_ABORT
            self._append_log(self.state)
            self.network.send(self.node_id, from_id, {
                "type": "VOTE_ABORT",
                "tx_id": self.tx_id,
            })
    
    def _on_pre_commit(self, message, from_id):
        if self.state != STATE_WAIT:
            return
        self.state = STATE_PRE_COMMIT
        self._append_log(self.state)
        self.network.send(self.node_id, from_id, {
            "type": "ACK",
            "tx_id": self.tx_id,
        })

    def _on_commit(self, message, from_id):
        if self.state in (STATE_COMMIT, STATE_ABORT):
            return
        self._apply_reservations()
        self.state = STATE_COMMIT
        self._append_log(self.state)

    def _on_abort(self, message, from_id):
        if self.state == STATE_COMMIT:
            return
        self.state = STATE_ABORT
        self._append_log(self.state)

    def _on_state_req(self, message, from_id):
        self.network.send(self.node_id, from_id, {
            "type": "STATE_RESP",
            "tx_id": self.tx_id,
            "state": self.state,
        })

    def get_state(self, tx_id):
        if tx_id != self.tx_id:
            return None
        return self.state

    def handle_pre_commit_timeout(self):
        if self.state != STATE_PRE_COMMIT:
            return None
        states = []
        for peer in self.peer_ids:
            if peer == self.node_id:
                continue
            state = self.network.request_state(self.node_id, peer, self.tx_id)
            if state is not None:
                states.append(state)
        decision = self._termination_decision(states)
        if decision == STATE_COMMIT:
            self._apply_reservations()
        self.state = decision
        self._append_log(self.state)
        return decision

    def handle_wait_timeout(self):
        if self.state != STATE_WAIT:
            return None
        states = []
        for peer in self.peer_ids:
            if peer == self.node_id:
                continue
            state = self.network.request_state(self.node_id, peer, self.tx_id)
            if state is not None:
                states.append(state)
        decision = self._wait_termination_decision(states)
        if decision == STATE_COMMIT:
            self._apply_reservations()
        self.state = decision
        self._append_log(self.state)
        return decision

    def _termination_decision(self, states):
        # Textbook Alignment: 3PC Termination Protocol (Özsu) cho Node đang ở PRE_COMMIT
        if any(s == STATE_ABORT for s in states):
            return STATE_ABORT
        if any(s == STATE_COMMIT for s in states):
            return STATE_COMMIT
        return STATE_COMMIT

    def _wait_termination_decision(self, states):
        # Textbook Alignment: 3PC Termination Protocol (Özsu) cho Node đang ở WAIT
        if any(s == STATE_ABORT for s in states):
            return STATE_ABORT
        if any(s == STATE_COMMIT for s in states):
            return STATE_COMMIT
        if any(s == STATE_PRE_COMMIT for s in states):
            return STATE_COMMIT
        return STATE_ABORT

    def _can_commit(self):
        for item in self.pending_reservations:
            if item["resource"] not in self.owned_resources:
                continue
            store = self.datastores[item["resource"]]
            if not store.can_reserve(item["item_id"], item["qty"]):
                return False
        return True

    def _apply_reservations(self):
        for item in self.pending_reservations:
            if item["resource"] not in self.owned_resources:
                continue
            store = self.datastores[item["resource"]]
            store.reserve(item["item_id"], item["qty"])

    def snapshot(self):
        return {
            "node": self.node_id,
            "state": self.state,
            "log": list(self.log),
        }

    def _append_log(self, state, reservations=None):
        entry = {
            "tx_id": self.tx_id,
            "state": state,
        }
        if reservations is not None:
            entry["reservations"] = list(reservations)
        self.log.append((self.tx_id, state))
        if self.log_path:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")

    def _load_log(self):
        try:
            with open(self.log_path, "r", encoding="utf-8") as f:
                last_tx = None
                last_state = None
                last_reservations = None
                for line in f:
                    if not line.strip():
                        continue
                    entry = json.loads(line)
                    last_tx = entry.get("tx_id")
                    last_state = entry.get("state")
                    if "reservations" in entry:
                        last_reservations = entry["reservations"]
                    if last_tx is not None and last_state is not None:
                        self.log.append((last_tx, last_state))
                if last_tx is not None:
                    self.tx_id = last_tx
                    self.state = last_state
                    if last_reservations is not None:
                        self.pending_reservations = list(last_reservations)
        except FileNotFoundError:
            return
