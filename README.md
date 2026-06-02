# 🚀 **Mô Phỏng Giao Thức Cam Kết Ba Giai Đoạn (3PC)**

<div align="center">

### 🎯 Hệ Thống Điều Phối Giao Dịch Phân Tán

![Python](https://img.shields.io/badge/Python-3.x-blue)
![Trạng Thái](https://img.shields.io/badge/Trạng%20Thái-Hoạt%20Động-green)
![Giấy Phép](https://img.shields.io/badge/Giấy%20Phép-MIT-orange)

</div>

---

## 📋 **Tổng Quan**

Dự án này triển khai **Mô Phỏng Giao Thức Cam Kết Ba Giai Đoạn (3PC)**, một thuật toán điều phối giao dịch phân tán mạnh mẽ được sử dụng trong các hệ thống đa người tham gia. Mô phỏng này trình bày cách một điều phối viên đảm bảo tính nhất quán trên nhiều người tham gia trong môi trường cơ sở dữ liệu phân tán.

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

## 🏗️ **Kiến Trúc**

### **Luồng Giao Thức Cam Kết Ba Giai Đoạn**

```
Giai Đoạn 1: YÊU CẦU BÌNH CHỌN
   Điều Phối Viên → Người Tham Gia (Bạn có thể cam kết giao dịch này không?)
   
Giai Đoạn 2: PRE-COMMIT
   Người Tham Gia → Điều Phối Viên (Có/Không bình chọn)
   Điều Phối Viên → Người Tham Gia (Pre-commit tất cả hay hủy bỏ?)
   
Giai Đoạn 3: COMMIT/HỦY BỎ
   Người Tham Gia → Điều Phối Viên (Xác nhận)
   Điều Phối Viên → Người Tham Gia (Quyết định cuối cùng: COMMIT hay HỦY BỎ)
```

### **Các Thành Phần Chính**

| Thành Phần | Vai Trò |
|-----------|--------|
| **Điều Phối Viên** 🎯 | Quyền lực trung tâm điều phối các giao dịch |
| **Người Tham Gia** 👥 | Các nút (P1, P2) quản lý tài nguyên và bình chọn cam kết |
| **Mạng** 🌐 | Mô phỏng truyền tin nhắn giữa các nút |
| **Kho Dữ Liệu** 💾 | Quản lý hàng tồn kho cho khách sạn, máy bay và ô tô |

---

## 🔑 **Các Tính Năng Chính**

✅ **Quyết Định Dựa Trên Sự Đồng Thuận** - Tất cả người tham gia phải đồng ý cam kết  
✅ **Ghi Nhật Ký Giao Dịch** - Đầy đủ hồi sơ của tất cả các hoạt động  
✅ **Quản Lý Trạng Thái** - Theo dõi INIT → WAIT → PRE_COMMIT → COMMIT/HỦY BỎ  
✅ **Mô Phỏng Mạng** - Truyền tin nhắn hệ thống phân tán thực tế  
✅ **Đặt Chỗ Đa Tài Nguyên** - Điều phối trên nhiều kho dữ liệu  
✅ **Xử Lý Lỗi** - Hủy bỏ nhẹ nhàng khi có bất đồng ý kiến  

---

## 🚀 **Bắt Đầu**

### **Điều Kiện Tiên Quyết**
- Python 3.x
- File CSV cho bộ dữ liệu (tự động tạo khi chạy lần đầu)

### **Cài Đặt**

```bash
# Chuyển đến thư mục mô phỏng
cd simulator

# Chạy mô phỏng
python run_simulation.py
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
- start_transaction(reservations)   # Khởi tạo giao dịch mới
```

### **Người Tham Gia**
```python
Participant(node_id, network, datastores, log_path)
- on_message(message, from_id)      # Xử lý yêu cầu điều phối viên
- can_commit()                      # Bình chọn về giao dịch
```

### **Kho Dữ Liệu**
```python
DataStore(name, csv_path)
- reserve(quantity)                 # Đặt chỗ tài nguyên
- commit()                          # Hoàn tất đặt chỗ
- abort()                           # Khôi phục đặt chỗ
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
