# RedeTI Hermes — piloto de monitoramento autonomo

Estado: **simulacao apenas**. Nao inicia Hermes, nao executa comandos das Issues nem altera GitHub, servicos ou repositorios. A autorizacao de 2026-11-03 limita-se a implementacao e teste, sem ativar execucao real.

## Funcionamento

- Timer systemd de usuario previsto para aproximadamente 60 segundos apos o ultimo ciclo, sem sobreposicao. Nao e instalado nem ativado pelo GitHub.
- Nenhum projeto por padrao. Apenas repositorios, checkouts e branches explicitamente autorizados na configuracao sao consultados.
- O Git origin local deve coincidir com o repositorio permitido.
- Issues abertas precisam da label `hermes-ready`, prefixo `[HERMES NEXT]`, autor dono do repositorio e metadados exatos de branch e SHA.
- Corpo da Issue: linhas `**Branch:** dev/ai-shared` e `**Commit SHA:** <SHA de 40 caracteres>`.
- Lock local impede sobreposicao na mesma maquina; escolhe no maximo uma Issue elegivel por projeto a cada consulta.
- Eventos: `would_dispatch`, `blocked`, `empty`, `idle`, `fatal`. Nao existe execucao de agente.
- Consultas com timeout de 20 segundos; saidas nao incluem corpo de Issues nem credenciais.

## Configuracao

Copie `config/autonomy.example.json`. Exemplo ilustrativo (substituir pelo estado verificado do Hermes Server):

```json
{
  "mode": "simulate",
  "projects": [
    {
      "repository": "owner/project",
      "checkout": "/caminho/absoluto/do/projeto",
      "allowed_branches": ["dev/ai-shared"]
    }
  ]
}
```

Qualquer modo diferente de `simulate` e rejeitado.

## Testes

```bash
python3 -m unittest discover -s tests -v
python3 scripts/autonomy_watcher.py --config config/autonomy.example.json
bash -n scripts/stage-autonomy-service.sh
```

## Preparar unidades inativas (opcional, depois de revisar)

```bash
bash scripts/stage-autonomy-service.sh
systemctl --user is-enabled redeti-hermes-autonomy.timer
```

O script apenas prepara as unidades; **nao executar** `systemctl --user enable --now redeti-hermes-autonomy.timer` nesta etapa.

## Gates para execucao real

1. Confirmar interface automatizavel do Hermes: skill conversacional nao implica runtime invocavel via CLI.
2. Testar chamada em ambiente isolado com tarefa inofensiva.
3. Implementar claim atomico ou garantir executor unico entre hosts.
4. Implementar timeouts, backoff, circuit breaker, controles de aprovacao, auditoria e parada de emergencia.
5. Homologar no Hermes Server e obter aprovacao separada para ativacao real.
