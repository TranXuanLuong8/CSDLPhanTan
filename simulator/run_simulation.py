import os

from coordinator import Coordinator
from datastore import DataStore
from network import Network
from participant import Participant
from data.generate_datasets import generate


def build_datastores(base_dir):
    return {
        "hotel": DataStore("hotel", os.path.join(base_dir, "Hotel_Rooms.csv")),
        "flight": DataStore("flight", os.path.join(base_dir, "Flight_Seats.csv")),
        "car": DataStore("car", os.path.join(base_dir, "Car_Rentals.csv")),
    }


def print_snapshot(title, nodes):
    print("\n" + title)
    for node in nodes:
        snap = node.snapshot()
        print(f"{snap['node']} state={snap['state']} log={snap['log']}")


def main():
    base_dir = os.path.join(os.path.dirname(__file__), "data")
    log_dir = os.path.join(os.path.dirname(__file__), "logs")
    os.makedirs(log_dir, exist_ok=True)
    for name in ("coordinator.log", "p1.log", "p2.log"):
        path = os.path.join(log_dir, name)
        if os.path.exists(path):
            os.remove(path)
    generate()
    stores = build_datastores(base_dir)

    network = Network()
    coordinator_id = "C"
    participant_ids = ["P1", "P2"]

    coordinator = Coordinator(
        coordinator_id,
        network,
        participant_ids,
        log_path=os.path.join(log_dir, "coordinator.log"),
    )

    p1 = Participant(
        "P1",
        network,
        datastores=stores,
        owned_resources={"hotel", "flight"},
        peer_ids=["P1", "P2"],
        log_path=os.path.join(log_dir, "p1.log"),
    )
    p2 = Participant(
        "P2",
        network,
        datastores=stores,
        owned_resources={"car"},
        peer_ids=["P1", "P2"],
        log_path=os.path.join(log_dir, "p2.log"),
    )

    network.register(coordinator_id, coordinator)
    network.register("P1", p1)
    network.register("P2", p2)

    tx_id = "TX-001"
    reservations = [
        {"resource": "hotel", "item_id": "H-1", "qty": 1},
        {"resource": "flight", "item_id": "F-1", "qty": 1},
        {"resource": "car", "item_id": "C-1", "qty": 1},
    ]

    coordinator.start_transaction(tx_id, reservations)
    coordinator.send_vote_req()
    
    coordinator.send_pre_commit()

    print_snapshot("Trước phân vùng", [coordinator, p1, p2])

    print("\n--- Mô phỏng phân vùng mạng: {C, P1} | {P2} ---")
    network.set_partitions([{coordinator_id, "P1"}, {"P2"}])

    print("--- Mô phỏng Coordinator lỗi ngay sau PRE_COMMIT ---")
    network.unregister(coordinator_id)

    print("\n--- Chạy giao thức kết thúc ---")
    p1_decision = p1.handle_pre_commit_timeout()
    p2_decision = p2.handle_pre_commit_timeout()

    print_snapshot("Sau phân vùng và hết thời gian chờ", [p1, p2])
    print(f"\nQuyết định kết thúc của P1: {p1_decision}")
    print(f"Quyết định kết thúc của P2: {p2_decision}")

    print("\n--- Mô phỏng Coordinator phục hồi ---")
    network.clear_partitions()
    network.register(coordinator.node_id, coordinator)
    recovered_state = coordinator.state
    print(f"Coordinator phục hồi ở trạng thái: {recovered_state}")

    resume_decision = coordinator.resume_after_crash()
    print(f"Coordinator tiếp tục quyết định: {resume_decision}")

    print("\n--- Trạng thái dữ liệu cuối ---")
    print("Ảnh hưởng đến tồn kho:")
    for name, store in stores.items():
        print(f"{name}: {store.snapshot()}")


if __name__ == "__main__":
    main()
