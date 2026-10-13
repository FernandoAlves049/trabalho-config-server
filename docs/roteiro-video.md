# Roteiro do vídeo — 15 minutos

Integrantes: Fernando, Felipe Montalvão e Victor Hugo.
O aviso exige entre 10 e 20 minutos. Este roteiro divide cerca de 5 minutos por integrante.
Adaptem as falas e ensaiem a demonstração antes de gravar.

## Preparação

1. Publiquem os dois repositórios e usem a URL real do GitHub em `CONFIG_GIT_URI`.
2. Compilem com `.\mvnw.cmd -B package` antes da gravação.
3. Abram a IDE, quatro terminais e as páginas do GitHub. Evitem mostrar credenciais.
4. Deixem abertas as URLs `/mensagem` dos três clientes e `/cliente-vendas/dev` do servidor.
5. Iniciem o servidor primeiro e os três clientes no perfil DEV. Confirmem as mensagens.
6. Combinem as trocas de fala e a mudança de perfil; não iniciem DEV e PROD simultaneamente.

## Fernando — 0:00 a 5:00

**0:00–1:00 | Apresentação e problema**

Fala sugerida: “Somos Fernando, Felipe Montalvão e Victor Hugo. Nosso trabalho demonstra
configuração centralizada com Spring Cloud Config. Quando cada serviço guarda suas
configurações separadamente, é mais difícil manter os ambientes consistentes e rastrear
alterações. Aqui, um servidor central consulta um repositório Git e entrega a configuração
correta a cada cliente.”

Mostrar: arquitetura do README e os dois repositórios GitHub.

**1:00–2:00 | Arquitetura**

Explicar: Config Server na porta 8888; Vendas, Estoque e Relatórios nas portas 8081, 8082 e
8083. São quatro processos Spring Boot. O segundo repositório guarda somente configurações.
O Git versiona os arquivos e o servidor informa o SHA do commit usado.

**2:00–3:15 | Servidor**

Mostrar `ConfigServerApplication.java` e explicar `@SpringBootApplication` e
`@EnableConfigServer`. Mostrar `pom.xml`: Web, Actuator, Config Server e BOM do Spring Cloud.
Os projetos vieram do Spring Initializr; o BOM controla as versões das dependências Cloud.

**3:15–5:00 | Propriedades e consulta**

Mostrar `config-server/src/main/resources/application.properties`.
Explicar nome, porta, URI Git via variável, clone na inicialização, branch `main` e Actuator.
O servidor não importa configuração de si próprio.
Abrir `/actuator/health` e `/cliente-vendas/dev/main`.
Explicar `name`, `profiles`, `propertySources` e `version`, sem ler o JSON inteiro.

## Felipe Montalvão — 5:00 a 10:00

**5:00–6:15 | Repositório de configurações**

Mostrar os seis arquivos `cliente-...-dev.properties` e `cliente-...-prod.properties`.
Explicar que o nome combina aplicação e ambiente. Abrir Vendas DEV e PROD e comparar
`mensagem.boasvindas`, `server.port` e `app.ambiente`. Os escapes Unicode preservam os acentos.

**6:15–7:30 | Cliente e importação**

Mostrar `cliente-vendas/pom.xml` e `application.properties`.
Explicar `spring.application.name=cliente-vendas`, perfil `dev`, label `main` e
`spring.config.import=optional:configserver:...`.
O prefixo `optional:` permite iniciar sem o servidor; nesse caso aparece o texto de fallback.
Na execução normal, o servidor deve estar ativo antes dos clientes.

**7:30–8:45 | Código do endpoint**

Abrir `ConfigController.java`. Explicar `@RestController`, `@Value`, `@GetMapping` e
`@RefreshScope`. O endpoint `/mensagem` retorna o valor remoto; `/configuracao` facilita
conferir o serviço e o ambiente. Os outros dois clientes usam o mesmo mecanismo, cada um
com seu próprio projeto e nome.

**8:45–10:00 | Demonstração DEV**

Abrir os três `/mensagem`, ler o resultado e relacioná-lo ao arquivo correspondente no GitHub.
Abrir `/configuracao` de Vendas e os endpoints de configuração dos outros dois serviços.
Explicar o fluxo: cliente inicia → solicita configuração → servidor consulta Git → cliente
aplica propriedades → serviço passa a responder na sua porta.

## Victor Hugo — 10:00 a 15:00

**10:00–11:15 | Perfil PROD**

Parar os três clientes e reiniciá-los com `--spring.profiles.active=prod` em terminais separados.
Mostrar uma mensagem `Ambiente PROD` e `/cliente-vendas/prod` no servidor.
Explicar que trocar o perfil seleciona outro arquivo; não foi necessário alterar o Java.
Voltar os clientes ao perfil DEV para a próxima demonstração.

**11:15–13:15 | Commit e atualização sem reiniciar**

1. No GitHub, editar somente `mensagem.boasvindas` em `cliente-vendas-dev.properties`.
2. Salvar um commit na branch `main`; se editar localmente, fazer também `git push`.
3. Atualizar `/cliente-vendas/dev/main` e mostrar a nova mensagem e o novo SHA.
4. Abrir `/mensagem` do cliente: a mensagem ainda é a antiga.
5. Executar no PowerShell:

```powershell
Invoke-RestMethod -Method Post -Uri 'http://localhost:8081/actuator/refresh' -ContentType 'application/json' -Body '{}'
Invoke-RestMethod -Uri 'http://localhost:8081/mensagem'
```

Explicar: o POST recarrega o ambiente e o `@RefreshScope` renova o controlador.
O commit não envia a atualização sozinho. Alterações de porta exigem reiniciar a aplicação.

**13:15–14:15 | Testes e limites da validação**

Mostrar `docs/validacao.md` e `docs/evidencias-testes.json`.
Explicar a suíte: inicia JARs reais, consulta endpoints, valida DEV/PROD, compara SHA,
faz commit, testa refresh e encerra os processos. A suíte registrada usa Git temporário local;
a demonstração gravada deve mostrar o backend GitHub real já publicado.
Mostrar que a mensagem de fallback é “Configuração não carregada”.

**14:15–15:00 | Conclusão e entrega**

Fala sugerida: “A configuração ficou separada do código e versionada em Git. Cada serviço
recebe os valores do seu nome e perfil. Demonstramos três clientes conectados, consulta direta
ao servidor, troca de ambiente e atualização da mensagem sem reiniciar. O repositório contém
o código, as instruções de execução, os testes e o relatório.”

Mostrar os links reais dos dois repositórios e indicar onde está o relatório.

## Se algo falhar na gravação

- Erro no servidor: conferir URL Git, branch `main` e conexão antes de continuar.
- Cliente sem mensagem: conferir servidor e nome do arquivo.
- Porta ocupada: parar o cliente anterior ao trocar de perfil.
- Commit sem atualização: conferir push, consultar o servidor e executar POST de refresh.

## Antes de enviar

- Confirmar duração entre 10 e 20 minutos e áudio compreensível.
- Inserir no README os links reais do repositório de configurações e do vídeo.
- Conferir acesso ao vídeo e aos repositórios usando uma janela sem login.
- Enviar o link do GitHub no local indicado até 14/10/2026, 23h59.
