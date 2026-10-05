# Verificação do escopo — Macaparana Saúde

Revisão de 04/10/2026. O resultado é um sistema acadêmico funcional com dados fictícios. Implementação e teste local não equivalem à implantação municipal. As evidências anteriores permanecem como histórico; a revisão tem evidências adicionais em `revisao/`.

| Requisito do enunciado | Resultado da revisão | Onde verificar |
|---|---|---|
| Pacientes SUS, acompanhantes e transporte sem TFD | Implementado; modalidades separadas | Pacientes, Solicitações |
| TFD, regulação, transporte, motorista, financeiro, faturamento e controle | Perfis implementados; faturamento adicionado nesta revisão | Login e permissões no servidor |
| Solicitação, análise, autorização e laudo | Implementado com bloqueio sem laudo e motivo da decisão | Solicitações |
| Calendário semanal e datas avulsas entre competências | Implementado com validade e proteção contra duplicidade | Calendário |
| Dados do paciente, acompanhante, endereço, embarque e banco | Implementado; um acompanhante cadastrado por paciente nesta versão | Pacientes |
| Unidade identificada por CNES e especialidade | Implementado; CNES informado manualmente, sem validação externa | Frota e referências / Solicitações |
| Reutilização de referências válidas | Cadastros ativos reutilizáveis e autorização dentro da validade | Solicitações / Calendário |
| Veículos, motoristas, capacidade e acessibilidade | Implementado; acompanhante ocupa lugar, conflitos e CNH verificados | Viagens |
| Rotas e alocação por data e trecho | Complementado: paradas ordenadas, intervalo de embarque/desembarque, capacidade em cada segmento | Rotas e trechos |
| Alterações rastreáveis | Auditoria de criação, retirada, nova alocação e alteração de rota justificada | Auditoria |
| Quilômetros reais, consumo e custos | Implementado no encerramento | Viagens / Indicadores e piloto |
| Mapas para apoio | Opcional no enunciado; não conectado. Rota e distância estimada são informadas pela equipe | Viagens |
| Confirmação antecipada e alternativa assistida | Implementado; canal e observação acrescentados. Resposta aparece na lista do motorista | Rotas e trechos / Viagens |
| WhatsApp quando viável e autorizado | Não integrado. É possível registrar uma resposta obtida externamente pela equipe; não há envio de mensagem | Confirmação assistida |
| Conferência mensal em tabela compacta de datas | Implementado com abertura da ocorrência e documentos | Conferência mensal |
| Declaração, viagem, permanência e prova separada do acompanhante | Implementado; permanência é texto obrigatório, documentos são independentes | Ocorrência / Conferência mensal |
| Folha, contabilidade, pagamento e pendências por etapa | Implementado; regras financeiras demonstrativas e estágios distintos | Ajudas de custo |
| Preparação da produção | Complementado: perfil de faturamento, procedimento informado, quantidade, destino de revisão, protocolo e CSV por competência | Produzir / faturar |
| Produção em sistemas oficiais | Depende de catálogo, elegibilidade, leiaute e homologação definidos com o município; CSV interno não deve ser importado como leiaute oficial | Documentação e aviso na tela |
| Painel assistencial, operacional, financeiro e documentos de origem | Implementado com vínculos entre paciente, solicitação, ocorrência, viagem, documentos e benefício | Visão geral / Indicadores / Detalhes |
| Indicadores de custo e desempenho | Complementado com custo por embarque em viagens encerradas, km/l, ausência e pendências, com denominadores explícitos | Indicadores e piloto |
| Proteção dos dados | Sessão, hash de senha, autorização no servidor, restrição do motorista, auditoria, consultas parametrizadas e backup local consistente | Testes / Manual de operação |
| Capacitação e suporte | Materiais e registros de oficina/chamado implementados; atendimento institucional precisa de equipe designada | Suporte / Manual |
| Demonstração em rotina municipal | Pendente de participação e autorização da prefeitura. Testes locais não são demonstração municipal | Plano de piloto |
| Medição de resultados do piloto | Ferramenta implementada com linha de base, resultado, período, fonte, responsável e distinção entre simulação e rotina municipal. Medição real pendente | Indicadores e piloto |
| e-SUS APS e integração CNES | Condicionadas a interfaces, credenciais e permissões; não conectadas | Limites de integração |

## Complementos desta revisão

O banco existente é migrado sem apagar seus registros. Viagens antigas continuam com um segmento integral. Nas viagens novas, a equipe pode definir paradas antes da alocação. A capacidade é calculada separadamente em cada intervalo; uma vaga pode ser reutilizada após o desembarque previsto. O embarque operacional continua registrado por ocorrência; não há rastreamento GPS nem comprovação automática de desembarque em cada parada.

O faturamento pode preparar somente ocorrências conciliadas. O código possui validação de formato, não de existência no catálogo oficial. CNS ausente, identificadores fictícios, elegibilidade e demais exigências do destinatário precisam ser revisados. Encaminhar registra protocolo interno e não transmite ao SUS. Registros encaminhados não são sobrescritos por nova preparação.

As métricas automáticas usam registros locais. Custo de transporte não inclui ajudas de custo; o custo por embarque usa pacientes embarcados nas mesmas viagens encerradas do numerador. A ocupação por trecho é reserva de lugares, incluindo acompanhante, e não medida de presença física do acompanhante. Não há economia, ganho percentual ou piloto municipal comprovado neste projeto.

## O que depende de terceiros

Validação técnica da revisão: 27 testes automatizados aprovados, fluxo completo até pagamento aprovado no navegador e sete capturas adicionais das novas funcionalidades; sem erros JavaScript nos fluxos verificados. Os dados usados são fictícios. Consulte `resultado-testes.txt`, `teste-navegador.json` e `revisao/resultado.json`.

1. Município: validar fluxos, valores, critérios de benefício, responsabilidades e aceite funcional.
2. Sistemas oficiais: disponibilizar interfaces e autorizar credenciais; definir procedimento, elegibilidade e leiaute por destino.
3. Infraestrutura: contas individuais, HTTPS, armazenamento e backups protegidos, monitoramento e recuperação testada antes de dados reais.
4. Equipe municipal: realizar a capacitação, operar o piloto, produzir fontes de medição e assinar o relatório de resultados.

Essas etapas não podem ser declaradas concluídas por alterações no código ou dados simulados.
