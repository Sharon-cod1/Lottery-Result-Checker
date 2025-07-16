from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib.humanize.templatetags.humanize import intcomma
from datetime import date
from .models import LotteryDraw, Prize

# Define prize rank (lower = higher priority)
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
    """
    Display homepage with list of all lottery draws (most recent first).
    """
    draws = LotteryDraw.objects.all().order_by('-draw_date')
    return render(request, 'lottery/home.html', {'draws': draws})


def check_result(request):
    """
    Handle ticket result checking logic.
    Supports both full-code and last-4-digit match detection.
    """
    if request.method == 'POST':
        # Get user input from form
        ticket_code = request.POST.get('ticket_code', '').strip().upper()
        draw_date = request.POST.get('draw_date')

        # Validate format: 2 letters + 6 digits
        clean_code = ''.join(c for c in ticket_code if c.isalnum())
        if len(clean_code) != 8 or not clean_code[:2].isalpha() or not clean_code[2:].isdigit():
            return render(request, 'lottery/result.html', {
                'error': 'Invalid ticket format. Must be 2 letters followed by 6 digits (e.g., DL123456)',
                'ticket_code': ticket_code,
                'draw_date': draw_date
            })

        # Extract last 4 digits for fallback match
        last_4_digits = clean_code[-4:]

        # Search for exact matches (1st, 2nd, 3rd, consolation)
        exact_prizes = Prize.objects.filter(
            lottery_draw__draw_date=draw_date,
            ticket_code=clean_code,
            prize_type__in=['1st', '2nd', '3rd', 'cons']
        ).select_related('lottery_draw')

        # Fallback: check last-4-digit matches (for 4th to 9th prize types)
        ending_prize = None
        prize_priority = {
            '4th': 1, '5th': 2, '6th': 3,
            '7th': 4, '8th': 5, '9th': 6
        }

        ending_matches = Prize.objects.filter(
            lottery_draw__draw_date=draw_date,
            ticket_code=last_4_digits,
            prize_type__in=prize_priority.keys()
        )

        if ending_matches.exists():
            # Choose highest priority match
            ending_prize = sorted(
                ending_matches,
                key=lambda p: prize_priority.get(p.prize_type, 99)
            )[0]

        # Combine exact + fallback results
        combined_prizes = list(exact_prizes)
        if ending_prize and not exact_prizes.exists():
            combined_prizes.append(ending_prize)

        # Prepare context for result template
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


def past_results(request):
    """
    Show past lottery draws along with 1st, 2nd, and 3rd prize info.
    """
    today = date.today()
    past_draws = LotteryDraw.objects.filter(draw_date__lt=today).order_by('-draw_date')

    draws_with_prizes = []
    for draw in past_draws:
        draws_with_prizes.append({
            'draw': draw,
            'first_prize': draw.prize_set.filter(prize_type='1st').first(),
            'second_prize': draw.prize_set.filter(prize_type='2nd').first(),
            'third_prize': draw.prize_set.filter(prize_type='3rd').first(),
        })

    return render(request, 'lottery/past_results.html', {
        'draws_with_prizes': draws_with_prizes
    })

def privacy_policy(request):
    return render(request, 'lottery/privacy.html')

def terms_of_service(request):
    return render(request, 'lottery/terms.html')