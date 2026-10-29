# RedeTI Dev Agent Framework

Framework compartilhado para colaborar entre ChatGPT (autor de codigo, scripts e conteudo) e Hermes Agent (sincronizacao, instalacao, testes e homologacao no ambiente local) usando GitHub como fonte de verdade.

## Ciclo operacional

1. ChatGPT examina contexto e codigo do projeto, prepara alteracao completa e publica commits no repositorio do projeto.
2. ChatGPT cria uma Issue `[HERMES NEXT]` com SHA de destino, branch, objetivos, passos de instalacao, verificacoes e criterios de aceite.
3. Hermes recebe `next` em seu chat nativo, busca a Issue, preserva mudancas locais, sincroniza Git, aplica no ambiente e testa.
4. Hermes publica evidencias: SHA remoto/local, testes, falhas e resultado. Nao gera codigo alternativo.
5. Se falhar por defeito de codigo, ChatGPT publica correcao; Hermes repete pull/testes. Somente fechar Issue apos homologacao verificavel.

## Governanca

Autonomia operacional para tarefas comuns. Alteracoes permanentes de cognicao, permissões de tools, skills, regras de contexto e rotinas exigem aprovacao explicita. Segredos nunca sao versionados. A divisao de responsabilidades e regra aprovada do projeto, nao instrucao para contornar permissões locais.

## Estrutura implementada

- `AGENTS.md`: politica compartilhada.
- `skills/redeti-next/SKILL.md`: protocolo nativo Hermes `next`.
- `scripts/next_bridge.py`: bridge multi-projeto que detecta origin via git, consulta fila e valida SHA remoto.
- `templates/`: AGENTS.md e modelo de Issue para novos projetos.
- `docs/CHANGE_PROCESS.md`: como propagar melhorias para framework e projetos.
- `CHANGELOG.md`: historico de versoes e evolucoes.

> Skill global, instalador, bridge e testes unitarios estao versionados. Validacao real no Hermes e homologacao entre varios repositorios ainda pendentes. Ver docs/INSTALL.md.

## Instalação
Consulte `docs/INSTALL.md` para instalar a skill global no Hermes. Cada projeto usa seu proprio GitHub origin; nao copiar credenciais ou configuracoes entre repositorios.
