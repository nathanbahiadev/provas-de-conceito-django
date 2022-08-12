from apps.bulk_create.utils import retry
from apps.bulk_create.models import Processo, ProcessoTemporario, Veiculo, Segurado


class Worker:
    def __init__(self, limit: int):
        self.limit = limit

    def dividir_processos(self, qtde):
        processos_temporarios = self.filtrar_processos(qtde)
        processos = {}
        index_inicial = 0
        index_final = self.limit

        for i in range(qtde):
            processos[str(i)] = processos_temporarios[index_inicial:index_final]
            index_inicial += self.limit
            index_final += self.limit

        return processos

    def run(self, name, processos):
        try:
            self.cadastrar_processos(processos)
            print(f'[INFO] Worker {name}: Pacote cadastrado com sucesso.')

        except Exception as e:
            print(f'[INFO] Worker {name}: Erro ao cadastrar processos ({e.__class__.__name__}: {e}).')
            self.relatar_erro(processos, e)

    def filtrar_processos(self, qtde):
        processos_temporarios = ProcessoTemporario.objects.filter(retirado=False)[:qtde*self.limit]
        return processos_temporarios

    @retry(times=3, raise_error=True)
    def cadastrar_processos(self, processos):
        lista_processos = []

        for p in processos:
            processo_json = p.to_json()
            placa_veiculo = processo_json['json_processo']['placa_veiculo']
            nome_cliente_final = processo_json['json_processo']['nome_cliente_final']
            endereco_cliente_final = processo_json['json_processo']['endereco_cliente_final']

            lista_processos.append(Processo(
                veiculo=Veiculo.objects.create(placa=placa_veiculo),
                segurado=Segurado.objects.create(nome=nome_cliente_final, endereco=endereco_cliente_final),
                **processo_json
            ))

        Processo.objects.bulk_create(lista_processos)
        ProcessoTemporario.objects.filter(id__in=[p.id for p in processos]).update(
            retirado=True,
            erro_ao_cadastrar=False,
            mensagem_erro=None,
        )

    def recuperar_processos_com_erro(self):
        print(f'[INFO] Worker (recuperação): Iniciando worker de recuperação de processos com erro')
        processos_com_erro = ProcessoTemporario.objects.filter(erro_ao_cadastrar=True)
        self.cadastrar_processos(processos_com_erro)

    def relatar_erro(self, processos, erro):
        ProcessoTemporario.objects.filter(id__in=[p.id for p in processos]).update(
            retirado=True,
            erro_ao_cadastrar=True,
            mensagem_erro=str(erro),
        )
