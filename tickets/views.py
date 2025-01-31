from django.shortcuts import render, redirect, get_object_or_404
from .models import Ticket, Arquivo, Mensagem
from accounts.models import CustomUser  # Certifique-se de que está importando o modelo correto de usuário
from django.contrib.auth.decorators import login_required
from gestao.models import Empresa
from .forms import MensagemForm, TicketForm 
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect
from .models import Ticket, Mensagem, Empresa
from accounts.models import CustomUser

# Listar tickets - Filtra por usuário se for cliente
@login_required
@login_required
def listar_tickets(request):
    if request.user.is_staff:
        # Administradores veem todos os tickets
        tickets = Ticket.objects.all().order_by('-data_criacao')
        template_name = 'ticket/listar_tickets.html'
    else:
        # Clientes veem os seus próprios tickets e os da sua empresa
        tickets = Ticket.objects.filter(solicitante=request.user).order_by('-data_criacao')
        
        # Garantir que o usuário tem uma empresa associada
        if hasattr(request.user, 'empresa') and request.user.empresa:
            tickets = tickets | Ticket.objects.filter(empresa=request.user.empresa).order_by('-data_criacao')
        
        template_name = 'ticket/listar_ticketsclient.html'

    # Filtro por status
    status = request.GET.get('status')
    if status:
        tickets = tickets.filter(status=status)

    # Busca por título
    query = request.GET.get('q')
    if query:
        tickets = tickets.filter(titulo__icontains=query)

    return render(request, template_name, {'tickets': tickets})




# Excluir ticket - Somente administrador pode excluir
@login_required
def excluir_ticket(request, id):
    ticket = get_object_or_404(Ticket, id=id)

    # Verifica se o usuário é o cliente do ticket ou administrador
    if ticket.solicitante == request.user or request.user.is_staff:
        ticket.delete()
        return redirect('listar_tickets')
    else:
        # Se não for o cliente ou administrador, retornar para a lista de tickets
        return redirect('listar_tickets')

# Criação de ticket - Admin ou Cliente
@login_required
def cadastrar_tickets(request):
    if request.method == 'POST':
        # Captura os dados diretamente do request.POST
        solicitante_id = request.POST.get('solicitante')
        solicitante = CustomUser.objects.get(id=solicitante_id)
        titulo = request.POST.get('titulo')  # Título adicionado
        descricao = request.POST.get('descricao')
        data_entrega = request.POST.get('data_entrega')
        empresa_id = request.POST.get('empresa')
        empresa = Empresa.objects.get(id=empresa_id)

        responsavel = None
        prioridade = request.POST.get('prioridade', 'Média')
        if request.user.is_staff:
            responsavel_id = request.POST.get('responsavel')
            responsavel = CustomUser.objects.get(id=responsavel_id)
            prioridade = request.POST.get('prioridade')

        # Cria o ticket com o título
        ticket = Ticket.objects.create(
            solicitante=solicitante,
            titulo=titulo,  # Incluindo o título
            descricao=descricao,
            data_entrega=data_entrega,
            empresa=empresa,
            responsavel=responsavel,
            prioridade=prioridade
        )

        # Processamento de arquivos
        arquivos = request.FILES.getlist('arquivos')
        if arquivos:
            for arquivo in arquivos:
                Arquivo.objects.create(ticket=ticket, arquivo=arquivo)

        if request.user.is_staff:
            # Administrador - renderiza o template de detalhes do ticket
            return render(request, 'ticket/detalhar_ticket.html', {'ticket': ticket})
        else:
            # Cliente - renderiza o template de detalhes do ticket cliente
            return render(request, 'ticket/detalhar_ticket_cliente.html', {'ticket': ticket})

    # Captura as opções de clientes, administradores e empresas
    clientes_e_administradores = CustomUser.objects.all()
    administradores = CustomUser.objects.filter(is_staff=True)
    empresas = Empresa.objects.all()

    # **Escolhe o template com base no tipo de usuário**
    if request.user.is_staff:
        template_name = 'ticket/cadastrar_tickets.html'
    else:
        template_name = 'ticket/cadastrar_ticketsclient.html'

    # Passando os dados preenchidos para o template
    return render(request, template_name, {
        'clientes_e_administradores': clientes_e_administradores,
        'administradores': administradores,
        'empresas': empresas,
        'titulo': request.POST.get('titulo', ''),  # Passando o título de volta para o template
        'descricao': request.POST.get('descricao', ''),
        'data_entrega': request.POST.get('data_entrega', ''),
        'empresa_id': request.POST.get('empresa', ''),
        'responsavel_id': request.POST.get('responsavel', ''),
        'prioridade': request.POST.get('prioridade', 'Média'),  # Passando a prioridade de volta
    })



# Detalhar ticket - Apenas admin ou solicitante pode acessar
@login_required
def detalhar_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)

    # Verifique se o usuário tem permissão para ver o ticket
    if not request.user.is_staff and ticket.solicitante != request.user:
        return HttpResponseForbidden("Você não tem permissão para visualizar este ticket.")

    # Obtenha todos os usuários (clientes e administradores)
    users = CustomUser.objects.all()  # Todos os usuários, incluindo administradores e clientes

    # Obtenha apenas os administradores para o responsável
    admins = CustomUser.objects.filter(is_staff=True)  # Somente administradores para o responsável

    empresas = Empresa.objects.all()  # Obtenha todas as empresas

    # Formulários
    mensagem_form = MensagemForm()
    ticket_form = TicketForm(instance=ticket)

    # Se for um POST de atualização do ticket
    if request.method == "POST":
        if "nova_mensagem" in request.POST:
            mensagem_form = MensagemForm(request.POST)
            if mensagem_form.is_valid():
                nova_mensagem = mensagem_form.save(commit=False)
                nova_mensagem.ticket = ticket
                nova_mensagem.autor = request.user
                nova_mensagem.save()
                return redirect('detalhar_ticket', ticket_id=ticket.id)

        elif request.user.is_staff and "atualizar_ticket" in request.POST:
            ticket_form = TicketForm(request.POST, instance=ticket)
            if ticket_form.is_valid():
                ticket_form.save()
                return redirect('detalhar_ticket', ticket_id=ticket.id)
        
         # Escolher o template com base no tipo de usuário
    if request.user.is_staff:
        template_name = "ticket/detalhar_ticket.html"
    else:
        template_name = "ticket/detalhar_ticket_cliente.html"

    # Passando os dados necessários para o template
    return render(request, template_name, {
        "ticket": ticket,
        "ticket_form": ticket_form,
        "mensagem_form": mensagem_form,
        "users": users,  # Todos os usuários (solicitante)
        "admins": admins,  # Apenas administradores (responsável)
        "empresas": empresas,
    })




def editar_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)

    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        descricao = request.POST.get('descricao')
        data_entrega = request.POST.get('data_entrega')
        status = request.POST.get('status') if request.user.is_staff else ticket.status
        observacoes = request.POST.get('observacoes')

        ticket.titulo = titulo
        ticket.descricao = descricao
        ticket.data_entrega = data_entrega
        ticket.status = status
        ticket.observacoes = observacoes

        ticket.save()

    # Renderiza o template com base no tipo de usuário
    if request.user.is_staff:
        template_name = "ticket/detalhar_ticket.html"
    else:
        template_name = "ticket/detalhar_ticket_cliente.html"

    return render(request, template_name, {'ticket': ticket})

def atualizar_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)

    if request.method == 'POST':
        solicitante_id = request.POST.get('solicitante')
        responsavel_id = request.POST.get('responsavel')
        empresa_id = request.POST.get('empresa')

        if solicitante_id:
            ticket.solicitante = get_object_or_404(CustomUser, id=solicitante_id)

        if responsavel_id:
            ticket.responsavel = get_object_or_404(CustomUser, id=responsavel_id)

        if empresa_id:
            ticket.empresa = get_object_or_404(Empresa, id=empresa_id)

        ticket.prioridade = request.POST.get('prioridade', ticket.prioridade)
        ticket.data_criacao = request.POST.get('data_criacao', ticket.data_criacao)
        ticket.previsao_entrega = request.POST.get('previsao_entrega', ticket.previsao_entrega)

        ticket.save()

    # Renderiza o template com base no tipo de usuário
    if request.user.is_staff:
        template_name = "ticket/detalhar_ticket.html"
    else:
        template_name = "ticket/detalhar_ticket_cliente.html"

    return render(request, template_name, {'ticket': ticket})

def responder_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)

    if request.method == 'POST':
        texto = request.POST.get('resposta')
        tipo_resposta = request.POST.get('tipo_resposta')  # Tipo de resposta: pública ou interna

        if texto:
            if tipo_resposta not in ['publica', 'interna']:
                tipo_resposta = 'publica'  # Definir 'publica' como padrão

            Mensagem.objects.create(ticket=ticket, autor=request.user, texto=texto, tipo=tipo_resposta)

    # Renderiza o template com base no tipo de usuário
    if request.user.is_staff:
        template_name = "ticket/detalhar_ticket.html"
    else:
        template_name = "ticket/detalhar_ticket_cliente.html"

    return render(request, template_name, {'ticket': ticket})

def excluir_resposta(request, resposta_id):
    # Verifica se o usuário é administrador
    if request.user.is_staff:
        resposta = get_object_or_404(Mensagem, id=resposta_id)
        resposta.delete()
    return redirect('detalhar_ticket', ticket_id=resposta.ticket.id)
