# Changelog

## 0.2.0 — 2026-10-29
- Skill global `redeti-next`, instalador seguro e bridge multi-projeto publicados.
- Modelos de onboarding e Issues e testes unitarios adicionados.
- Vault vinculado ao framework central; testes reais de instalacao e homologacao continuam pendentes.


## 0.1.0 — 2026-10-29
- Inicio do repositorio compartilhado RedeTI Dev Agent Framework.
- Politica cognitiva de dez regras e papeis ChatGPT/Hermes documentados.
- Processo de propagacao de melhorias entre projetos definido.
- Integracao NEXT generica: planejada; nao homologada neste novo repositorio.


## Integracao consultiva Brain Core / NEXT — 04/11/2026
- `next_bridge.py fetch` inclui parecer de contexto local opcional do Brain Core, apenas sobre a Issue ja elegivel, marcado como nao autorizador.
- Falha ou ausencia do Brain nao interfere no fluxo NEXT nem altera gates de autoria, labels, SHA, branch e aprovacao existente.
- Consulta somente local em acionamento humano do NEXT; agendamento Brain separado, sem execucao automatica de Issues.
- Novo teste de integracao com plano valido, invalido, indisponivel e regressao da selecao de Issues.
