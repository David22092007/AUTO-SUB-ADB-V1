import re
from g4f.client import Client

def fix_to_srt(input_text):
# Bước 1: Tách số thứ tự ra khỏi dòng thời gian
    # Tìm: (Số) (Thời gian) -> Thay bằng: (Số)\n(Thời gian)
    text = re.sub(r"^(\d+)\s+(\d{2}:\d{2}:\d{2},\d{3} -->)", r"\1\n\2", input_text, flags=re.MULTILINE)
    
    # Bước 2: Tách nội dung ra khỏi dòng thời gian (nếu nó dính liền phía sau)
    # Tìm: (Thời gian) (Nội dung) -> Thay bằng: (Thời gian)\n(Nội dung)
    text = re.sub(r"(\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3})\s+(?!\n)", r"\1\n", text)
    
    # Bước 3: Chuẩn hóa khoảng cách dòng
    # Xóa dòng trống thừa và đảm bảo mỗi khối cách nhau đúng 1 dòng trống
    blocks = []
    # Chia text thành các khối dựa trên số thứ tự ở đầu dòng
    raw_blocks = re.split(r'\n(?=\d+\n)', text.strip())
    
    for b in raw_blocks:
        lines = [line.strip() for line in b.split('\n') if line.strip()]
        if len(lines) >= 3:
            # Đúng chuẩn: Dòng 1 (Số), Dòng 2 (Time), Dòng 3+ (Nội dung)
            blocks.append("\n".join(lines))
        elif len(lines) == 2:
            # Trường hợp thiếu nội dung hoặc lỗi khác (dự phòng)
            blocks.append("\n".join(lines))
            
    return "\n\n".join(blocks)

client = Client()

# Cải thiện prompt để AI chỉ tập trung vào dữ liệu thô
prompt = """
Dịch đoạn sau qua tiếng Việt, giữ nguyên định dạng file .srt. 
CHỈ TRẢ VỀ nội dung file srt, không thêm lời dẫn, không giải thích.

Dữ liệu:
1 00:00:00,520 --> 00:00:02,919 CCTV監視カメラからのビデオ録画 
2 00:00:03,320 --> 00:00:04,440 空にまた光が走った 
3 00:00:05,200 --> 00:00:06,319 共謀者を乗せた飛行機の後 
4 00:00:06,680 --> 00:00:08,400 モハメド・アリ・アルハダド陸軍長官 
5 00:00:09,440 --> 00:00:11,080 ～から離陸直後に墜落した 
6 00:00:12,120 --> 00:00:13,200 アンカラは上記のすべてを行います 
7 00:00:13,559 --> 00:00:15,200 飛行機が死んだ。リビア首相によると、 
8 00:00:16,119 --> 00:00:17,359 飛行機에는 quân đội cũng có chỉ huy 
9 00:00:17,720 --> 00:00:19,640 リビア軍、生産代理店のディレクター 
10 00:00:19,960 --> 00:00:21,519 軍、参謀長補佐官 
11 00:00:21,960 --> 00:00:23,359 そして貪欲なオフィスから出てきた写真家 
12 00:00:23,680 --> 00:00:24,279 参謀長.
"""

response = client.chat.completions.create(
    model="gemma-3-27b-it",
    messages=[{"role": "user", "content": prompt}],
    web_search=False
)

raw_content = response.choices[0].message.content

# Hậu xử lý: Loại bỏ các thẻ ```srt hoặc ``` nếu AI tự ý thêm vào
clean_content = re.sub(r'```[a-zA-Z]*\n|```', '', raw_content).strip()

# In ra kết quả sạch
print(fix_to_srt(clean_content))