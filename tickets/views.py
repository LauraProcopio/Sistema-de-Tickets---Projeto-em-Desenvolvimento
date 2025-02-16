from django.shortcuts import render, redirect, get_object_or_404
from accounts.models import CustomUser  # Certifique-se de que está importando o modelo correto de usuário
from django.contrib.auth.decorators import login_required
from gestao.models import Empresa
from .forms import MensagemForm, TicketForm 
from django.http import HttpResponseForbidden
from .models import Ticket, Mensagem, Empresa, Arquivo
from django.contrib import messages
from django.utils.dateparse import parse_date 
from django.core.paginator import Paginator

# Listar tickets - Filtra por usuário se for cliente
@login_required
def listar_tickets(request):
    if request.user.is_staff:
        # Administradores veem todos os tickets
        tickets = Ticket.objects.all()
        template_name = 'ticket/listar_tickets.html'
    else:
        # Clientes veem os seus próprios tickets e os da sua empresa
        tickets = Ticket.objects.filter(solicitante=request.user)
        
        # Garantir que o usuário tem uma empresa associada
        if hasattr(request.user, 'empresa') and request.user.empresa:
            tickets = tickets | Ticket.objects.filter(empresa=request.user.empresa)
        
        template_name = 'ticket/listar_ticketsclient.html'

    # Filtro por status
    status = request.GET.get('status')
    if status:
        tickets = tickets.filter(status=status)

    # Busca por título
    query = request.GET.get('q')
    if query:
        tickets = tickets.filter(titulo__icontains=query)

    # Ordenação
    ordenar_por = request.GET.get('ordenar_por', 'data')  # Padrão: ordenar por data
    if ordenar_por == 'id':
        tickets = tickets.order_by('id')
    else:
        tickets = tickets.order_by('-data_criacao')

    # Aplicando a paginação
    paginator = Paginator(tickets, 5)  # 5 tickets por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, template_name, {'tickets': page_obj})


# Excluir ticket - Somente administrador pode excluir
@login_required
def excluir_ticket(request, id):
    ticket = get_object_or_404(Ticket, id=id)

    # Verifica se o usuário é o cliente do ticket ou administrador
    if ticket.solicitante == request.user or request.user.is_staff:
        titulo_ticket = ticket.titulo  # Captura o título antes de excluir
        id_ticket = ticket.id  # Captura o ID antes de excluir
        ticket.delete()

        # Mensagem informando qual ticket foi excluído
        messages.success(request, f"Ticket #{id_ticket} - '{titulo_ticket}' foi excluído com sucesso!")

        return redirect('listar_tickets')
    else:
        # Se não for o cliente ou administrador, retornar para a lista de tickets
        messages.error(request, "Você não tem permissão para excluir este ticket.")
        return redirect('listar_tickets')



# Criação de ticket - Admin ou Cliente
@login_required
def cadastrar_tickets(request):
    if request.method == 'POST':
        # Captura os dados diretamente do request.POST
        solicitante_id = request.POST.get('solicitante')
        empresa_id = request.POST.get('empresa')
        responsavel_id = request.POST.get('responsavel') if request.user.is_staff else None
        titulo = request.POST.get('titulo')
        descricao = request.POST.get('descricao')
        data_entrega = request.POST.get('data_entrega')
        prioridade = request.POST.get('prioridade', 'Média')

        # Verificações de existência antes de buscar os objetos
        solicitante = get_object_or_404(CustomUser, id=solicitante_id) if solicitante_id else request.user
        empresa = Empresa.objects.filter(id=empresa_id).first() if empresa_id else None
        responsavel = get_object_or_404(CustomUser, id=responsavel_id) if responsavel_id else None

        # Criando o ticket
        ticket = Ticket.objects.create(
            solicitante=solicitante,
            titulo=titulo,
            descricao=descricao,
            data_entrega=data_entrega,
            empresa=empresa,
            responsavel=responsavel,
            prioridade=prioridade
        )

        # Processamento de arquivos
        arquivos = request.FILES.getlist('arquivos')
        for arquivo in arquivos:
            Arquivo.objects.create(ticket=ticket, arquivo=arquivo)

        # Redirecionamento baseado no tipo de usuário
        if request.user.is_staff:
         return redirect('detalhar_ticket', ticket_id=ticket.id)
        else:
            return redirect('detalhar_ticket_cliente', ticket_id=ticket.id)


    # Captura as opções para o formulário
    clientes_e_administradores = CustomUser.objects.all()
    administradores = CustomUser.objects.filter(is_staff=True)
    empresas = Empresa.objects.all()

    # Escolhe o template com base no tipo de usuário
    template_name = 'ticket/cadastrar_tickets.html' if request.user.is_staff else 'ticket/cadastrar_ticketsclient.html'

    return render(request, template_name, {
        'clientes_e_administradores': clientes_e_administradores,
        'administradores': administradores,
        'empresas': empresas,
        'titulo': request.POST.get('titulo', ''),
        'descricao': request.POST.get('descricao', ''),
        'data_entrega': request.POST.get('data_entrega', ''),
        'empresa_id': request.POST.get('empresa', ''),
        'responsavel_id': request.POST.get('responsavel', ''),
        'prioridade': request.POST.get('prioridade', 'Média'),
    })


# Detalhar ticket - Apenas admin ou solicitante pode acessar
@login_required
def detalhar_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)

    # Verifique se o usuário tem permissão para ver o ticket
    if not request.user.is_staff and ticket.solicitante != request.user:
        if not (hasattr(request.user, 'empresa') and request.user.empresa == ticket.empresa):
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

    if not request.user.is_staff and ticket.solicitante != request.user:
        return HttpResponseForbidden("Você não tem permissão para editar este ticket.")


    if request.method == 'POST':
        ticket.titulo = request.POST.get('titulo', ticket.titulo) or ticket.titulo
        ticket.descricao = request.POST.get('descricao', ticket.descricao) or ticket.descricao
        ticket.status = request.POST.get('status', ticket.status) if request.user.is_staff else ticket.status
        ticket.observacoes = request.POST.get('observacoes', ticket.observacoes) or ticket.observacoes

        data_entrega = request.POST.get('data_entrega')
        ticket.data_entrega = parse_date(data_entrega) if data_entrega else ticket.data_entrega

        ticket.save()

    template_name = "ticket/detalhar_ticket.html" if request.user.is_staff else "ticket/detalhar_ticket_cliente.html"
    return render(request, template_name, {'ticket': ticket})



def atualizar_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)

    if request.method == 'POST':
        # Pegando os IDs do formulário
        solicitante_id = request.POST.get('solicitante')
        responsavel_id = request.POST.get('responsavel')
        empresa_id = request.POST.get('empresa')
        novo_status = request.POST.get('status')

        # Atualizar apenas se os valores forem válidos
        if solicitante_id:
            solicitante = CustomUser.objects.filter(id=solicitante_id).first()
            if solicitante:
                ticket.solicitante = solicitante

        if responsavel_id:
            responsavel = CustomUser.objects.filter(id=responsavel_id).first()
            if responsavel:
                ticket.responsavel = responsavel

        if empresa_id:
            empresa = Empresa.objects.filter(id=empresa_id).first()
            if empresa:
                ticket.empresa = empresa

        # Validando status antes de salvar
        status_permitidos = ["Aberto", "Em andamento", "Concluído"]
        if novo_status in status_permitidos:
            ticket.status = novo_status

        # Atualizando outros campos
        ticket.prioridade = request.POST.get('prioridade', ticket.prioridade)
        ticket.previsao_entrega = request.POST.get('previsao_entrega', ticket.previsao_entrega)
        
        # Garantindo que a data de atualização seja tratada corretamente
        data_atualizacao = request.POST.get("data_atualizacao")
        if data_atualizacao:
            ticket.data_atualizacao = data_atualizacao  # Supondo que o campo aceite strings formatadas corretamente
        
        ticket.save()
        messages.success(request, "Ticket atualizado com sucesso!")

        return redirect('detalhar_ticket', ticket_id=ticket.id)

    # Renderiza o template correto
    template_name = "ticket/detalhar_ticket.html" if request.user.is_staff else "ticket/detalhar_ticket_cliente.html"
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
