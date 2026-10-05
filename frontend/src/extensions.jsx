import React, { useState } from "react";
import { useApp, money, dateFmt } from "./context";
import { Header, Table, Info, Button, MonthInput } from "./ui";

function Form({ action, children, label = "Salvar", fixed = {} }) {
  const { run, busy } = useApp();
  const [message, setMessage] = useState("");
  return (
    <form
      className="extension-form"
      onSubmit={async (e) => {
        e.preventDefault();
        const form = e.currentTarget;
        try {
          const data = { ...Object.fromEntries(new FormData(form)), ...fixed };
          const result = await run(action, data);
          setMessage(result.message);
        } catch (error) {
          setMessage(error.message);
        }
      }}
    >
      <fieldset disabled={busy}>
        <div className="form-grid">{children}</div>
        <button className="btn primary" type="submit">
          {label}
        </button>
        <p role="status">{message}</p>
      </fieldset>
    </form>
  );
}
function Input({ label, name, type = "text", value = "", ...rest }) {
  return (
    <label className="field">
      {label}
      <input name={name} type={type} defaultValue={value} required {...rest} />
    </label>
  );
}
function Choice({ label, name, items }) {
  return (
    <label className="field">
      {label}
      <select name={name} required>
        {items.map(([id, text]) => (
          <option key={id} value={id}>
            {text}
          </option>
        ))}
      </select>
    </label>
  );
}
function Memo({ label, name, value = "" }) {
  return (
    <label className="field">
      {label}
      <textarea name={name} defaultValue={value} required rows={3} />
    </label>
  );
}

export function Segments() {
  const { S, find, patientFor, requestFor, can } = useApp();
  const [selected, setSelected] = useState("");
  const trip = S.trips.find((t) => t.id === Number(selected)) || S.trips[0];
  if (!trip)
    return (
      <>
        <Header title="Rotas e trechos" />
        <Info>Cadastre uma viagem para planejar os trechos.</Info>
      </>
    );
  const stored = S.route_stops.filter((s) => s.trip_id === trip.id);
  const stops = stored.length
    ? stored
    : [
        { position: 0, name: "Origem" },
        { position: 1, name: "Destino / retorno" },
      ];
  const passengers = S.occurrences.filter((o) => o.trip_id === trip.id);
  const vehicle = find("vehicles", trip.vehicle_id);
  return (
    <>
      <Header
        title="Rotas e trechos"
        subtitle="Capacidade por segmento da rota, com acompanhante e acessibilidade."
      />
      <label className="field">
        Viagem
        <select value={trip.id} onChange={(e) => setSelected(e.target.value)}>
          {S.trips.map((t) => (
            <option key={t.id} value={t.id}>
              #{t.id} · {dateFmt(t.date)} · {t.destination}
            </option>
          ))}
        </select>
      </label>
      <section className="card">
        <h2>Ocupação por trecho · {vehicle?.plate}</h2>
        <Table
          headers={["Trecho", "Lugares ocupados", "Capacidade"]}
          rows={stops
            .slice(0, -1)
            .map((s, i) => [
              `${s.name} → ${stops[i + 1].name}`,
              passengers
                .filter((o) => o.segment_start <= i && i < o.segment_end)
                .reduce((n, o) => n + 1 + (requestFor(o)?.companion || 0), 0),
              vehicle?.capacity,
            ])}
        />
      </section>
      <section className="card">
        <h2>Lista por trecho</h2>
        <Table
          headers={[
            "Paciente",
            "Embarque → desembarque",
            "Confirmação",
            "Canal",
            "Origem",
          ]}
          rows={passengers.map((o) => [
            patientFor(o)?.name,
            `${stops[o.segment_start]?.name} → ${stops[o.segment_end]?.name}`,
            o.confirmation,
            o.confirmation_channel,
            <Button act="trip-detail" id={trip.id}>
              Viagem #{trip.id}
            </Button>,
          ])}
        />
      </section>
      {can("transporte") && trip.status === "Planejada" && (
        <section className="card">
          <h2>Definir paradas</h2>
          <Info>
            Altere antes de alocar passageiros. Cada linha é uma parada; inclua
            o retorno se necessário. Alterações exigem justificativa e ficam na
            auditoria.
          </Info>
          <Form
            key={trip.id}
            action="route.save"
            fixed={{ trip_id: trip.id }}
            label="Salvar rota"
          >
            <Memo
              label="Paradas em ordem"
              name="stops"
              value={stops.map((s) => s.name).join("\n")}
            />
            <Input label="Justificativa" name="reason" />
          </Form>
        </section>
      )}
      {can("transporte") && trip.status === "Planejada" && (
        <section className="card">
          <h2>Alocar por trecho</h2>
          <Form
            action="trip.allocate"
            fixed={{ trip_id: trip.id }}
            label="Alocar no trecho"
          >
            <Choice
              name="occurrence_id"
              label="Agendamento"
              items={S.occurrences
                .filter((o) => o.date === trip.date && !o.trip_id)
                .map((o) => [o.id, patientFor(o)?.name])}
            />
            <Choice
              name="segment_start"
              label="Parada de embarque"
              items={stops.slice(0, -1).map((s) => [s.position, s.name])}
            />
            <Choice
              name="segment_end"
              label="Parada de desembarque"
              items={stops.slice(1).map((s) => [s.position, s.name])}
            />
          </Form>
        </section>
      )}
      {can("transporte", "motorista") && trip.status === "Planejada" && (
        <section className="card">
          <h2>Confirmação assistida</h2>
          <Form action="occurrence.confirm" label="Registrar confirmação">
            <Choice
              name="id"
              label="Passageiro"
              items={passengers
                .filter((o) => o.boarding === "Pendente")
                .map((o) => [o.id, patientFor(o)?.name])}
            />
            <Choice
              name="status"
              label="Resposta"
              items={[
                ["Confirmado", "Confirmado"],
                ["Recusado", "Recusado"],
              ]}
            />
            <Choice
              name="channel"
              label="Canal"
              items={[
                "Telefone",
                "Presencial",
                "Agente de saúde",
                "WhatsApp autorizado",
              ].map((x) => [x, x])}
            />
            <Memo
              name="note"
              label="Registro do contato (sem dados clínicos)"
            />
          </Form>
          <Info>
            A resposta é registrada pela equipe. Nenhuma mensagem é enviada
            automaticamente.
          </Info>
        </section>
      )}
    </>
  );
}

export function Production() {
  const { S, month, patientFor, requestFor, facilityFor, can } = useApp();
  const occurrences = S.occurrences.filter((o) => o.date.startsWith(month));
  return (
    <>
      <Header
        title="Preparação da produção"
        subtitle="Conferência interna por competência para a equipe de faturamento."
      />
      <MonthInput />
      <Info>
        Arquivo de preparação interna. Código, elegibilidade, catálogo e leiaute
        precisam de validação pelo faturamento antes de qualquer lançamento em
        sistema oficial. Não há transmissão automática.
      </Info>
      <section className="card">
        <Table
          headers={[
            "Paciente / data",
            "Referência",
            "Pendência / etapa",
            "Documentos e origem",
          ]}
          rows={occurrences.map((o) => {
            const r = requestFor(o),
              p = S.production.find((p) => p.occurrence_id === o.id);
            return [
              `${patientFor(o)?.name} · ${dateFmt(o.date)}`,
              `${facilityFor(r)?.name} · CNES ${facilityFor(r)?.cnes}`,
              !o.trip_id
                ? "Transporte: alocar viagem"
                : o.boarding !== "Embarcou"
                  ? `Transporte: ${o.boarding}`
                  : !o.attendance
                    ? "Regulação: comprovar atendimento"
                    : p?.status || "Faturamento: preparar",
              <Button act="occurrence-detail" id={o.id}>
                Ocorrência #{o.id}
              </Button>,
            ];
          })}
        />
      </section>
      {can("faturamento") && (
        <section className="card">
          <h2>Preparar ou corrigir registro</h2>
          <Form action="production.save">
            <Choice
              name="occurrence_id"
              label="Atendimento comprovado"
              items={occurrences
                .filter((o) => o.attendance && o.boarding === "Embarcou")
                .map((o) => [o.id, `${patientFor(o)?.name} · ${o.date}`])}
            />
            <Input
              name="procedure_code"
              label="Procedimento informado (10 dígitos)"
              pattern="[0-9]{10}"
            />
            <Input
              name="quantity"
              label="Quantidade"
              type="number"
              min="1"
              max="999"
              value="1"
            />
            <Input
              name="destination"
              label="Sistema / setor destinatário para revisão"
            />
            <Memo
              name="note"
              label="Validações e pendências para revisão oficial"
            />
          </Form>
        </section>
      )}
      <section className="card">
        <h2>Registros preparados</h2>
        <a className="btn" href={`/api/production/export?month=${month}`}>
          Exportar preparação CSV
        </a>
        <Table
          headers={[
            "ID",
            "Ocorrência",
            "Procedimento",
            "Quantidade",
            "Etapa",
            "Protocolo",
          ]}
          rows={S.production
            .filter((p) => occurrences.some((o) => o.id === p.occurrence_id))
            .map((p) => [
              p.id,
              <Button act="occurrence-detail" id={p.occurrence_id}>
                #{p.occurrence_id}
              </Button>,
              p.procedure_code,
              p.quantity,
              p.status,
              p.protocol || "Pendente",
            ])}
        />
        {can("faturamento") && (
          <Form
            action="production.submit"
            label="Registrar encaminhamento para revisão"
          >
            <Choice
              name="id"
              label="Produção preparada"
              items={S.production
                .filter(
                  (p) =>
                    p.status === "Preparada" &&
                    occurrences.some((o) => o.id === p.occurrence_id),
                )
                .map((p) => [p.id, `#${p.id} · ocorrência ${p.occurrence_id}`])}
            />
            <Input
              name="protocol"
              label="Protocolo interno de encaminhamento"
            />
          </Form>
        )}
      </section>
    </>
  );
}

export function Pilot() {
  const { S, month, can } = useApp();
  const trips = S.trips.filter(
    (t) => t.date.startsWith(month) && t.status === "Encerrada",
  );
  const occurrences = S.occurrences.filter((o) => o.date.startsWith(month));
  const boarded = occurrences.filter((o) => o.boarding === "Embarcou").length;
  const km = trips.reduce((n, t) => n + t.km, 0),
    liters = trips.reduce((n, t) => n + t.liters, 0),
    cost = trips.reduce((n, t) => n + t.cost_cents, 0);
  const closedIds = new Set(trips.map((t) => t.id));
  const closedPassengers = occurrences.filter(
    (o) => closedIds.has(o.trip_id) && o.boarding === "Embarcou",
  ).length;
  return (
    <>
      <Header
        title="Indicadores e piloto"
        subtitle="Métricas observadas e comparação documentada com a linha de base."
      />
      <MonthInput />
      <section className="card">
        <Table
          headers={["Indicador da competência", "Valor", "Definição"]}
          rows={[
            [
              "Custo das viagens encerradas",
              money(cost),
              "Soma do custo registrado; não inclui benefícios",
            ],
            ["Quilômetros reais", km, "Viagens encerradas"],
            [
              "Consumo (km/l)",
              liters ? (km / liters).toFixed(2) : "Sem consumo registrado",
              "Quilômetros / litros nas viagens encerradas",
            ],
            [
              "Custo por embarque",
              closedPassengers
                ? money(cost / closedPassengers)
                : "Sem embarques",
              "Custo das viagens encerradas / embarques de pacientes nessas viagens",
            ],
            ["Embarques", boarded, "Ocorrências marcadas Embarcou"],
            [
              "Ausências",
              occurrences.filter((o) => o.boarding === "Ausente").length,
              "Ocorrências marcadas Ausente",
            ],
            [
              "Comprovações pendentes",
              occurrences.filter(
                (o) => o.boarding === "Embarcou" && !o.attendance,
              ).length,
              "Embarcou sem comprovação de atendimento",
            ],
          ]}
        />
        <p>
          <a href="#trips">Consultar viagens de origem</a> ·{" "}
          <a href="#review">Consultar atendimentos e documentos</a> ·{" "}
          <a href="#finance">Consultar benefícios</a>
        </p>
      </section>
      <section className="card">
        <h2>Medições registradas</h2>
        <Info>
          Uma simulação acadêmica não comprova resultados em rotina municipal.
          Cadastre a fonte, o período e o responsável por cada medição.
        </Info>
        <Table
          headers={[
            "Indicador",
            "Origem",
            "Base",
            "Medido",
            "Variação",
            "Fonte / responsável",
          ]}
          rows={S.pilot_measurements.map((m) => [
            `${m.indicator} (${m.unit})`,
            `${m.scenario} · ${m.start_date} a ${m.end_date}`,
            m.baseline,
            m.measured,
            m.baseline
              ? `${(((m.measured - m.baseline) / m.baseline) * 100).toFixed(1)}%`
              : "Base zero; sem variação percentual",
            `${m.source} · ${m.responsible}`,
          ])}
        />
      </section>
      {can("auditor") && (
        <section className="card">
          <h2>Registrar medição do piloto</h2>
          <Form action="pilot.create">
            <Input name="indicator" label="Indicador" />
            <Input name="unit" label="Unidade (minutos, reais, %, etc.)" />
            <Input
              name="baseline"
              label="Linha de base"
              type="number"
              min="0"
              step="any"
            />
            <Input
              name="measured"
              label="Resultado medido"
              type="number"
              min="0"
              step="any"
            />
            <Input name="start_date" label="Início" type="date" />
            <Input name="end_date" label="Fim" type="date" />
            <Choice
              name="scenario"
              label="Origem"
              items={["Simulação acadêmica", "Rotina municipal"].map((x) => [
                x,
                x,
              ])}
            />
            <Input name="responsible" label="Responsável pela medição" />
            <Memo name="source" label="Fonte, método e evidência verificável" />
          </Form>
        </section>
      )}
    </>
  );
}

export function Support() {
  const { S, can } = useApp();
  return (
    <>
      <Header
        title="Capacitação e suporte"
        subtitle="Registro de treinamento, dúvidas e resolução de chamados."
      />
      <section className="card">
        <p>
          <a href="/docs/operacao.html" target="_blank" rel="noreferrer">
            Manual de operação, capacitação e piloto
          </a>
        </p>
        <Table
          headers={["Tipo", "Título", "Responsável", "Situação", "Registro"]}
          rows={S.service_records.map((r) => [
            r.kind,
            r.title,
            r.owner,
            r.status,
            r.notes,
          ])}
        />
      </section>
      <section className="card">
        <h2>Abrir registro</h2>
        <Form action="service.create">
          <Choice
            name="kind"
            label="Tipo"
            items={[
              ["Suporte", "Suporte"],
              ["Capacitação", "Capacitação"],
            ]}
          />
          <Input name="title" label="Título" />
          <Input name="owner" label="Responsável / equipe" />
          <Memo
            name="notes"
            label="Descrição, participantes ou passos para reprodução (sem dados pessoais)"
          />
        </Form>
      </section>
      {can() && (
        <section className="card">
          <h2>Concluir registro</h2>
          <Form action="service.close">
            <Choice
              name="id"
              label="Registro aberto"
              items={S.service_records
                .filter((r) => r.status === "Aberto")
                .map((r) => [r.id, r.title])}
            />
            <Memo name="notes" label="Solução ou evidência da capacitação" />
          </Form>
        </section>
      )}
    </>
  );
}
