import re
from pdfminer.high_level import extract_text
from dateutil.parser import parse

def parse_lottery_pdf(pdf_path):
    text = extract_text(pdf_path)
    
    # Extract draw information
    draw_match = re.search(r'DHANALEKSHMI LOTTERY NO\.(.+?) DRAW held on:\s*(.+?),', text)
    draw_name = draw_match.group(1).strip() if draw_match else "Unknown"
    draw_date = parse(draw_match.group(2)).date() if draw_match else None
    draw_time = parse(draw_match.group(2)).time() if draw_match else None
    
    prizes = []
    
    # Helper function to clean ticket codes
    def clean_code(code):
        return ''.join(c for c in code if c.isalnum()).upper()
    
    # 1st Prize (format: AB 123456)
    first_prize_match = re.search(r'1st Prize Rs :(\d+)/-\s*1\)\s*([A-Z]{2})\s*(\d+)\s*\(([^)]+)', text)
    if first_prize_match:
        code = f"{first_prize_match.group(2)}{first_prize_match.group(3)}"
        prizes.append({
            'type': '1st',
            'amount': float(first_prize_match.group(1).replace(',', '')),
            'ticket_code': clean_code(code),
            'location': first_prize_match.group(4)
        })
    
    # 2nd Prize
    second_prize_match = re.search(r'2nd Prize Rs :(\d+)/-\s*1\)\s*([A-Z]{2})\s*(\d+)\s*\(([^)]+)', text)
    if second_prize_match:
        code = f"{second_prize_match.group(2)}{second_prize_match.group(3)}"
        prizes.append({
            'type': '2nd',
            'amount': float(second_prize_match.group(1).replace(',', '')),
            'ticket_code': clean_code(code),
            'location': second_prize_match.group(4)
        })
    
    # 3rd Prize
    third_prize_match = re.search(r'3rd Prize Rs :(\d+)/-\s*1\)\s*([A-Z]{2})\s*(\d+)\s*\(([^)]+)', text)
    if third_prize_match:
        code = f"{third_prize_match.group(2)}{third_prize_match.group(3)}"
        prizes.append({
            'type': '3rd',
            'amount': float(third_prize_match.group(1).replace(',', '')),
            'ticket_code': clean_code(code),
            'location': third_prize_match.group(4)
        })
    
    # Consolation Prizes (format: AB 123456)
    cons_prizes_match = re.search(r'Cons Prize-Rs :(\d+)/-\s*((?:[A-Z]{2}\s*\d+\s*)+)', text)
    if cons_prizes_match:
        amount = float(cons_prizes_match.group(1).replace(',', ''))
        ticket_codes = re.findall(r'([A-Z]{2})\s*(\d+)', cons_prizes_match.group(2))
        for letter_part, number_part in ticket_codes:
            code = f"{letter_part}{number_part}"
            prizes.append({
                'type': 'cons',
                'amount': amount,
                'ticket_code': clean_code(code),
                'location': None
            })
    
    # 4th-9th Prizes (last 4 digits only)
    for prize_type, prize_text in [
        ('4th', '4th Prize-Rs :(\d+)/-'),
        ('5th', '5th Prize-Rs :(\d+)/-'),
        ('6th', '6th Prize-Rs :(\d+)/-'),
        ('7th', '7th Prize-Rs :(\d+)/-'),
        ('8th', '8th Prize-Rs :(\d+)/-'),
        ('9th', '9th Prize-Rs :(\d+)/-'),
    ]:
        prize_section = re.search(prize_text + r'(.*?)(?=\n\d+\s+Prize-Rs|\Z)', text, re.DOTALL)
        if prize_section:
            amount = float(prize_section.group(1).replace(',', ''))
            numbers = re.findall(r'\b\d{4}\b', prize_section.group(2))
            for num in numbers:
                prizes.append({
                    'type': prize_type,
                    'amount': amount,
                    'ticket_code': num,  # Just the last 4 digits
                    'location': None
                })
    
    return {
        'draw_name': draw_name,
        'draw_date': draw_date,
        'draw_time': draw_time,
        'prizes': prizes
    }