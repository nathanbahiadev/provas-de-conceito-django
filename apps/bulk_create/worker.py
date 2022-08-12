from threading import Thread

from apps.bulk_create.utils import retry, criar_nome_worker
from apps.bulk_create.models import Processo, ProcessoTemporario, Veiculo, Segurado


class Worker:
    def __init__(self, qtde_workers: int, limite_processos: int):
        self.qtde_workers = qtde_workers
        self.limite_processos = limite_processos

    def run(self):
        while True:
            processos_temporarios: dict = self.dividir_processos()
            existem_processos_temporarios = len(processos_temporarios['0']) > 0

            if existem_processos_temporarios:
                threads = [
                    Thread(target=self.main, args=[criar_nome_worker(n), processos_temporarios[str(n)]])
                    for n in range(self.qtde_workers)
                ]
                [th.start() for th in threads]
                [th.join() for th in threads]

            else:
                th = Thread(target=self.recuperar_processos_com_erro)
                th.start() and th.join()
                break

    def dividir_processos(self):
        processos_temporarios = self.filtrar_processos()

        index_inicial = 0
        index_final = self.limite_processos
        processos_por_workers = {}

        for worker in range(self.qtde_workers):
            processos_por_workers[str(worker)] = processos_temporarios[index_inicial:index_final]
            index_inicial += self.limite_processos
            index_final += self.limite_processos

        return processos_por_workers

    def main(self, nome_worker, processos):
        try:
            self.cadastrar_processos(processos)
            print(f'[INFO] Worker {nome_worker}: Pacote cadastrado com sucesso.')

        except Exception as e:
            print(f'[INFO] Worker {nome_worker}: Erro ao cadastrar processos ({e.__class__.__name__}: {e}).')
            self.relatar_erro(processos, e)

    def filtrar_processos(self):
        qtde_processos = self.qtde_workers * self.limite_processos
        processos_temporarios = ProcessoTemporario.objects.filter(retirado=False)[:qtde_processos]
        return processos_temporarios

    @retry(times=3, raise_error=True)
    def cadastrar_processos(self, processos):
        lista_processos = []

        for p in processos:
            processo_json = p.to_json()
            veiculo = Veiculo.objects.create(placa=processo_json['json_processo']['placa_veiculo'])
            segurado = Segurado.objects.create(
                nome=processo_json['json_processo']['nome_cliente_final'],
                endereco=processo_json['json_processo']['endereco_cliente_final']
            )
            lista_processos.append(Processo(veiculo=veiculo, segurado=segurado, **processo_json))

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
