# Validação executada

Data: 13/10/2026. JDK 21.0.12, Maven 3.9.16, Spring Boot 4.0.8 e Spring Cloud 2025.1.3.

## Compilação

`mvn -B package`: **BUILD SUCCESS** nos quatro módulos e no agregador.
Foram gerados quatro JARs executáveis. A compilação foi feita com Maven instalado;
os Wrappers estão incluídos para uso no computador de quem executar o projeto.
O Wrapper raiz também foi executado com `mvnw.cmd -v`: Maven 3.10.0, Java 21.0.12.
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

## Limites da validação

O backend testado foi **Git local temporário (file://)**, com cópia dos seis arquivos
de `repo-configs`. O teste faz commits reais sem alterar a pasta original.
**Não foi testado um repositório GitHub remoto**, porque os repositórios ainda precisam
ser publicados e o login/URL real não foi informado.
Após a publicação, iniciar o servidor com `CONFIG_GIT_URI` apontando ao GitHub e
conferir os endpoints do README. O vídeo e a publicação ainda precisam ser concluídos pelo grupo.
