from django.shortcuts import render, redirect
from django.db.models import Q
from .models import LotteryDraw, Prize
from django.contrib.humanize.templatetags.humanize import intcomma
from datetime import date

def home(request):
    draws = LotteryDraw.objects.all().order_by('-draw_date')
    return render(request, 'lottery/home.html', {'draws': draws})

def check_result(request):
    if request.method == 'POST':
        ticket_code = request.POST.get('ticket_code', '').strip().upper()
        draw_date = request.POST.get('draw_date')
        
        # Clean and validate ticket code
        clean_code = ''.join(c for c in ticket_code if c.isalnum())
        if len(clean_code) != 8 or not clean_code[:2].isalpha() or not clean_code[2:].isdigit():
            return render(request, 'lottery/result.html', {
                'error': 'Invalid ticket format. Must be 2 letters followed by 6 digits (e.g., DL123456)',
                'ticket_code': ticket_code,
                'draw_date': draw_date
            })
        
        last_4_digits = clean_code[-4:]
        
        # Check for exact matches (1st-3rd and consolation prizes)
        exact_prizes = Prize.objects.filter(
            lottery_draw__draw_date=draw_date,
            ticket_code=clean_code,
            prize_type__in=['1st', '2nd', '3rd', 'cons']
        ).select_related('lottery_draw')
        
        # Check for ending matches (4th-9th prizes)
        ending_prizes = Prize.objects.filter(
            lottery_draw__draw_date=draw_date,
            ticket_code=last_4_digits,
            prize_type__in=['4th', '5th', '6th', '7th', '8th', '9th']
        ).select_related('lottery_draw')
        
        # Combine results
        combined_prizes = list(exact_prizes) + list(ending_prizes)
        
        context = {
            'ticket_code': ticket_code,
            'draw_date': draw_date,
            'prizes': combined_prizes,
            'last_4_digits': last_4_digits,
            'has_exact_match': bool(exact_prizes),
        }
        return render(request, 'lottery/result.html', context)
    
    return redirect('home')

def past_results(request):
    today = date.today()
    past_draws = LotteryDraw.objects.filter(draw_date__lt=today).order_by('-draw_date')
    
    # Prepare the data for each draw
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