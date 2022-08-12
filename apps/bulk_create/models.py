import json

from django.db import models


class ProcessoBase(models.Model):
    cliente_id = models.PositiveIntegerField()
    usuario_id = models.PositiveIntegerField()
    json_processo = models.TextField()
    data_cadastro = models.DateTimeField(auto_now_add=True)

    def to_json(self):
        return {
            'cliente_id': self.cliente_id,
            'usuario_id': self.usuario_id,
            'json_processo': json.loads(self.json_processo)
        }

    class Meta:
        abstract = True


class ProcessoTemporario(ProcessoBase):
    retirado = models.BooleanField(default=False)
    erro_ao_cadastrar = models.BooleanField(default=False)
    mensagem_erro = models.TextField(blank=True, null=True)


class Segurado(models.Model):
    nome = models.CharField(max_length=255)
    endereco = models.CharField(max_length=255)


class Veiculo(models.Model):
    placa = models.CharField(max_length=255)


class Processo(ProcessoBase):
    segurado = models.ForeignKey(Segurado, on_delete=models.CASCADE, blank=True, null=True)
    veiculo = models.ForeignKey(Veiculo, on_delete=models.CASCADE, blank=True, null=True)
