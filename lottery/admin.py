from django.contrib import admin
from .models import LotteryDraw, Prize
from .pdf_parser import parse_lottery_pdf
from django.shortcuts import redirect
import os

class PrizeInline(admin.TabularInline):
    model = Prize
    extra = 0

@admin.register(LotteryDraw)
class LotteryDrawAdmin(admin.ModelAdmin):
    list_display = ('draw_name', 'draw_date', 'draw_time')
    inlines = [PrizeInline]
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        
        # Parse the PDF and create Prize objects
        pdf_path = obj.result_pdf.path
        parsed_data = parse_lottery_pdf(pdf_path)
        
        # Update draw info if not set
        if not obj.draw_name:
            obj.draw_name = parsed_data['draw_name']
        if not obj.draw_date:
            obj.draw_date = parsed_data['draw_date']
        if not obj.draw_time:
            obj.draw_time = parsed_data['draw_time']
        obj.save()
        
        # Create prizes
        for prize_data in parsed_data['prizes']:
            Prize.objects.create(
                lottery_draw=obj,
                prize_type=prize_data['type'],
                amount=prize_data['amount'],
                ticket_code=prize_data['ticket_code'],
                location=prize_data['location']
            )

admin.site.register(Prize)