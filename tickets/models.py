from django.db import models
from django.conf import settings
from gestao.models import Empresa  # Importando o modelo Empresa do app Gestão

class Ticket(models.Model):
    
    solicitante = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='tickets', on_delete=models.CASCADE
    )
    titulo = models.CharField(max_length=255, null=False, blank=False)  # Definindo um valor padrão
    descricao = models.TextField()
    data_entrega = models.DateField()
    empresa = models.ForeignKey(
        Empresa, related_name='tickets', on_delete=models.CASCADE, null=True, blank=True
    )
    responsavel = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='tickets_responsaveis', 
        on_delete=models.SET_NULL, null=True, blank=True, 
        limit_choices_to={'is_staff': True}
    )
    
    STATUS_CHOICES = [
        ('Aberto', 'Aberto'),
        ('Em andamento', 'Em andamento'),
        ('Concluído', 'Concluído'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Aberto')

    PRIORIDADE_CHOICES = [
        ('Baixa', 'Baixa'),
        ('Média', 'Média'),
        ('Alta', 'Alta'),
    ]
    prioridade = models.CharField(max_length=6, choices=PRIORIDADE_CHOICES, default='Média')

    data_criacao = models.DateTimeField(auto_now_add=True)
    previsao_entrega = models.DateField(null=True, blank=True)
    # Anotações internas, visíveis apenas para admins
    observacoes = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Ticket #{self.id} - {self.descricao[:30]}"

    class Meta:
        ordering = ['-data_criacao']

class Arquivo(models.Model):
    ticket = models.ForeignKey(
        Ticket, related_name='arquivos', on_delete=models.CASCADE
    )
    arquivo = models.FileField(upload_to='tickets/arquivos/')
    data_upload = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Arquivo {self.id} - {self.arquivo.name}"

class Mensagem(models.Model):
    ticket = models.ForeignKey('Ticket', related_name='mensagens', on_delete=models.CASCADE)
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    texto = models.TextField()
    data_envio = models.DateTimeField(auto_now_add=True)
    tipo = models.CharField(max_length=10, choices=[('publica', 'Pública'), ('interna', 'Interna')], default='publica')

    def __str__(self):
        return f"Mensagem de {self.autor} para o ticket {self.ticket.id} ({self.tipo})"
