package br.edu.trabalho.relatorios;

import java.util.Map;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.cloud.context.config.annotation.RefreshScope;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

/** Valores injetados do Config Server e renovados com POST /actuator/refresh. */
@RefreshScope
@RestController
public class ConfigController {
    @Value("${mensagem.boasvindas:Configuração não carregada}")
    private String mensagem;

    @Value("${spring.application.name}")
    private String servico;

    @Value("${app.ambiente:indisponivel}")
    private String ambiente;

    @GetMapping(value = "/mensagem", produces = "text/plain;charset=UTF-8")
    public String mensagem() {
        return mensagem;
    }

    @GetMapping("/configuracao")
    public Map<String, String> configuracao() {
        return Map.of("servico", servico, "ambiente", ambiente, "mensagem", mensagem);
    }
}
