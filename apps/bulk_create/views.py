from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from apps.bulk_create.worker import Worker
from apps.bulk_create.utils import criar_processos
from apps.bulk_create.models import ProcessoTemporario


programa = {'executando': False}


@csrf_exempt
def receber_json_processos_temporarios(request, qtde_processos):
    json_processos = criar_processos(qtde_processos)
    ProcessoTemporario.objects.bulk_create([
        ProcessoTemporario(**json_processo)
        for json_processo in json_processos
    ])

    return JsonResponse({
        'mensagem': 'Processos recebidos com sucesso.',
        'tipo': 'sucesso'
    }, safe=False)


@csrf_exempt
def worker(request, qtde_workers: int, limite_processos: int):
    if programa['executando']:
        return JsonResponse({
            'mensagem': 'Processamento em execução.',
            'tipo': 'sucesso'
        }, safe=False)

    programa['executando'] = True

    worker_principal = Worker(qtde_workers=qtde_workers, limite_processos=limite_processos)
    worker_principal.run()

    programa['executando'] = False

    return JsonResponse({
        'mensagem': 'Processamento finalizado.',
        'tipo': 'sucesso',
    }, safe=False)
