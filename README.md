# Configuração centralizada com Spring Cloud Config

**Integrantes:** Fernando, Felipe Montalvão e Victor Hugo.

Trabalho prático: quatro aplicações Spring Boot independentes, com as configurações dos clientes servidas por um Config Server a partir de um repositório Git.

## Links da atividade

- Código: https://github.com/FernandoAlves049/trabalho-config-server
- Configurações: https://github.com/FernandoAlves049/repo-configs
- Relatório: [docs/relatorio.pdf](docs/relatorio.pdf)
- Vídeo: a gravar; inserir o link após a gravação.

## Entrega

- Repositório do código: `trabalho-config-server`, já publicado.
- Repositório de configurações: `repo-configs`, já publicado separadamente.
- Relatório: `docs/relatorio.pdf` (duas páginas); versão editável em `docs/relatorio.md`.
- Apresentação: `docs/roteiro-video.md`, com roteiro de 15 minutos.
- Evidências dos testes executados: `docs/evidencias-testes.json` e `docs/validacao.md`.

Conforme o aviso da atividade, enviar o link do GitHub até **14/10/2026 às 23h59**, com o mesmo grupo do trabalho em Delphi, e produzir vídeo de **10 a 20 minutos**.

## Arquitetura

```text
GitHub: repo-configs / branch main
                 |
                 | clone / consulta de commits
                 v
       Config Server (localhost:8888)
                 |
                 | GET /{application}/{profile}/{label}
          +------+-------+
          |      |       |
       Vendas Estoque Relatórios
        8081    8082     8083
```

O cliente é identificado por `spring.application.name`; o perfil seleciona `dev` ou `prod`;
a label seleciona a branch `main`. O Git permite rastrear alterações pelo SHA do commit.
A atualização em um cliente já iniciado é explícita: commit no Git e `POST /actuator/refresh`.

## Estrutura

```text
trabalho-config-server/
├── config-server/        # @EnableConfigServer e acesso ao Git
├── cliente-vendas/       # /mensagem e /configuracao
├── cliente-estoque/
├── cliente-relatorios/
├── docs/                 # relatório, roteiro e evidências
├── scripts/              # teste completo de integração
├── .github/workflows/    # compilação automática no GitHub
├── pom.xml               # agregador; não é uma quinta aplicação
├── mvnw, mvnw.cmd        # Maven Wrapper
└── README.md

repo-configs/             # publicar em um segundo repositório
├── cliente-vendas-dev.properties
├── cliente-vendas-prod.properties
├── cliente-estoque-dev.properties
├── cliente-estoque-prod.properties
├── cliente-relatorios-dev.properties
├── cliente-relatorios-prod.properties
└── README.md
```

Os arquivos `application.properties` ficam em `src/main/resources` de cada aplicação.
Cada projeto contém seu próprio `pom.xml` e Maven Wrapper, e pode ser aberto e executado separadamente em uma IDE.

## Requisitos e versões

- JDK **21** (`java -version` deve mostrar 21 ou superior compatível).
- Git e acesso à internet para baixar dependências e acessar o GitHub.
- Maven fornecido pelo Wrapper; não é necessário instalar Maven separadamente.
- Python **3.10+** somente para a suíte de integração.
- Spring Boot **4.0.8** e Spring Cloud **2025.1.3**.

Os quatro projetos foram gerados no [Spring Initializr](https://start.spring.io/).
O arquivo `initializr.json` em cada projeto registra a URL e os parâmetros utilizados.
A versão do parent Maven foi normalizada de `4.0.8.RELEASE` para `4.0.8`, identificador publicado no Maven Central.
O Spring Web é fornecido pelo starter `spring-boot-starter-webmvc` no Spring Boot 4.
A compatibilidade de versões segue a [publicação oficial do Spring Cloud 2025.1.3](https://spring.io/blog/2026/08/20/spring-cloud-2025-1-3-has-been-released/).

## 1. Obter os projetos

Os dois repositórios já estão publicados. Para obter uma cópia com o histórico Git,
abra um terminal na pasta onde deseja guardar o trabalho:

```powershell
git clone https://github.com/FernandoAlves049/trabalho-config-server.git
git clone https://github.com/FernandoAlves049/repo-configs.git
cd trabalho-config-server
```

Mantenha as duas pastas lado a lado para executar a suíte de integração.
Se já tem o pacote local, pode usar os arquivos existentes para compilar e demonstrar.
Para fazer commits e enviar alterações, prefira as cópias clonadas acima.

## 2. Compilar

Na pasta **trabalho-config-server**, usando PowerShell:

```powershell
java -version
.\mvnw.cmd -B package
```

Se `JAVA_HOME` ainda não estiver definido, configure-o para a pasta do seu JDK (sem `bin`)
antes de executar o Wrapper. O primeiro build precisa de internet.
No Linux/macOS use `bash ./mvnw -B package`.

## 3. Iniciar as quatro aplicações

Abra quatro terminais PowerShell na pasta **trabalho-config-server**.

**Terminal 1 — iniciar primeiro o Config Server:**

```powershell
$env:CONFIG_GIT_URI = 'https://github.com/FernandoAlves049/repo-configs.git'
java -jar .\config-server\target\config-server-0.0.1-SNAPSHOT.jar
```

Aguarde o servidor iniciar e confirme `http://localhost:8888/actuator/health`.
O servidor já tem a URL deste repositório como padrão; CONFIG_GIT_URI permite sobrescrevê-la.

**Terminal 2 — Vendas:**

```powershell
java -jar .\cliente-vendas\target\cliente-vendas-0.0.1-SNAPSHOT.jar
```

**Terminal 3 — Estoque:**

```powershell
java -jar .\cliente-estoque\target\cliente-estoque-0.0.1-SNAPSHOT.jar
```

**Terminal 4 — Relatórios:**

```powershell
java -jar .\cliente-relatorios\target\cliente-relatorios-0.0.1-SNAPSHOT.jar
```

Para parar, use `Ctrl+C` em cada terminal. Alternativamente, execute um módulo pelo Wrapper
dentro da pasta dele: `.\mvnw.cmd spring-boot:run`.

## 4. Demonstrar DEV

| URL | Resposta esperada |
| --- | --- |
| http://localhost:8081/mensagem | Bem-vindo ao sistema de Vendas - Ambiente DEV |
| http://localhost:8082/mensagem | Serviço de Estoque inicializado - Ambiente DEV |
| http://localhost:8083/mensagem | Serviço de Relatórios em execução - Ambiente DEV |
| http://localhost:8081/configuracao | JSON com serviço, ambiente e mensagem |
| http://localhost:8888/cliente-vendas/dev | Configuração de Vendas, perfil dev |
| http://localhost:8888/cliente-estoque/dev | Configuração de Estoque, perfil dev |
| http://localhost:8888/cliente-relatorios/dev | Configuração de Relatórios, perfil dev |
| http://localhost:8888/actuator/health | `status: UP` |

Nos endpoints do servidor, confira `name`, `profiles`, `label`, `version` e `propertySources`.
O campo `version` corresponde ao SHA de um commit do repositório de configurações.

## 5. Selecionar PROD

Pare os três clientes DEV. O Config Server permanece ativo. Inicie cada cliente com:

```powershell
java -jar .\cliente-vendas\target\cliente-vendas-0.0.1-SNAPSHOT.jar --spring.profiles.active=prod
java -jar .\cliente-estoque\target\cliente-estoque-0.0.1-SNAPSHOT.jar --spring.profiles.active=prod
java -jar .\cliente-relatorios\target\cliente-relatorios-0.0.1-SNAPSHOT.jar --spring.profiles.active=prod
```

Execute cada comando em seu próprio terminal. As portas são as mesmas da execução DEV,
e as mensagens terminam em `Ambiente PROD`. Consulte também `http://localhost:8888/cliente-vendas/prod`.
O perfil PROD é uma demonstração acadêmica de ambientes, não uma infraestrutura de produção.

## 6. Demonstrar atualização e versionamento

Volte ao perfil DEV. Em `repo-configs/cliente-vendas-dev.properties`, altere:

```properties
mensagem.boasvindas=Mensagem atualizada por commit Git - Ambiente DEV
```

Na pasta do repositório de configurações:

```powershell
git add cliente-vendas-dev.properties
git commit -m "Atualiza mensagem de boas-vindas de Vendas"
git push
```

Consulte `http://localhost:8888/cliente-vendas/dev/main` para ver a nova configuração e o novo SHA.
Antes de atualizar o cliente, `/mensagem` conserva o texto anterior. Em seguida:

```powershell
Invoke-RestMethod -Method Post -Uri 'http://localhost:8081/actuator/refresh' -ContentType 'application/json' -Body '{}'
Invoke-RestMethod -Uri 'http://localhost:8081/mensagem'
```

O `@RefreshScope` recria o controlador com os valores atualizados. O commit sozinho não
envia atualizações automaticamente aos clientes. Alterar `server.port` requer reiniciar o cliente.
Para voltar a uma configuração anterior sem reescrever o histórico, use `git revert SHA_DO_COMMIT`,
faça `git push` e repita o refresh.

## 7. Executar os testes de integração

Pare os serviços manuais, compile e execute:

```powershell
.\mvnw.cmd -B package
python .\scripts\testar-integracao.py --configs ..\repo-configs
```

A suíte inicia os JARs reais, copia os arquivos para um Git temporário, faz commits e
valida DEV, PROD, mensagens, portas, SHA, refresh e fallback sem servidor. Encerra os
processos iniciados por ela e salva logs/evidências em `.run/`.
Use `--java "C:\caminho\jdk\bin\java.exe"` e `--git "C:\caminho\git.exe"` se necessário.
O acesso ao GitHub também foi validado; confira `docs/evidencias-github.json`.
O build Maven compila e empacota; os testes de comportamento estão nesta suíte Python.

## Propriedades principais

| Propriedade | Função |
| --- | --- |
| `spring.application.name` | Identifica o servidor ou cliente; seleciona o nome do arquivo remoto |
| `spring.profiles.active` | Seleciona DEV ou PROD; padrão DEV |
| `spring.config.import` | Importa a configuração do Config Server; `optional:` permite iniciar sem ele |
| `spring.cloud.config.label` | Branch Git solicitada pelo cliente; padrão `main` |
| `spring.cloud.config.server.git.uri` | Endereço Git lido pelo servidor, definido por `CONFIG_GIT_URI` |
| `spring.cloud.config.server.git.clone-on-start` | Clona/valida o repositório na inicialização |
| `spring.cloud.config.server.git.default-label` | Branch padrão do servidor |
| `spring.cloud.config.server.git.try-master-branch` | Desativa o fallback automático para a branch `master` |
| `spring.cloud.config.server.git.refresh-rate` | `0` consulta o Git a cada requisição de configuração |
| `server.port` | Porta HTTP; 8888 no servidor, 8081/8082/8083 nos clientes |
| `server.address` | Restringe esta demonstração à máquina local |
| `management.endpoints.web.exposure.include` | `*` expõe os endpoints Actuator conforme a atividade |
| `mensagem.boasvindas` | Texto remoto retornado em `/mensagem` |
| `app.ambiente` | Perfil identificado em `/configuracao` |

Variáveis opcionais: `CONFIG_SERVER_URL` (padrão `http://localhost:8888`),
`CONFIG_GIT_LABEL` (padrão `main`) e `APP_PROFILE` (padrão `dev`).
Sem Config Server, os clientes usam a porta local de fallback e exibem `Configuração não carregada`.
O servidor não configura `spring.config.import` nem aponta para si mesmo.

## Concluir a entrega

Os repositórios do código e das configurações estão públicos e ligados na seção
“Links da atividade”. O Config Server já usa a URL real de `repo-configs` como padrão.

Foram aprovadas **30 verificações com Git local** e **13 verificações adicionais
usando o GitHub remoto**, incluindo o SHA publicado e as mensagens dos três clientes DEV.
Confira `docs/validacao.md` e os arquivos de evidências.

Grave o vídeo de 10 a 20 minutos seguindo `docs/roteiro-video.md` e inclua seu link
na seção “Links da atividade”. Para entregar, envie:
https://github.com/FernandoAlves049/trabalho-config-server.

## Problemas comuns

- **Erro no clone:** confira `CONFIG_GIT_URI`, acesso ao GitHub e branch `main`.
- **Configuração não carregada:** confira o servidor e o nome exato dos arquivos e serviços.
- **Porta ocupada:** pare o processo anterior antes de alternar DEV/PROD ou rodar os testes.
- **Mensagem não mudou após commit:** confirme o push, consulte o servidor e execute o POST de refresh.
- **Acentos no arquivo:** mantenha os escapes `\u00xx` nos `.properties`; o endpoint retorna texto UTF-8.

## Referências

- [Spring Cloud Config Client](https://docs.spring.io/spring-cloud-config/reference/client.html)
- [Spring Cloud Config Server](https://docs.spring.io/spring-cloud-config/reference/server.html)
- [Guia oficial de configuração centralizada e refresh](https://spring.io/guides/gs/centralized-configuration/)
- [Spring Cloud 2025.1.3 e compatibilidade](https://spring.io/blog/2026/08/20/spring-cloud-2025-1-3-has-been-released/)
