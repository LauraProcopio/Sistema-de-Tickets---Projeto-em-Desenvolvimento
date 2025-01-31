# views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from accounts.models import CustomUser  # Certifique-se de que o modelo está correto
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from tickets.models import Ticket
from gestao.models import Cliente, Empresa, Departamento  # Importa o modelo Cliente
from django.db.models import Count
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from .forms import AlterarEmailForm

# Função de Cadastro de Usuário
# Cadastro de usuário
from django.shortcuts import render

def cadastro(request):
    if request.method == 'POST':
        # Obtendo dados do formulário
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        role = request.POST.get('role')

        # Verifica se todos os campos obrigatórios foram preenchidos
        if not all([username, email, password1, password2]):
            messages.warning(request, "Preencha todos os campos obrigatórios.")
            return render(request, 'cadastroelogin/cadastro.html')

        # Verifica se as senhas coincidem
        if password1 != password2:
            messages.warning(request, "As senhas não coincidem. Tente novamente.")
            return render(request, 'cadastroelogin/cadastro.html')

        # Verifica se o nome de usuário já está em uso
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

            # Mensagem de sucesso após o cadastro
            messages.success(request, "Usuário cadastrado com sucesso!")

            # Redireciona para a página de login
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
    # Contar tickets por empresa
    tickets_por_empresa = (
        Ticket.objects.values('empresa__nome')  # Obtém o nome da empresa
        .annotate(total_tickets=Count('id'))  # Conta os tickets
        .order_by('-total_tickets')  # Ordena do maior para o menor
    )

    # Criando listas para o gráfico
    labels = [item['empresa__nome'] for item in tickets_por_empresa]
    data = [item['total_tickets'] for item in tickets_por_empresa]

    # Listagem dos últimos 10 tickets
    tickets_recentes = Ticket.objects.order_by('-data_criacao')[:10]

    context = {
        'labels': labels,
        'data': data,
        'tickets_recentes': tickets_recentes,
    }

    return render(request, 'dashboard/dashboard_adm.html', context)

@login_required
@staff_member_required
def gerar_relatorio_pdf(request):
    # Criar resposta como PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="relatorio_tickets.pdf"'

    p = canvas.Canvas(response)
    p.drawString(100, 800, "Relatório de Tickets")

    tickets = Ticket.objects.all()

    y = 750
    for ticket in tickets:
        p.drawString(50, y, f"Empresa: {ticket.empresa} | Status: {ticket.status} | Prioridade: {ticket.prioridade}")
        y -= 20

    p.save()
    return response

@login_required
def dashboard_cliente(request):
    # Recupera o cliente associado ao usuário logado
    try:
        cliente = Cliente.objects.get(email=request.user.email)
    except Cliente.DoesNotExist:
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



