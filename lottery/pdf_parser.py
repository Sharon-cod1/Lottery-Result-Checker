import re
import pdfplumber
from dateutil.parser import parse



def parse_lottery_pdf(pdf_path):
    """
    Parses a Kerala Lottery PDF and extracts draw information and prize details.

    Args:
        pdf_path (str): Path to the lottery result PDF.

    Returns:
        dict: Contains draw metadata and a list of prize-winning ticket information.
    """

    # Step 1: Extract text from all pages using pdfplumber
    with pdfplumber.open(pdf_path) as pdf:
        text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])

    # Step 2: Extract draw name, date and time
    draw_match = re.search(r'DHANALEKSHMI LOTTERY NO\.(.+?) DRAW held on:\s*(.+?),', text)
    draw_name = draw_match.group(1).strip() if draw_match else "Unknown"
    draw_date = parse(draw_match.group(2)).date() if draw_match else None
    draw_time = parse(draw_match.group(2)).time() if draw_match else None

    prizes = []  # Will hold all prize entries

    # Utility: Clean ticket codes like 'AB 123456' => 'AB123456'
    def clean_code(code):
        return ''.join(c for c in code if c.isalnum()).upper()

    # Step 3: Extract 1st, 2nd, and 3rd full-code prizes using regex
    def extract_full_prize(prize_type, pattern):
        match = re.search(pattern, text)
        if match:
            code = f"{match.group(2)}{match.group(3)}"
            prizes.append({
                'type': prize_type,
                'amount': float(match.group(1).replace(',', '')),
                'ticket_code': clean_code(code),
                'location': match.group(4).strip()
            })

    extract_full_prize(
        '1st',
        r'1st Prize Rs *: *(\d+)/-.*?1\)\s*([A-Z]{2})\s*(\d+)\s*\(([^)]+)\)'
    )
    extract_full_prize(
        '2nd',
        r'2nd Prize Rs *: *(\d+)/-.*?1\)\s*([A-Z]{2})\s*(\d+)\s*\(([^)]+)\)'
    )
    extract_full_prize(
        '3rd',
        r'3rd Prize Rs *: *(\d+)/-.*?1\)\s*([A-Z]{2})\s*(\d+)\s*\(([^)]+)\)'
    )

    # Step 4: Extract consolation prizes (same number, different prefixes)
    cons_match = re.search(r'Cons Prize-Rs *: *(\d+)/-\s*((?:[A-Z]{2}\s*\d+\s*)+)', text)
    if cons_match:
        amount = float(cons_match.group(1).replace(',', ''))
        ticket_codes = re.findall(r'([A-Z]{2})\s*(\d+)', cons_match.group(2))
        for letters, numbers in ticket_codes:
            code = f"{letters}{numbers}"
            prizes.append({
                'type': 'cons',
                'amount': amount,
                'ticket_code': clean_code(code),
                'location': None
            })

    # Step 5: Extract last-4-digit-based prizes (4th to 9th)
    for prize_type in ['4th', '5th', '6th', '7th', '8th', '9th']:
        # Pattern explanation:
        # - (\d+): prize amount
        # - (.*?): block of numbers following prize amount
        # - Stop at next prize section or end of text
        pattern = rf'{prize_type} Prize-Rs *: *(\d+)/-(.*?)(?=\n\d{{1,2}}[a-zA-Z]*\s+Prize|$)'
        match = re.search(pattern, text, re.DOTALL)
        if match:
            amount = float(match.group(1).replace(',', ''))
            number_block = match.group(2)
            last4_list = re.findall(r'\b\d{4}\b', number_block)
            for last4 in last4_list:
                prizes.append({
                    'type': prize_type,
                    'amount': amount,
                    'ticket_code': last4,
                    'location': None
                })

    # Return structured result
    return {
        'draw_name': draw_name,
        'draw_date': draw_date,
        'draw_time': draw_time,
        'prizes': prizes
    }
