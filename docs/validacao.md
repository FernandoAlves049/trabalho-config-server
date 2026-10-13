# Validação executada

Data: 13/10/2026. JDK 21.0.12, Maven 3.9.16, Spring Boot 4.0.8 e Spring Cloud 2025.1.3.

## Compilação

`mvn -B package`: **BUILD SUCCESS** nos quatro módulos e no agregador.
Foram gerados quatro JARs executáveis. A compilação foi feita com Maven instalado;
os Wrappers estão incluídos para uso no computador de quem executar o projeto.
Não há testes unitários Java; os testes de comportamento são a suíte de integração abaixo.

## Integração

**30/30 verificações aprovadas**, executando os quatro serviços reais.

| Cenário | Resultado |
| --- | --- |
| Saúde do Config Server | UP |
| Propriedades e SHA dos três clientes em DEV e PROD | Corretos |
| Mensagens, portas e ambiente dos três clientes | Corretos nos dois perfis |
| Commit novo no Git | Novo SHA e nova configuração visíveis no servidor |
| Cliente antes do refresh | Mantém a mensagem anterior |
| POST de refresh com JSON | Mensagem atualizada sem reiniciar o cliente |
| Cliente sem servidor | Importação opcional e mensagem de fallback |

Os resultados completos estão em `evidencias-testes.json`.
Reprodução: compile com `.\mvnw.cmd -B package` e execute
`python scripts/testar-integracao.py --configs ../repo-configs`.

## Validação com GitHub remoto

**13/13 verificações aprovadas** usando o repositório público
https://github.com/FernandoAlves049/repo-configs.git.

O Config Server iniciou com a URI padrão publicada, clonou o repositório remoto e
retornou o commit `fb4f0edde762c5ce5d1ddd230f6c08c47cda5d81`. As propriedades, mensagens, portas e ambientes
dos três clientes DEV foram conferidos contra o servidor.
Os registros estão em `evidencias-github.json`.

Código publicado: https://github.com/FernandoAlves049/trabalho-config-server.
Configurações publicadas: https://github.com/FernandoAlves049/repo-configs.
O vídeo ainda precisa ser gravado e seu link incluído no README.

## Escopo

DEV, PROD, versionamento, refresh e fallback foram testados com Git local temporário.
O acesso ao GitHub e o funcionamento dos três clientes DEV foram confirmados
na execução remota adicional. Os serviços foram encerrados após os testes.
