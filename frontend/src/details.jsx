import React from "react";
import { useApp, dateFmt, money, timeFmt, cleanName } from "./context";
import {
  Actions,
  Button,
  Person,
  Detail,
  Badge,
  Table,
  DocList,
  Info,
  Sub,
} from "./ui";
import { RequestTable } from "./pages";

export function PatientDetail({ id }) {
  const { S, find, requestFor } = useApp(),
    p = find("patients", id);
  return (
    <>
      <div className="detail-grid">
        <Detail label="Contato">{p.phone || "—"}</Detail>
        <Detail label="Nascimento">{dateFmt(p.birth)}</Detail>
        <Detail label="Endereço">{p.address || "—"}</Detail>
        <Detail label="Embarque">{p.boarding}</Detail>
        <Detail label="CPF">
          {p.cpf ? "***.***.***-" + p.cpf.slice(-2) : "Não informado"}
        </Detail>
        <Detail label="Acompanhante">
          {p.companion || "Sem acompanhante"}
        </Detail>
        <Detail label="Acessibilidade">
          {p.accessible ? "Veículo acessível" : "Padrão"}
        </Detail>
        <Detail label="Dados bancários">
          {p.bank || "Não disponíveis para este perfil"}
        </Detail>
      </div>
      <h3 className="section-title">Solicitações e tratamentos</h3>
      <RequestTable rows={S.requests.filter((r) => r.patient_id === p.id)} />
      <h3 className="section-title">Eventos de atendimento</h3>
      <Table
        headers={["Data", "Embarque", "Atendimento", ""]}
        rows={S.occurrences
          .filter((o) => requestFor(o)?.patient_id === p.id)
          .sort((a, b) => b.date.localeCompare(a.date))
          .map((o) => [
            dateFmt(o.date),
            <Badge>{o.boarding}</Badge>,
            <Badge>{o.attendance ? "Comprovado" : "Pendente"}</Badge>,
            <Button act="occurrence-detail" id={o.id} variant="small">
              Abrir
            </Button>,
          ])}
      />
    </>
  );
}
export function RequestDetail({ id }) {
  const { S, find, can, facilityFor } = useApp(),
    r = find("requests", id),
    p = find("patients", r.patient_id),
    f = facilityFor(r);
  return (
    <>
      <Person patient={p} />
      <div className="detail-grid" style={{ marginTop: 22 }}>
        <Detail label="Modalidade">
          <Badge>{r.kind}</Badge>
        </Detail>
        <Detail label="Situação">
          <Badge>{r.status}</Badge>
        </Detail>
        <Detail label="Referência">
          {f?.name}
          <br />
          <small>CNES {f?.cnes}</small>
        </Detail>
        <Detail label="Especialidade">{r.specialty}</Detail>
        <Detail label="Validade">
          {dateFmt(r.start_date)} → {dateFmt(r.end_date)}
        </Detail>
        <Detail label="Acompanhante">
          {r.companion ? p.companion : "Não autorizado"}
        </Detail>
      </div>
      {r.reason && <Info>Última decisão: {r.reason}</Info>}
      <h3 className="section-title">Documentos da solicitação</h3>
      <DocList link="request_id" id={r.id} />
      <Actions>
        {can("regulacao") && (
          <>
            <Button
              act="document-request"
              id={r.id}
              variant="small"
              icon="plus"
            >
              Anexar laudo
            </Button>
            {["Em análise", "Pendente"].includes(r.status) && (
              <Button
                act="request-decide"
                id={r.id}
                variant="primary small"
                icon="check"
              >
                Analisar solicitação
              </Button>
            )}
            {r.status === "Autorizada" && (
              <Button
                act="schedule-new"
                id={r.id}
                variant="primary small"
                icon="calendar"
              >
                Agendar tratamento
              </Button>
            )}
          </>
        )}
      </Actions>
      <h3 className="section-title">Agendamentos vinculados</h3>
      <Table
        headers={["Data", "Viagem", "Atendimento", ""]}
        rows={S.occurrences
          .filter((o) => o.request_id === r.id)
          .sort((a, b) => a.date.localeCompare(b.date))
          .map((o) => [
            dateFmt(o.date),
            o.trip_id ? "#V" + o.trip_id : "Sem alocação",
            <Badge>{o.attendance ? "Comprovado" : "Pendente"}</Badge>,
            <Button act="occurrence-detail" id={o.id} variant="small">
              Abrir
            </Button>,
          ])}
      />
    </>
  );
}
export function OccurrenceDetail({ id }) {
  const { S, find, requestFor, patientFor, can } = useApp(),
    o = find("occurrences", id),
    r = requestFor(o),
    p = patientFor(o),
    t = find("trips", o.trip_id),
    benefits = S.benefits.filter((b) => b.occurrence_id === o.id);
  return (
    <>
      <Person patient={p} />
      <div className="detail-grid" style={{ marginTop: 22 }}>
        <Detail label="Solicitação">
          #{r.id} · <Badge>{r.kind || "Operacional"}</Badge>
        </Detail>
        <Detail label="Viagem">
          {t
            ? `#V${t.id} · ${t.destination} · ${t.departure}`
            : "Aguardando alocação"}
        </Detail>
        <Detail label="Confirmação">
          <Badge>{o.confirmation}</Badge>
        </Detail>
        <Detail label="Embarque">
          <Badge>{o.boarding}</Badge>
        </Detail>
        <Detail label="Atendimento">
          <Badge>{o.attendance ? "Comprovado" : "Pendente"}</Badge>
        </Detail>
        <Detail label="Acompanhante">
          {r.companion ? (
            <Badge>{o.companion_proof ? "Comprovado" : "Pendente"}</Badge>
          ) : (
            "Não previsto"
          )}
        </Detail>
        <Detail label="Permanência">{o.permanence || "Não registrada"}</Detail>
        <Detail label="Rastreabilidade">
          Ocorrência #{o.id} · solicitação #{r.id}
        </Detail>
      </div>
      <h3 className="section-title">Declarações e comprovantes</h3>
      <DocList link="occurrence_id" id={o.id} />
      <Actions>
        {can("regulacao") && (
          <>
            <Button
              act="document-occurrence"
              id={o.id}
              variant="small"
              icon="plus"
            >
              Anexar declaração
            </Button>
            {o.boarding === "Embarcou" && (
              <Button
                act="occurrence-prove"
                id={o.id}
                variant="primary small"
                icon="check"
              >
                Conciliar atendimento
              </Button>
            )}
          </>
        )}
        {t && (
          <Button act="trip-detail" id={t.id} variant="small" icon="bus">
            Abrir viagem
          </Button>
        )}
      </Actions>
      {benefits.length > 0 && (
        <>
          <h3 className="section-title">Benefícios vinculados</h3>
          <Table
            headers={["Beneficiário", "Valor", "Situação"]}
            rows={benefits.map((b) => [
              b.beneficiary,
              money(b.amount_cents),
              <Badge>{b.status}</Badge>,
            ])}
          />
        </>
      )}
      <Info>
        O embarque não comprova o atendimento. A declaração do acompanhante é
        conferida separadamente. Valores de benefício são demonstrativos.
      </Info>
    </>
  );
}
export function TripDetail({ id }) {
  const { S, find, can, seats, segmentLabel, patientFor, requestFor } =
      useApp(),
    t = find("trips", id),
    v = find("vehicles", t.vehicle_id),
    d = find("drivers", t.driver_id),
    occs = S.occurrences.filter((o) => o.trip_id === t.id);
  return (
    <>
      <div className="detail-grid">
        <Detail label="Data e horário">
          {dateFmt(t.date)} · {t.departure}–{t.arrival}
        </Detail>
        <Detail label="Situação">
          <Badge>{t.status}</Badge>
        </Detail>
        <Detail label="Veículo">
          {v.name} · {v.plate}
          {v.accessible ? " · acessível" : ""}
        </Detail>
        <Detail label="Motorista">{cleanName(d.name)}</Detail>
        <Detail label="Ocupação">
          {seats(t)} de {v.capacity} lugares
        </Detail>
        <Detail label="Percurso estimado">{t.estimated_km} km</Detail>
        <div style={{ gridColumn: "1/-1" }}>
          <Detail label="Rota e trechos">{t.route}</Detail>
        </div>
      </div>
      <Actions>
        {can("transporte") && t.status === "Planejada" && (
          <Button
            act="trip-allocate"
            id={t.id}
            variant="primary small"
            icon="plus"
          >
            Alocar paciente
          </Button>
        )}
        {can("transporte", "motorista") && t.status === "Planejada" && (
          <Button act="trip-close" id={t.id} variant="small" icon="check">
            Encerrar viagem
          </Button>
        )}
        <Button act="trip-print" id={t.id} variant="small" icon="file">
          Imprimir lista
        </Button>
      </Actions>
      <h3 className="section-title">
        Lista operacional · {occs.length} pacientes
      </h3>
      <Table
        headers={["Passageiro / embarque", "Trecho", "Confirmação", "Operação"]}
        rows={occs.map((o) => {
          const p = patientFor(o),
            r = requestFor(o),
            canOperate =
              can("transporte", "motorista") &&
              t.status === "Planejada" &&
              o.boarding === "Pendente";
          return [
            <>
              {cleanName(p?.name)}
              {r.companion > 0 && <Sub>+ {p.companion}</Sub>}
              <Sub>
                {p?.boarding}
                {p?.accessible ? " · acessível" : ""}
              </Sub>
            </>,
            <>
              <small>{segmentLabel(o)}</small>
            </>,
            <>
              <Badge>{o.confirmation}</Badge>
              {canOperate && o.confirmation !== "Confirmado" && (
                <div style={{ marginTop: 7 }}>
                  <Button act="confirm" id={o.id} variant="small">
                    Confirmar
                  </Button>
                </div>
              )}
            </>,
            <>
              <Badge>{o.boarding}</Badge>
              {canOperate && (
                <Actions>
                  {o.confirmation === "Confirmado" && (
                    <Button act="board" id={o.id} variant="small">
                      Embarcou
                    </Button>
                  )}
                  <Button act="absent" id={o.id} variant="small">
                    Ausente
                  </Button>
                  {can("transporte") && (
                    <Button act="trip-release" id={o.id} variant="small danger">
                      Retirar
                    </Button>
                  )}
                </Actions>
              )}
            </>,
          ];
        })}
      />
      {t.status === "Encerrada" && (
        <>
          <h3 className="section-title">Execução registrada</h3>
          <div className="detail-grid">
            <Detail label="Quilometragem real">{t.km} km</Detail>
            <Detail label="Combustível">{t.liters} litros</Detail>
            <Detail label="Custo total informado">{money(t.cost_cents)}</Detail>
            <Detail label="Ocorrências">{t.notes || "Sem observações"}</Detail>
          </div>
        </>
      )}
      <Info>
        Confirmação assistida e lista compartilhada com o motorista. Cada
        alocação reserva lugares entre as paradas escolhidas. A ocupação exibida
        é o pico por trecho.
      </Info>
    </>
  );
}
export function AuditDetail({ id }) {
  const { find } = useApp(),
    a = find("audit", id);
  return (
    <>
      <div className="detail-grid">
        <Detail label="Ação">{a.action}</Detail>
        <Detail label="Quando">{timeFmt(a.created_at)}</Detail>
        <Detail label="Responsável">{a.actor}</Detail>
        <Detail label="Registro">
          {a.entity} #{a.entity_id || "—"}
        </Detail>
      </div>
      <h3 className="section-title">Antes</h3>
      <pre className="audit-json">
        {a.before_json
          ? JSON.stringify(JSON.parse(a.before_json), null, 2)
          : "Criação ou evento sem estado anterior."}
      </pre>
      <h3 className="section-title">Depois</h3>
      <pre className="audit-json">
        {a.after_json
          ? JSON.stringify(JSON.parse(a.after_json), null, 2)
          : "Sem alteração de dados."}
      </pre>
      {a.reason && <p>Justificativa: {a.reason}</p>}
    </>
  );
}
export const detailComponents = {
  "patient-detail": PatientDetail,
  "request-detail": RequestDetail,
  "occurrence-detail": OccurrenceDetail,
  "trip-detail": TripDetail,
  "audit-detail": AuditDetail,
};
