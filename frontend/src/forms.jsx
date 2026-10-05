import React, { useState } from "react";
import { useApp, cleanName, money } from "./context";
import { Field, Select, Check, Info, Badge, Button } from "./ui";

const Hidden = ({ name, value }) => (
  <input type="hidden" name={name} value={value} />
);
const Note = ({ label = "Justificativa", name = "reason" }) => (
  <label className="full">
    {label}
    <textarea name={name} required={name === "reason"} maxLength={1000} />
  </label>
);
export const titles = {
  "patient-new": "Cadastrar paciente",
  "request-new": "Nova solicitação",
  "request-decide": "Análise da solicitação",
  "schedule-new": "Agendar tratamento",
  "document-request": "Anexar laudo",
  "document-occurrence": "Anexar declaração",
  "trip-new": "Planejar viagem",
  "trip-allocate": "Alocar paciente",
  "trip-release": "Retirar da viagem",
  "trip-close": "Encerrar viagem",
  "occurrence-prove": "Conciliar atendimento",
  "benefit-calculate": "Calcular competência",
  "benefit-advance": "Atualizar benefício",
  "vehicle-new": "Cadastrar veículo",
  "driver-new": "Cadastrar motorista",
  "facility-new": "Cadastrar referência",
  "rule-new": "Nova regra demonstrativa",
};
const actionNames = {
  "patient-new": "patient.create",
  "request-new": "request.create",
  "request-decide": "request.decide",
  "schedule-new": "schedule.create",
  "document-request": "document.create",
  "document-occurrence": "document.create",
  "trip-new": "trip.create",
  "trip-allocate": "trip.allocate",
  "trip-release": "trip.release",
  "trip-close": "trip.close",
  "occurrence-prove": "occurrence.prove",
  "benefit-calculate": "benefit.calculate",
  "benefit-advance": "benefit.advance",
  "vehicle-new": "vehicle.create",
  "driver-new": "driver.create",
  "facility-new": "facility.create",
  "rule-new": "rule.create",
};
const saveLabels = {
  "patient-new": "Cadastrar paciente",
  "request-new": "Criar solicitação",
  "request-decide": "Registrar decisão",
  "schedule-new": "Gerar agendamentos",
  "document-request": "Anexar documento",
  "document-occurrence": "Anexar documento",
  "trip-new": "Criar viagem",
  "trip-allocate": "Alocar passageiro",
  "trip-release": "Registrar alteração",
  "trip-close": "Encerrar e salvar execução",
  "occurrence-prove": "Confirmar comprovação",
  "benefit-calculate": "Calcular valores demonstrativos",
  "benefit-advance": "Registrar etapa",
  "rule-new": "Criar versão",
};

function Fields({ type, id }) {
  const { S, find, month, patientFor, requestFor, facilityFor } = useApp();
  const requests = S.requests.filter((r) => r.status === "Autorizada"),
    selected = requests.find((r) => r.id === Number(id)) || requests[0];
  if (type === "patient-new")
    return (
      <div className="form-grid">
        <Field label="Nome completo" name="name" />
        <Field
          label="Nascimento"
          name="birth"
          type="date"
          optional
          max={S.today}
        />
        <Field
          label="CPF fictício (opcional)"
          name="cpf"
          optional
          maxLength={14}
        />
        <Field
          label="CNS fictício (opcional)"
          name="cns"
          optional
          maxLength={15}
        />
        <Field
          label="Telefone"
          name="phone"
          type="tel"
          optional
          maxLength={30}
        />
        <Field label="Ponto de embarque" name="boarding" />
        <Field label="Endereço" name="address" full />
        <Field label="Nome do acompanhante" name="companion" optional />
        <Field
          label="CPF do acompanhante (opcional)"
          name="companion_cpf"
          optional
          maxLength={14}
        />
        <Field
          label="Dados bancários fictícios (opcional)"
          name="bank"
          full
          optional
        />
        <Check label="Necessita de veículo acessível" name="accessible" />
      </div>
    );
  if (type === "request-new")
    return (
      <>
        <div className="form-grid">
          <Select
            label="Paciente"
            name="patient_id"
            items={S.patients.map((p) => [p.id, cleanName(p.name)])}
          />
          <Select
            label="Modalidade"
            name="kind"
            items={["TFD", "Transporte sanitário"].map((x) => [x, x])}
          />
          <Select
            label="Unidade de referência"
            name="facility_id"
            items={S.facilities.map((f) => [f.id, f.name + " · " + f.cnes])}
          />
          <Field label="Especialidade" name="specialty" />
          <Field
            label="Início da validade"
            name="start_date"
            type="date"
            value={S.today}
          />
          <Field
            label="Fim da validade"
            name="end_date"
            type="date"
            value={S.today}
          />
          <Check label="Solicitar acompanhante cadastrado" name="companion" />
        </div>
        <Info>
          O processo será criado em análise. Anexe o laudo e registre a decisão
          antes de gerar agendamentos.
        </Info>
      </>
    );
  if (type === "request-decide")
    return (
      <>
        <Hidden name="id" value={id} />
        <div className="form-grid">
          <Select
            label="Decisão"
            name="status"
            items={[
              ["Autorizada", "Autorizar"],
              ["Pendente", "Solicitar correção"],
              ["Negada", "Negar"],
            ]}
          />
          <Note />
        </div>
      </>
    );
  if (type === "schedule-new") {
    const date =
      S.today < selected.start_date
        ? selected.start_date
        : S.today > selected.end_date
          ? selected.end_date
          : S.today;
    return (
      <>
        <Info>
          Use a mesma data de início e fim para um agendamento avulso. Para
          recorrência, escolha os dias da semana. Datas existentes não serão
          duplicadas.
        </Info>
        <div className="form-grid">
          <Select
            label="Solicitação autorizada"
            name="request_id"
            value={selected.id}
            items={requests.map((r) => [
              r.id,
              `#${r.id} · ${cleanName(find("patients", r.patient_id)?.name)} · ${r.specialty}`,
            ])}
          />
          <Field label="Início" name="start_date" type="date" value={date} />
          <Field label="Fim" name="end_date" type="date" value={date} />
          <div className="full">
            <label>Dias da recorrência</label>
            <div className="weekday">
              {["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"].map((d, i) => (
                <Check key={d} label={d} name="weekday" value={i} />
              ))}
            </div>
          </div>
        </div>
      </>
    );
  }
  if (type.startsWith("document-")) {
    const isRequest = type === "document-request";
    return (
      <>
        <Hidden name={isRequest ? "request_id" : "occurrence_id"} value={id} />
        <div className="form-grid">
          <Select
            label="Tipo de documento"
            name="kind"
            items={(isRequest
              ? ["Laudo"]
              : ["Declaração do paciente", "Declaração do acompanhante"]
            ).map((x) => [x, x])}
          />
          <label className="full">
            Arquivo (PDF, imagem ou TXT · até 4 MB)
            <input
              className="file-input"
              type="file"
              name="file"
              accept=".pdf,.png,.jpg,.jpeg,.txt"
              required
            />
          </label>
        </div>
        <Info>
          Utilize somente documentos fictícios. O arquivo será vinculado ao
          evento, com identificação do usuário e resumo SHA-256.
        </Info>
      </>
    );
  }
  if (type === "trip-new")
    return (
      <>
        <div className="form-grid">
          <Field label="Data" name="date" type="date" value={S.today} />
          <Field label="Destino" name="destination" value="Recife" />
          <Field label="Saída" name="departure" type="time" value="05:00" />
          <Field
            label="Retorno previsto (mesmo dia)"
            name="arrival"
            type="time"
            value="17:00"
          />
          <Select
            label="Veículo"
            name="vehicle_id"
            items={S.vehicles.map((v) => [
              v.id,
              `${v.name} · ${v.capacity} lugares${v.accessible ? " · acessível" : ""}`,
            ])}
          />
          <Select
            label="Motorista"
            name="driver_id"
            items={S.drivers.map((d) => [d.id, cleanName(d.name)])}
          />
          <Field
            label="Percurso total estimado (km)"
            name="estimated_km"
            type="number"
            value="220"
            min="0"
            max="5000"
            step=".1"
          />
          <Field
            label="Rota / trechos de ida e volta"
            name="route"
            value="Macaparana → Recife → Macaparana"
            full
          />
        </div>
        <Info>
          O sistema verifica conflitos de horário, validade da CNH e, na
          alocação, capacidade e acessibilidade. A distância é informada
          manualmente.
        </Info>
      </>
    );
  if (type === "trip-allocate") {
    const t = find("trips", id);
    return (
      <>
        <Hidden name="trip_id" value={id} />
        <div className="form-grid">
          <Select
            label="Agendamento na data da viagem"
            name="occurrence_id"
            items={S.occurrences
              .filter((o) => o.date === t.date && !o.trip_id)
              .map((o) => [
                o.id,
                `${cleanName(patientFor(o)?.name)} · ${facilityFor(requestFor(o))?.city}${requestFor(o)?.companion ? " + acompanhante" : ""}`,
              ])}
          />
        </div>
        <Info>
          Confira se a rota atende a unidade de referência. O lugar fica
            reservado em todos os trechos desta rota. Para reservar parte do percurso, use Rotas e trechos.
        </Info>
      </>
    );
  }
  if (type === "trip-release") {
    const o = find("occurrences", id);
    return (
      <>
        <Hidden name="trip_id" value={o.trip_id} />
        <Hidden name="occurrence_id" value={id} />
        <Field label="Motivo da alteração" name="reason" maxLength={1000} />
        <Info>
          O agendamento permanece no calendário, aguardando nova alocação.
        </Info>
      </>
    );
  }
  if (type === "trip-close")
    return (
      <>
        <Hidden name="id" value={id} />
        <div className="form-grid">
          <Field
            label="Quilômetros realmente percorridos"
            name="km"
            type="number"
            min="0.1"
            max="10000"
            step=".1"
          />
          <Field
            label="Combustível consumido (litros)"
            name="liters"
            type="number"
            min="0"
            max="2000"
            step=".1"
          />
          <Field
            label="Custo total da viagem (R$)"
            name="cost"
            type="number"
            min="0"
            max="100000"
            step=".01"
          />
          <Note label="Ocorrências e alterações de rota" name="notes" />
        </div>
        <Info>
          Registre previamente o embarque ou a ausência de todos os passageiros.
          O custo é informado pelo operador e não inclui ajudas de custo.
        </Info>
      </>
    );
  if (type === "occurrence-prove") {
    const o = find("occurrences", id),
      r = requestFor(o);
    return (
      <>
        <Hidden name="id" value={id} />
        <Info>
          A conciliação exige embarque registrado e declaração anexada. Para
          comprovar o acompanhante, anexe também a declaração dele.
        </Info>
        <div className="form-grid">
          <Field
            label="Permanência / período de atendimento"
            name="permanence"
            value={o.permanence || "Atendimento ambulatorial no mesmo dia"}
            full
            maxLength={500}
          />
          {r.companion > 0 && (
            <Check
              label="Comprovar também o acompanhante"
              name="companion_proof"
              checked={!!o.companion_proof}
            />
          )}
        </div>
      </>
    );
  }
  if (type === "benefit-calculate")
    return (
      <>
        <Field label="Competência" name="month" type="month" value={month} />
        <Info amber>
          Serão considerados apenas atendimentos de TFD autorizado, com embarque
          e comprovação. Acompanhantes exigem comprovação própria. Recalcular
          preserva benefícios já existentes.
        </Info>
      </>
    );
  if (type === "benefit-advance") {
    const b = find("benefits", id);
    return (
      <>
        <Hidden name="id" value={id} />
        <p>
          {b.beneficiary} · {money(b.amount_cents)} · <Badge>{b.status}</Badge>
        </p>
        <div className="form-grid">
          {b.status !== "Calculado" && (
            <Field
              label="Referência contábil / comprovante"
              name="accounting_ref"
              value={b.accounting_ref || ""}
              full
              maxLength={120}
            />
          )}{" "}
          {b.status === "Contabilidade" && (
            <Field
              label="Data do pagamento"
              name="payment_date"
              type="date"
              value={S.today}
              max={S.today}
            />
          )}
        </div>
        <Info>
          Esta operação registra o andamento do processo no demonstrador. Não
          envia ordens bancárias nem realiza pagamentos.
        </Info>
      </>
    );
  }
  if (type === "vehicle-new")
    return (
      <div className="form-grid">
        <Field label="Identificação / modelo" name="name" />
        <Field label="Placa" name="plate" maxLength={10} />
        <Field
          label="Capacidade de passageiros"
          name="capacity"
          type="number"
          value="8"
          min="1"
          max="60"
          step="1"
        />
        <Check label="Veículo acessível" name="accessible" />
      </div>
    );
  if (type === "driver-new")
    return (
      <div className="form-grid">
        <Field label="Nome" name="name" />
        <Field label="CNH fictícia" name="license" maxLength={30} />
        <Field label="Validade da CNH" name="valid_until" type="date" />
      </div>
    );
  if (type === "facility-new")
    return (
      <>
        <div className="form-grid">
          <Field label="Nome da unidade" name="name" />
          <Field label="CNES (7 dígitos)" name="cnes" maxLength={7} />
          <Field label="Município" name="city" />
          <Field label="Endereço" name="address" optional />
        </div>
        <Info>
          Cadastro manual. Não há validação automática na base oficial do CNES.
        </Info>
      </>
    );
  if (type === "rule-new")
    return (
      <>
        <div className="form-grid">
          <Field
            label="Identificação da versão"
            name="label"
            value="Exemplo acadêmico — sem validade normativa"
            full
          />
          <Field
            label="Paciente por ocorrência (R$)"
            name="patient_rate"
            type="number"
            value="35"
            min="0"
            max="10000"
            step=".01"
          />
          <Field
            label="Acompanhante por ocorrência (R$)"
            name="companion_rate"
            type="number"
            value="25"
            min="0"
            max="10000"
            step=".01"
          />
        </div>
        <Info amber>
          Regra simplificada para apresentação acadêmica. A nova versão será
          aplicada aos próximos cálculos, inclusive de competências anteriores.
          Benefícios existentes preservam valor e versão.
        </Info>
      </>
    );
  return null;
}

export function BusinessForm({ type, id }) {
  const { run, busy, open, close } = useApp(),
    [error, setError] = useState("");
  async function submit(event) {
    event.preventDefault();
    if (busy) return;
    setError("");
    const form = event.currentTarget,
      fd = new FormData(form),
      data = Object.fromEntries(fd),
      action = actionNames[type];
    try {
      for (const key of [
        "id",
        "request_id",
        "patient_id",
        "facility_id",
        "vehicle_id",
        "driver_id",
        "trip_id",
        "occurrence_id",
      ])
        if (data[key]) data[key] = Number(data[key]);
      for (const input of form.querySelectorAll(
        "input[type=checkbox]:not([name=weekday])",
      ))
        data[input.name] = input.checked;
      if (action === "schedule.create")
        data.weekdays = fd.getAll("weekday").map(Number);
      if (action === "document.create") {
        const file = fd.get("file");
        if (!file?.size || file.size > 4 * 1024 * 1024)
          throw Error("Selecione um arquivo de até 4 MB.");
        data.name = file.name;
        data.content = await new Promise((resolve, reject) => {
          const reader = new FileReader();
          reader.onload = () => resolve(reader.result.split(",")[1]);
          reader.onerror = () => reject(Error("Falha ao ler arquivo."));
          reader.readAsDataURL(file);
        });
        delete data.file;
      }
      const result = await run(action, data);
      if (["request.create", "request.decide"].includes(action))
        open("request-detail", result.id);
      else if (["trip.create", "trip.close"].includes(action))
        open("trip-detail", result.id);
      else if (["trip.allocate", "trip.release"].includes(action))
        open("trip-detail", data.trip_id);
      else if (action === "document.create")
        open(
          data.request_id ? "request-detail" : "occurrence-detail",
          data.request_id || data.occurrence_id,
        );
      else if (action === "occurrence.prove")
        open("occurrence-detail", data.id);
      else close();
    } catch (error) {
      setError(error.message);
    }
  }
  return (
    <form id="modal-form" data-form={actionNames[type]} onSubmit={submit}>
      <fieldset disabled={busy} className="form-fieldset">
        <div className="modal-body">
          <Fields type={type} id={id} />
          {error && (
            <div className="form-error" role="alert">
              {error}
            </div>
          )}
        </div>
        <div className="modal-footer">
          <Button act="close">Cancelar</Button>
          <button type="submit" className="btn primary" disabled={busy}>
            {busy ? "Salvando…" : saveLabels[type] || "Salvar"}
          </button>
        </div>
      </fieldset>
    </form>
  );
}
