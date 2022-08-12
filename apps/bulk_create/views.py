from threading import Thread

from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from apps.bulk_create.utils import make_fake_processos, make_worker_name
from apps.bulk_create.worker import Worker
from apps.bulk_create.models import ProcessoTemporario


threads = []


@csrf_exempt
def receber_json_processos_temporarios(request, qtde):
    json_processos = make_fake_processos(qtde=qtde)
    ProcessoTemporario.objects.bulk_create([
        ProcessoTemporario(**json_processo) for json_processo in json_processos
    ])

    return JsonResponse({
        'mensagem': 'Processos recebidos com sucesso',
        'tipo': 'sucesso'
    }, safe=False)


@csrf_exempt
def worker(request, qtde: int, limit: int):
    global threads

    if threads:
        return JsonResponse({
            'mensagem': 'Já um processo sendo executado. Caso queira adicionar ou remover mais workers, '
                        'pare o processo em execução e insira novos parâmetros nesta função.',
            'tipo': 'sucesso'
        }, safe=False)

    __worker = Worker(limit=limit)

    while True:
        processos = __worker.dividir_processos(qtde)
        existem_processos = len(processos['0']) > 0
        threads = []

        if existem_processos:
            for i in range(qtde):
                threads.append(
                    Thread(target=__worker.run, args=[make_worker_name(i), processos[str(i)]])
                )
            [th.start() for th in threads]
            [th.join() for th in threads]

        else:
            th = Thread(target=__worker.recuperar_processos_com_erro)
            th.start() and th.join()
            break

    threads = []

    return JsonResponse({
        'mensagem': 'Processamento finalizado.',
        'tipo': 'sucesso',
    }, safe=False)
