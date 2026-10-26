import { Segments, Production, Pilot, Support } from "./extensions";
import React from "react";
import {
  useApp,
  money,
  dateFmt,
  shortDate,
  timeFmt,
  cleanName,
} from "./context";
import {
  Header,
  Metric,
  Button,
  Badge,
  Person,
  Table,
  Sub,
  Toolbar,
  MonthInput,
  Icon,
  Landscape,
  Empty,
  Info,
  Detail,
} from "./ui";

export function RequestTable({ rows }) {
  const { find, facilityFor } = useApp();
  return (
    <Table
      headers={[
        "Paciente",
        "Modalidade",
        "Referência / especialidade",
        "Situação",
        "",
      ]}
      rows={rows.map((r) => [
        <Person patient={find("patients", r.patient_id)} />,
        <Badge>{r.kind}</Badge>,
        <>
          {facilityFor(r)?.city}
          <Sub>{r.specialty}</Sub>
        </>,
        <Badge>{r.status}</Badge>,
        <Button act="request-detail" id={r.id} variant="small" icon="arrow">
          Abrir
        </Button>,
      ])}
    />
  );
}
function RouteCard({ trip: t }) {
  const { find, seats } = useApp(),
    vehicle = find("vehicles", t.vehicle_id),
    count = seats(t);
  return (
    <div className="route-card">
      <div className="route-top">
        <div className="route-name">
          <span className="route-icon">
            <Icon name="bus" />
          </span>
          <div>
            <strong>
              Macaparana <Icon name="arrow" /> {t.destination}
            </strong>
            <small>
              {vehicle?.name} · {vehicle?.plate}
            </small>
          </div>
        </div>
        <Badge>{t.status}</Badge>
      </div>
      <div className="route-meta">
        <span>
          <Icon name="clock" />
          {shortDate(t.date)} · {t.departure}
        </span>
        <span>
          <Icon name="users" />
          {count} passageiros
        </span>
        <Button act="trip-detail" id={t.id} variant="small" icon="arrow">
          {count}/{vehicle?.capacity} lugares
        </Button>
      </div>
      <div className="progress">
        <span
          style={{
            width:
              Math.min(100, (count / (vehicle?.capacity || 1)) * 100) + "%",
          }}
        />
      </div>
    </div>
  );
}
export function Dashboard() {
  const { S, can, month } = useApp(),
    todayTrips = S.trips.filter((t) => t.date === S.today),
    pending = S.requests.filter((r) =>
      ["Em análise", "Pendente"].includes(r.status),
    ),
    proof = S.occurrences.filter(
      (o) => o.boarding === "Embarcou" && !o.attendance,
    ),
    unallocated = S.occurrences.filter((o) => !o.trip_id && o.date >= S.today),
    spent = S.trips
      .filter((t) => t.date.startsWith(month))
      .reduce((n, t) => n + t.cost_cents, 0);
  const months = Array.from({ length: 6 }, (_, i) => {
      const d = new Date(S.today + "T12:00:00");
      d.setMonth(d.getMonth() - 5 + i, 1);
      const key = d.toISOString().slice(0, 7);
      return {
        label: d
          .toLocaleDateString("pt-BR", { month: "short" })
          .replace(".", ""),
        value: S.occurrences.filter(
          (o) => o.date.startsWith(key) && o.boarding === "Embarcou",
        ).length,
      };
    }),
    max = Math.max(1, ...months.map((m) => m.value));
  return (
    <>
      <Header
        title="Visão geral"
        subtitle="Acompanhe o cuidado, do planejamento à prestação de contas."
      >
        {can("regulacao") && (
          <Button act="request-new" variant="primary" icon="plus">
            Nova solicitação
          </Button>
        )}
      </Header>
      <section className="welcome">
        <div>
          <span className="eyebrow">Saúde em movimento</span>
          <h2>Cada viagem, uma continuidade do cuidado.</h2>
          <p>
            Planeje os próximos deslocamentos e acompanhe o que precisa de
            atenção.
          </p>
        </div>
        <Landscape />
      </section>
      <div className="metrics">
        <Metric
          label="Pacientes cadastrados"
          value={S.patients.length}
          foot="Base única · pacientes fictícios"
          icon="users"
        />
        <Metric
          label="Viagens de hoje"
          value={todayTrips.length}
          foot={`${todayTrips.filter((t) => t.status === "Planejada").length} planejadas para execução`}
          icon="bus"
        />
        <Metric
          label="Solicitações pendentes"
          value={pending.length}
          foot="Aguardando análise ou documentação"
          icon="file"
        />
        <Metric
          label="Custo de transporte"
          value={money(spent)}
          foot={`Realizado em ${month.split("-").reverse().join("/")} · sem benefícios`}
          icon="wallet"
        />
      </div>
      <div className="grid-main">
        <section className="card">
          <div className="card-head">
            <div>
              <h2>Viagens de hoje</h2>
              <p>Rotas, passageiros e disponibilidade</p>
            </div>
            <a href="#trips" className="link-btn">
              Ver todas <Icon name="arrow" />
            </a>
          </div>
          <div className="card-body">
            {todayTrips.length ? (
              todayTrips.map((t) => <RouteCard key={t.id} trip={t} />)
            ) : (
              <Empty>Nenhuma viagem para hoje. Planeje em Viagens.</Empty>
            )}
          </div>
        </section>
        <section className="card">
          <div className="card-head">
            <div>
              <h2>Deslocamentos realizados</h2>
              <p>Embarques registrados por mês</p>
            </div>
            <Icon name="chart" />
          </div>
          <div className="card-body">
            <div className="chart">
              {months.map((m) => (
                <div className="chart-col" key={m.label}>
                  <span className="chart-value">{m.value}</span>
                  <div
                    className="chart-bar"
                    style={{ height: Math.max(3, (m.value / max) * 96) }}
                  />
                  <span>{m.label}</span>
                </div>
              ))}
            </div>
            <div className="chart-legend">
              <span>Total no período</span>
              <strong>
                {months.reduce((n, m) => n + m.value, 0)} embarques de pacientes
              </strong>
            </div>
            {[
              [
                proof.length,
                "Comprovações pendentes",
                "Embarques sem declaração conciliada",
                "file",
              ],
              [
                unallocated.length,
                "Agendamentos sem viagem",
                "A partir de hoje",
                "calendar",
              ],
            ].map(([count, title, text, icon]) => (
              <div className="pending-item" key={title}>
                <span className="pending-icon">
                  <Icon name={icon} />
                </span>
                <div>
                  <strong>{title}</strong>
                  <small>{text}</small>
                </div>
                <span className="number">{count}</span>
              </div>
            ))}
          </div>
        </section>
      </div>
      <section className="card">
        <div className="card-head">
          <div>
            <h2>Últimas solicitações</h2>
            <p>Acompanhe a situação dos processos</p>
          </div>
          <a href="#requests" className="link-btn">
            Ver solicitações <Icon name="arrow" />
          </a>
        </div>
        <RequestTable rows={S.requests.slice(0, 5)} />
      </section>
    </>
  );
}
export function Patients() {
  const { S, can, matches } = useApp(),
    rows = S.patients.filter((p) =>
      matches(p.name + " " + p.cpf + " " + p.boarding),
    );
  return (
    <>
      <Header
        title="Pacientes"
        subtitle="Um cadastro, todo o histórico de cuidado."
      >
        {can("regulacao") && (
          <Button act="patient-new" variant="primary" icon="plus">
            Cadastrar paciente
          </Button>
        )}
      </Header>
      <section className="card">
        <Toolbar placeholder="Buscar paciente, CPF ou ponto de embarque…" />
        <Table
          headers={[
            "Paciente",
            "Contato",
            "Acompanhante",
            "Acessibilidade",
            "",
          ]}
          rows={rows.map((p) => [
            <Person patient={p} />,
            p.phone || "Não informado",
            p.companion || "Sem acompanhante",
            <Badge>{p.accessible ? "Veículo acessível" : "Padrão"}</Badge>,
            <Button act="patient-detail" id={p.id} variant="small" icon="arrow">
              Histórico
            </Button>,
          ])}
        />
        <div className="card-foot">
          {rows.length} pacientes · cadastros demonstrativos
        </div>
      </section>
    </>
  );
}
export function Requests() {
  const { S, can, matches, find } = useApp();
  return (
    <>
      <Header
        title="Solicitações"
        subtitle="Analise documentos e autorize TFD ou transporte sanitário."
      >
        {can("regulacao") && (
          <Button act="request-new" variant="primary" icon="plus">
            Nova solicitação
          </Button>
        )}
      </Header>
      <section className="card">
        <Toolbar placeholder="Buscar paciente, especialidade ou situação…" />
        <RequestTable
          rows={S.requests.filter((r) =>
            matches(
              find("patients", r.patient_id)?.name +
                " " +
                r.specialty +
                " " +
                r.status,
            ),
          )}
        />
      </section>
    </>
  );
}
export function Calendar() {
  const { S, month, can, requestFor, patientFor, handle, busy } = useApp(),
    [y, m] = month.split("-").map(Number),
    first = new Date(y, m - 1, 1),
    offset = (first.getDay() + 6) % 7,
    days = new Date(y, m, 0).getDate(),
    cells = Math.ceil((offset + days) / 7) * 7;
  return (
    <>
      <Header
        title="Calendário de tratamento"
        subtitle="Recorrências e datas avulsas, com continuidade entre competências."
      >
        {can("regulacao") && (
          <Button act="schedule-new" variant="primary" icon="plus">
            Agendar tratamento
          </Button>
        )}
      </Header>
      <section className="card">
        <div className="toolbar">
          <MonthInput />
          <span className="muted" style={{ marginLeft: "auto", fontSize: 12 }}>
            {S.occurrences.filter((o) => o.date.startsWith(month)).length}{" "}
            agendamentos no mês
          </span>
        </div>
        <div className="table-wrap">
          <div className="calendar">
            {["SEG", "TER", "QUA", "QUI", "SEX", "SÁB", "DOM"].map((d) => (
              <div key={d} className="cal-heading">
                {d}
              </div>
            ))}
            {Array.from({ length: cells }, (_, i) => {
              const n = i - offset + 1;
              if (n < 1 || n > days)
                return <div key={i} className="cal-day out" />;
              const date = `${month}-${String(n).padStart(2, "0")}`;
              return (
                <div
                  key={i}
                  className={`cal-day ${date === S.today ? "today" : ""}`}
                >
                  <span className="cal-number">{n}</span>
                  {S.occurrences
                    .filter((o) => o.date === date)
                    .map((o) => (
                      <button
                        key={o.id}
                        disabled={busy}
                        className={`cal-event ${requestFor(o)?.kind === "Transporte sanitário" ? "blue" : ""}`}
                        data-act="occurrence-detail"
                        data-id={o.id}
                        onClick={() => handle("occurrence-detail", o.id)}
                        title={patientFor(o)?.name}
                      >
                        {o.trip_id ? "●" : "○"} {cleanName(patientFor(o)?.name)}
                      </button>
                    ))}
                </div>
              );
            })}
          </div>
        </div>
        <div className="legend">
          <span>● Alocado em viagem</span>
          <span>○ Aguardando alocação</span>
          <span>Verde: TFD · Azul: transporte sanitário</span>
        </div>
      </section>
    </>
  );
}
export function Trips() {
  const {
      S,
      can,
      matches,
      find,
      seats,
      requestFor,
      tripFilter,
      setTripFilter,
    } = useApp(),
    rows = S.trips.filter(
      (t) =>
        (!tripFilter || t.date === tripFilter) &&
        matches(t.destination + " " + find("drivers", t.driver_id)?.name),
    );
  return (
    <>
      <Header
        title={
          S.user.role === "motorista"
            ? "Minhas viagens"
            : "Planejamento de viagens"
        }
        subtitle="Organize rotas, confirme passageiros e acompanhe a execução."
      >
        {can("transporte") && (
          <Button act="trip-new" variant="primary" icon="plus">
            Planejar viagem
          </Button>
        )}
      </Header>
      <div className="metrics">
        <Metric
          label="Viagens cadastradas"
          value={S.trips.length}
          foot="Histórico e planejamento"
          icon="bus"
        />
        <Metric
          label="Lugares reservados"
          value={S.occurrences
            .filter((o) => o.trip_id)
            .reduce((n, o) => n + 1 + (requestFor(o)?.companion || 0), 0)}
          foot="Inclui acompanhantes autorizados"
          icon="users"
        />
        <Metric
          label="Quilômetros realizados"
          value={S.trips.reduce((n, t) => n + t.km, 0).toLocaleString("pt-BR")}
          foot="Registrados no encerramento"
          icon="pin"
        />
        <Metric
          label="Viagens encerradas"
          value={S.trips.filter((t) => t.status === "Encerrada").length}
          foot="Com execução registrada"
          icon="check"
        />
      </div>
      <section className="card">
        <Toolbar placeholder="Buscar destino ou motorista…">
          <label className="check">
            Data{" "}
            <input
              id="trip-date"
              type="date"
              value={tripFilter}
              onChange={(e) => setTripFilter(e.target.value)}
            />
          </label>
          {tripFilter && (
            <Button variant="small" onClick={() => setTripFilter("")}>
              Limpar data
            </Button>
          )}
        </Toolbar>
        <Table
          headers={[
            "Viagem / destino",
            "Saída e retorno",
            "Veículo / motorista",
            "Ocupação",
            "Situação",
            "",
          ]}
          rows={rows.map((t) => [
            <>
              {t.destination}
              <Sub>
                #V{String(t.id).padStart(3, "0")} · {dateFmt(t.date)}
              </Sub>
            </>,
            `${t.departure} → ${t.arrival}`,
            <>
              {find("vehicles", t.vehicle_id)?.name}
              <Sub>{cleanName(find("drivers", t.driver_id)?.name)}</Sub>
            </>,
            `${seats(t)} / ${find("vehicles", t.vehicle_id)?.capacity}`,
            <Badge>{t.status}</Badge>,
            <Button act="trip-detail" id={t.id} variant="small" icon="arrow">
              Operação
            </Button>,
          ])}
        />
      </section>
    </>
  );
}
export function Review() {
  const { S, month, matches, requestFor, handle, busy } = useApp(),
    occs = S.occurrences.filter((o) => o.date.startsWith(month)),
    dates = [...new Set(occs.map((o) => o.date))].sort(),
    patients = S.patients.filter(
      (p) =>
        occs.some((o) => requestFor(o)?.patient_id === p.id) && matches(p.name),
    );
  return (
    <>
      <Header
        title="Conferência mensal"
        subtitle="Concilie deslocamento, atendimento, permanência e acompanhante."
      />
      <Info>
        Cada data abre os eventos e documentos de origem. A confirmação de
        embarque e a declaração de atendimento são registros separados.
      </Info>
      <section className="card">
        <Toolbar placeholder="Buscar paciente…">
          <MonthInput />
        </Toolbar>
        <Table
          className="review-table"
          headers={[
            "Paciente",
            ...dates.map(shortDate),
            "Acompanhante",
            "Pendências",
          ]}
          rows={patients.map((p) => {
            const list = occs.filter((o) => requestFor(o)?.patient_id === p.id),
              withComp = list.filter((o) => requestFor(o)?.companion);
            return [
              <Person patient={p} />,
              ...dates.map((d) => {
                const records = list.filter((o) => o.date === d);
                return records.length ? (
                  records.map((o) => (
                    <button
                      key={o.id}
                      disabled={busy}
                      className={`review-cell ${o.boarding === "Ausente" ? "absent" : o.attendance ? "" : "pending"}`}
                      data-act="occurrence-detail"
                      data-id={o.id}
                      onClick={() => handle("occurrence-detail", o.id)}
                      title={`Abrir ${cleanName(p.name)} em ${dateFmt(d)}`}
                    >
                      {o.attendance
                        ? "✓"
                        : o.boarding === "Ausente"
                          ? "×"
                          : "•"}
                    </button>
                  ))
                ) : (
                  <span className="muted">—</span>
                );
              }),
              withComp.length
                ? `${withComp.filter((o) => o.companion_proof).length}/${withComp.length} comprovados`
                : "—",
              <Badge>
                {list.every(
                  (o) =>
                    o.attendance &&
                    (!requestFor(o)?.companion || o.companion_proof),
                )
                  ? "Comprovado"
                  : "Pendente"}
              </Badge>,
            ];
          })}
        />
        <div className="legend">
          <span>✓ Atendimento comprovado</span>
          <span>• Aguardando etapa ou documento</span>
          <span>× Ausência registrada</span>
          <span>— Sem agendamento</span>
        </div>
      </section>
    </>
  );
}
export function Finance() {
  const { S, month, can, find, patientFor, matches } = useApp(),
    benefits = S.benefits.filter((b) =>
      find("occurrences", b.occurrence_id)?.date.startsWith(month),
    ),
    total = (status) =>
      benefits
        .filter((b) => !status || b.status === status)
        .reduce((n, b) => n + b.amount_cents, 0),
    rule = S.rules[0];
  return (
    <>
      <Header
        title="Ajudas de custo"
        subtitle="Acompanhe o cálculo, a conferência e o registro de pagamento."
      >
        {can("financeiro") && (
          <Button act="benefit-calculate" variant="primary" icon="plus">
            Calcular competência
          </Button>
        )}
        <a className="btn" href="/api/export">
          <Icon name="down" /> Exportar folha
        </a>
      </Header>
      <Info amber>
        Valores exclusivamente ilustrativos. O cálculo usa a regra demonstrativa
        vigente e não representa concessão nem pagamento real. Transporte
        sanitário não gera benefício de TFD.
      </Info>
      <div className="metrics">
        <Metric
          label="Total da competência"
          value={money(total())}
          foot="Benefícios gerados · sem custo das viagens"
          icon="wallet"
        />
        <Metric
          label="Em conferência"
          value={money(total("Calculado") + total("Aprovado"))}
          foot="Calculados e aprovados"
          icon="clipboard"
        />
        <Metric
          label="Na contabilidade"
          value={money(total("Contabilidade"))}
          foot="Aguardando registro do pagamento"
          icon="file"
        />
        <Metric
          label="Pagamento registrado"
          value={money(total("Pago"))}
          foot="Baixas demonstrativas"
          icon="check"
        />
      </div>
      <section className="card">
        <Toolbar placeholder="Buscar paciente ou situação…">
          <MonthInput />
        </Toolbar>
        <Table
          headers={[
            "Paciente / atendimento",
            "Beneficiário",
            "Valor",
            "Situação",
            "Referência",
            "",
          ]}
          rows={benefits
            .filter((b) =>
              matches(
                patientFor(find("occurrences", b.occurrence_id))?.name +
                  " " +
                  b.status,
              ),
            )
            .map((b) => [
              <>
                {cleanName(
                  patientFor(find("occurrences", b.occurrence_id))?.name,
                )}
                <Sub>
                  {dateFmt(find("occurrences", b.occurrence_id)?.date)} · regra
                  #{b.rule_id}
                </Sub>
              </>,
              b.beneficiary,
              money(b.amount_cents),
              <Badge>{b.status}</Badge>,
              b.accounting_ref || "—",
              <>
                {can("financeiro") && b.status !== "Pago" && (
                  <Button act="benefit-advance" id={b.id} variant="small">
                    {
                      {
                        Calculado: "Aprovar",
                        Aprovado: "Encaminhar",
                        Contabilidade: "Registrar pagamento",
                      }[b.status]
                    }
                  </Button>
                )}{" "}
                <Button
                  act="occurrence-detail"
                  id={b.occurrence_id}
                  variant="small"
                  icon="eye"
                >
                  Origem
                </Button>
              </>,
            ])}
        />
      </section>
      <section className="card">
        <div className="card-head">
          <div>
            <h2>Regra demonstrativa vigente</h2>
            <p>Novas versões preservam os valores já calculados.</p>
          </div>
          {can() && (
            <Button act="rule-new" variant="small" icon="plus">
              Nova versão
            </Button>
          )}
        </div>
        <div className="card-body">
          {rule && (
            <div className="detail-grid">
              <Detail label="Identificação">{rule.label}</Detail>
              <Detail label="Valores por ocorrência">
                {money(rule.patient_cents)} paciente ·{" "}
                {money(rule.companion_cents)} acompanhante
              </Detail>
            </div>
          )}
        </div>
      </section>
    </>
  );
}
export function Fleet() {
  const { S, can } = useApp();
  return (
    <>
      <Header
        title="Frota e referências"
        subtitle="Mantenha os recursos usados no planejamento e na regulação."
      />
      <div className="columns">
        <section className="card">
          <div className="card-head">
            <h2>Veículos</h2>
            {can("transporte") && (
              <Button act="vehicle-new" variant="small" icon="plus">
                Adicionar
              </Button>
            )}
          </div>
          <Table
            headers={["Veículo", "Lugares", "Acessível"]}
            rows={S.vehicles.map((v) => [
              <>
                {v.name}
                <Sub>{v.plate}</Sub>
              </>,
              v.capacity,
              v.accessible ? "Sim" : "Não",
            ])}
          />
        </section>
        <section className="card">
          <div className="card-head">
            <h2>Motoristas</h2>
            {can("transporte") && (
              <Button act="driver-new" variant="small" icon="plus">
                Adicionar
              </Button>
            )}
          </div>
          <Table
            headers={["Motorista", "Validade CNH"]}
            rows={S.drivers.map((d) => [
              cleanName(d.name),
              <>
                {dateFmt(d.valid_until)}{" "}
                {d.valid_until < S.today && <Badge>Vencida</Badge>}
              </>,
            ])}
          />
        </section>
      </div>
      <section className="card">
        <div className="card-head">
          <div>
            <h2>Unidades de referência</h2>
            <p>
              CNES demonstrativos cadastrados manualmente · sem consulta externa
            </p>
          </div>
          {can("regulacao") && (
            <Button act="facility-new" variant="small" icon="plus">
              Cadastrar unidade
            </Button>
          )}
        </div>
        <Table
          headers={["Unidade", "CNES", "Município"]}
          rows={S.facilities.map((f) => [f.name, f.cnes, f.city])}
        />
      </section>
    </>
  );
}
export function Audit() {
  const { S, matches } = useApp();
  return (
    <>
      <Header
        title="Trilha de auditoria"
        subtitle="Consulte autoria, horário e alterações dos eventos registrados."
      />
      <section className="card">
        <Toolbar placeholder="Buscar usuário, ação ou entidade…" />
        <Table
          headers={["Quando", "Responsável", "Ação", "Registro", ""]}
          rows={S.audit
            .filter((a) => matches(a.actor + " " + a.action + " " + a.entity))
            .map((a) => [
              timeFmt(a.created_at),
              a.actor,
              a.action,
              `${a.entity} ${a.entity_id ? "#" + a.entity_id : ""}`,
              <Button act="audit-detail" id={a.id} variant="small" icon="eye">
                Detalhes
              </Button>,
            ])}
        />
        <div className="card-foot">
          Últimos 300 eventos · o banco preserva o histórico completo.
        </div>
      </section>
    </>
  );
}
export function Help() {
  return (
    <>
      <Header
        title="Entrega acadêmica"
        subtitle="Sistema funcional, protótipo navegável e documentação do projeto."
      />
      <div className="help-grid">
        <section className="card help-card">
          <Icon name="file" />
          <h2>Documentação Macaparana</h2>
          <p>
            Problema, requisitos, arquitetura, dados, casos de uso, testes e
            limitações.
          </p>
          <a
            className="btn"
            href="/docs/Documentacao-Macaparana.pdf"
            target="_blank"
            rel="noreferrer"
          >
            Abrir documento <Icon name="arrow" />
          </a>
        </section>
      </div>
      <section className="card">
        <div className="card-head">
          <h2>Uma demonstração em seis etapas</h2>
        </div>
        <div className="card-body steps">
          {[
            [
              "Cadastre e solicite",
              "Cadastre um paciente e abra uma solicitação TFD ou transporte sanitário.",
            ],
            [
              "Anexe e autorize",
              "Anexe um laudo fictício e registre a decisão da regulação.",
            ],
            [
              "Agende e planeje",
              "Gere datas avulsas ou recorrentes e aloque os pacientes nas viagens.",
            ],
            [
              "Confirme e registre o embarque",
              "A confirmação assistida alimenta a lista operacional do motorista.",
            ],
            [
              "Comprove e confira",
              "Anexe declarações separadas, registre a permanência e confira o mês.",
            ],
            [
              "Calcule e acompanhe",
              "Para TFD, calcule valores demonstrativos e percorra o fluxo até o pagamento.",
            ],
          ].map(([title, text]) => (
            <div className="step" key={title}>
              <div>
                <strong>{title}</strong>
                <p>{text}</p>
              </div>
            </div>
          ))}
        </div>
      </section>
      <Info>
        Frontend em React e backend em Python. Integrações com CNES, e-SUS APS,
        WhatsApp, mapas e contabilidade não estão conectadas. Esta versão local
        utiliza dados fictícios e regras acadêmicas simplificadas.
      </Info>
    </>
  );
}
function Delivery() {
  return <Help />;
}
export const pages = {
  segments: Segments,
  production: Production,
  pilot: Pilot,
  support: Support,
  dashboard: Dashboard,
  patients: Patients,
  requests: Requests,
  calendar: Calendar,
  trips: Trips,
  review: Review,
  finance: Finance,
  fleet: Fleet,
  audit: Audit,
  help: Delivery,
};
