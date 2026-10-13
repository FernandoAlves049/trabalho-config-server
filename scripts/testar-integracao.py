"""Teste real das quatro aplicações, sem alterar o repositório de configurações original.

Requer: JDK 21, Git, Python 3.10+ e os JARs gerados por ./mvnw package.
Uso: python scripts/testar-integracao.py --configs ../repo-configs
"""
from pathlib import Path
from urllib.request import Request, urlopen
import argparse
import json
import os
import shutil
import socket
import subprocess
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
APPS = ['cliente-vendas', 'cliente-estoque', 'cliente-relatorios']
PORTS = [8081, 8082, 8083]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--configs', type=Path, default=ROOT.parent / 'repo-configs')
parser.add_argument('--java', default='java')
parser.add_argument('--git', default='git')
parser.add_argument('--evidencias', type=Path, default=ROOT / '.run/evidencias-testes.json')
args = parser.parse_args()
processes = []
logs = []
checks = []
run_dir = ROOT / '.run/integracao'
run_dir.mkdir(parents=True, exist_ok=True)

def check(name, condition, detail):
    checks.append({'teste': name, 'resultado': 'OK' if condition else 'FALHA', 'detalhe': detail})
    print(('OK  ' if condition else 'FALHA  ') + name, flush=True)
    if not condition:
        raise AssertionError(f'{name}: {detail}')

def http(url, method='GET'):
    req = Request(url, data=b'{}' if method == 'POST' else None, method=method,
                  headers={'Content-Type': 'application/json'} if method == 'POST' else {})
    with urlopen(req, timeout=10) as response:
        return response.read().decode('utf-8')

def wait_health(port, process):
    deadline = time.monotonic() + 90
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError(f'Aplicação encerrou. Consulte {run_dir}')
        try:
            if json.loads(http(f'http://localhost:{port}/actuator/health'))['status'] == 'UP':
                return
        except Exception:
            pass
        time.sleep(0.5)
    raise TimeoutError(f'Porta {port} não ficou saudável. Consulte {run_dir}')

def start(app, suffix='', options=()):
    jar = ROOT / app / 'target' / (app + '-0.0.1-SNAPSHOT.jar')
    if not jar.exists():
        raise FileNotFoundError(f'Compile primeiro com ./mvnw package: {jar}')
    log = (run_dir / (app + suffix + '.log')).open('w', encoding='utf-8')
    logs.append(log)
    env = os.environ.copy()
    # Do not inherit profile/server/repository overrides from a previous manual demo.
    for key in ['APP_PROFILE', 'CONFIG_SERVER_URL', 'CONFIG_GIT_URI', 'CONFIG_GIT_LABEL', 'SPRING_PROFILES_ACTIVE']:
        env.pop(key, None)
    proc = subprocess.Popen([args.java, '-Xms48m', '-Xmx256m', '-jar', str(jar), *options],
                            cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, env=env,
                            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
    processes.append(proc)
    return proc

def stop(proc):
    if proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=15)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=10)

def git(repo, *commands):
    return subprocess.check_output([args.git, '-c', 'user.name=Teste Integracao', '-c',
                                   'user.email=teste@example.invalid', '-C', str(repo), *commands],
                                  stderr=subprocess.STDOUT, text=True, encoding='utf-8').strip()

def properties(path):
    result = {}
    for line in path.read_text(encoding='utf-8').splitlines():
        if line.strip() and not line.startswith('#'):
            key, value = line.split('=', 1)
            result[key] = value.encode('ascii').decode('unicode_escape')
    return result

try:
    for port in [8888, *PORTS, 18081]:
        with socket.socket() as sock:
            if sock.connect_ex(('127.0.0.1', port)) == 0:
                raise RuntimeError(f'Porta {port} já está ocupada. Pare a execução anterior.')
    with tempfile.TemporaryDirectory(prefix='config-git-', dir=run_dir) as temp:
        # TemporaryDirectory recursively removes only this generated directory.
        if not Path(temp).resolve().is_relative_to(run_dir.resolve()):
            raise RuntimeError('Diretório temporário fora da área de testes')
        repo = Path(temp) / 'origin'
        repo.mkdir()
        for source in args.configs.glob('*.properties'):
            shutil.copy2(source, repo / source.name)
        if len(list(repo.glob('*.properties'))) != 6:
            raise ValueError('Esperados seis arquivos de configuração DEV/PROD.')
        git(repo, 'init', '-b', 'main')
        git(repo, 'add', '.')
        git(repo, 'commit', '-m', 'Configuracoes iniciais para teste')
        initial_sha = git(repo, 'rev-parse', 'HEAD')
        server = start('config-server', options=[f'--spring.cloud.config.server.git.uri={repo.as_uri()}',
                       f'--spring.cloud.config.server.git.basedir={Path(temp) / "clone"}'])
        wait_health(8888, server)
        check('Config Server saudável', True, 'GET /actuator/health: UP')
        for profile in ['dev', 'prod']:
            clients = []
            for app, port in zip(APPS, PORTS):
                expected = properties(repo / (app + '-' + profile + '.properties'))
                response = json.loads(http(f'http://localhost:8888/{app}/{profile}'))
                merged = {}
                for source in reversed(response['propertySources']):
                    merged.update(source['source'])
                check(f'{app}/{profile}: propriedades remotas',
                      all(str(merged.get(k)) == v for k, v in expected.items()), merged)
                check(f'{app}/{profile}: versionamento Git', response['version'] == initial_sha, response['version'])
                client = start(app, '-' + profile, [f'--spring.profiles.active={profile}'])
                clients.append(client)
                wait_health(port, client)
                message = http(f'http://localhost:{port}/mensagem')
                check(f'{app}/{profile}: mensagem e porta', message == expected['mensagem.boasvindas'], message)
                configuration = json.loads(http(f'http://localhost:{port}/configuracao'))
                check(f'{app}/{profile}: ambiente', configuration['ambiente'] == profile and configuration['servico'] == app,
                      configuration)
            if profile == 'dev':
                changed = repo / 'cliente-vendas-dev.properties'
                original = http('http://localhost:8081/mensagem')
                changed.write_text('mensagem.boasvindas=Mensagem atualizada por commit Git - Ambiente DEV\nserver.port=8081\napp.ambiente=dev\n', encoding='utf-8')
                git(repo, 'add', '.')
                git(repo, 'commit', '-m', 'Atualiza mensagem DEV de Vendas')
                new_sha = git(repo, 'rev-parse', 'HEAD')
                latest = json.loads(http('http://localhost:8888/cliente-vendas/dev/main'))
                check('Novo commit visível no Config Server', latest['version'] == new_sha and new_sha != initial_sha, new_sha)
                check('Cliente conserva valor até refresh', http('http://localhost:8081/mensagem') == original, original)
                refreshed_keys = json.loads(http('http://localhost:8081/actuator/refresh', 'POST'))
                updated = http('http://localhost:8081/mensagem')
                check('Atualização sem reiniciar cliente', 'mensagem.boasvindas' in refreshed_keys and updated.startswith('Mensagem atualizada por commit'), updated)
                check('Processo do cliente permanece ativo', clients[0].poll() is None, {'pid': clients[0].pid})
                initial_sha = new_sha
            for client in clients:
                stop(client)
        stop(server)
        fallback = start('cliente-vendas', '-fallback', ['--server.port=18081'])
        wait_health(18081, fallback)
        check('Importação opcional sem servidor', http('http://localhost:18081/mensagem') == 'Configuração não carregada',
              'Mensagem de fallback; porta local 18081 para este teste')
        stop(fallback)
except Exception as exc:
    checks.append({'teste':'execução da suíte', 'resultado':'FALHA', 'detalhe':str(exc)})
    raise
finally:
    for proc in reversed(processes):
        stop(proc)
    for log in logs:
        log.close()
    args.evidencias.parent.mkdir(parents=True, exist_ok=True)
    args.evidencias.write_text(json.dumps({'backend_testado':'Git local temporário (file://), não GitHub remoto',
        'checks':checks, 'total':len(checks), 'aprovados':sum(x['resultado']=='OK' for x in checks)},
        ensure_ascii=False, indent=2), encoding='utf-8')
print(f'{len(checks)} verificações concluídas. Evidências: {args.evidencias}', flush=True)
