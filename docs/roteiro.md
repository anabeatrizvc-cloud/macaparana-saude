# Roteiro de apresentação

**Macaparana Saúde — sugestão de demonstração de 8 a 12 minutos.** Use exclusivamente a base fictícia. Deixe o servidor aberto, o navegador preparado e os três arquivos da pasta `exemplos` acessíveis.

## 1. Apresente o problema — 1 minuto

“O projeto conecta regulação, transporte e financeiro para acompanhar o paciente desde a solicitação até a comprovação e o registro de eventual ajuda de custo. O foco é manter rastreabilidade e distinguir TFD de transporte sanitário.”

Explique que o sistema é um demonstrador acadêmico com dados fictícios, sem integração oficial ou pagamento real. Abra a Visão geral e mostre que os números derivam dos registros locais.

## 2. Mostre a cadeia de dados — 2 minutos

1. Entre com **admin / demo123**.
2. Em **Pacientes**, abra o histórico de Maria de Lourdes. Mostre endereço de embarque e acompanhante.
3. Em **Solicitações**, abra uma solicitação autorizada de TFD. Mostre laudo, validade e agendamentos.
4. Abra uma solicitação de transporte sanitário e explique por que ela não gera automaticamente ajuda de custo de TFD.
5. Em **Calendário**, navegue entre competências para mostrar a continuidade da recorrência de Maria.

## 3. Demonstre a operação — 2 minutos

1. Em **Viagens**, abra a viagem de hoje para Recife.
2. Observe que acompanhantes também ocupam lugares e que há um veículo acessível.
3. Confirme um paciente pendente, se houver, e registre **Embarcou**.
4. Explique: embarque confirma o deslocamento, não o atendimento.
5. Mostre o botão de impressão da lista operacional.

Evite encerrar uma viagem com passageiros ainda pendentes; o sistema bloqueará essa operação. Esse bloqueio pode ser demonstrado deliberadamente, explicando a mensagem.

## 4. Comprove e confira — 2 minutos

1. Em **Conferência mensal**, abra a célula de hoje do paciente cujo embarque acabou de registrar.
2. Clique **Anexar declaração**, selecione declaração do paciente e use `exemplos/declaracao-paciente.txt`.
3. Se há acompanhante, anexe separadamente `exemplos/declaracao-acompanhante.txt`, selecionando o tipo correto.
4. Clique **Conciliar atendimento**, informe permanência e marque o acompanhante somente quando a declaração dele estiver anexada.
5. Mostre que a tabela mensal passa a indicar comprovação e que cada célula abre seus documentos.

## 5. Demonstre o financeiro — 2 minutos

1. Abra **Ajudas de custo** na competência correta.
2. Clique **Calcular competência**. Explique que os valores são fictícios e que somente TFD comprovado é considerado.
3. Encontre um benefício em **Calculado** e clique **Aprovar**.
4. Clique **Encaminhar** e informe uma referência fictícia, como `DEMO-APRESENTACAO`.
5. Clique **Registrar pagamento**, confirme referência e data de hoje.
6. Use **Origem** para voltar ao atendimento. Mostre a exportação CSV.

O registro de pagamento é apenas uma etapa de acompanhamento. Não há transferência bancária ou envio à contabilidade real.

## 6. Encerre com evidência — 1 minuto

Mostre **Auditoria** e abra um evento gerado durante a demonstração. Apresente autor, data/hora e estados anterior e posterior. Abra **Entrega acadêmica** para acessar documentação e protótipo.

Se houver tempo, saia e entre como **motorista / demo123**: somente suas viagens e dados operacionais ficam disponíveis. Esse perfil não recebe documentos clínicos nem dados bancários.

## Cenário completo partindo do zero

Para uma demonstração mais longa, execute esta sequência. Ela foi usada como base para o teste automatizado de navegador.

| Etapa | Ação |
| --- | --- |
| 1 | Cadastre um paciente fictício com nome, endereço e embarque |
| 2 | Crie solicitação TFD com validade abrangendo hoje |
| 3 | Anexe `laudo-ficticio.txt` e autorize com justificativa |
| 4 | Gere uma ocorrência avulsa para hoje |
| 5 | Crie viagem hoje das 18:00 às 20:00 para evitar as viagens iniciais de 05:00 a 17:00 |
| 6 | Aloque o paciente, confirme e registre embarque |
| 7 | Encerre a viagem com km, litros e custo demonstrativos |
| 8 | Anexe declaração do paciente à ocorrência e concilie atendimento |
| 9 | Calcule a competência, aprove, encaminhe e registre pagamento |
| 10 | Recarregue a tela e mostre os dados preservados e a auditoria |

## Perguntas prováveis do professor

**Por que Python, React e SQLite?** React organiza as telas em componentes com estado; Python concentra regras e permissões; SQLite oferece persistência sem configurar um banco externo. O frontend já está compilado, permitindo apresentar o sistema com apenas o servidor Python. A arquitetura pode evoluir após levantamento municipal.

**É só um protótipo?** A interface funciona sobre uma API e um banco persistente, com testes de regras e de fluxo. É um demonstrador funcional, com limitações explícitas para implantação real.

**Como evitam benefício duplicado?** O banco restringe ocorrência e beneficiário a um único item; recalcular não duplica e preserva valor e versão da regra.

**O transporte sanitário é tratado como TFD?** Não. O processo guarda modalidade própria e o cálculo exclui transporte sanitário.

**WhatsApp, CNES e e-SUS estão integrados?** Não nesta versão. As integrações dependem de interfaces, credenciais, permissões e homologação.

**Os valores são os valores legais?** Não. São R$ 35 e R$ 25 apenas como exemplos de parametrização acadêmica.

**O sistema está pronto para usar com pacientes reais?** Não. Faltam homologação do domínio, infraestrutura protegida, controles adicionais, regras oficiais, capacitação e piloto.

**Como sabem que funciona?** A entrega inclui testes automatizados de domínio e HTTP, um fluxo completo pelos formulários no Chrome e capturas das telas. Os relatórios acompanham o projeto.

**O que falta para atender integralmente em produção municipal?** Regras de permanência/benefício homologadas, integrações oficiais autorizadas, produção em leiaute homologado, infraestrutura protegida e execução/medição de piloto real. Trechos estruturados, preparação interna de produção e registro de medições foram acrescentados na revisão de 04/10/2026. Cadastro independente de múltiplos acompanhantes permanece uma evolução do modelo.

## Plano de contingência

- Se a porta 8000 estiver ocupada, use `python server.py --port 8002` e ajuste a URL.
- Se o servidor parar, reinicie; o banco preserva registros salvos.
- Se não houver tempo de executar tudo, use os exemplos já comprovados do dia anterior para mostrar conferência e financeiro.
- Se a máquina não executar Python, apresente os PDFs e as capturas; eles não substituem o sistema funcional, mas preservam a explicação do trabalho.
- Não apague o banco durante a apresentação. Para uma base nova, use outro caminho com `--db`.

## Antes de enviar

Confira os dados de identificação acadêmica na capa, abra os PDFs, teste o acesso local e anexe o pacote ZIP. O nome da instituição, professor e integrantes precisa ser preenchido pelo aluno quando não tiver sido informado.
