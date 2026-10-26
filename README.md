# Macaparana Sa?de

Sistema acad?mico para organizar Tratamento Fora do Domic?lio (TFD), transporte sanit?rio e ajudas de custo. A aplica??o acompanha o paciente desde a solicita??o e o agendamento at? a viagem, a comprova??o do atendimento e o registro financeiro.

O frontend usa **React**, o backend usa **Python** e os dados ficam em **SQLite**. A interface compilada est? inclu?da no reposit?rio: para executar a demonstra??o local, basta ter Python instalado.

> Use somente dados fict?cios. Os valores e as regras financeiras s?o demonstrativos. O projeto n?o est? homologado para opera??o municipal nem integrado a sistemas oficiais.

## Funcionalidades

- Cadastro de pacientes, acompanhantes, unidades de refer?ncia, ve?culos e motoristas.
- Solicita??es de TFD e transporte sanit?rio, com laudos e an?lise de autoriza??o.
- Agendamento avulso ou recorrente, calend?rio e confer?ncia mensal.
- Planejamento de viagens com verifica??o de hor?rios, habilita??o, acessibilidade e capacidade por trecho.
- Confirma??o assistida, lista de passageiros, embarque, aus?ncia e encerramento da viagem.
- Comprova??o separada de atendimento do paciente e do acompanhante.
- C?lculo demonstrativo de benef?cios, aprova??o, contabilidade e registro de pagamento.
- Prepara??o interna de produ??o e exporta??o CSV para revis?o.
- Indicadores, medi??es do piloto, suporte e registros de capacita??o.
- Acesso por perfil e auditoria das opera??es.

## Executar localmente

### Requisitos

| Objetivo | Necess?rio |
| --- | --- |
| Executar o sistema e os testes Python | Python 3.11 ou superior; vers?o utilizada no projeto: 3.14.4. |
| Alterar e compilar o frontend | Node.js 24 e npm. |
| Automa??es de navegador e gera??o de documentos | Depend?ncias opcionais indicadas abaixo e Google Chrome. |

O backend usa a biblioteca padr?o do Python e n?o exige instala??o de pacotes. Node.js s? ? necess?rio para desenvolver ou recompilar a interface.

### Clonar e iniciar

```powershell
git clone https://github.com/anabeatrizvc-cloud/macaparana-saude.git
cd macaparana-saude
py server.py
```

No Windows, `py` usa o inicializador do Python. Se o ambiente disponibilizar `python` ou `python3`, use esse comando no lugar de `py`. O arquivo `iniciar.bat` tamb?m inicia o projeto, desde que `python` esteja configurado no PATH.

Abra **[http://localhost:8000](http://localhost:8000)**. Entre com usu?rio **admin** e senha **demo123**.

O servidor fica restrito a `127.0.0.1`. Mantenha o terminal aberto e pressione `Ctrl+C` para encerr?-lo. Na primeira execu??o, o banco ? criado com exemplos fict?cios; nas seguintes, os dados s?o preservados.

Para usar outra porta e uma base separada para estudo:

```powershell
py server.py --port 8002 --db data/estudo.db
```

Acesse `http://localhost:8002`. Reiniciar o servidor encerra as sess?es de login, mas n?o apaga o banco.

## Perfis de demonstra??o

Todos os usu?rios abaixo usam a senha `demo123`. Essas credenciais fazem parte da base fict?cia criada por `app/seed.py`.

| Usu?rio | Responsabilidade principal |
| --- | --- |
| `admin` | Administra??o e acesso a todas as funcionalidades. |
| `regulacao` | Pacientes, solicita??es, documentos, agenda e comprova??o. |
| `transporte` | Frota, motoristas, viagens, trechos e aloca??o. |
| `motorista` | Suas viagens e dados operacionais dos passageiros. |
| `financeiro` | Benef?cios, etapas financeiras e exporta??o da folha. |
| `faturamento` | Prepara??o, encaminhamento e exporta??o interna da produ??o. |
| `auditor` | Consultas, auditoria, exporta??es e registro de medi??es do piloto. |

As permiss?es s?o verificadas no servidor. A resposta da API tamb?m limita os dados enviados conforme o perfil.

## Arquitetura e organiza??o

```text
Navegador (React)
    ? API HTTP (server.py)
    ? Regras e permiss?es (app/domain.py e app/extensions.py)
    ? Banco SQLite (data/macaparana.db)
```

O navegador consulta `/api/state` e envia opera??es para `/api/action`. O servidor valida a sess?o, aplica as regras e confirma a transa??o. Depois de uma altera??o, a interface consulta novamente o estado. O backend usa `http.server` e consultas SQL diretas, sem Flask, Django ou ORM.

| Caminho | Responsabilidade |
| --- | --- |
| `server.py` | Servidor HTTP, autentica??o, sess?es, API e arquivos est?ticos. |
| `app/domain.py` | Regras centrais, permiss?es, persist?ncia e auditoria. |
| `app/extensions.py` | Migra??es, capacidade por trecho, produ??o, piloto e suporte. |
| `app/schema.sql` | Estrutura inicial das tabelas e restri??es. |
| `app/seed.py` | Inicializa??o do banco e exemplos de demonstra??o. |
| `frontend/src/main.jsx` | Inicializa??o React, navega??o, estado e coordena??o das a??es. |
| `frontend/src/context.jsx` | Contexto compartilhado, chamadas ? API e formata??o. |
| `frontend/src/pages.jsx` | P?ginas principais. |
| `frontend/src/details.jsx` | Detalhes de pacientes, solicita??es, atendimentos, viagens e auditoria. |
| `frontend/src/forms.jsx` | Formul?rios e prepara??o dos dados enviados. |
| `frontend/src/extensions.jsx` | Telas de trechos, produ??o, piloto e suporte. |
| `frontend/src/ui.jsx` | Componentes visuais reutiliz?veis. |
| `frontend/src/react.css` e `static/style.css` | Estilos da interface. |
| `frontend/package-lock.json` | Vers?es resolvidas das depend?ncias do frontend. |
| `static/build/` | Interface compilada, pronta para ser servida pelo Python. |
| `tests/` | Testes de dom?nio, funcionalidades complementares e HTTP. |
| `scripts/` | Backup, verifica??es, gera??o de documentos e empacotamento. |
| `docs/` | Documentação Macaparana em PDF. |
| `exemplos/` | Laudo e declara??es fict?cias para testar anexos. |
| `data/` | Banco, backups e arquivos locais; n?o versionada. |

O banco atual combina `schema.sql` com as migra??es de `extensions.py`. Uma solicita??o pode gerar v?rias ocorr?ncias de atendimento; cada ocorr?ncia pode ser alocada a uma viagem. Embarque, atendimento e comprova??o do acompanhante s?o registros distintos.

## Desenvolver o frontend

Instale as depend?ncias a partir do lockfile:

```powershell
cd frontend
npm ci
```

Mantenha o backend na porta 8000 e, em outro terminal dentro de `frontend`, execute:

```powershell
npm run dev
```

Acesse **http://127.0.0.1:5173/build/**. O Vite atualiza a interface ao salvar os arquivos e encaminha as chamadas `/api` ao Python.

Para atualizar a vers?o servida diretamente pelo Python:

```powershell
npm run build
```

O build grava os arquivos em `static/build/`. Edite os fontes e os estilos, depois recompile; os arquivos de `static/build/assets/` s?o gerados automaticamente. Ao publicar uma mudan?a visual, inclua tamb?m o build atualizado para manter a execu??o com Python funcionando.

Se n?o houver Node instalado, `py scripts/setup_node.py`, executado na raiz, baixa uma distribui??o port?til oficial para `.tools/` e verifica seu checksum. Adicione a pasta extra?da ao PATH do terminal antes de usar `npm`.

## Testes e verifica??es

Na raiz do projeto:

```powershell
py -m unittest discover -s tests -v
```

A su?te cont?m 27 testes cobrindo autoriza??o, agenda, viagens, documentos, benef?cios, permiss?es, auditoria, produ??o e backup. Os testes HTTP usam um servidor pr?prio; n?o exigem que a aplica??o principal esteja aberta.

Para executar a su?te e salvar a evid?ncia em `docs/resultado-testes.txt`:

```powershell
py scripts/run_tests.py
```

### Ferramentas opcionais

```powershell
py -m pip install playwright markdown pymupdf
```

Os scripts de navegador usam Google Chrome instalado. Os geradores de documentos dependem de fontes e capturas locais que não acompanham o repositório; uma clonagem nova inclui apenas o PDF principal. Execute somente as ferramentas necess?rias:

| Comando na raiz | Resultado ou requisito |
| --- | --- |
| `py scripts/browser_check.py` | Verifica telas e gera capturas; requer o sistema na porta 8000. |
| `py scripts/e2e_flow.py` | Executa fluxo integrado com banco tempor?rio e servidor na porta 8001. |
| `py scripts/capture_flows.py` | Gera evid?ncias dos fluxos com banco isolado na porta 8004. |
| `py scripts/check_revision.py` | Verifica funcionalidades complementares e gera evid?ncias da revis?o. |
| `py scripts/build_docs.py` | Gera HTML, diagramas e PDFs da documenta??o. |
| `py scripts/build_presentation.py` | Gera guia, slides e pacote dos materiais de apresenta??o. |
| `py scripts/revision_docs.py` | Atualiza materiais da revis?o e suas vers?es de leitura. |
| `py scripts/inspect_pdfs.py` | Inspeciona PDFs e cria pr?vias locais. |

Os documentos e relat?rios representam a execu??o em que foram gerados; n?o s?o atualizados automaticamente ao modificar o c?digo.

## Banco e backup

O arquivo padr?o ? `data/macaparana.db`. Ele cont?m os registros e os anexos. Para gerar uma c?pia consistente usando a API do SQLite:

```powershell
py scripts/backup.py
```

O destino padr?o fica em `data/backups/`, com data e hora no nome. Para escolher o destino:

```powershell
py scripts/backup.py --source data/macaparana.db --target data/backups/copia-estudo.db
```

O script exige um destino novo, diferente da origem, e verifica a integridade da c?pia. Para validar um backup sem alterar a base principal:

```powershell
py server.py --port 8002 --db data/backups/copia-estudo.db
```

Alterar `seed.py` n?o substitui os exemplos de um banco j? inicializado. Para uma demonstra??o nova, use outro caminho com `--db`.

## Documentação

Consulte a [Documentação Macaparana (PDF)](docs/Documentacao-Macaparana.pdf) para requisitos, regras, arquitetura e limites do projeto. Apenas esse PDF é versionado em `docs/`; os demais materiais ficam locais.

## O que entra no Git

S?o versionados c?digo-fonte, configura??es do projeto, lockfile, testes, scripts, exemplos fict?cios, documenta??o e frontend compilado. O build e os materiais de consulta permitem execu??o e apresenta??o offline ap?s obter o reposit?rio.

O `.gitignore` exclui banco e backups, logs, ambientes virtuais, caches, `node_modules`, ferramentas port?teis, configura??es pessoais do editor, arquivos de ambiente privados e pacotes de entrega. Arquivos `.env.example` podem ser versionados como modelos, sem valores privados.

Para gerar e verificar um pacote distribu?vel localmente:

```powershell
py scripts/package_delivery.py
py scripts/verify_package.py
```

O ZIP completo e seu checksum ficam em `entrega/`, fora do Git. A verifica??o extrai o pacote em uma pasta tempor?ria, confere a integridade e testa a inicializa??o.

## Problemas comuns

| Sintoma | O que conferir |
| --- | --- |
| `python` n?o encontrado ou abre a Microsoft Store | Use `py` no Windows ou configure o Python no PATH. |
| Porta 8000 ocupada | Use `--port 8002` e acesse a nova porta. O proxy do Vite aponta para 8000. |
| Altera??es React n?o aparecem no servidor Python | Execute `npm run build` dentro de `frontend` e recarregue a p?gina. |
| Vite abre, mas a API falha | Confirme que o backend est? ativo em `127.0.0.1:8000`. |
| Mudan?as no seed n?o aparecem | O banco j? foi inicializado; use outro arquivo com `--db`. |
| Automa??o n?o encontra Chrome | Instale Google Chrome e as depend?ncias opcionais. |

## Limites da demonstra??o

N?o h? integra??o oficial com faturamento p?blico, envio por WhatsApp, mapa, transfer?ncia banc?ria ou implanta??o com pacientes reais. O CSV de produ??o ? prepara??o interna e n?o representa transmiss?o ou aceite oficial. Os registros de pagamento representam acompanhamento administrativo, n?o movimenta??o banc?ria.

Uma implanta??o real exige valida??o das regras aplic?veis, revis?o de seguran?a, prote??o dos dados, infraestrutura e defini??o dos procedimentos de opera??o e suporte.
