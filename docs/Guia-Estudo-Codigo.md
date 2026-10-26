# Guia de estudo do código — Macaparana Saúde

Este guia explica a organização do projeto a partir dos arquivos locais revisados em 24/10/2026. O objetivo é ajudar você a localizar cada responsabilidade e acompanhar uma operação desde o clique na tela até a gravação no banco.

## 1. Como o sistema funciona

O projeto é um demonstrador de gestão de Tratamento Fora do Domicílio (TFD), transporte sanitário e ajudas de custo. Há três partes principais:

| Parte | Tecnologia | Responsabilidade |
| --- | --- | --- |
| Interface, ou frontend | React, JSX e CSS | Mostrar telas, receber informações e enviar pedidos ao servidor. |
| Servidor, ou backend | Python e biblioteca padrão | Autenticar, verificar permissões, aplicar regras e responder às operações. |
| Banco de dados | SQLite | Guardar cadastros, viagens, documentos, benefícios e histórico. |

Fluxo de uma alteração: tela React → chamada HTTP → `server.py` → `app/domain.py` ou `app/extensions.py` → SQLite → resposta → atualização da tela.

O navegador não abre o banco diretamente. Ele usa a API, que é o conjunto de endereços HTTP disponibilizados pelo servidor. O backend usa `http.server`, sem Flask ou Django. As consultas ao SQLite são escritas em SQL, sem um ORM intermediário.

## 2. Mapa das pastas

```text
macaparana/
├── server.py           Inicialização, servidor HTTP e API
├── iniciar.bat         Atalho de inicialização no Windows
├── README.md           Instruções gerais
├── app/                Regras, criação do banco e dados iniciais
├── frontend/           Código-fonte e ferramentas do React
│   └── src/            Componentes, páginas, contexto e formulários
├── static/             Estilos, marca e interface compilada
│   └── build/assets/   JavaScript e CSS gerados pelo Vite
├── tests/              Testes automatizados em Python
├── scripts/            Ferramentas de desenvolvimento e entrega
├── exemplos/           Documentos fictícios para anexar
├── docs/               Documentação, diagramas, PDFs e evidências
│   ├── telas/          Capturas gerais da interface
│   ├── fluxos/         Capturas e resultados de operações completas
│   └── revisao/        Evidências das funcionalidades complementares
├── data/               Banco e arquivos locais de trabalho
├── .tools/             Node.js portátil
├── .git/               Histórico e configuração do Git
└── __pycache__/        Cache gerado pelo Python
```

`entrega/` é uma pasta de saída prevista nos scripts, mas não estava presente na revisão. `frontend/node_modules/` contém dependências instaladas. Pastas `__pycache__/` também podem aparecer dentro dos pacotes Python. O conteúdo dessas pastas automáticas varia conforme o uso.

## 3. Arquivos da raiz

### server.py

É o ponto de entrada do backend. A função `main()` lê `--port` e `--db`, prepara a pasta do banco, chama `initialize()` e inicia um `ThreadingHTTPServer` em `127.0.0.1`. O endereço padrão é `http://localhost:8000`.

A classe `Handler` atende às requisições. `send()` monta respostas e cabeçalhos; `user()` identifica a sessão pelo cookie; `do_GET()` atende consultas e arquivos; `do_POST()` processa login, logout e alterações.

| Endereço | O que faz |
| --- | --- |
| `POST /api/login` | Valida usuário e senha e cria uma sessão. |
| `POST /api/logout` | Encerra a sessão. |
| `GET /api/state` | Devolve os dados que aquele perfil pode consultar. |
| `POST /api/action` | Recebe uma ação e seus dados e chama as regras de negócio. |
| `GET /api/documents/{id}` | Baixa um documento, após verificar o perfil. |
| `GET /api/export` | Exporta a folha de benefícios em CSV. |
| `GET /api/production/export` | Exporta a preparação interna da produção por competência. |

As sessões ficam no dicionário `SESSIONS`, na memória do processo. Reiniciar o servidor encerra essas sessões, mas preserva os registros do SQLite. Nas alterações, `commit()` confirma a gravação e `rollback()` desfaz a transação quando ocorre uma falha.

### Outros arquivos

| Arquivo | Explicação |
| --- | --- |
| `iniciar.bat` | Muda para a pasta do projeto, mostra instruções e executa `python server.py`. |
| `README.md` | Apresenta instalação, demonstração, desenvolvimento, testes e links da entrega. |
| `.gitignore` | Lista arquivos locais que o Git deve ignorar, como banco, dependências, ferramentas e caches. Não apaga esses arquivos. |
| `.gitattributes` | Define tratamento de texto, finais de linha e arquivos binários para o Git. |

## 4. app/ — regras e persistência

### __init__.py

Marca `app` como pacote Python. Permite imports como `from app.domain import connect`. Não concentra regras da aplicação.

### domain.py

É o arquivo central das regras de negócio. Leia primeiro os auxiliares e depois acompanhe um ramo da função `execute()` por vez.

| Nome | Função no projeto |
| --- | --- |
| `RuleError` | Representa uma operação recusada por uma regra do sistema. |
| `now()` | Produz a data e hora atual em UTC, em formato ISO. |
| `require()` | Lança `RuleError` se uma condição não for atendida. |
| `required()` | Lê um texto obrigatório, remove espaços nas pontas e verifica tamanho. |
| `day()` | Converte e valida uma data. |
| `number()` | Converte um valor numérico e verifica limites. |
| `get()` | Busca um registro por ID e recusa IDs inexistentes. |
| `insert()` e `update()` | Executam gravações nas tabelas. |
| `log()` | Registra autor, ação, entidade, estados anterior e posterior e justificativa. |
| `PERMISSIONS` | Relaciona cada ação aos perfis autorizados a executá-la. |
| `execute()` | Seleciona a regra conforme o nome da ação, valida os dados e altera os registros. |
| `connect()` | Abre o SQLite, permite acessar colunas pelo nome e ativa chaves estrangeiras. |
| `state()` | Monta a resposta da API, filtrando dados conforme o perfil. |

Exemplos de ações são `patient.create`, `request.decide`, `schedule.create`, `trip.allocate`, `occurrence.prove` e `benefit.calculate`. Elas não são nomes de funções separadas: são valores usados para escolher ramos de `execute()`.

Observe as regras de autorização com laudo, datas de agendamento, conflitos de veículo ou motorista, acessibilidade, comprovação de atendimento e etapas financeiras. Embarcar e comprovar atendimento são situações diferentes. O acompanhante também tem sua própria comprovação.

`state()` merece atenção: além de buscar dados, restringe informações. O motorista recebe suas viagens e dados operacionais; dados bancários, documentos e auditoria têm regras próprias de acesso. Esconder um botão no React não substitui essas verificações.

### extensions.py

Reúne funcionalidades complementares, chamadas pelo domínio principal. Não é uma biblioteca externa.

| Elemento | Responsabilidade |
| --- | --- |
| `migrate()` | Acrescenta colunas de trecho e confirmação e cria as tabelas complementares quando necessário. |
| `stops()` | Busca as paradas ordenadas da viagem; usa origem e destino padrão quando não há paradas cadastradas. |
| `capacity()` | Verifica a ocupação em cada trecho, incluindo acompanhante. |
| `PERMISSIONS` | Define acesso às ações complementares. |
| `execute_extension()` | Trata rotas, produção, suporte, capacitação e medições do piloto. |
| `extend_state()` | Acrescenta dados complementares à resposta de consulta. |

A capacidade por trecho permite reutilizar um assento depois que alguém desembarca. O que importa é quantos passageiros estão simultaneamente em cada intervalo entre paradas.

As ações complementares incluem `route.save`, `production.save`, `production.submit`, `service.create`, `service.close` e `pilot.create`. Produção encaminhada significa preparação para revisão interna; esse código não realiza transmissão oficial a um sistema externo.

### schema.sql

Define as tabelas iniciais. `PRIMARY KEY` identifica registros; `REFERENCES` vincula tabelas; `UNIQUE` impede duplicidades; `CHECK` restringe valores aceitos.

| Tabela | O que guarda |
| --- | --- |
| `users` | Usuários, perfis, hash de senha, salt e vínculo com motorista. |
| `patients` | Pacientes, contatos, embarque, acessibilidade e acompanhante. |
| `facilities` | Unidades de referência e identificação CNES. |
| `vehicles` | Veículos, placas, capacidade e acessibilidade. |
| `drivers` | Motoristas e validade da habilitação. |
| `requests` | Solicitações, modalidade, especialidade, validade e decisão. |
| `trips` | Viagens, horários, recursos, percurso e execução. |
| `occurrences` | Cada data agendada de uma solicitação, com viagem, confirmação, embarque e comprovações. |
| `documents` | Metadados e conteúdo binário dos documentos anexados. |
| `rules` | Versões dos valores demonstrativos dos benefícios. |
| `benefits` | Benefícios por ocorrência e beneficiário, com valor e etapa financeira. |
| `audit` | Histórico das operações. |

O esquema efetivo inclui também as tabelas criadas por `extensions.py`: `route_stops` (paradas), `production` (produção preparada), `service_records` (suporte e capacitação) e `pilot_measurements` (medições do piloto). Portanto, estudar apenas `schema.sql` não mostra todo o banco atual.

Relação central: paciente → solicitações → ocorrências. Uma solicitação pode gerar várias datas; cada ocorrência pode ser vinculada a uma viagem. Documentos pertencem a uma solicitação ou a uma ocorrência. Benefícios se ligam à ocorrência e à versão da regra usada no cálculo.

### seed.py

`initialize()` executa o esquema e a migração e cria a base fictícia quando ainda não há usuários. Em uma base existente, preserva os registros e verifica a presença do usuário de faturamento. `password_hash()` usa PBKDF2-HMAC-SHA256 com salt para derivar o valor armazenado da senha.

Os dados iniciais ajudam a demonstrar o fluxo sem preencher tudo manualmente. Alterar os exemplos desse arquivo não substitui automaticamente os registros de um banco já inicializado.

## 5. frontend/ — código da interface

| Arquivo ou pasta | Explicação |
| --- | --- |
| `package.json` | Define o projeto, dependências e comandos `dev`, `build` e `preview`. |
| `package-lock.json` | Registra a resolução exata das dependências para instalações reproduzíveis. |
| `vite.config.js` | Configura React, caminho `/build/`, saída em `static/build` e proxy para o Python durante o desenvolvimento. |
| `index.html` | Página de entrada usada para montar a aplicação React. |
| `node_modules/` | Código das dependências instaladas. É gerado pela instalação; não é o lugar para alterar as telas do projeto. |
| `src/` | Código-fonte da interface, detalhado abaixo. |

### src/main.jsx

Monta a aplicação e coordena seu funcionamento. `Login` apresenta o acesso; `Shell` monta navegação e área principal; `Modal` abre detalhes ou formulários; `App` gerencia os estados e disponibiliza o contexto.

Procure `load()` para entender a consulta a `/api/state`, `login()` para o acesso, `run()` para o envio de ações e `handle()` para o tratamento dos comandos da interface. `printTrip()` prepara a lista imprimível. A navegação acompanha o trecho da URL depois de `#`, como `#patients`.

O estado `S` contém a resposta do backend. `find()`, `patientFor()`, `requestFor()` e outros auxiliares localizam registros relacionados. `can()` e `allowed()` controlam o que a interface oferece ao perfil atual.

### src/context.jsx

Define `AppContext` e o hook `useApp()`, que permitem compartilhar estado e funções entre componentes. Também reúne `roles`, `navigation`, formatação de dinheiro e datas, tratamento de nomes e iniciais e a função `api()`.

`api()` encapsula `fetch`: escolhe GET ou POST, envia JSON e transforma uma resposta de erro em uma exceção que a tela pode mostrar. Context é o mecanismo de compartilhamento no React; não é um banco de dados.

### src/pages.jsx

Contém as páginas principais e o mapa `pages`, usado para selecionar a tela pela navegação.

| Componente | Tela ou função |
| --- | --- |
| `Dashboard` | Visão geral, números e resumos. |
| `Patients` | Lista e busca de pacientes. |
| `Requests` | Solicitações e seus estados. |
| `Calendar` | Agenda de ocorrências. |
| `Trips` | Planejamento e consulta de viagens. |
| `Review` | Conferência mensal dos atendimentos. |
| `Finance` | Benefícios e etapas financeiras. |
| `Fleet` | Frota, motoristas e referências. |
| `Audit` | Histórico de operações. |
| `Help` e `Delivery` | Orientações e materiais da entrega. |
| `RequestTable` e `RouteCard` | Elementos de apresentação reutilizados nas páginas. |

### src/details.jsx

Mostra um registro por vez nos diálogos. `PatientDetail` reúne dados e histórico do paciente; `RequestDetail`, solicitação, documentos e agenda; `OccurrenceDetail`, a data de atendimento e comprovações; `TripDetail`, viagem, passageiros e execução; `AuditDetail`, estados anterior e posterior de uma operação.

O objeto `detailComponents` liga comandos como `patient-detail` aos componentes. Essas telas consultam o contexto e oferecem botões que abrem formulários ou disparam ações.

### src/forms.jsx

`Fields` escolhe os campos pelo tipo de operação. `BusinessForm` trata o envio, coleta `FormData`, converte IDs e checkboxes, prepara recorrência e lê anexos. `actionNames` relaciona o tipo de formulário à ação enviada ao backend; `titles` e `saveLabels` definem textos dos diálogos.

Anexos são convertidos para Base64 para viajar dentro do JSON. Depois o backend valida e guarda o conteúdo no banco. Procure `submit()` para seguir esse caminho.

### src/extensions.jsx

Apresenta `Segments` (rotas e trechos), `Production` (preparação e encaminhamento), `Pilot` (indicadores e medições) e `Support` (suporte e capacitação). Os componentes locais `Form`, `Input`, `Choice` e `Memo` ajudam a montar esses formulários.

Apesar de ter o mesmo nome de `app/extensions.py`, este arquivo roda no navegador. O Python aplica as regras correspondentes no servidor.

### src/ui.jsx e src/react.css

`ui.jsx` reúne peças reutilizáveis: `Icon`, `Brand`, `Landscape`, `Badge`, `Button`, `Actions`, `Empty`, `Sub`, `Person`, `Table`, `Header`, `Metric`, `Info`, `Detail`, `Toolbar`, `MonthInput`, `DocList`, `Field`, `Select` e `Check`.

Essas peças desenham ícones, marca, ilustração, etiquetas de situação, botões, tabelas, campos e listas de documentos. Alterar um componente compartilhado pode afetar várias telas.

`react.css` complementa os estilos da interface React. O estilo principal vem de `static/style.css`, importado em `main.jsx`.

## 6. static/ — recursos servidos ao navegador

| Caminho | Responsabilidade |
| --- | --- |
| `style.css` | Estilos principais: cores, layout, tabelas, formulários e adaptação das telas; também usado na lista imprimível. |
| `mark.svg` | Marca gráfica do sistema. |
| `build/index.html` | Entrada da interface compilada, servida pelo Python. |
| `build/assets/index-LpzJtuha.js` | JavaScript compilado da aplicação e suas dependências nesta versão. |
| `build/assets/index-BkEvR2BM.css` | CSS compilado nesta versão. |

Os nomes com sufixo variável são gerados pelo build e podem mudar. Para modificar a interface, edite os arquivos-fonte e rode o build. Edições diretas nos arquivos compilados serão substituídas na próxima compilação.

## 7. tests/ — exemplos executáveis das regras

| Arquivo | O que verifica |
| --- | --- |
| `__init__.py` | Organização do pacote de testes. |
| `test_domain.py` | Laudo para autorização, recorrência, conflitos, CNH, lotação, acessibilidade, comprovações, benefícios, pagamento, auditoria e fluxo completo. |
| `test_extensions.py` | Capacidade por trecho, produção, permissões, migração, backup, piloto, suporte e confirmação assistida. |
| `test_http.py` | Login e cookie, logout, origem das requisições, permissões, downloads, exportações e bloqueio de acesso a arquivos internos. |

Os testes usam `unittest`. Para estudar uma regra, compare o teste com o trecho de `execute()` que ele chama. Um teste geralmente prepara dados, executa uma operação e compara o resultado esperado. A suíte revisada contém 27 testes.

## 8. scripts/ — ferramentas de apoio

Esses scripts não são todos necessários para iniciar o sistema. Alguns geram arquivos, outros executam testes ou iniciam instâncias temporárias.

| Arquivo | Para que serve |
| --- | --- |
| `backup.py` | Usa a API de backup do SQLite, exige destino novo e verifica a integridade da cópia. |
| `run_tests.py` | Executa a suíte Python e salva a saída em `docs/resultado-testes.txt`. |
| `setup_node.py` | Baixa Node.js LTS portátil para Windows, confere SHA256 e extrai em `.tools/`. |
| `browser_check.py` | Usa Playwright e Chrome para conferir telas e capturar desktop e celular; espera servidor na porta 8000. |
| `e2e_flow.py` | Exercita um fluxo integrado no navegador com banco temporário e servidor próprio na porta 8001. |
| `capture_flows.py` | Executa operações pela interface, verifica a API e gera evidências em `docs/fluxos/`, com base isolada na porta 8004. |
| `check_revision.py` | Executa cenários das funcionalidades complementares e produz evidências em `docs/revisao/`. |
| `build_docs.py` | Gera documentação HTML, diagramas e PDFs a partir das fontes e capturas. |
| `build_presentation.py` | Produz guia, slides e pacote dos materiais de apresentação. |
| `revision_docs.py` | Atualiza os documentos da revisão e gera versões consultáveis e PDFs. |
| `inspect_pdfs.py` | Inspeciona PDFs de `docs/` e gera prévias de páginas para revisão visual. |
| `package_delivery.py` | Monta o ZIP do sistema, manifesto de integridade e arquivo SHA256 da entrega. |
| `verify_package.py` | Extrai o pacote em local temporário, verifica hashes e testa a inicialização da entrega. |

Playwright, Markdown e PyMuPDF são usados pelas ferramentas que precisam deles. O servidor principal usa a biblioteca padrão do Python. Leia o início e o final de cada script antes de executá-lo para entender suas entradas e saídas.

## 9. exemplos/ — anexos para demonstração

| Arquivo | Uso |
| --- | --- |
| `laudo-ficticio.txt` | Exemplo de laudo para anexar à solicitação. |
| `declaracao-paciente.txt` | Exemplo de declaração de atendimento do paciente. |
| `declaracao-acompanhante.txt` | Exemplo de declaração do acompanhante. |

São arquivos de entrada para testar o envio de documentos. Eles não executam código. Depois de anexado, o conteúdo é armazenado na tabela `documents`.

## 10. docs/ — material de consulta

As versões `.md` são textos editáveis, `.html` são páginas para leitura no navegador e `.pdf` são versões de distribuição. Os arquivos gerados não se atualizam sozinhos quando uma fonte muda.

| Arquivos | Conteúdo |
| --- | --- |
| `documentacao.md`, `documentacao.html`, `Documentacao-Macaparana.pdf` | Documentação geral de requisitos, regras, arquitetura e entrega. |
| `Guia-Completo-Apresentacao.md`, `.html` e `.pdf` | Explicações e preparação para apresentar o projeto. |
| `roteiro.md`, `roteiro.html`, `Roteiro-de-Apresentacao.pdf` | Sequência sugerida de demonstração. |
| `Slides-Apresentacao.html` e `.pdf` | Apresentação em slides. |
| `prototipo.html`, `Prototipo-de-Telas.pdf` | Galeria de telas do sistema. |
| `fluxos.html`, `Fluxos-Funcionando.pdf` | Operações demonstradas com capturas e resultados. |
| `revisao.html`, `Revisao-Fluxos.pdf` | Evidências da revisão funcional. |
| `operacao.md`, `.html` e `.pdf` | Manual de operação e orientação do piloto. |
| `verificacao-escopo.md`, `.html` e `.pdf` | Conferência do escopo e distinção entre implementação e evolução prevista. |
| `modelo-dados.mmd`, `modelo-dados.svg` | Fonte Mermaid e imagem do modelo de dados. Confira também as migrações para estudar o esquema atual. |
| `fluxo.mmd`, `fluxo.svg` | Fonte e imagem do fluxo do processo. |
| `arquitetura.svg` | Diagrama da arquitetura. |
| `doc.css` | Aparência das páginas de documentação. |
| `mark.svg` | Marca usada nos documentos. |
| `identificacao.json` | Dados de identificação usados na geração dos materiais. |
| `resultado-testes.txt` | Registro de uma execução de testes, com data e resultado. |
| `teste-navegador.json` | Resultado registrado da verificação de interface. |
| `Guia-Estudo-Codigo.md` e `.docx` | Este guia em texto editável e em formato Word. |

### Subpastas de evidências

`telas/` contém PNGs das telas gerais. `fluxos/` contém PNGs numerados das etapas, `manifesto.json` com verificações e descrições, `folha-demonstrativa.csv` exportada e `laudo-baixado.txt` obtido no teste de download. `revisao/` contém capturas da revisão, `resultado.json` e `preparacao-producao.csv`.

O inventário ao final lista cada imagem. PNGs são fotografias de um estado da aplicação, não componentes editáveis. Os relatórios descrevem a execução em que foram gerados; não são uma consulta em tempo real.

## 11. data/, ferramentas e arquivos automáticos

| Caminho | Explicação |
| --- | --- |
| `data/macaparana.db` | Banco persistente local, incluindo anexos. |
| `data/server-output.log` e `server-error.log` | Saída e erros de execuções locais do servidor. |
| `data/github-repository.json` | Arquivo local de metadados do repositório; não participa das regras do sistema. |
| `data/doc-debug.pdf` | Artefato local de trabalho com documentação. |
| `data/pdf-preview/` | Imagens de páginas dos PDFs, para inspeção visual. |
| `data/presentation-preview/` | Imagens de páginas dos materiais de apresentação. |
| `.tools/node-v24.21.0-win-x64/` | Distribuição portátil do Node.js, com executável e ferramentas npm. |
| `.tools/node-v24.21.0-win-x64.zip` | Arquivo compactado dessa distribuição. |
| `.git/` | Objetos, referências, índice, logs e configuração interna do Git. |
| `__pycache__/` e arquivos `.pyc` | Cache compilado dos módulos Python. |

O backup padrão de `scripts/backup.py` é criado em `data/backups/` quando o script é executado. A pasta não precisa existir antecipadamente. Arquivos auxiliares do SQLite também podem aparecer durante o uso.

Os scripts de empacotamento podem criar `entrega/Macaparana-Saude-Entrega.zip`, `entrega/Material-Apresentacao-Macaparana.zip` e `entrega/SHA256.txt`. O pacote completo inclui um manifesto `MANIFESTO-SHA256.json` usado para verificar integridade. Esses itens são saídas de entrega, não módulos da aplicação.

Dependências de terceiros, caches e internals do Git são explicados por categoria porque têm muitos arquivos automáticos e variam conforme instalação. Para estudar a lógica escrita neste projeto, concentre-se em `app/`, `frontend/src/`, `server.py` e `tests/`.

## 12. Exemplo completo: cadastrar um paciente

1. A página `Patients`, em `pages.jsx`, oferece a ação de cadastro.
2. O tratamento em `main.jsx` abre o diálogo apropriado.
3. `BusinessForm` e `Fields`, em `forms.jsx`, exibem os campos.
4. `submit()` coleta os valores e identifica a ação `patient.create`.
5. `run()` envia `{ action, data }` para `/api/action` usando `api()`.
6. `server.py` identifica o usuário, abre a transação e chama `execute()`.
7. `domain.py` verifica o perfil, os campos obrigatórios e as condições do cadastro.
8. O registro é inserido em `patients` e a operação é registrada em `audit`.
9. O servidor confirma a transação e devolve o resultado.
10. `run()` chama `load()`, recebe o estado atualizado e o React redesenha a lista.

Para entender erros, siga o mesmo caminho: `require()` pode lançar `RuleError`; o servidor devolve um JSON de erro; `api()` lança uma exceção; o formulário mostra a mensagem. Os campos da tela ajudam o usuário, mas a validação definitiva ocorre no backend.

## 13. Ordem sugerida de estudo

1. Leia o `README.md` e abra o sistema para reconhecer os termos das telas.
2. Leia `schema.sql` e `migrate()` em `app/extensions.py`. Desenhe as relações entre paciente, solicitação, ocorrência e viagem.
3. Leia `seed.py` e identifique como os dados fictícios são ligados.
4. Leia `server.py`, começando por `main()` e pelos endpoints.
5. Estude os auxiliares de `domain.py` e acompanhe apenas `patient.create` de ponta a ponta.
6. Leia `context.jsx` e os trechos `load()`, `run()` e `handle()` de `main.jsx`.
7. Compare `pages.jsx`, `details.jsx` e `forms.jsx`: lista, detalhe e edição de uma operação.
8. Leia `ui.jsx` e os CSS para entender o visual que se repete.
9. Estude viagens, comprovação e benefícios no domínio, junto com os testes correspondentes.
10. Termine com os dois arquivos `extensions`, os testes HTTP e os scripts de apoio.

Exercícios: localize onde a falta de laudo impede autorização; explique por que embarque não comprova atendimento; descubra como o acompanhante ocupa um assento; acompanhe a filtragem do perfil motorista; encontre onde a regra financeira fica vinculada ao benefício.

## 14. Onde mexer para cada mudança

| Mudança desejada | Arquivos a investigar |
| --- | --- |
| Texto ou conteúdo de uma página | `frontend/src/pages.jsx` ou `extensions.jsx`. |
| Detalhe de paciente, solicitação ou viagem | `frontend/src/details.jsx`. |
| Campos de um formulário | `frontend/src/forms.jsx`; confira também validação e persistência no backend. |
| Botões, tabelas e campos compartilhados | `frontend/src/ui.jsx`. |
| Cores, espaçamentos e layout | `static/style.css` e `frontend/src/react.css`. |
| Navegação e coordenação da interface | `context.jsx` e `main.jsx`. |
| Regra ou permissão de uma operação | `app/domain.py` ou `app/extensions.py`. |
| Dados permitidos em uma consulta | `state()` e `extend_state()`. |
| Nova tabela ou coluna | `schema.sql` para estrutura inicial e uma migração adequada para bancos existentes. |
| Dados iniciais de demonstração | `app/seed.py`. |
| Endpoint, sessão ou arquivo servido | `server.py`. |
| Comportamento esperado de uma regra | `tests/`. |

## 15. Comandos para acompanhar o estudo

Na raiz do projeto, inicie o servidor:

```powershell
py server.py
```

Neste ambiente, `py` encontra o Python instalado. O atalho `iniciar.bat` usa `python`; ele depende de esse comando estar configurado no Windows. Abra `http://localhost:8000` e use a conta demonstrativa `admin`, senha `demo123`.

Para estudar com outro banco, sem trocar o arquivo principal:

```powershell
py server.py --port 8002 --db data/estudo.db
```

Para executar os testes:

```powershell
py -m unittest discover -s tests -v
```

Com Node/npm disponíveis no PATH, compile a interface:

```powershell
cd frontend
npm ci
npm run build
```

Neste ambiente já existe Node portátil. Na raiz, com as dependências instaladas, a alternativa é:

```powershell
cd frontend
& ../.tools/node-v24.21.0-win-x64/node.exe node_modules/vite/bin/vite.js build
```

Para desenvolvimento com recarga automática, mantenha o Python na porta 8000 e execute `npm run dev` em outro terminal, dentro de `frontend`. A interface de desenvolvimento usa `http://127.0.0.1:5173/build/`. O proxy encaminha as chamadas da API para o backend.

## 16. Vocabulário para ler o código

| Termo | Significado neste projeto |
| --- | --- |
| JSX | Sintaxe que permite escrever a estrutura visual dentro do JavaScript. |
| Componente | Função React que representa uma parte da interface. |
| Props | Valores recebidos por um componente, como `id` ou `patient`. |
| Hook | Função React como `useState`, `useEffect` ou o hook local `useApp`. |
| Estado | Dados em memória que orientam a renderização da interface. |
| JSON | Formato usado nas mensagens entre navegador e servidor. |
| ID | Identificador de um registro. `patient_id` aponta para um paciente. |
| Migração | Alteração da estrutura de um banco que pode já conter dados. |
| Seed | Preenchimento inicial com dados de exemplo. |
| Build | Transformação do código-fonte em arquivos servidos ao navegador. |
| Transação | Grupo de alterações confirmado ou desfeito como uma unidade. |
| Auditoria | Registro de quem realizou uma operação e do que mudou. |
| Competência | Mês de referência usado em conferências e filtros. |
| Ocorrência | Uma data concreta de atendimento vinculada a uma solicitação. |


## 17. Invent?rio das capturas e pr?vias

Os nomes abaixo correspondem aos arquivos presentes na revis?o. A numera??o indica a sequ?ncia das capturas.

### docs/telas/

| Arquivo | Conte?do identificado pelo nome |
| --- | --- |
| `01-login.png` | Captura: login. |
| `02-dashboard.png` | Captura: dashboard. |
| `03-patients.png` | Captura: patients. |
| `04-requests.png` | Captura: requests. |
| `05-calendar.png` | Captura: calendar. |
| `06-trips.png` | Captura: trips. |
| `07-review.png` | Captura: review. |
| `08-finance.png` | Captura: finance. |
| `09-fleet.png` | Captura: fleet. |
| `10-audit.png` | Captura: audit. |
| `11-help.png` | Captura: help. |
| `12-operacao.png` | Captura: operacao. |
| `13-mobile.png` | Captura: mobile. |

### docs/fluxos/

| Arquivo | Conte?do identificado pelo nome |
| --- | --- |
| `01-painel.png` | Captura: painel. |
| `02-cadastro.png` | Captura: cadastro. |
| `03-historico.png` | Captura: historico. |
| `04-recursos.png` | Captura: recursos. |
| `05-solicitacao.png` | Captura: solicitacao. |
| `06-bloqueio-laudo.png` | Captura: bloqueio laudo. |
| `07-pendencia.png` | Captura: pendencia. |
| `08-laudo.png` | Captura: laudo. |
| `09-autorizacao.png` | Captura: autorizacao. |
| `10-recorrencia.png` | Captura: recorrencia. |
| `11-calendario.png` | Captura: calendario. |
| `12-competencia.png` | Captura: competencia. |
| `13-viagem.png` | Captura: viagem. |
| `14-alocacao.png` | Captura: alocacao. |
| `15-lotacao.png` | Captura: lotacao. |
| `16-confirmacao.png` | Captura: confirmacao. |
| `17-embarque.png` | Captura: embarque. |
| `18-encerramento.png` | Captura: encerramento. |
| `19-bloqueio-comprovacao.png` | Captura: bloqueio comprovacao. |
| `20-prova-paciente.png` | Captura: prova paciente. |
| `21-prova-acompanhante.png` | Captura: prova acompanhante. |
| `22-conferencia.png` | Captura: conferencia. |
| `23-calculo.png` | Captura: calculo. |
| `24-aprovacao.png` | Captura: aprovacao. |
| `25-contabilidade.png` | Captura: contabilidade. |
| `26-pagamento.png` | Captura: pagamento. |
| `27-exportacao.png` | Captura: exportacao. |
| `28-regra.png` | Captura: regra. |
| `29-transporte-autorizado.png` | Captura: transporte autorizado. |
| `30-transporte-comprovado.png` | Captura: transporte comprovado. |
| `31-transporte-sem-beneficio.png` | Captura: transporte sem beneficio. |
| `32-negativa.png` | Captura: negativa. |
| `33-auditoria.png` | Captura: auditoria. |
| `34-motorista.png` | Captura: motorista. |
| `35-lista-motorista.png` | Captura: lista motorista. |
| `36-regulacao.png` | Captura: regulacao. |
| `37-transporte.png` | Captura: transporte. |
| `38-financeiro.png` | Captura: financeiro. |
| `39-auditor.png` | Captura: auditor. |
| `40-retirada.png` | Captura: retirada. |
| `41-realocacao.png` | Captura: realocacao. |
| `42-ausencia.png` | Captura: ausencia. |
| `43-bloqueio-encerramento.png` | Captura: bloqueio encerramento. |
| `44-lista-impressao.png` | Captura: lista impressao. |
| `45-conflito-horario.png` | Captura: conflito horario. |
| `46-cnh-vencida.png` | Captura: cnh vencida. |
| `47-acessibilidade.png` | Captura: acessibilidade. |
| `48-agenda-sem-duplicidade.png` | Captura: agenda sem duplicidade. |
| `49-documento-download.png` | Captura: documento download. |

### docs/revisao/

| Arquivo | Conte?do identificado pelo nome |
| --- | --- |
| `01-rota-trechos.png` | Captura: rota trechos. |
| `02-alocacao-confirmacao.png` | Captura: alocacao confirmacao. |
| `03-producao-preparada.png` | Captura: producao preparada. |
| `04-producao-encaminhada.png` | Captura: producao encaminhada. |
| `05-indicadores-piloto.png` | Captura: indicadores piloto. |
| `06-capacitacao-suporte.png` | Captura: capacitacao suporte. |
| `07-mobile.png` | Captura: mobile. |

### data/pdf-preview/

| Arquivo | Conte?do identificado pelo nome |
| --- | --- |
| `Documentacao-Macaparana-1.png` | Pr?via de p?gina: Documentacao Macaparana 1. |
| `Documentacao-Macaparana-18.png` | Pr?via de p?gina: Documentacao Macaparana 18. |
| `Documentacao-Macaparana-19.png` | Pr?via de p?gina: Documentacao Macaparana 19. |
| `Documentacao-Macaparana-3.png` | Pr?via de p?gina: Documentacao Macaparana 3. |
| `Documentacao-Macaparana-7.png` | Pr?via de p?gina: Documentacao Macaparana 7. |
| `Fluxos-Funcionando-1.png` | Pr?via de p?gina: Fluxos Funcionando 1. |
| `Fluxos-Funcionando-3.png` | Pr?via de p?gina: Fluxos Funcionando 3. |
| `Fluxos-Funcionando-51.png` | Pr?via de p?gina: Fluxos Funcionando 51. |
| `Prototipo-de-Telas-1.png` | Pr?via de p?gina: Prototipo de Telas 1. |
| `Prototipo-de-Telas-15.png` | Pr?via de p?gina: Prototipo de Telas 15. |
| `Prototipo-de-Telas-16.png` | Pr?via de p?gina: Prototipo de Telas 16. |
| `Prototipo-de-Telas-3.png` | Pr?via de p?gina: Prototipo de Telas 3. |
| `Roteiro-de-Apresentacao-1.png` | Pr?via de p?gina: Roteiro de Apresentacao 1. |
| `Roteiro-de-Apresentacao-3.png` | Pr?via de p?gina: Roteiro de Apresentacao 3. |
| `Roteiro-de-Apresentacao-4.png` | Pr?via de p?gina: Roteiro de Apresentacao 4. |

### data/presentation-preview/

| Arquivo | Conte?do identificado pelo nome |
| --- | --- |
| `Guia-Completo-Apresentacao-1.png` | Pr?via de p?gina: Guia Completo Apresentacao 1. |
| `Guia-Completo-Apresentacao-28.png` | Pr?via de p?gina: Guia Completo Apresentacao 28. |
| `Guia-Completo-Apresentacao-4.png` | Pr?via de p?gina: Guia Completo Apresentacao 4. |
| `review-19.png` | Pr?via de p?gina: review 19. |
| `review-4.png` | Pr?via de p?gina: review 4. |
| `Slides-Apresentacao-1.png` | Pr?via de p?gina: Slides Apresentacao 1. |
| `Slides-Apresentacao-12.png` | Pr?via de p?gina: Slides Apresentacao 12. |
| `Slides-Apresentacao-4.png` | Pr?via de p?gina: Slides Apresentacao 4. |
