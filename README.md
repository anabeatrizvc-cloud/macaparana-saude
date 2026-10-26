# Macaparana Saúde

Sistema acadêmico para organizar Tratamento Fora do Domicílio (TFD), transporte sanitário e ajudas de custo. A aplicação acompanha o paciente desde a solicitação e o agendamento até a viagem, a comprovação do atendimento e o registro financeiro.

O frontend usa **React**, o backend usa **Python** e os dados ficam em **SQLite**. A interface compilada está incluída no repositório: para executar a demonstração local, basta ter Python instalado.

> Use somente dados fictícios. Os valores e as regras financeiras são demonstrativos. O projeto não está homologado para operação municipal nem integrado a sistemas oficiais.

## Alunos

| Nome | Matrícula |
| --- | --- |
| Ana Beatriz Vasconcelos | 01707957 |
| Juliana Eugênia Anacleto Barbosa | 01800345 |
| Thayana Araujo brito da Silva | 01784035 |
| Lucas Gabriel de Aguiar Santiago | 01814331 |
| Mikael Lucas da Silva | 01815744 |

## Funcionalidades

- Cadastro de pacientes, acompanhantes, unidades de referência, veículos e motoristas.
- Solicitações de TFD e transporte sanitário, com laudos e análise de autorização.
- Agendamento avulso ou recorrente, calendário e conferência mensal.
- Planejamento de viagens com verificação de horários, habilitação, acessibilidade e capacidade por trecho.
- Confirmação assistida, lista de passageiros, embarque, ausência e encerramento da viagem.
- Comprovação separada de atendimento do paciente e do acompanhante.
- Cálculo demonstrativo de benefícios, aprovação, contabilidade e registro de pagamento.
- Preparação interna de produção e exportação CSV para revisão.
- Indicadores, medições do piloto, suporte e registros de capacitação.
- Acesso por perfil e auditoria das operações.

## Executar localmente

### Requisitos

| Objetivo | Necessário |
| --- | --- |
| Executar o sistema e os testes Python | Python 3.11 ou superior; versão utilizada no projeto: 3.14.4. |
| Alterar e compilar o frontend | Node.js 24 e npm. |
| Automações de navegador e geração de documentos | Dependências opcionais indicadas abaixo e Google Chrome. |

O backend usa a biblioteca padrão do Python e não exige instalação de pacotes. Node.js só é necessário para desenvolver ou recompilar a interface.

### Clonar e iniciar

```powershell
git clone https://github.com/anabeatrizvc-cloud/macaparana-saude.git
cd macaparana-saude
py server.py
```

No Windows, `py` usa o inicializador do Python. Se o ambiente disponibilizar `python` ou `python3`, use esse comando no lugar de `py`. O arquivo `iniciar.bat` também inicia o projeto, desde que `python` esteja configurado no PATH.

Abra **[http://localhost:8000](http://localhost:8000)**. Entre com usuário **admin** e senha **demo123**.

O servidor fica restrito a `127.0.0.1`. Mantenha o terminal aberto e pressione `Ctrl+C` para encerrá-lo. Na primeira execução, o banco é criado com exemplos fictícios; nas seguintes, os dados são preservados.

Para usar outra porta e uma base separada para estudo:

```powershell
py server.py --port 8002 --db data/estudo.db
```

Acesse `http://localhost:8002`. Reiniciar o servidor encerra as sessões de login, mas não apaga o banco.

## Perfis de demonstração

Todos os usuários abaixo usam a senha `demo123`. Essas credenciais fazem parte da base fictícia criada por `app/seed.py`.

| Usuário | Responsabilidade principal |
| --- | --- |
| `admin` | Administração e acesso a todas as funcionalidades. |
| `regulacao` | Pacientes, solicitações, documentos, agenda e comprovação. |
| `transporte` | Frota, motoristas, viagens, trechos e alocação. |
| `motorista` | Suas viagens e dados operacionais dos passageiros. |
| `financeiro` | Benefícios, etapas financeiras e exportação da folha. |
| `faturamento` | Preparação, encaminhamento e exportação interna da produção. |
| `auditor` | Consultas, auditoria, exportações e registro de medições do piloto. |

As permissões são verificadas no servidor. A resposta da API também limita os dados enviados conforme o perfil.

## Arquitetura e organização

```text
Navegador (React)
    → API HTTP (server.py)
    → Regras e permissões (app/domain.py e app/extensions.py)
    → Banco SQLite (data/macaparana.db)
```

O navegador consulta `/api/state` e envia operações para `/api/action`. O servidor valida a sessão, aplica as regras e confirma a transação. Depois de uma alteração, a interface consulta novamente o estado. O backend usa `http.server` e consultas SQL diretas, sem Flask, Django ou ORM.

| Caminho | Responsabilidade |
| --- | --- |
| `server.py` | Servidor HTTP, autenticação, sessões, API e arquivos estáticos. |
| `app/domain.py` | Regras centrais, permissões, persistência e auditoria. |
| `app/extensions.py` | Migrações, capacidade por trecho, produção, piloto e suporte. |
| `app/schema.sql` | Estrutura inicial das tabelas e restrições. |
| `app/seed.py` | Inicialização do banco e exemplos de demonstração. |
| `frontend/src/main.jsx` | Inicialização React, navegação, estado e coordenação das ações. |
| `frontend/src/context.jsx` | Contexto compartilhado, chamadas à API e formatação. |
| `frontend/src/pages.jsx` | Páginas principais. |
| `frontend/src/details.jsx` | Detalhes de pacientes, solicitações, atendimentos, viagens e auditoria. |
| `frontend/src/forms.jsx` | Formulários e preparação dos dados enviados. |
| `frontend/src/extensions.jsx` | Telas de trechos, produção, piloto e suporte. |
| `frontend/src/ui.jsx` | Componentes visuais reutilizáveis. |
| `frontend/src/react.css` e `static/style.css` | Estilos da interface. |
| `frontend/package-lock.json` | Versões resolvidas das dependências do frontend. |
| `static/build/` | Interface compilada, pronta para ser servida pelo Python. |
| `tests/` | Testes de domínio, funcionalidades complementares e HTTP. |
| `scripts/` | Backup, verificações, geração de documentos e empacotamento. |
| `docs/` | Documentação Macaparana em PDF. |
| `exemplos/` | Laudo e declarações fictícias para testar anexos. |
| `data/` | Banco, backups e arquivos locais; não versionada. |

O banco atual combina `schema.sql` com as migrações de `extensions.py`. Uma solicitação pode gerar várias ocorrências de atendimento; cada ocorrência pode ser alocada a uma viagem. Embarque, atendimento e comprovação do acompanhante são registros distintos.

## Desenvolver o frontend

Instale as dependências a partir do lockfile:

```powershell
cd frontend
npm ci
```

Mantenha o backend na porta 8000 e, em outro terminal dentro de `frontend`, execute:

```powershell
npm run dev
```

Acesse **http://127.0.0.1:5173/build/**. O Vite atualiza a interface ao salvar os arquivos e encaminha as chamadas `/api` ao Python.

Para atualizar a versão servida diretamente pelo Python:

```powershell
npm run build
```

O build grava os arquivos em `static/build/`. Edite os fontes e os estilos, depois recompile; os arquivos de `static/build/assets/` são gerados automaticamente. Ao publicar uma mudança visual, inclua também o build atualizado para manter a execução com Python funcionando.

Se não houver Node instalado, `py scripts/setup_node.py`, executado na raiz, baixa uma distribuição portátil oficial para `.tools/` e verifica seu checksum. Adicione a pasta extraída ao PATH do terminal antes de usar `npm`.

## Testes e verificações

Na raiz do projeto:

```powershell
py -m unittest discover -s tests -v
```

A suíte contém 27 testes cobrindo autorização, agenda, viagens, documentos, benefícios, permissões, auditoria, produção e backup. Os testes HTTP usam um servidor próprio; não exigem que a aplicação principal esteja aberta.

Para executar a suíte e salvar a evidência em `docs/resultado-testes.txt`:

```powershell
py scripts/run_tests.py
```

### Ferramentas opcionais

```powershell
py -m pip install playwright markdown pymupdf
```

Os scripts de navegador usam Google Chrome instalado. Os geradores de documentos dependem de fontes e capturas locais que não acompanham o repositório; uma clonagem nova inclui apenas o PDF principal. Execute somente as ferramentas necessárias:

| Comando na raiz | Resultado ou requisito |
| --- | --- |
| `py scripts/browser_check.py` | Verifica telas e gera capturas; requer o sistema na porta 8000. |
| `py scripts/e2e_flow.py` | Executa fluxo integrado com banco temporário e servidor na porta 8001. |
| `py scripts/capture_flows.py` | Gera evidências dos fluxos com banco isolado na porta 8004. |
| `py scripts/check_revision.py` | Verifica funcionalidades complementares e gera evidências da revisão. |
| `py scripts/build_docs.py` | Gera HTML, diagramas e PDFs da documentação. |
| `py scripts/build_presentation.py` | Gera guia, slides e pacote dos materiais de apresentação. |
| `py scripts/revision_docs.py` | Atualiza materiais da revisão e suas versões de leitura. |
| `py scripts/inspect_pdfs.py` | Inspeciona PDFs e cria prévias locais. |

Os documentos e relatórios representam a execução em que foram gerados; não são atualizados automaticamente ao modificar o código.

## Banco e backup

O arquivo padrão é `data/macaparana.db`. Ele contém os registros e os anexos. Para gerar uma cópia consistente usando a API do SQLite:

```powershell
py scripts/backup.py
```

O destino padrão fica em `data/backups/`, com data e hora no nome. Para escolher o destino:

```powershell
py scripts/backup.py --source data/macaparana.db --target data/backups/copia-estudo.db
```

O script exige um destino novo, diferente da origem, e verifica a integridade da cópia. Para validar um backup sem alterar a base principal:

```powershell
py server.py --port 8002 --db data/backups/copia-estudo.db
```

Alterar `seed.py` não substitui os exemplos de um banco já inicializado. Para uma demonstração nova, use outro caminho com `--db`.

## Documentação

Consulte a [Documentação Macaparana (PDF)](docs/Documentacao-Macaparana.pdf) para requisitos, regras, arquitetura e limites do projeto. Apenas esse PDF é versionado em `docs/`; os demais materiais ficam locais.

## O que entra no Git

São versionados código-fonte, configurações do projeto, lockfile, testes, scripts, exemplos fictícios, documentação e frontend compilado. O build e os materiais de consulta permitem execução e apresentação offline após obter o repositório.

O `.gitignore` exclui banco e backups, logs, ambientes virtuais, caches, `node_modules`, ferramentas portáteis, configurações pessoais do editor, arquivos de ambiente privados e pacotes de entrega. Arquivos `.env.example` podem ser versionados como modelos, sem valores privados.

Para gerar e verificar um pacote distribuível localmente:

```powershell
py scripts/package_delivery.py
py scripts/verify_package.py
```

O ZIP completo e seu checksum ficam em `entrega/`, fora do Git. A verificação extrai o pacote em uma pasta temporária, confere a integridade e testa a inicialização.

## Problemas comuns

| Sintoma | O que conferir |
| --- | --- |
| `python` não encontrado ou abre a Microsoft Store | Use `py` no Windows ou configure o Python no PATH. |
| Porta 8000 ocupada | Use `--port 8002` e acesse a nova porta. O proxy do Vite aponta para 8000. |
| Alterações React não aparecem no servidor Python | Execute `npm run build` dentro de `frontend` e recarregue a página. |
| Vite abre, mas a API falha | Confirme que o backend está ativo em `127.0.0.1:8000`. |
| Mudanças no seed não aparecem | O banco já foi inicializado; use outro arquivo com `--db`. |
| Automação não encontra Chrome | Instale Google Chrome e as dependências opcionais. |

## Limites da demonstração

Não há integração oficial com faturamento público, envio por WhatsApp, mapa, transferência bancária ou implantação com pacientes reais. O CSV de produção é preparação interna e não representa transmissão ou aceite oficial. Os registros de pagamento representam acompanhamento administrativo, não movimentação bancária.

Uma implantação real exige validação das regras aplicáveis, revisão de segurança, proteção dos dados, infraestrutura e definição dos procedimentos de operação e suporte.
