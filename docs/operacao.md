# Operação, capacitação, suporte e piloto

## Iniciar e demonstrar

Execute `iniciar.bat`, abra `http://localhost:8000` e use um dos perfis `admin`, `regulacao`, `transporte`, `motorista`, `financeiro`, `faturamento` ou `auditor`. A senha acadêmica é `demo123`. Use somente dados fictícios neste ambiente.

## Oficina de capacitação proposta — 90 minutos

| Duração | Público | Exercício e evidência |
|---|---|---|
| 10 min | Todos | Acesso por perfil, finalidade dos dados e localização do manual |
| 20 min | Regulação | Cadastrar paciente/acompanhante, anexar laudo, decidir e gerar agenda entre competências |
| 20 min | Transporte/motorista | Definir paradas, alocar por trecho, confirmar por telefone, imprimir lista, registrar embarque/ausência e execução |
| 20 min | Regulação/financeiro | Anexar declarações independentes, conferir permanência, calcular benefício, encaminhar e registrar pagamento fictício |
| 10 min | Faturamento | Preparar ocorrência, registrar pendências, exportar CSV interno e encaminhar para revisão |
| 10 min | Controle/gestão | Consultar auditoria, abrir suporte e registrar medição com fonte |

Registre a oficina em Suporte, tipo Capacitação, com responsável, participantes por função, data, exercício, dúvidas e referência à evidência. Conclua somente após a realização. Não registre uma oficina planejada como realizada.

## Rotas por trecho

Crie a viagem em Viagens. Em Rotas e trechos, selecione-a e informe uma parada por linha, por exemplo: Macaparana, Carpina, Recife, Macaparana. Defina embarque e desembarque do agendamento. O sistema conta paciente e acompanhante em cada intervalo ocupado e bloqueia excesso de capacidade. O cadastro padrão em Viagens reserva o percurso completo.

Para alterar paradas com passageiros, retire as alocações ainda não embarcadas com justificativa, altere a rota e faça nova alocação e confirmação. Viagens encerradas e embarques registrados são protegidos. A lista operacional e sua impressão mostram os trechos.

## Produção e faturamento

Selecione a competência, confira as pendências e abra a ocorrência para consultar documentos. Prepare somente atendimento comprovado. Informe código, quantidade, destino e observações de revisão. Confira CNS, CNES, modalidade, prova e regras aplicáveis antes do encaminhamento. O CSV contém identificadores dos registros de origem para conciliação; não é arquivo oficial homologado. O protocolo indica encaminhamento interno para revisão, não aceite ou transmissão por sistema oficial.

## Suporte

Registre título, responsável e passos para reproduzir o problema. Evite nomes de pacientes e informações clínicas no texto. A gestão deve designar uma pessoa para triagem diária. Interrupção do serviço e suspeita de exposição de dados devem ser encaminhadas imediatamente ao responsável municipal designado. Não há serviço externo ou SLA contratado por este projeto.

O administrador registra a solução e conclui o chamado. A trilha de auditoria conserva autor, data e alteração. Dúvidas recorrentes devem gerar uma sessão de capacitação e atualização do manual.

## Backup e recuperação local

Execute `python scripts/backup.py`. O script cria uma cópia SQLite consistente em `data/backups` e verifica a integridade. Opcionalmente informe `--source` e `--target`; o destino precisa ser novo. A cópia contém os mesmos dados sensíveis do banco e deve ficar em armazenamento com acesso restrito. Backups, banco e sessões não entram no Git nem no pacote de entrega.

Para testar a recuperação sem sobrescrever a base principal, execute `python server.py --port 8005 --db data/backups/NOME-DA-COPIA.db` e confira cadastros, documentos e totais. Encerre esse servidor ao final. A restauração de produção exige procedimento acordado com a equipe responsável; a cópia local não substitui backup externo protegido.

## Plano de piloto municipal

1. Obter aceite da prefeitura e responsáveis por regulação, transporte, financeiro, faturamento e controle. Validar fluxos, regras, proteção dos dados e infraestrutura antes de dados reais.
2. Selecionar uma rota e uma equipe. Definir período de linha de base e período de piloto comparáveis, volume, critérios de inclusão e fontes.
3. Medir tempo de análise/conferência, ocorrências sem prova, ausências, km, litros, custo e ocupação por trecho. Registrar numerador, denominador e método. Não comparar períodos incompatíveis sem explicar diferenças.
4. Executar a oficina e registrar evidências. Operar com acompanhamento, registrar problemas e corrigir antes de expandir.
5. Em Indicadores e piloto, registrar linha de base, resultado, unidade, período, fonte e responsável. Usar Simulação acadêmica para testes; Rotina municipal somente para medições reais verificáveis.
6. Revisar resultados com a equipe. Registrar limitações, volume, incidentes, aceite e decisão sobre continuidade. A variação percentual é aritmética e não prova causal de melhoria.

### Modelo de relatório de resultado

Município/unidade; responsáveis; autorização; período; público e volume; critérios; infraestrutura; oficinas realizadas; indicadores e fontes; linha de base; resultado; denominadores; pendências; incidentes; limitações; decisão; assinatura/aceite. Até a execução com a prefeitura, o resultado municipal permanece não medido.
