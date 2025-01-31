from django.shortcuts import render, redirect, get_object_or_404
from django.db.utils import IntegrityError
from .models import Empresa, Departamento, Cliente
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib.auth.hashers import make_password
from django.contrib import messages

# Create your views here.
# Listar Empresas
def listar_empresas(request):
    query = request.GET.get('q', '')
    empresas = Empresa.objects.filter(nome__icontains=query) if query else Empresa.objects.all()
    return render(request, 'listar_empresas.html', {'empresas': empresas, 'query': query})

# Cadastrar Empresas
def cadastrar_empresa(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        cnpj = request.POST.get('cnpj')
        endereco = request.POST.get('endereco')
        Empresa.objects.create(nome=nome, cnpj=cnpj, endereco=endereco)
        return redirect('listar_empresas')  # Redireciona para a página de listagem
    return render(request, 'cadastrar_empresas.html')

# Editar Empresas
def editar_empresa(request, id):
    empresa = get_object_or_404(Empresa, id=id)  # Retorna 404 se a empresa não existir
    if request.method == 'POST':
        empresa.nome = request.POST.get('nome')
        empresa.cnpj = request.POST.get('cnpj')
        empresa.endereco = request.POST.get('endereco')
        empresa.save()
        return redirect('listar_empresas')  # Redireciona após salvar
    return render(request, 'editar_empresa.html', {'empresa': empresa})

# Excluir Empresas
def excluir_empresa(request, id):
    empresa = get_object_or_404(Empresa, id=id)
    empresa.delete()
    return redirect('listar_empresas')  # Redireciona após excluir

# fim da view de empresas


# Início das views de departamentos 
def listar_departamentos(request):
    query = request.GET.get('q', '')  # Obtém o valor da busca (se houver)
    
    if query:
        departamentos = Departamento.objects.filter(nome__icontains=query)  # Filtra os departamentos pelo nome
    else:
        departamentos = Departamento.objects.all()  # Se não houver filtro, pega todos os departamentos
    
    return render(request, 'listar_departamentos.html', {'departamentos': departamentos})

# Cadastrar Departamentos
def cadastrar_departamentos(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        sigla = request.POST.get('sigla')
       
        Departamento.objects.create(nome=nome, sigla=sigla)
        return redirect('listar_departamentos')
    
    return render(request, 'cadastrar_departamentos.html')

# Editar Departamentos
def editar_departamento(request, id):
    departamento = get_object_or_404(Departamento, id=id)

    if request.method == 'POST':
        departamento.nome = request.POST.get('nome')
        departamento.sigla = request.POST.get('sigla')  # Adicionando sigla caso tenha sido alterada
        departamento.save()
        return redirect('listar_departamentos')
    
    return render(request, 'editar_departamento.html', {'departamento': departamento})

# Excluir Departamentos
def excluir_departamento(request, id):
    departamento = get_object_or_404(Departamento, id=id)
    departamento.delete()
    return redirect('listar_departamentos')
# Fim das views de departamentos

# Início das views de clientes
def listar_clientes(request):
    query = request.GET.get('q', '')
    if query:
        clientes = Cliente.objects.filter(nome__icontains=query)
    else:
        clientes = Cliente.objects.all()

    return render(request, 'listar_clientes.html', {'clientes': clientes})

def cadastrar_cliente(request):
    empresas = Empresa.objects.all()
    departamentos = Departamento.objects.all()

    if request.method == 'POST':
        nome = request.POST.get('nome')
        cpf = request.POST.get('cpf')
        telefone = request.POST.get('telefone')
        email = request.POST.get('email')
        empresa_id = request.POST.get('empresa')
        departamento_id = request.POST.get('departamento')

        # Validação para evitar que CPF vazio seja enviado
        if not cpf:
            return render(request, 'cadastrar_clientes.html', {
                'empresas': empresas,
                'departamentos': departamentos,
                'error': 'O campo CPF é obrigatório.'
            })

        # Verificar se o CPF já existe no banco de dados
        if Cliente.objects.filter(cpf=cpf).exists():
            return render(request, 'cadastrar_clientes.html', {
                'empresas': empresas,
                'departamentos': departamentos,
                'error': f'O CPF {cpf} já está cadastrado.'
            })

        empresa = get_object_or_404(Empresa, id=empresa_id)
        departamento = get_object_or_404(Departamento, id=departamento_id)

        Cliente.objects.create(
            nome=nome,
            cpf=cpf,
            telefone=telefone,
            email=email,
            empresa=empresa,
            departamento=departamento
        )
        return redirect('listar_clientes')

    return render(request, 'cadastrar_clientes.html', {
        'empresas': empresas,
        'departamentos': departamentos
    })

def editar_cliente(request, id):
    cliente = get_object_or_404(Cliente, id=id)
    empresas = Empresa.objects.all()
    departamentos = Departamento.objects.all()

    if request.method == 'POST':
        nome = request.POST.get('nome')
        cpf = request.POST.get('cpf')
        telefone = request.POST.get('telefone')
        email = request.POST.get('email')
        empresa_id = request.POST.get('empresa')
        departamento_id = request.POST.get('departamento')

        # Validação dos campos obrigatórios
        if not nome or not email or not empresa_id or not departamento_id:
            return render(request, 'editar_cliente.html', {
                'cliente': cliente,
                'empresas': empresas,
                'departamentos': departamentos,
                'error': 'Todos os campos são obrigatórios.',
            })

        # Atualizar o cliente
        empresa = get_object_or_404(Empresa, id=empresa_id)
        departamento = get_object_or_404(Departamento, id=departamento_id)

        cliente.nome = nome
        cliente.cpf = cpf
        cliente.telefone = telefone
        cliente.email = email
        cliente.empresa = empresa
        cliente.departamento = departamento
        cliente.save()

        return redirect('listar_clientes')  # Redireciona para a lista de clientes após a edição

    return render(request, 'editar_cliente.html', {
        'cliente': cliente,
        'empresas': empresas,
        'departamentos': departamentos
    })

def excluir_cliente(request, id):
    cliente = get_object_or_404(Cliente, id=id)
    cliente.delete()
    return redirect('listar_clientes')
# Fim das views de clientes


#Inicio das views de admins
#Listar admins
@login_required
def listar_adms(request):
    if request.user.role != 'admin':
        return HttpResponseForbidden("Você não tem permissão para acessar esta página.")

    User = get_user_model()  # Usando o CustomUser
    
    # Verifica se há uma busca
    search_query = request.GET.get('q', '')
    if search_query:
        admins = User.objects.filter(role='admin', username__icontains=search_query)  # Filtra administradores pelo nome
    else:
        admins = User.objects.filter(role='admin')  # Caso não haja filtro, retorna todos os administradores
    
    return render(request, 'listar_adms.html', {'admins': admins})

#Cadastrar admins
@login_required
def cadastrar_adm(request):
    if request.user.role != 'admin':
        return HttpResponseForbidden("Você não tem permissão para acessar esta página.")

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')

        # A senha será fixada para '12345'
        password = '12345'  # Definindo a senha fixa
        confirm_password = request.POST.get('confirm_password')
        is_active = request.POST.get('is_active') == 'True'

        # Verificando se o e-mail já está em uso
        User = get_user_model()
        if User.objects.filter(email=email).exists():
            messages.error(request, "Este e-mail já está em uso.")
            return render(request, 'cadastrar_adm.html', {'error': "Este e-mail já está em uso."})

        # Criação do administrador
        user = User.objects.create(
            username=username,
            email=email,
            password=make_password(password),  # Senha criptografada
            is_active=is_active,
            role='admin'  # Atribuindo o papel de administrador
        )

        messages.success(request, "Administrador cadastrado com sucesso!")
        return redirect('listar_adms')

    return render(request, 'cadastrar_adm.html')

#Editar admins
@login_required
def editar_adm(request, admin_id):
    if request.user.role != 'admin':
        return HttpResponseForbidden("Você não tem permissão para acessar esta página.")

    admin = get_user_model().objects.get(id=admin_id)

    if request.method == 'POST':
        # Recuperando os valores dos campos
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        is_active = request.POST.get('is_active') == 'True'

        # Verificando se o botão de reset foi pressionado
        if request.POST.get('reset_password') == 'true':
            password = '12345'  # Resetando a senha para '12345'
            confirm_password = '12345'  # Garantir que a senha confirmada também seja '12345'

        # Validação de senha
        if password and password != confirm_password:
            messages.error(request, "As senhas não coincidem!")
            return render(request, 'editar_adm.html', {'admin': admin, 'error': "As senhas não coincidem."})

        # Atualizando os dados do administrador
        admin.username = username
        admin.email = email
        admin.password = make_password(password)  # Criptografar a nova senha
        admin.is_active = is_active
        admin.save()

        messages.success(request, "Administrador atualizado com sucesso!")
        return redirect('listar_adms')

    return render(request, 'editar_adm.html', {'admin': admin})


#Excluir admins
@login_required
def excluir_adm(request, id):
    User = get_user_model()
    admin = get_object_or_404(User, id=id)
    
    if admin.role == 'admin':
        admin.delete()  # Exclui o administrador
    return redirect('listar_adms')