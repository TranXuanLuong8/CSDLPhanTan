# 🚀 **Mô Phỏng Giao Thức Cam Kết Ba Giai Đoạn (3PC)**

<div align="center">

### 🎯 Hệ Thống Điều Phối Giao Dịch Phân Tán

![Python](https://img.shields.io/badge/Python-3.x-blue)
![Trạng Thái](https://img.shields.io/badge/Trạng%20Thái-Hoạt%20Động-green)
![Giấy Phép](https://img.shields.io/badge/Giấy%20Phép-MIT-orange)

</div>

---

## 📋 **Tổng Quan**

Dự án này triển khai **Mô Phỏng Giao Thức Cam Kết Ba Giai Đoạn (3PC)**, một thuật toán điều phối giao dịch phân tán mạnh mẽ được sử dụng trong các hệ thống đa người tham gia. Mô phỏng này trình bày cách một điều phối viên đảm bảo tính nhất quán trên nhiều người tham gia và cách hệ thống xử lý lỗi để tránh bị chặn.

Mô phỏng tập trung vào việc chứng minh tính **không bị chặn (non-blocking)** của 3PC khi Coordinator gặp sự cố.

### 🎪 **Trường Hợp Sử Dụng**
Hệ thống mô phỏng một **nền tảng đặt chỗ** cho các loại hình du lịch:
- 🏨 Đặt Phòng Khách Sạn
- ✈️ Đặt Chỗ Máy Bay
- 🚗 Quản Lý Cho Thuê Ô Tô

---

## 📁 **Cấu Trúc Dự Án**

```
3PCS/
├── simulator/
│   ├── 🔗 network.py              # Lớp giao tiếp mạng
│   ├── 📍 coordinator.py          # Triển khai nút điều phối
│   ├── 👥 participant.py          # Triển khai nút người tham gia
│   ├── 💾 datastore.py            # Quản lý lưu trữ dữ liệu
│   ├── ⚙️ run_simulation.py        # Trình chạy mô phỏng chính
│   ├── logs/                      # Nhật ký giao dịch
│   └── data/
│       ├── 📊 Hotel_Rooms.csv     # Dữ liệu hàng tồn kho khách sạn
│       ├── 📊 Flight_Seats.csv    # Dữ liệu chỗ máy bay
│       ├── 📊 Car_Rentals.csv     # Dữ liệu cho thuê ô tô
│       └── 🔧 generate_datasets.py # Trình tạo bộ dữ liệu
└── README.md                      # File này
```

---

## 🏗️ **Kiến Trúc và Kịch Bản Lỗi**

### **Luồng Giao Thức 3PC**

1.  **Giai Đoạn 1: YÊU CẦU BÌNH CHỌN (VOTE_REQUEST)**
    *   Điều Phối Viên → Người Tham Gia: "Bạn có thể cam kết giao dịch này không?"
2.  **Giai Đoạn 2: PRE-COMMIT**
    *   Người Tham Gia → Điều Phối Viên: "Có, tôi có thể." (Vote Commit)
    *   Điều Phối Viên → Người Tham Gia: "Chuẩn bị cam kết." (Pre-commit)
3.  **Giai Đoạn 3: COMMIT**
    *   Người Tham Gia → Điều Phối Viên: "Đã nhận lệnh Pre-commit." (ACK)
    *   Điều Phối Viên → Người Tham Gia: "Cam kết giao dịch." (Commit)

### **Kịch Bản Mô Phỏng Lỗi**

Mô phỏng được thiết kế để kiểm tra khả năng phục hồi của 3PC:

1.  **Coordinator gửi PRE_COMMIT** đến tất cả các participant.
2.  **Sự cố xảy ra**:
    *   **Mạng bị phân vùng**, cô lập một participant (`P2`) khỏi Coordinator (`C`) và participant còn lại (`P1`).
    *   **Coordinator (`C`) bị crash** ngay sau đó.
3.  **Giao thức Chấm dứt (Termination Protocol)** được kích hoạt:
    *   Các participant bị hết thời gian chờ (timeout) vì không nhận được lệnh `COMMIT` cuối cùng.
    *   Chúng sẽ hỏi trạng thái của các participant khác.
    *   Vì tất cả đã ở trạng thái `PRE_COMMIT`, chúng có thể tự quyết định `COMMIT` một cách an toàn mà không cần Coordinator.

---

## 🚀 **Bắt Đầu**

### **Điều Kiện Tiên Quyết**
- Python 3.x

### **Chạy Mô Phỏng**

1.  **Chuyển đến thư mục gốc của dự án:**
    ```bash
    cd /path/to/3PCS
    ```

2.  **Chạy kịch bản mô phỏng:**
    ```bash
    python simulator/run_simulation.py
    ```

    Lệnh này sẽ thực hiện các bước sau:
    - Xóa và tạo lại các file log trong thư mục `logs/`.
    - Tạo bộ dữ liệu mới, lớn hơn (100 bản ghi mỗi loại) trong `data/`.
    - Chạy kịch bản mô phỏng 3PC với lỗi đã định sẵn.
    - In ra trạng thái của các nút tại các thời điểm quan trọng và quyết định cuối cùng của chúng.

```

### **Đầu Ra**
- 📝 Nhật ký giao dịch được lưu trong thư mục `logs/`
- 🎯 Đầu ra bảng điều khiển hiển thị trạng thái giao dịch
- 💾 Hàng tồn kho cập nhật sau các cam kết thành công

---

## 📊 **Nguồn Dữ Liệu**

Mô phỏng hoạt động với ba hệ thống đặt chỗ:

| Tài Nguyên | File | Mục Đích |
|-----------|------|---------|
| 🏨 Khách Sạn | `Hotel_Rooms.csv` | Tính khả dụng phòng & giá cả |
| ✈️ Máy Bay | `Flight_Seats.csv` | Hàng tồn kho chỗ ngồi |
| 🚗 Ô Tô | `Car_Rentals.csv` | Tính khả dụng phương tiện |

---

## 🔬 **Cách Hoạt Động**

1. **Khởi Tạo** - Tạo điều phối viên và những người tham gia
2. **Tải Dữ Liệu** - Đọc hàng tồn kho từ file CSV
3. **Xử Lý Giao Dịch** - Gửi yêu cầu đặt chỗ
4. **Điều Phối** - Chạy giao thức 3PC trên tất cả những người tham gia
5. **Ghi Nhật Ký Kết Quả** - Ghi lại kết quả trong nhật ký giao dịch
6. **Xác Minh Trạng Thái** - Hiển thị trạng thái cuối cùng của tất cả các nút

### **Trạng Thái Giao Dịch**

```
STATE_INIT      → Trạng thái ban đầu
STATE_WAIT      → Chờ bình chọn từ người tham gia
STATE_PRE_COMMIT→ Tất cả người tham gia đã đồng ý
STATE_COMMIT    → Giao dịch được cam kết thành công
STATE_ABORT     → Giao dịch bị khôi phục
```

---

## 📝 **Tổng Quan API**

### **Điều Phối Viên**
```python
Coordinator(node_id, network, participant_ids, log_path)
- on_message(message, from_id)      # Xử lý tin nhắn đến
- start_transaction(tx_id, reservations)   # Khởi tạo giao dịch mới
- send_vote_req()                   # Gửi yêu cầu bỏ phiếu
- send_pre_commit()                 # Gửi PRE_COMMIT (khi đủ phiếu)
- resume_after_crash()              # Phục hồi sau khi crash
```

### **Người Tham Gia**
```python
Participant(node_id, network, datastores, owned_resources, peer_ids, log_path)
- on_message(message, from_id)      # Xử lý yêu cầu điều phối viên
- handle_pre_commit_timeout()       # Quyết định khi timeout ở PRE_COMMIT
- handle_wait_timeout()             # Quyết định khi timeout ở WAIT
```

### **Kho Dữ Liệu**
```python
DataStore(name, csv_path)
- can_reserve(item_id, qty)         # Kiểm tra khả dụng
- reserve(item_id, qty)             # Đặt chỗ tài nguyên
```

---

## 📈 **Các Trường Hợp Sử Dụng**

🎫 **Nền Tảng Đặt Du Lịch** - Điều phối các đặt chỗ đa bước  
🏦 **Hệ Thống Ngân Hàng** - Đảm bảo tính nhất quán trên các tài khoản  
🛍️ **Thương Mại Điện Tử** - Quản lý hàng tồn kho trên nhiều kho hàng  
💼 **Hệ Thống Doanh Nghiệp** - Quản lý giao dịch phân tán  

---

## 🛠️ **Phát Triển**

### **Mở Rộng Hệ Thống**

Để thêm các loại người tham gia mới:
```python
from participant import Participant
new_participant = Participant("P3", network, datastores, log_path)
```

Để thêm các loại tài nguyên mới:
```python
from datastore import DataStore
new_resource = DataStore("resource_name", "path/to/data.csv")
```

---

## 📚 **Tài Liệu Tham Khảo**

- 📖 **Giao Thức 3PC**: [Giao thức cam kết ba giai đoạn](https://en.wikipedia.org/wiki/Three-phase_commit_protocol)
- 💡 Được thiết kế cho các khóa học hệ thống phân tán và cơ sở dữ liệu
- 🎓 Triển khai giáo dục của các thuật toán đồng thuận

---

## 📄 **Giấy Phép**

Dự án này được cung cấp nguyên trạng cho mục đích giáo dục.

---

## 🤝 **Đóng Góp**

Tự do mở rộng mô phỏng với:
- Các kịch bản giao dịch phức tạp hơn
- Mô phỏng lỗi mạng
- Chỉ số hiệu suất và phân tích
- Các loại tài nguyên bổ sung

---

## 📞 **Hỗ Trợ**

Để giải quyết các vấn đề hoặc có câu hỏi về mô phỏng giao thức 3PCS:
- Kiểm tra nhật ký trong thư mục `logs/` để xem chi tiết thực thi
- Xem lại ảnh chụp trạng thái được in ra trong quá trình mô phỏng
- Kiểm tra tin nhắn giao dịch trong nhật ký điều phối viên/người tham gia

---
