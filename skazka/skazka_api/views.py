from django.shortcuts import render
from django.http import JsonResponse
from telegram import Bot
from telegram.error import TelegramError

from .forms import ClientForm, PriceForm, CalculatorForm

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
        form_type = None

        if 'phone_contact' in request.POST:
            form_type = 'contact'
        elif 'name' in request.POST:
            form_type = 'calculator'
        elif 'question-1__count_flat[]' in request.POST:
            form_type = 'quiz'
        elif 'apartment' in request.POST:
            form_type = 'apartment'    
        elif 'phone' in request.POST:
            form_type = 'phone'

        if form_type:
            return handle_form_submission(request, form_type, contact_form, price_form, calculator_form)

    return render(request, 'index.html', {'contact_form': contact_form, 'price_form': price_form, 'calculator_form': calculator_form})

def handle_form_submission(request, form_type, contact_form, price_form, calculator_form):
    if form_type == 'contact':
        return handle_contact_form(request, contact_form)
    elif form_type == 'calculator':
        return handle_calculator_form(request, calculator_form)
    elif form_type == 'quiz':
        return handle_quiz_form(request)
    elif form_type == 'phone':
        return handle_phone_form(request, price_form)
    elif form_type == 'apartment':
        return handle_apartment_form(request)
    else:
        return JsonResponse({'success': False, 'message': 'Форма неверная', 'errors': dict(request.POST)})

def handle_contact_form(request, contact_form):
    contact_form = ClientForm(request.POST)
    if contact_form.is_valid():
        phone_number = contact_form.cleaned_data['phone_contact']
        msg = f'Обратный звонок\n\n Телефон: {phone_number}'
        send_telegram_message(TELEGRAM_GROUP_CHAT_ID, msg)
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False, 'message': 'Форма неверная', 'errors': dict(contact_form.errors)})

def handle_apartment_form(request):
    selected_options = {
        'from': request.POST['from'],
        'apartment': request.POST['apartment'],
        'phone': request.POST['phone'],
    }
    msg = ''
    msg = f'Понравилась квартира\n\n'
    msg += f'Откуда: {selected_options["from"]}\n'
    msg += f'Квартира: {selected_options["apartment"]}\n'
    msg += f'Телефон: {selected_options["phone"]}'
    send_telegram_message(TELEGRAM_GROUP_CHAT_ID, msg)
    return JsonResponse({'success': True})

def handle_calculator_form(request, calculator_form):
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
        sum_value = request.POST['sum']

        name = calculator_form.cleaned_data['name']
        phone = calculator_form.cleaned_data['phone']

        msg = f'{from_form}\nСумма кредита: {price}\nПервый платеж: {first_payment}\nСрок кредита: {credit_term}\nПоддержка: {state}\nБанк: {bank} || Процент:{percents}\nПлатеж по калькулятору: {payment}\nФинальная сумма кредита: {sum_value}\n\nФИО: {name}\nТелефон: {phone}'
        send_telegram_message(TELEGRAM_GROUP_CHAT_ID, msg)
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False, 'message': 'Форма неверная', 'errors': dict(calculator_form.errors)})

def handle_quiz_form(request):
    selected_options = {
        'from': request.POST['from'],
        'count_flat': request.POST.getlist('question-1__count_flat[]'),
        'area': request.POST.getlist('question-2__area[]'),
        'decor': request.POST.getlist('question-3__decor[]'),
        'time': request.POST.getlist('question-4__time[]'),
        'mortgage': request.POST.getlist('question-5__mortgage[]'),
        'phone': request.POST['phone'],
    }

    msg = f'Запрос на подбор квартиры\n\n'
    msg += f'Откуда: {selected_options["from"]}\n'
    msg += f'Количество комнат: {", ".join(selected_options["count_flat"])}\n'
    msg += f'Площадь: {", ".join(selected_options["area"])}\n'
    msg += f'Отделка: {", ".join(selected_options["decor"])}\n'
    msg += f'Срок сдачи: {", ".join(selected_options["time"])}\n'
    msg += f'Ипотека: {", ".join(selected_options["mortgage"])}\n'
    msg += f'Телефон: {selected_options["phone"]}'
    
    send_telegram_message(TELEGRAM_GROUP_CHAT_ID, msg)
    return JsonResponse({'success': True})

def handle_phone_form(request, price_form):
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
