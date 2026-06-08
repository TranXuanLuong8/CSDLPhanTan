import json

STATE_INIT = "INIT"
STATE_WAIT = "WAIT"
STATE_PRE_COMMIT = "PRE_COMMIT"
STATE_COMMIT = "COMMIT"
STATE_ABORT = "ABORT"


class Coordinator:
    def __init__(self, node_id, network, participant_ids, log_path=None):
        self.node_id = node_id
        self.network = network
        self.participant_ids = list(participant_ids)
        self.state = STATE_INIT
        self.tx_id = None
        self.reservations = []                  # Danh sách yêu cầu đặt chỗ/thay đổi tài nguyên của giao dịch
        self.votes = {}                         # Từ điển (Dict) dùng để gom phiếu bầu của các nút gửi về
        self.acks = {}                          # Từ điển dùng để gom xác nhận (ACK) ở pha Pre-Commit
        self.log = []                           # Mảng lưu lịch sử các bước chạy trên RAM
        self.log_path = log_path                # Đường dẫn file nhật ký cứng để khôi phục khi sập nguồn
        if self.log_path:
            self._load_log()

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
        self._append_log(self.state, reservations=self.reservations)

    def send_vote_req(self):
        for pid in self.participant_ids:
            self.network.send(self.node_id, pid, {
                "type": "VOTE_REQ",
                "tx_id": self.tx_id,
                "reservations": self.reservations,
            })

    def _on_vote(self, message, from_id):
        self.votes[from_id] = message["type"]

    def handle_vote_timeout(self):
        if self.state != STATE_WAIT:
            return None
        if self.can_pre_commit():
            return self.send_pre_commit()
        self.state = STATE_ABORT
        self._append_log(self.state)
        self._broadcast_abort()
        return STATE_ABORT

    def can_pre_commit(self):
        if len(self.votes) != len(self.participant_ids):
            return False
        return all(v == "VOTE_COMMIT" for v in self.votes.values())

    def send_pre_commit(self):
        if not self.can_pre_commit():
            self.state = STATE_ABORT
            self._append_log(self.state)
            self._broadcast_abort()
            return False
        self.state = STATE_PRE_COMMIT
        self._append_log(self.state)
        for pid in self.participant_ids:
            self.network.send(self.node_id, pid, {
                "type": "PRE_COMMIT",
                "tx_id": self.tx_id,
            })
        return True

    def _on_ack(self, message, from_id):
        self.acks[from_id] = True

    def handle_ack_timeout(self):
        if self.state != STATE_PRE_COMMIT:
            return None
        if self.can_commit():
            return self.send_commit()
        self.state = STATE_COMMIT
        self._append_log(self.state)
        for pid in self.participant_ids:
            self.network.send(self.node_id, pid, {
                "type": "COMMIT",
                "tx_id": self.tx_id,
            })
        return STATE_COMMIT

    def can_commit(self):
        return len(self.acks) == len(self.participant_ids)

    def send_commit(self):
        if not self.can_commit():
            return False
        self.state = STATE_COMMIT
        self._append_log(self.state)
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

    def resume_after_crash(self):
        if self.state == STATE_WAIT:
            self.send_vote_req()
            return STATE_WAIT
        if self.state == STATE_PRE_COMMIT:
            # Phat lai PRE_COMMIT khong can dem lai vote.
            for pid in self.participant_ids:
                self.network.send(self.node_id, pid, {
                    "type": "PRE_COMMIT",
                    "tx_id": self.tx_id,
                })
            return STATE_PRE_COMMIT
        if self.state == STATE_COMMIT:
            # Phat lai COMMIT khong can dem lai ACK.
            for pid in self.participant_ids:
                self.network.send(self.node_id, pid, {
                    "type": "COMMIT",
                    "tx_id": self.tx_id,
                })
            return STATE_COMMIT
        if self.state == STATE_ABORT:
            self._broadcast_abort()
            return STATE_ABORT
        return None

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
                        self.reservations = list(last_reservations)
        except FileNotFoundError:
            return
