import re
import os

# --- CẤU HÌNH TÊN FILE ---
INPUT_FILE = 'dwc_e16mp_pma_x4_ns_scan_pg.spf'
OUTPUT_FILE = 'add_scan_chains.tcl'

def extract_spf_scan_chains():
    # 1. Kiểm tra sự tồn tại của file SPF đầu vào
    if not os.path.exists(INPUT_FILE):
        print(f"Lỗi: Không tìm thấy file cấu hình '{INPUT_FILE}' tại thư mục hiện tại.")
        return

    print(f"--- Đang phân tích file cấu hình DFT: {INPUT_FILE} ---")
    
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # 2. Định nghĩa Regex quét khối dữ liệu ScanChain
    # Bắt cặp: Group 1 = Tên Scanchain trong "", Group 2 = Toàn bộ nội dung trong cặp dấu { }
    chain_block_pattern = re.compile(r'ScanChain\s+"([^"]+)"\s*\{([^}]+)\}', re.DOTALL)
    chain_blocks = chain_block_pattern.findall(content)

    results = []
    unique_commands = set() # Bộ nhớ đệm chống trùng lặp dữ liệu

    # 3. Duyệt qua từng khối ScanChain tìm thấy
    for chain_name, block_content in chain_blocks:
        # Tìm chính xác giá trị nằm trong dấu "" của ScanIn và ScanOut bên trong khối
        scan_in_match = re.search(r'ScanIn\s+"([^"]+)"', block_content)
        scan_out_match = re.search(r'ScanOut\s+"([^"]+)"', block_content)

        if scan_in_match and scan_out_match:
            # Trích xuất nguyên văn chuỗi ký tự nằm trong dấu ngoặc kép
            scan_in_val = scan_in_match.group(1)
            scan_out_val = scan_out_match.group(1)

            # Tạo câu lệnh add_scan_chain tiêu chuẩn theo yêu cầu của bạn
            cmd = f"add_scan_chain {chain_name} {scan_in_val} {scan_out_val}"

            # Lọc trùng lặp trước khi lưu trữ
            if cmd not in unique_commands:
                unique_commands.add(cmd)
                results.append(cmd)

    # 4. Xuất kết quả ra file lệnh Tcl
    if results:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f_out:
            f_out.write("\n".join(results) + "\n")
        print(f"--- Hoàn thành! ---")
        print(f"Đã trích xuất thành công {len(results)} chuỗi scan duy nhất.")
        print(f"Kết quả lưu tại file: {OUTPUT_FILE}")
    else:
        print("Cảnh báo: Không tìm thấy cấu trúc ScanChain hợp lệ nào trong file SPF.")

if __name__ == "__main__":
    extract_spf_scan_chains()