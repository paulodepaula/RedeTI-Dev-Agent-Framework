# Processo de evolucao compartilhada

1. Identificar se a mudanca e **metodo compartilhado** ou **codigo/decisao especifica do projeto**.
2. Para metodo: avaliar impacto em cognicao, tools, skills, contexto e rotinas. Exigir aprovacao humana explicita quando modificar suas regras permanentes.
3. Publicar versao rastreavel no **RedeTI-Dev-Agent-Framework** (documentacao, skill e scripts conforme necessario).
4. Atualizar os projetos consumidores, preferencialmente via versao/tag e changelog, sem sobrescrever personalizacoes.
5. ChatGPT publica codigo e instrucoes no repositorio de cada projeto. Hermes apenas sincroniza e testa.
6. Verificar implantacao por commit/SHA remoto, testes executados e relatorio GitHub. Nao encerrar tarefa sem evidencias; em erro de codigo devolver diagnostico para ChatGPT.
7. Registrar quais projetos foram atualizados e quais ainda estao pendentes.

## Publicacao de instrucao NEXT
Cada Issue de deploy deve identificar: projeto/repo, branch, SHA/versao alvo, arquivos afetados, ambiente autorizado, comandos de verificacao, criterios de aceite e procedimentos de rollback quando aplicaveis. O bridge do framework deve ser parametrizado; nao fixar `redeti_vault` em novos projetos.

## Limite
Documentacao de um procedimento nao implica que ele esteja automaticamente instalado no Hermes ou em outros projetos. Cada ambiente precisa de instalacao e homologacao propria.
