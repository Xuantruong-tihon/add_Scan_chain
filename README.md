# Cấu trúc thư mục
spf_extractor_tool/
├── README.md                     		# Hướng dẫn sử dụng
├── extract_spf_chains.py         		# File script Python ở trên
├── dwc_e16mp_pma_x4_ns_scan_pg.spf  	# Tệp dữ liệu mẫu đầu vào (Cắt lấy khoảng 20-30 dòng mẫu)
└── add_scan_chains.tcl           		# Thư mục chứa kết quả mẫu để đối chiếu

# SPF Scan Chain Extractor Tool

## 1. Giới thiệu tổng quan
Công cụ hỗ trợ tự động hóa việc bóc tách thông tin ScanChains (ScanChain, ScanIn, ScanOut) từ tệp cấu hình định dạng STIL/SPF (`.spf`) được tạo trong giai đoạn Synthesis+DFT khi Hand-off để chuyển đổi sang định dạng lệnh Tcl (`add_scan_chain`) dành cho quá trình ATPG .

## 2. Yêu cầu hệ thống
- Môi trường chạy: Linux (HPC Cluster) hoặc Windows.
- Phiên bản: Python 3.6 trở lên (Chỉ sử dụng thư viện tiêu chuẩn `re`, `os`).

## 3. Cách sử dụng
1. Thiết lập cây thư mục như trên, đảm bảo file script extract_spf_chains.py nằm cùng cấp với tệp dữ liệu đầu vào ( file .spf)
2. Sửa đổi tên file .spf của dự án ở phần đầu của script "extract_spf_chains.py" .
3. Thực thi script bằng lệnh: python3 extract_spf_chains.py
