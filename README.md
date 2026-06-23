# SPF Scan Chain Extractor

Công cụ tự động bóc tách thông tin **ScanChain / ScanIn / ScanOut** từ tệp
cấu hình định dạng STIL/SPF (`.spf`) được tạo trong giai đoạn
**Synthesis + DFT hand-off**, và chuyển đổi sang các lệnh Tcl
`add_scan_chain` dùng cho quá trình **ATPG**.

So với bản gốc, phiên bản này được bổ sung khả năng **phát hiện xung đột
dữ liệu** — điểm yếu lớn nhất của bản gốc là khi 1 tên ScanChain bị lặp lại
trong file SPF với ScanIn/ScanOut **khác nhau** (lỗi hand-off / merge dữ
liệu), nó sẽ âm thầm sinh ra 2 lệnh `add_scan_chain` xung đột cho cùng 1
tên chain mà không cảnh báo gì.

## 1. Cấu trúc bộ tool

```
spf_scan_chain_extractor/
├── extract_spf_chains.py              # Script chính, chạy bằng CLI
├── README.md                          # Tài liệu này
└── sample_data/
    ├── dwc_e16mp_pma_x4_ns_scan_pg.spf   # File SPF MẪU (input)
    ├── add_scan_chains.tcl               # Output MẪU sau khi chạy thử
    └── extract_warnings.log              # Log cảnh báo MẪU sau khi chạy thử
```

## 2. Input cần có

File `.spf` (định dạng STIL) chứa các khối khai báo ScanChain, ví dụ:

```
ScanChain "scan_cr" {
  ScanLength 256;
  ScanIn "scan_in_cr";
  ScanOut "scan_out_cr";
  ScanInversion 0;
}
```

Tool chỉ cần 3 thông tin trong mỗi khối: **tên chain** (trong `ScanChain
"..."`), **ScanIn**, **ScanOut**. Các trường khác (`ScanLength`,
`ScanInversion`...) được bỏ qua.

> Lưu ý: tool giả định bên trong 1 khối `ScanChain { ... }` không có dấu
> `{}` lồng nhau — đúng với format STIL/SPF chuẩn cho phần khai báo
> ScanChain. Nếu file thực tế của bạn có cấu trúc lồng phức tạp hơn, báo
> lại để mình điều chỉnh regex.

## 3. Cách dùng

### Chạy nhanh với tham số mặc định
(mặc định: đọc `dwc_e16mp_pma_x4_ns_scan_pg.spf`, xuất ra `add_scan_chains.tcl`
trong thư mục hiện tại)

```bash
python3 extract_spf_chains.py
```

### Chạy với tham số tùy chỉnh

```bash
python3 extract_spf_chains.py --input my_design.spf --output add_scan_chains.tcl --log warnings.log
```

### Chạy thử với dữ liệu mẫu đi kèm

```bash
python3 extract_spf_chains.py \
  --input  sample_data/dwc_e16mp_pma_x4_ns_scan_pg.spf \
  --output sample_data/add_scan_chains.tcl \
  --log    sample_data/extract_warnings.log
```

### Các tham số dòng lệnh (CLI)

| Tham số      | Viết tắt | Mặc định                              | Ý nghĩa |
|--------------|----------|----------------------------------------|---------|
| `--input`    | `-i`     | `dwc_e16mp_pma_x4_ns_scan_pg.spf`       | File `.spf` đầu vào |
| `--output`   | `-o`     | `add_scan_chains.tcl`                   | File `.tcl` kết quả |
| `--log`      | `-l`     | (không có)                              | File log ghi chi tiết cảnh báo/xung đột (tùy chọn) |
| `--quiet`    | `-q`     | (tắt)                                   | Không in log chi tiết, chỉ in kết quả cuối |

## 4. Output

### File `.tcl` — chỉ chứa các chain **hợp lệ và không xung đột**

```tcl
add_scan_chain scan_cr scan_in_cr scan_out_cr
add_scan_chain scan_mpll0 scan_in_mpll0 scan_out_mpll0
add_scan_chain scan_rx0 scan_in_rx0 scan_out_rx0
add_scan_chain scan_tx2 scan_in_tx2 scan_out_tx2
```

### Log cảnh báo (console + file `--log` nếu chỉ định)

Có 2 loại cảnh báo:

**a. Chain thiếu ScanIn/ScanOut** — bị loại khỏi output, liệt kê rõ tên:
```
[CẢNH BÁO] 1 ScanChain bị thiếu ScanIn/ScanOut (đã bỏ qua):
    - scan_ref
```

**b. Chain trùng tên nhưng I/O khác nhau (xung đột thật)** — bị loại khỏi
output, liệt kê đầy đủ các giá trị khác nhau để kỹ sư đối chiếu thủ công:
```
[XUNG ĐỘT] 1 ScanChain trùng tên nhưng I/O khác nhau (CẦN KIỂM TRA LẠI THỦ CÔNG, đã loại khỏi output):
    - scan_tx1:
        ScanIn="scan_in_tx1_v1"  ScanOut="scan_out_tx1_v1"
        ScanIn="scan_in_tx1_v2"  ScanOut="scan_out_tx1_v2"
```

> Trường hợp **trùng lặp y hệt** (cùng tên, cùng ScanIn, cùng ScanOut — ví
> dụ do merge nhiều report PnR chứa lại cùng dữ liệu) thì tool **tự gộp
> thành 1 lệnh duy nhất**, không coi là lỗi và không cần báo cáo.

### Thống kê đối soát (in cuối cùng, ẩn nếu dùng `--quiet`)

```
--- Thống kê đối soát ---
    Tổng số khối ScanChain quét được : 8
    Số tên chain duy nhất            : 5
    Số lệnh add_scan_chain hợp lệ     : 4
    Số chain thiếu ScanIn/ScanOut     : 1
    Số chain xung đột I/O (cần xử lý) : 1
```

Dùng để đối chiếu nhanh: `4 hợp lệ + 1 thiếu trường + 1 xung đột (2 lần xuất
hiện) = 8 khối ban đầu` (sau khi đã gộp `scan_rx0` lặp y hệt từ 2 → 1 tên).

## 5. Quy trình xử lý khi gặp cảnh báo

1. **Chain thiếu ScanIn/ScanOut**: kiểm tra lại file SPF gốc — thường do
   bước hand-off bị cắt thiếu hoặc generate sai từ PnR. Bổ sung thủ công
   hoặc yêu cầu DFT/PnR team xuất lại.
2. **Chain xung đột I/O**: đây là dấu hiệu file SPF bị merge nhầm từ 2
   phiên bản khác nhau, hoặc có 2 block trùng tên do lỗi đặt tên chain
   trong RTL/PnR. **Không tự động chọn 1 trong 2** — cần xác nhận với
   team PnR/DFT phiên bản nào đúng trước khi đưa vào ATPG, vì add nhầm
   I/O sẽ làm sai toàn bộ scan pattern.

## 6. Yêu cầu hệ thống

- Môi trường: Linux (HPC Cluster) hoặc Windows.
- Python 3.6+, chỉ dùng thư viện tiêu chuẩn (`re`, `os`, `sys`, `argparse`).
- Không cần cài thêm package ngoài.

## 7. Mở rộng trong tương lai (gợi ý)

- Hỗ trợ thêm biến thể tên trường (`ScanInPort`/`ScanOutPort`...) nếu file
  SPF từ tool khác dùng tên khác.
- Cho phép chọn chiến lược xử lý xung đột qua CLI (ví dụ `--prefer-last`
  để tự lấy bản ghi cuối cùng) nếu sau này có quy ước rõ ràng.
- Thêm validate định dạng SDC/Tcl của `add_scan_chain` (escape ký tự đặc
  biệt trong tên pin nếu cần).
