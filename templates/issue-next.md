# [HERMES NEXT] <ID> - <Titulo>

**Repositorio:** owner/repo
**Branch:** dev/ai-shared (ou branch real de entrega)
**Commit SHA:** <40 caracteres>
**Responsavel pelo codigo:** ChatGPT
**Responsavel pela implantacao/teste:** Hermes

## Objetivo
Aplicar e verificar codigo ja publicado.

## Procedimento local
1. Preservar alteracoes locais.
2. Fetch e pull --ff-only na branch.
3. Conferir HEAD com SHA declarado.
4. Instalar/configurar dentro de escopo autorizado.
5. Executar comandos de teste e coletar evidencias.

## Criterios de aceite
- SHA local = SHA remoto = SHA da Issue.
- Testes listados passaram.
- Nenhum segredo em commits ou relatorios.
- Report concluido via next_bridge.py.

## Falha
Documentar logs sanitizados, comandos e diagnostico; nao escrever codigo no ambiente. Manter Issue aberta ate patch do ChatGPT.
