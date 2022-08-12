import json
from time import sleep
from random import choice
from functools import wraps

from faker import Faker


faker_factory = Faker('pt_BR')


def make_fake_processos(qtde):
    return [{
        'cliente_id': 61,
        'usuario_id': 277,
        'json_processo': json.dumps({
            'nome_cliente_final': faker_factory.name(),
            'endereco_cliente_final': faker_factory.address(),
            'placa_veiculo': faker_factory.license_plate(),
        })
    }for _ in range(qtde)]


def make_worker_name(n):
    return choice([
        f'{n+1} - Ada Lovelace',
        f'{n+1} - Brian Kernighan',
        f'{n+1} - Dennis Ritchie',
        f'{n+1} - Bjarne Stroustrup',
        f'{n+1} - Guido van Rossum',
        f'{n+1} - Brendan Eich',
        f'{n+1} - Lars Bak',
        f'{n+1} - Robert Griesemer',
        f'{n+1} - Sebastián Ramírez',
        f'{n+1} - Jean Reinhardt',
        f'{n+1} - Armin Ronacher',
        f'{n+1} - Michael Bayer',
    ])


def retry(times: int = 3, exceptions: tuple = (Exception,), raise_error: bool = False):
    """
    @param times: inteiro -> quantidade de vezes que a função será executada em caso de erro
    @param exceptions: lista -> tipos de erros esperados para a função, por padrão recebe 'Exception', que abrange todos os tipos de erro
    @param raise_error: boleano -> indicador para verificar quando ao exceder a quantidade de tentativas se a excessão será levantada ou passada
    """
    count = 0

    def decorator(func):
        @wraps(func)
        def inner(*args, **kwargs):
            try:
                return func(*args, **kwargs)

            except tuple(exceptions) as e:
                nonlocal count

                if count < times:
                    count += 1
                    print('Erro ao executar função. Tentando novamente...') and sleep(10)
                    return inner(*args, **kwargs)

                if raise_error:
                    raise e

        return inner
    return decorator
