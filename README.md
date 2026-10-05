# Macaparana Saúde

Demonstrador acadêmico de gestão de TFD, transporte sanitário e ajudas de custo, com **backend Python, frontend React e banco SQLite**. Entrega com sistema funcional, protótipo de telas, documentação e testes. **Use somente dados fictícios.**

Repositório: [anabeatrizvc-cloud/macaparana-saude](https://github.com/anabeatrizvc-cloud/macaparana-saude) — privado; acesso depende de permissão na conta GitHub.

## Iniciar

Requisito para apresentar: Python 3.11 ou superior (verificado com Python 3.14.4). A interface React já está compilada em `static/build`; não precisa de Node.js nem internet para executar a entrega.

No Windows, abra `iniciar.bat`. Ou execute na pasta do projeto:

```powershell
python server.py
```

Abra **http://localhost:8000**. Usuário **admin**, senha **demo123**.

O terminal precisa permanecer aberto. Para parar, pressione Ctrl+C. Na primeira execução, o banco é criado com dados fictícios; nas seguintes, os registros são preservados.

Se a porta estiver ocupada:

```powershell
python server.py --port 8002
```

Abra então `http://localhost:8002`. O servidor escuta apenas em `127.0.0.1`; não há publicação na internet.

## Perfis

Todos usam a senha demonstrativa `demo123`:

| Usuário | Acesso |
| --- | --- |
| admin | Todas as funcionalidades |
| regulacao | Cadastros, solicitações, laudos, agenda e comprovação |
| transporte | Frota, motoristas, viagens, alocação e execução |
| motorista | Apenas suas viagens e dados operacionais |
| financeiro | Consulta, cálculo, etapas financeiras e exportação |
| auditor | Consulta, auditoria e exportação; sem alterações de negócio |

## Entrega

- `docs/Documentacao-Macaparana.pdf`: documentação acadêmica e técnica.
- `docs/Prototipo-de-Telas.pdf`: telas anotadas, desktop e celular.
- `docs/Roteiro-de-Apresentacao.pdf`: demonstração guiada.
- `docs/documentacao.html`: documentação navegável, também acessível sem servidor.
- `docs/prototipo.html`: galeria de telas; o sistema é o protótipo interativo.
- `docs/roteiro.html`: roteiro de apresentação.
- `docs/fluxos.html`: galeria das etapas executadas pela interface React e verificadas na API.
- `docs/Fluxos-Funcionando.pdf`: capturas dos fluxos integrados, estados e bloqueios.
- `docs/fluxos/manifesto.json`: resultado das verificações e descrição de cada captura.
- `docs/documentacao.md` e `docs/roteiro.md`: fontes editáveis.
- `docs/modelo-dados.mmd` e `docs/fluxo.mmd`: diagramas Mermaid editáveis.
- `app/schema.sql`: modelo relacional executável.
- `exemplos/`: laudo e declarações fictícias para testar anexos.
- `entrega/Macaparana-Saude-Entrega.zip`: pacote completo para enviar.

Faculdade, disciplina, professor e integrantes não foram informados. Preencha a identificação em `docs/identificacao.json` e gere novamente os documentos, ou edite as fontes para personalizar a entrega.

## Funcionalidades

Cadastros, autorização com laudo, recorrências entre competências, planejamento com conflitos de horário e lotação, lista do motorista, comprovações separadas, tabela mensal por datas, benefícios demonstrativos com versão da regra, fluxo até registro de pagamento, exportação CSV e auditoria.

**Não é uma implantação municipal pronta:** não há integração oficial, WhatsApp, mapa, ordem bancária, homologação de regras TFD, infraestrutura de produção, MFA, criptografia do banco ou piloto com pacientes reais. A documentação diferencia o que foi implementado, o que é simplificado e o que permanece como evolução.

## Banco e cópia de segurança

O arquivo `data/macaparana.db` guarda registros e anexos. Faça a cópia com o servidor parado, mantenha o backup em local protegido e teste a restauração em uma instância separada:

```powershell
python server.py --port 8002 --db data/copia-para-validacao.db
```

Para uma demonstração nova, use outro arquivo de banco com `--db`; não é necessário apagar o banco existente. Exemplo: `python server.py --db data/nova-demonstracao.db`.

## Testes

```powershell
python -m unittest discover -s tests -v
```

Testes de navegador e geração de documentação são ferramentas de desenvolvimento opcionais:

```powershell
python -m pip install playwright markdown pymupdf
python scripts/e2e_flow.py
python scripts/browser_check.py
python scripts/capture_flows.py
python scripts/build_docs.py
```

Os scripts de navegador usam Google Chrome instalado. `browser_check.py` requer o servidor na porta 8000. `build_docs.py` lê os arquivos locais e valida o conteúdo exportado. O teste ponta a ponta usa banco temporário na porta 8001; as capturas dos fluxos usam outra base isolada na porta 8004. Ambos encerram suas instâncias ao terminar.

## Desenvolvimento React

Frontend em React 19, compilado com Vite 8. Requer Node.js 24 LTS para desenvolvimento (verificado com 24.21.0). Instale Node no ambiente ou use `python scripts/setup_node.py` para baixar uma cópia portátil oficial em `.tools` e adicionar sua pasta ao PATH da sessão.

```powershell
cd frontend
npm ci
npm run build
```

O build atualiza `static/build`, servido pelo Python. Para desenvolvimento com recarga automática, mantenha `python server.py` em outro terminal e execute `npm run dev` na pasta `frontend`; acesse `http://127.0.0.1:5173/build/`. O proxy do Vite encaminha `/api` para a API local e ajusta a origem apenas nessa conexão de desenvolvimento. A autorização continua no backend.

A interface usa componentes JSX, Context e hooks de estado/efeito; não injeta a aplicação anterior com `innerHTML`. Busca, filtros, diálogos e estados de operação são gerenciados pelo React. Formulários enviam dados JSON à mesma API Python validada pelos testes.

## Estrutura

```text
server.py                  Servidor HTTP local, sessão e API
app/domain.py              Regras e permissões no servidor
app/schema.sql             Tabelas, relações e restrições
app/seed.py                Base fictícia e usuários de demonstração
frontend/src/              Componentes React, contexto, formulários e páginas JSX
frontend/package-lock.json Dependências exatas do frontend
static/build/              Interface React compilada para execução offline
static/style.css           Estilo visual compartilhado com a lista imprimível
tests/                     Testes de domínio e HTTP
scripts/                   Verificação visual e geração dos documentos
docs/                      Documentos, diagramas, telas e evidências
exemplos/                  Anexos fictícios
data/                      Banco persistente local
```
# Revisão do escopo — 04/10/2026

Complementos: capacidade por trecho com paradas ordenadas, confirmação assistida com canal, perfil `faturamento`, preparação/encaminhamento de produção e CSV interno, indicadores de custo/consumo, medições do piloto com fonte, registros de capacitação/suporte e `python scripts/backup.py`.

Consulte [verificação completa](docs/verificacao-escopo.md), [operação e piloto](docs/operacao.md) e [novas evidências](docs/revisao.html). A senha do novo perfil é `demo123`, como os demais perfis acadêmicos. A migração preserva o banco existente.

Integrações oficiais, leiautes homologados, implantação com dados reais e execução do piloto municipal dependem da prefeitura. O CSV de produção é preparação interna e não representa transmissão ou aceite oficial.
