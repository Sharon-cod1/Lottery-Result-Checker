from django.shortcuts import render, redirect
from django.db.models import Q
from .models import LotteryDraw, Prize
from django.contrib.humanize.templatetags.humanize import intcomma
from datetime import date

# Prize type priority for comparison (lower = higher prize)
PRIZE_RANK = {
    '1st': 1,
    '2nd': 2,
    '3rd': 3,
    'cons': 4,
    '4th': 5,
    '5th': 6,
    '6th': 7,
    '7th': 8,
    '8th': 9,
    '9th': 10
}

def home(request):
    draws = LotteryDraw.objects.all().order_by('-draw_date')
    return render(request, 'lottery/home.html', {'draws': draws})


def check_result(request):
    if request.method == 'POST':
        ticket_code = request.POST.get('ticket_code', '').strip().upper()
        draw_date = request.POST.get('draw_date')
        
        # Validate ticket format (2 letters + 6 digits)
        clean_code = ''.join(c for c in ticket_code if c.isalnum())
        if len(clean_code) != 8 or not clean_code[:2].isalpha() or not clean_code[2:].isdigit():
            return render(request, 'lottery/result.html', {
                'error': 'Invalid ticket format. Must be 2 letters followed by 6 digits (e.g., DL123456)',
                'ticket_code': ticket_code,
                'draw_date': draw_date
            })
        
        last_4_digits = clean_code[-4:]
        
        # Check for exact full ticket matches (1st-3rd and consolation prizes)
        exact_prizes = Prize.objects.filter(
            lottery_draw__draw_date=draw_date,
            ticket_code=clean_code,
            prize_type__in=['1st', '2nd', '3rd', 'cons']
        ).select_related('lottery_draw')
        
        # NEW: Check each prize category separately to find exact match
        ending_prize = None
        # Map prize types to priority (lower number = higher prize)
        prize_priority = {
            '4th': 1,
            '5th': 2,
            '6th': 3,
            '7th': 4,
            '8th': 5,
            '9th': 6
        }

        # Find all ending matches
        ending_matches = Prize.objects.filter(
            lottery_draw__draw_date=draw_date,
            ticket_code=last_4_digits,
            prize_type__in=prize_priority.keys()
        )

        # Pick the prize with the highest priority
        ending_prize = None
        if ending_matches.exists():
            ending_prize = sorted(
                ending_matches, 
                key=lambda p: prize_priority.get(p.prize_type, 99)
            )[0]
        
        # Combine results
        combined_prizes = list(exact_prizes)
        if ending_prize and not exact_prizes.exists():
            combined_prizes.append(ending_prize)
        
        context = {
            'ticket_code': ticket_code,
            'formatted_ticket': f"{clean_code[:2]} {clean_code[2:]}",
            'draw_date': draw_date,
            'prizes': combined_prizes,
            'last_4_digits': last_4_digits,
            'has_exact_match': bool(exact_prizes),
            'intcomma': intcomma,
        }
        return render(request, 'lottery/result.html', context)
    
    return redirect('home')
# def check_result(request):
#     if request.method == 'POST':
#         ticket_code = request.POST.get('ticket_code', '').strip().upper()
#         draw_date = request.POST.get('draw_date')
        
#         # Validate ticket format (2 letters + 6 digits)
#         clean_code = ''.join(c for c in ticket_code if c.isalnum())
#         if len(clean_code) != 8 or not clean_code[:2].isalpha() or not clean_code[2:].isdigit():
#             return render(request, 'lottery/result.html', {
#                 'error': 'Invalid ticket format. Must be 2 letters followed by 6 digits (e.g., DL123456)',
#                 'ticket_code': ticket_code,
#                 'draw_date': draw_date
#             })
        
#         last_4_digits = clean_code[-4:]
        
#         # ✅ Check for exact full ticket matches (1st-3rd and consolation prizes)
#         full_match_prizes = Prize.objects.filter(
#             lottery_draw__draw_date=draw_date,
#             prize_type__in=['1st', '2nd', '3rd', 'cons']
#         ).select_related('lottery_draw')

#         # ✅ Extract prizes where full ticket code matches
#         exact_prizes = full_match_prizes.filter(ticket_code=clean_code)

#         # ✅ Consolation prize fallback logic (match full 6-digit part with different prefix)
#         if not exact_prizes.exists():
#             prefix = clean_code[:2]
#             number_part = clean_code[2:]
#             consolation_match = full_match_prizes.filter(
#                 prize_type='cons',
#                 ticket_code__endswith=number_part
#             ).exclude(ticket_code__startswith=prefix).first()

#             if consolation_match:
#                 exact_prizes = [consolation_match]

#         # 4th to 9th prize: match by last 4 digits
#         ending_prize = None
#         prize_categories = [
#             ('4th', '4th Prize-Rs :5000/-'),
#             ('5th', '5th Prize-Rs :2000/-'), 
#             ('6th', '6th Prize-Rs :1000/-'),
#             ('7th', '7th Prize-Rs :500/-'),
#             ('8th', '8th Prize-Rs :200/-'),
#             ('9th', '9th Prize-Rs :100/-')
#         ]
        
#         for prize_type, _ in prize_categories:
#             prize = Prize.objects.filter(
#                 lottery_draw__draw_date=draw_date,
#                 ticket_code=last_4_digits,
#                 prize_type=prize_type
#             ).first()
            
#             if prize:
#                 ending_prize = prize
#                 break  # stop at first match

#         # Combine results
#         combined_prizes = list(exact_prizes)
#         if ending_prize and not exact_prizes:
#             combined_prizes.append(ending_prize)
        
#         context = {
#             'ticket_code': ticket_code,
#             'formatted_ticket': f"{clean_code[:2]} {clean_code[2:]}",
#             'draw_date': draw_date,
#             'prizes': combined_prizes,
#             'last_4_digits': last_4_digits,
#             'has_exact_match': bool(exact_prizes),
#             'intcomma': intcomma,
#         }
#         return render(request, 'lottery/result.html', context)
    
#     return redirect('home')

def past_results(request):
    today = date.today()
    past_draws = LotteryDraw.objects.filter(draw_date__lt=today).order_by('-draw_date')

    draws_with_prizes = []
    for draw in past_draws:
        draws_with_prizes.append({
            'draw': draw,
            'first_prize': draw.prize_set.filter(prize_type='1st').first(),
            'second_prize': draw.prize_set.filter(prize_type='2nd').first(),
            'third_prize': draw.prize_set.filter(prize_type='3rd').first()
        })

    return render(request, 'lottery/past_results.html', {
        'draws_with_prizes': draws_with_prizes
    })
