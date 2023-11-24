from django.shortcuts import render,redirect
from django.http import HttpResponseRedirect
from django.conf import settings
from telegram import Bot
from telegram.error import TelegramError
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .forms import ClientForm, PriceForm, CalculatorForm

from django.contrib import messages


TELEGRAM_BOT_TOKEN = '5599450991:AAH4w_cTs1h3UpLxJyMKL0bPGQ8-5SQBGZ0'
TELEGRAM_GROUP_CHAT_ID = '-4082298212'

def send_telegram_message(chat_id, message):
    bot = Bot(token=TELEGRAM_BOT_TOKEN)

    try:
        bot.send_message(chat_id=chat_id, text=message)
        return True
    except TelegramError as e:
        print(f"Error sending Telegram message: {e}")
        return False

def index(request):

    contact_form = ClientForm()
    price_form = PriceForm()
    calculator_form = CalculatorForm()

    if request.method == 'POST':
        print(request.POST)
        if 'phone_contact' in request.POST:
            contact_form = ClientForm(request.POST)
            if contact_form.is_valid():
                phone_number = contact_form.cleaned_data['phone_contact']
                msg = f'Обратный звонок\n\n Телефон: {phone_number}'
                send_telegram_message(TELEGRAM_GROUP_CHAT_ID, msg)
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'message': 'Форма неверная', 'errors': dict(contact_form.errors)})
        elif 'name' not in request.POST:
            price_form = PriceForm(request.POST)
            if price_form.is_valid():
                phone_number = price_form.cleaned_data['phone']
                form_value = price_form.cleaned_data['from_value']
                type_messenger = request.POST['type']
                msg = f'{form_value}\n\nНомер телефона: {phone_number}\nМессенджер {type_messenger}'
                send_telegram_message(TELEGRAM_GROUP_CHAT_ID, msg)
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'message': 'Форма неверная', 'errors': dict(price_form.errors)})
        elif 'name' in request.POST:
            calculator_form = CalculatorForm(request.POST)
            if calculator_form.is_valid():
                from_form = request.POST['from']
                price = request.POST['price']
                first_payment = request.POST['first_payment']
                credit_term = request.POST['credit_term']
                state = request.POST['state']
                bank = request.POST['bank']
                percents = request.POST['percents']
                payment = request.POST['payment']
                sum = request.POST['sum']

                name = calculator_form.cleaned_data['name']
                phone = calculator_form.cleaned_data['phone']

                msg = f'{from_form}\nСумма кредита: {price}\nПервый платеж: {first_payment}\nСрок кредита: {credit_term}\nПоддержка: {state}\nБанк: {bank} || Процент:{percents}\nПлатеж по калькулятору: {payment}\nФинальная сумма кредита: {sum}\n\nФИО: {name}\nТелефон: {phone}'
                send_telegram_message(TELEGRAM_GROUP_CHAT_ID, msg)

                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'message': 'Форма неверная', 'errors': dict(price_form.errors)})

    context = {
        'contact_form': contact_form,
        'price_form': price_form,
        'calculator_form': calculator_form,
    }

    return render(request, 'index.html', context=context)