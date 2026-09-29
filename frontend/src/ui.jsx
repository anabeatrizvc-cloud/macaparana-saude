import React from "react";
import { useApp, cleanName, initials, dateFmt } from "./context";

const paths = {
  home: "M3 10 12 3l9 7v10a1 1 0 0 1-1 1h-5v-7H9v7H4a1 1 0 0 1-1-1z",
  users:
    "M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2 M16 3a4 4 0 0 1 0 8 M22 21v-2a4 4 0 0 0-3-3.87 M9 3a4 4 0 1 0 0 8 4 4 0 0 0 0-8",
  file: "M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z M14 2v6h6 M8 13h8 M8 17h5",
  calendar:
    "M8 2v4 M16 2v4 M3 10h18 M5 4h14a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2 M7 14h2 M12 14h2 M7 18h2",
  bus: "M5 17h14V5a2 2 0 0 0-2-2H7a2 2 0 0 0-2 2z M5 10h14 M5 6h14 M7 17v3 M17 17v3 M8 14h.01 M16 14h.01 M2 8v4 M22 8v4",
  check: "M20 6 9 17l-5-5",
  clipboard:
    "M9 3H6a2 2 0 0 0-2 2v15a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V5a2 2 0 0 0-2-2h-3 M9 2h6v4H9z M8 12l2 2 5-5 M8 18h8",
  wallet: "M20 7V4H5a3 3 0 0 0 0 6h16v10H5a3 3 0 0 1-3-3V7 M16 13h6v4h-6z",
  shield: "M12 3 3 7v5c0 5 9 9 9 9s9-4 9-9V7z M8 12l3 3 5-6",
  settings:
    "M12 8a4 4 0 1 0 0 8 4 4 0 0 0 0-8 M12 2v3 M12 19v3 M2 12h3 M19 12h3 M5 5l2 2 M17 17l2 2 M5 19l2-2 M17 7l2-2",
  help: "M9 9a3 3 0 0 1 6 0c0 2-3 2-3 5 M12 17h.01 M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20",
  plus: "M12 5v14 M5 12h14",
  arrow: "M5 12h14 M14 7l5 5-5 5",
  down: "M12 3v12 M7 10l5 5 5-5 M4 16v5h16v-5",
  search: "M21 21l-5-5 M10 3a7 7 0 1 0 0 14 7 7 0 0 0 0-14",
  clock: "M12 8v5l3 2 M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20",
  pin: "M20 10c0 6-8 12-8 12S4 16 4 10a8 8 0 1 1 16 0 M12 7a3 3 0 1 0 0 6 3 3 0 0 0 0-6",
  logout: "M9 21H4V3h5 M9 12h12 M17 8l4 4-4 4",
  close: "M6 6l12 12 M18 6 6 18",
  menu: "M3 6h18 M3 12h18 M3 18h18",
  eye: "M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12 M12 9a3 3 0 1 0 0 6 3 3 0 0 0 0-6",
  chart: "M4 20V10 M10 20V4 M16 20v-7 M22 20H2",
};
export function Icon({ name }) {
  return (
    <svg
      className="icon"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d={paths[name] || paths.file} />
    </svg>
  );
}
export function Brand() {
  return (
    <div className="brand">
      <img src="/mark.svg" alt="" />
      <div>
        <strong>
          Macaparana<span style={{ fontWeight: 400 }}> Saúde</span>
        </strong>
        <small>Gestão de deslocamentos</small>
      </div>
    </div>
  );
}
export function Landscape() {
  return (
    <svg
      className="welcome-art"
      viewBox="0 0 260 130"
      fill="none"
      aria-hidden="true"
    >
      <path
        d="M4 101c43-29 61 7 105-13s86-2 146-18"
        stroke="#c0ccae"
        strokeWidth="2"
        strokeDasharray="5 6"
      />
      <path
        d="M187 72V35h39v53 M199 29h15v-9h-15v9 M194 50h25 M207 38v23"
        stroke="#a2b390"
        strokeWidth="2"
      />
      <path
        d="M28 88V67c0-8 5-12 12-12h55c9 0 20 21 20 28v17H28z"
        fill="#d2dfc1"
        stroke="#a3b38f"
        strokeWidth="2"
      />
      <path
        d="M37 64h17v17H37z M61 64h17v17H61z M85 64h12l10 17H85z"
        fill="#edf2e6"
      />
      <circle cx="46" cy="101" r="9" fill="#9bae88" />
      <circle cx="46" cy="101" r="4" fill="#e7eddc" />
      <circle cx="97" cy="101" r="9" fill="#9bae88" />
      <circle cx="97" cy="101" r="4" fill="#e7eddc" />
      <path
        d="M150 74V38 M140 50l10-12 10 12 M141 61l9-11 9 11"
        stroke="#b3c3a1"
        strokeWidth="3"
      />
      <circle cx="54" cy="26" r="10" fill="#d5dfc6" />
      <path d="M231 103h-12 M20 113h106" stroke="#c2ceb2" strokeWidth="2" />
    </svg>
  );
}
const colors = {
  Autorizada: "green",
  Confirmado: "green",
  Embarcou: "green",
  Comprovado: "green",
  Pago: "green",
  Encerrada: "green",
  Pendente: "amber",
  "Em análise": "amber",
  Planejada: "blue",
  Calculado: "purple",
  Aprovado: "green",
  Contabilidade: "blue",
  Ausente: "red",
  Negada: "red",
  Recusado: "red",
  TFD: "purple",
  "Transporte sanitário": "blue",
};
export const Badge = ({ children }) => (
  <span className={`badge ${colors[children] || ""}`}>{children}</span>
);
export function Button({
  children,
  act,
  id = "",
  variant = "",
  icon,
  onClick,
  ...props
}) {
  const app = useApp();
  return (
    <button
      type="button"
      className={`btn ${variant}`}
      data-act={act}
      data-id={id}
      disabled={app?.busy}
      onClick={onClick || (() => app.handle(act, id))}
      {...props}
    >
      {icon && <Icon name={icon} />} {children}
    </button>
  );
}
export const Actions = ({ children }) => (
  <div className="actions">{children}</div>
);
export const Empty = ({ children = "Nenhum registro encontrado." }) => (
  <div className="empty">
    <Icon name="file" />
    <p>{children}</p>
  </div>
);
export const Sub = ({ children }) => (
  <small style={{ display: "block", marginTop: 4 }}>{children}</small>
);
export const Person = ({ patient: p }) => (
  <div className="person">
    <span className="avatar">{initials(p?.name)}</span>
    <div>
      <strong>{cleanName(p?.name)}</strong>
      <small>{p?.boarding || "Cadastro municipal"}</small>
    </div>
  </div>
);
export function Table({ headers, rows, className = "" }) {
  return rows.length ? (
    <div className="table-wrap">
      <table className={className}>
        <thead>
          <tr>
            {headers.map((h, i) => (
              <th key={i}>{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((r, i) => (
            <tr key={i}>
              {r.map((c, j) => (
                <td key={j}>{c}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  ) : (
    <Empty />
  );
}
export const Header = ({ title, subtitle, children }) => (
  <div className="page-head">
    <div>
      <h1>{title}</h1>
      <p>{subtitle}</p>
    </div>
    <Actions>{children}</Actions>
  </div>
);
export const Metric = ({ label, value, foot, icon }) => (
  <div className="metric">
    <div className="metric-top">
      {label}
      <span className="metric-icon">
        <Icon name={icon} />
      </span>
    </div>
    <div className="metric-value">{value}</div>
    <div className="metric-foot">{foot}</div>
  </div>
);
export const Info = ({ children, amber = false }) => (
  <div className={`info ${amber ? "amber" : ""}`}>{children}</div>
);
export const Detail = ({ label, children }) => (
  <div className="detail-item">
    <small>{label}</small>
    <strong>{children}</strong>
  </div>
);
export function Toolbar({ placeholder = "Buscar por nome…", children }) {
  const { search, setSearch } = useApp();
  return (
    <div className="toolbar">
      <div className="search">
        <Icon name="search" />
        <input
          id="search"
          type="search"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder={placeholder}
          aria-label={placeholder}
        />
      </div>
      {children}
    </div>
  );
}
export function MonthInput() {
  const { month, setMonth } = useApp();
  return (
    <label className="check">
      Competência{" "}
      <input
        id="month"
        type="month"
        value={month}
        required
        aria-label="Competência"
        onChange={(e) => {
          if (e.target.value) setMonth(e.target.value);
        }}
      />
    </label>
  );
}
export function DocList({ link, id }) {
  const { S } = useApp();
  const documents = S.documents.filter((d) => d[link] === Number(id));
  return documents.length ? (
    documents.map((d) => (
      <div className="doc-item" key={d.id}>
        <div>
          <Icon name="file" /> {d.kind}
          <small>
            {d.name} · {dateFmt(d.created_at)}
          </small>
        </div>
        <a className="btn small" href={`/api/documents/${d.id}`}>
          <Icon name="down" /> Baixar
        </a>
      </div>
    ))
  ) : (
    <p className="muted">Nenhum documento anexado.</p>
  );
}
export const Field = ({
  label,
  name,
  type = "text",
  value = "",
  optional = false,
  full = false,
  ...props
}) => (
  <label className={full ? "full" : ""}>
    {label}
    <input
      name={name}
      type={type}
      defaultValue={value}
      required={!optional}
      maxLength={300}
      {...props}
    />
  </label>
);
export const Select = ({ label, name, items, value }) => (
  <label>
    {label}
    <select name={name} required defaultValue={value ?? items[0]?.[0]}>
      {items.map(([id, label]) => (
        <option key={id} value={id}>
          {label}
        </option>
      ))}
    </select>
  </label>
);
export const Check = ({ label, name, checked = false, value }) => (
  <label className="check">
    <input type="checkbox" name={name} defaultChecked={checked} value={value} />
    {label}
  </label>
);
