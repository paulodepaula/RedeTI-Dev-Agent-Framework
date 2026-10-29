# Instalar o framework no Hermes

Execute uma vez no terminal Bash do Hermes:

```bash
gh repo clone paulodepaula/RedeTI-Dev-Agent-Framework ~/RedeTI-Dev-Agent-Framework
cd ~/RedeTI-Dev-Agent-Framework
bash scripts/install-hermes.sh
python3 -m unittest discover -s tests -v
```

Se o repo ja existir, atualizar com `git pull --ff-only` em vez de clonar. A instalacao cria dois links em `~/.hermes` e preserva qualquer skill preexistente que nao seja symlink. Ao migrar a skill anterior do Vault, substitui somente o symlink `redeti-next`.

Abra a sessao do Hermes dentro do checkout do projeto e invoque `/redeti-next`. Como mensagem livre `next`, o reconhecimento depende de o contexto do projeto ter carregado `AGENTS.md`; `/redeti-next` e o comando explicito.

O bridge detecta o projeto pelo `origin` GitHub do checkout, nao e necessario editar strings fixas. Autenticacao `gh` e acesso ao projeto precisam existir. Nenhum segredo e gravado pelo framework.

## Publicar melhoria do metodo
ChatGPT atualiza este framework e seu CHANGELOG, prepara a compatibilidade de projetos consumidores e instrui Hermes a sincronizar e testar. Nao atualizar automaticamente servidores de outros projetos sem testes.
