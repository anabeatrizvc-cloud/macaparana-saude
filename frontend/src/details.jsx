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
  const { S, find, requestFor } = useApp();
  const patient = find("patients", id);
  return (
    <>
      <div className="detail-grid">
        <Detail label="Contato">{patient.phone || "—"}</Detail>
        <Detail label="Nascimento">{dateFmt(patient.birth)}</Detail>
        <Detail label="Endereço">{patient.address || "—"}</Detail>
        <Detail label="Embarque">{patient.boarding}</Detail>
        <Detail label="CPF">
          {patient.cpf
            ? "***.***.***-" + patient.cpf.slice(-2)
            : "Não informado"}
        </Detail>
        <Detail label="Acompanhante">
          {patient.companion || "Sem acompanhante"}
        </Detail>
        <Detail label="Acessibilidade">
          {patient.accessible ? "Veículo acessível" : "Padrão"}
        </Detail>
        <Detail label="Dados bancários">
          {patient.bank || "Não disponíveis para este perfil"}
        </Detail>
      </div>
      <h3 className="section-title">Solicitações e tratamentos</h3>
      <RequestTable
        rows={S.requests.filter((request) => request.patient_id === patient.id)}
      />
      <h3 className="section-title">Eventos de atendimento</h3>
      <Table
        headers={["Data", "Embarque", "Atendimento", ""]}
        rows={S.occurrences
          .filter(
            (occurrence) => requestFor(occurrence)?.patient_id === patient.id,
          )
          .sort((first, second) => second.date.localeCompare(first.date))
          .map((occurrence) => [
            dateFmt(occurrence.date),
            <Badge>{occurrence.boarding}</Badge>,
            <Badge>{occurrence.attendance ? "Comprovado" : "Pendente"}</Badge>,
            <Button act="occurrence-detail" id={occurrence.id} variant="small">
              Abrir
            </Button>,
          ])}
      />
    </>
  );
}
export function RequestDetail({ id }) {
  const { S, find, can, facilityFor } = useApp();
  const request = find("requests", id);
  const patient = find("patients", request.patient_id);
  const facility = facilityFor(request);
  return (
    <>
      <Person patient={patient} />
      <div className="detail-grid" style={{ marginTop: 22 }}>
        <Detail label="Modalidade">
          <Badge>{request.kind}</Badge>
        </Detail>
        <Detail label="Situação">
          <Badge>{request.status}</Badge>
        </Detail>
        <Detail label="Referência">
          {facility?.name}
          <br />
          <small>CNES {facility?.cnes}</small>
        </Detail>
        <Detail label="Especialidade">{request.specialty}</Detail>
        <Detail label="Validade">
          {dateFmt(request.start_date)} → {dateFmt(request.end_date)}
        </Detail>
        <Detail label="Acompanhante">
          {request.companion ? patient.companion : "Não autorizado"}
        </Detail>
      </div>
      {request.reason && <Info>Última decisão: {request.reason}</Info>}
      <h3 className="section-title">Documentos da solicitação</h3>
      <DocList link="request_id" id={request.id} />
      <Actions>
        {can("regulacao") && (
          <>
            <Button
              act="document-request"
              id={request.id}
              variant="small"
              icon="plus"
            >
              Anexar laudo
            </Button>
            {["Em análise", "Pendente"].includes(request.status) && (
              <Button
                act="request-decide"
                id={request.id}
                variant="primary small"
                icon="check"
              >
                Analisar solicitação
              </Button>
            )}
            {request.status === "Autorizada" && (
              <Button
                act="schedule-new"
                id={request.id}
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
          .filter((occurrence) => occurrence.request_id === request.id)
          .sort((first, second) => first.date.localeCompare(second.date))
          .map((occurrence) => [
            dateFmt(occurrence.date),
            occurrence.trip_id ? "#V" + occurrence.trip_id : "Sem alocação",
            <Badge>{occurrence.attendance ? "Comprovado" : "Pendente"}</Badge>,
            <Button act="occurrence-detail" id={occurrence.id} variant="small">
              Abrir
            </Button>,
          ])}
      />
    </>
  );
}
export function OccurrenceDetail({ id }) {
  const { S, find, requestFor, patientFor, can } = useApp();
  const occurrence = find("occurrences", id);
  const request = requestFor(occurrence);
  const patient = patientFor(occurrence);
  const trip = find("trips", occurrence.trip_id);
  const benefits = S.benefits.filter(
    (benefit) => benefit.occurrence_id === occurrence.id,
  );
  return (
    <>
      <Person patient={patient} />
      <div className="detail-grid" style={{ marginTop: 22 }}>
        <Detail label="Solicitação">
          #{request.id} · <Badge>{request.kind || "Operacional"}</Badge>
        </Detail>
        <Detail label="Viagem">
          {trip
            ? `#V${trip.id} · ${trip.destination} · ${trip.departure}`
            : "Aguardando alocação"}
        </Detail>
        <Detail label="Confirmação">
          <Badge>{occurrence.confirmation}</Badge>
        </Detail>
        <Detail label="Embarque">
          <Badge>{occurrence.boarding}</Badge>
        </Detail>
        <Detail label="Atendimento">
          <Badge>{occurrence.attendance ? "Comprovado" : "Pendente"}</Badge>
        </Detail>
        <Detail label="Acompanhante">
          {request.companion ? (
            <Badge>
              {occurrence.companion_proof ? "Comprovado" : "Pendente"}
            </Badge>
          ) : (
            "Não previsto"
          )}
        </Detail>
        <Detail label="Permanência">
          {occurrence.permanence || "Não registrada"}
        </Detail>
        <Detail label="Rastreabilidade">
          Ocorrência #{occurrence.id} · solicitação #{request.id}
        </Detail>
      </div>
      <h3 className="section-title">Declarações e comprovantes</h3>
      <DocList link="occurrence_id" id={occurrence.id} />
      <Actions>
        {can("regulacao") && (
          <>
            <Button
              act="document-occurrence"
              id={occurrence.id}
              variant="small"
              icon="plus"
            >
              Anexar declaração
            </Button>
            {occurrence.boarding === "Embarcou" && (
              <Button
                act="occurrence-prove"
                id={occurrence.id}
                variant="primary small"
                icon="check"
              >
                Conciliar atendimento
              </Button>
            )}
          </>
        )}
        {trip && (
          <Button act="trip-detail" id={trip.id} variant="small" icon="bus">
            Abrir viagem
          </Button>
        )}
      </Actions>
      {benefits.length > 0 && (
        <>
          <h3 className="section-title">Benefícios vinculados</h3>
          <Table
            headers={["Beneficiário", "Valor", "Situação"]}
            rows={benefits.map((benefit) => [
              benefit.beneficiary,
              money(benefit.amount_cents),
              <Badge>{benefit.status}</Badge>,
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
    useApp();
  const trip = find("trips", id);
  const vehicle = find("vehicles", trip.vehicle_id);
  const driver = find("drivers", trip.driver_id);
  const occurrences = S.occurrences.filter(
    (occurrence) => occurrence.trip_id === trip.id,
  );
  return (
    <>
      <div className="detail-grid">
        <Detail label="Data e horário">
          {dateFmt(trip.date)} · {trip.departure}–{trip.arrival}
        </Detail>
        <Detail label="Situação">
          <Badge>{trip.status}</Badge>
        </Detail>
        <Detail label="Veículo">
          {vehicle.name} · {vehicle.plate}
          {vehicle.accessible ? " · acessível" : ""}
        </Detail>
        <Detail label="Motorista">{cleanName(driver.name)}</Detail>
        <Detail label="Ocupação">
          {seats(trip)} de {vehicle.capacity} lugares
        </Detail>
        <Detail label="Percurso estimado">{trip.estimated_km} km</Detail>
        <div style={{ gridColumn: "1/-1" }}>
          <Detail label="Rota e trechos">{trip.route}</Detail>
        </div>
      </div>
      <Actions>
        {can("transporte") && trip.status === "Planejada" && (
          <Button
            act="trip-allocate"
            id={trip.id}
            variant="primary small"
            icon="plus"
          >
            Alocar paciente
          </Button>
        )}
        {can("transporte", "motorista") && trip.status === "Planejada" && (
          <Button act="trip-close" id={trip.id} variant="small" icon="check">
            Encerrar viagem
          </Button>
        )}
        <Button act="trip-print" id={trip.id} variant="small" icon="file">
          Imprimir lista
        </Button>
      </Actions>
      <h3 className="section-title">
        Lista operacional · {occurrences.length} pacientes
      </h3>
      <Table
        headers={["Passageiro / embarque", "Trecho", "Confirmação", "Operação"]}
        rows={occurrences.map((occurrence) => {
          const patient = patientFor(occurrence);
          const request = requestFor(occurrence);
          const canOperate =
            can("transporte", "motorista") &&
            trip.status === "Planejada" &&
            occurrence.boarding === "Pendente";
          return [
            <>
              {cleanName(patient?.name)}
              {request.companion > 0 && <Sub>+ {patient.companion}</Sub>}
              <Sub>
                {patient?.boarding}
                {patient?.accessible ? " · acessível" : ""}
              </Sub>
            </>,
            <>
              <small>{segmentLabel(occurrence)}</small>
            </>,
            <>
              <Badge>{occurrence.confirmation}</Badge>
              {canOperate && occurrence.confirmation !== "Confirmado" && (
                <div style={{ marginTop: 7 }}>
                  <Button act="confirm" id={occurrence.id} variant="small">
                    Confirmar
                  </Button>
                </div>
              )}
            </>,
            <>
              <Badge>{occurrence.boarding}</Badge>
              {canOperate && (
                <Actions>
                  {occurrence.confirmation === "Confirmado" && (
                    <Button act="board" id={occurrence.id} variant="small">
                      Embarcou
                    </Button>
                  )}
                  <Button act="absent" id={occurrence.id} variant="small">
                    Ausente
                  </Button>
                  {can("transporte") && (
                    <Button
                      act="trip-release"
                      id={occurrence.id}
                      variant="small danger"
                    >
                      Retirar
                    </Button>
                  )}
                </Actions>
              )}
            </>,
          ];
        })}
      />
      {trip.status === "Encerrada" && (
        <>
          <h3 className="section-title">Execução registrada</h3>
          <div className="detail-grid">
            <Detail label="Quilometragem real">{trip.km} km</Detail>
            <Detail label="Combustível">{trip.liters} litros</Detail>
            <Detail label="Custo total informado">
              {money(trip.cost_cents)}
            </Detail>
            <Detail label="Ocorrências">
              {trip.notes || "Sem observações"}
            </Detail>
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
  const { find } = useApp();
  const auditEntry = find("audit", id);
  return (
    <>
      <div className="detail-grid">
        <Detail label="Ação">{auditEntry.action}</Detail>
        <Detail label="Quando">{timeFmt(auditEntry.created_at)}</Detail>
        <Detail label="Responsável">{auditEntry.actor}</Detail>
        <Detail label="Registro">
          {auditEntry.entity} #{auditEntry.entity_id || "—"}
        </Detail>
      </div>
      <h3 className="section-title">Antes</h3>
      <pre className="audit-json">
        {auditEntry.before_json
          ? JSON.stringify(JSON.parse(auditEntry.before_json), null, 2)
          : "Criação ou evento sem estado anterior."}
      </pre>
      <h3 className="section-title">Depois</h3>
      <pre className="audit-json">
        {auditEntry.after_json
          ? JSON.stringify(JSON.parse(auditEntry.after_json), null, 2)
          : "Sem alteração de dados."}
      </pre>
      {auditEntry.reason && <p>Justificativa: {auditEntry.reason}</p>}
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
