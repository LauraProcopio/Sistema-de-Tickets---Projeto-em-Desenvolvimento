# views.py
from django.shortcuts import render, redirect 
from django.contrib import messages 
from django.contrib.auth import authenticate, login, logout 
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required 
from django.contrib.admin.views.decorators import staff_member_required 
from accounts.models import CustomUser
from tickets.models import Ticket
from django.db.models import Count 
from django.http import HttpResponse 
from reportlab.pdfgen import canvas 
from django.contrib.auth import update_session_auth_hash, get_user_model 
from django.contrib.auth.forms import PasswordChangeForm 
from .forms import AlterarEmailForm 
import io
import xlsxwriter 
from reportlab.lib.pagesizes import letter 
from reportlab.platypus import Table, TableStyle 
from reportlab.lib import colors 


# Função de Cadastro de Usuário
# Cadastro de usuário
from django.shortcuts import render # type: ignore

def cadastro(request):
    if request.method == 'POST':
        # Obtendo dados do formulário
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        role = request.POST.get('role', 'user')

        # Verifica se todos os campos obrigatórios foram preenchidos
        if not all([username, email, password1, password2]):
            messages.warning(request, "Preencha todos os campos obrigatórios.")
            return render(request, 'cadastroelogin/cadastro.html')

        # Verifica se as senhas coincidem
        if password1 != password2:
            messages.warning(request, "As senhas não coincidem. Tente novamente.")
            return render(request, 'cadastroelogin/cadastro.html')

        # Verifica se o nome de usuário já está em us

        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, "Nome de usuário já está em uso.")
            return render(request, 'cadastroelogin/cadastro.html')

        # Verifica se o e-mail já está cadastrado



        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "E-mail já cadastrado.")
            return render(request, 'cadastroelogin/cadastro.html')

        try:
            user = CustomUser.objects.create(
                username=username,
                email=email,
                password=make_password(password1),  # Criptografa a senha
                role=role,
                is_staff=True if role == 'admin' else False,
            )

             #Mensagem de sucesso após o cadastro
            messages.success(request, "Usuário cadastrado com sucesso!")

             #Redireciona para a página de login
            return redirect('login')  # 'login' deve ser o nome da URL para a página de login

        except Exception as e:
           messages.error(request, f"Ocorreu um erro ao cadastrar o usuário: {e}")
        return render(request, 'cadastroelogin/cadastro.html')

    # Exibe lista de usuários cadastrados
    usuario_list = CustomUser.objects.all()
    
    return render(request, 'cadastroelogin/cadastro.html', {'usuario_list': usuario_list})


# Função de Login de Usuário
def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Login realizado com sucesso!")

            # Verifica o tipo de usuário (role) e redireciona para o painel adequado
        if user.role == 'admin':  # Caso seja administrador
            if user.is_staff:  # Verifica se o usuário é staff
                    return redirect('dashboard_adm')  # Página do admin
            else:
                    messages.error(request, "Acesso negado. Você não tem permissão de administrador.")
                    return redirect('login')  # Redireciona de volta ao login

        else:  # Caso seja cliente
                return redirect('dashboard_cliente')  # Página do cliente
    else:
            messages.error(request, "Usuário ou senha inválidos.")
            return render(request, 'cadastroelogin/login.html')  # Página de login

    return render(request, 'cadastroelogin/login.html')

# Função de Logout de Usuário
def user_logout(request):
    logout(request)
    messages.success(request, "Logout realizado com sucesso!")
    return redirect('login')  # Redireciona de volta para a página de login após o logout

@login_required
@staff_member_required

def dashboard_adm(request):
    # Captura os filtros da URL
    status_filtro = request.GET.get('status', '')
    prioridade_filtro = request.GET.get('prioridade', '')

    # Filtra os tickets se houver filtros
    tickets = Ticket.objects.all()
    if status_filtro:
        tickets = tickets.filter(status=status_filtro)
    if prioridade_filtro:
        tickets = tickets.filter(prioridade=prioridade_filtro)

    # Contar tickets por empresa
    tickets_por_empresa = tickets.values('empresa__nome').annotate(total_tickets=Count('id')).order_by('-total_tickets')

    # Contar tickets por status
    tickets_por_status = tickets.values('status').annotate(total_tickets=Count('id')).order_by('-total_tickets')

    # Criando listas para os gráficos
    labels_empresa = [item['empresa__nome'] for item in tickets_por_empresa]
    data_empresa = [item['total_tickets'] for item in tickets_por_empresa]

    labels_status = [item['status'] for item in tickets_por_status]
    data_status = [item['total_tickets'] for item in tickets_por_status]

    # Últimos 10 tickets filtrados
    tickets_recentes = tickets.order_by('-data_criacao')[:10]

    context = {
        'labels_empresa': labels_empresa,
        'data_empresa': data_empresa,
        'labels_status': labels_status,
        'data_status': data_status,
        'tickets_recentes': tickets_recentes,
        'status_filtro': status_filtro,
        'prioridade_filtro': prioridade_filtro,
    }

    return render(request, 'dashboard/dashboard_adm.html', context)

@login_required
@staff_member_required
def gerar_relatorio_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="relatorio_tickets.pdf"'
    
    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter
    
    p.setFont("Helvetica-Bold", 16)
    p.drawString(200, height - 50, "Relatório de Tickets")
    p.setFont("Helvetica", 12)
    
    tickets = Ticket.objects.all().values_list('empresa__nome', 'status', 'prioridade', 'data_criacao')
    
    table_data = [['Empresa', 'Status', 'Prioridade', 'Data de Criação']] + list(tickets)
    
    table = Table(table_data, colWidths=[130, 100, 100, 120])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ]))
    
    table.wrapOn(p, width, height)
    table.drawOn(p, 50, height - 200)
    
    p.showPage()
    p.save()
    return response


def gerar_relatorio_excel(request):
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet("Relatório de Tickets")
    
    bold = workbook.add_format({'bold': True, 'bg_color': '#D3D3D3'})
    
    headers = ['Empresa', 'Status', 'Prioridade', 'Data de Criação']
    for col_num, header in enumerate(headers):
        worksheet.write(0, col_num, header, bold)
    
    tickets = Ticket.objects.all().values_list('empresa__nome', 'status', 'prioridade', 'data_criacao')
    for row_num, row_data in enumerate(tickets, start=1):
        for col_num, cell_data in enumerate(row_data):
            worksheet.write(row_num, col_num, str(cell_data))
    
    worksheet.autofilter(0, 0, row_num, len(headers) - 1)
    
    workbook.close()
    output.seek(0)
    
    response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="relatorio_tickets.xlsx"'
    return response

@login_required
def dashboard_cliente(request):
    User = get_user_model()
    # Recupera o cliente associado ao usuário logado
    try:
        cliente = User.objects.get(email=request.user.email)
    except User.DoesNotExist:
        cliente = None

    if cliente:
        # Filtra os tickets pela empresa do cliente
        tickets_cliente = Ticket.objects.filter(empresa=cliente.empresa).order_by('-data_criacao')
    else:
        tickets_cliente = []  # Caso o cliente não seja encontrado

    return render(request, 'dashboard/dashboard_cliente.html', {
        'tickets_cliente': tickets_cliente,
    })


def alterar_cadastro(request):
    # Formulários
    if request.method == 'POST':
        email_form = AlterarEmailForm(request.POST, instance=request.user)
        password_form = PasswordChangeForm(request.user, request.POST)

        if email_form.is_valid() and password_form.is_valid():
            # Salvar mudanças de e-mail
            email_form.save()
            
            # Salvar mudanças de senha
            password_form.save()
            update_session_auth_hash(request, password_form.user)  # Manter a sessão ativa após a alteração da senha
            
            return redirect('dashboard')  # Redirecionar para o dashboard ou onde for necessário
    else:
        email_form = AlterarEmailForm(instance=request.user)
        password_form = PasswordChangeForm(request.user)
    
    return render(request, 'cadastroelogin/alterar_cadastro.html', {
        'email_form': email_form,
        'password_form': password_form,
        'user': request.user,
    })

def alterar_cadastro_cliente(request):
    # Formulários
    if request.method == 'POST':
        email_form = AlterarEmailForm(request.POST, instance=request.user)
        password_form = PasswordChangeForm(request.user, request.POST)

        if email_form.is_valid() and password_form.is_valid():
            # Salvar mudanças de e-mail
            email_form.save()
            
            # Salvar mudanças de senha
            password_form.save()
            update_session_auth_hash(request, password_form.user)  # Manter a sessão ativa após a alteração da senha
            
            return redirect('dashboard')  # Redirecionar para o dashboard ou onde for necessário
    else:
        email_form = AlterarEmailForm(instance=request.user)
        password_form = PasswordChangeForm(request.user)
    
    return render(request, 'cadastroelogin/alterar_cadastro_cliente.html', {
        'email_form': email_form,
        'password_form': password_form,
        'user': request.user,
    })



