import React, { useEffect, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import { renderToStaticMarkup } from "react-dom/server";
import {
  AppContext,
  api,
  navigation,
  roles,
  initials,
  dateFmt,
  cleanName,
} from "./context";
import { Brand, Landscape, Icon, Field, Select, Table } from "./ui";
import { pages } from "./pages";
import { detailComponents } from "./details";
import { BusinessForm, titles } from "./forms";
import "../../static/style.css";
import "./react.css";

function Login() {
  const { login, busy } = React.useContext(AppContext),
    [error, setError] = useState("");
  async function submit(event) {
    event.preventDefault();
    setError("");
    const data = Object.fromEntries(new FormData(event.currentTarget));
    try {
      await login(data);
    } catch (error) {
      setError(error.message);
    }
  }
  return (
    <div className="login">
      <section className="login-art">
        <Brand />
        <h1>
          Cuidado que
          <br />
          vai mais longe.
        </h1>
        <p>
          Uma visão integrada de cada paciente, cada viagem e cada etapa do
          cuidado.
        </p>
        <Landscape />
        <div className="copyright">
          MACAPARANA · PERNAMBUCO
          <br />
          <br />
          Projeto acadêmico · dados exclusivamente fictícios
        </div>
      </section>
      <section className="login-panel">
        <div className="login-box">
          <span className="eyebrow">Bem-vindo ao ambiente de demonstração</span>
          <h2>Acesse sua área</h2>
          <p>Acompanhe os deslocamentos em saúde do município.</p>
          <form id="login-form" onSubmit={submit}>
            <Select
              label="Perfil de demonstração"
              name="username"
              items={Object.entries(roles)}
              value="admin"
            />
            <Field
              label="Senha"
              name="password"
              type="password"
              value="demo123"
            />
            {error && (
              <div className="login-error" role="alert">
                {error}
              </div>
            )}
            <button className="btn primary" type="submit" disabled={busy}>
              {busy ? "Entrando…" : "Entrar no sistema"} <Icon name="arrow" />
            </button>
          </form>
          <div className="demo-credentials">
            <strong>Acesso acadêmico</strong>
            <br />
            Todos os perfis usam a senha <strong>demo123</strong>.<br />
            Explore com dados fictícios, sem integrações externas.
          </div>
          <p style={{ marginTop: 25, fontSize: 11 }}>
            <a
              href="/docs/Documentacao-Macaparana.pdf"
              target="_blank"
              rel="noreferrer"
            >
              Documentação do projeto <Icon name="arrow" />
            </a>
          </p>
        </div>
      </section>
    </div>
  );
}

function Modal() {
  const { dialog, close, busy, find } = React.useContext(AppContext),
    ref = useRef(null);
  useEffect(() => {
    const node = ref.current;
    if (dialog && !node.open) node.showModal();
    if (!dialog && node.open) node.close();
  }, [dialog]);
  let title = "",
    Content = null;
  if (dialog) {
    const { type, id } = dialog;
    Content = detailComponents[type];
    title = titles[type] || "";
    if (type === "patient-detail")
      title = cleanName(find("patients", id)?.name);
    if (type === "request-detail")
      title = `Solicitação #${String(id).padStart(4, "0")}`;
    if (type === "occurrence-detail")
      title = `Atendimento · ${dateFmt(find("occurrences", id)?.date)}`;
    if (type === "trip-detail")
      title = `Viagem #V${String(id).padStart(3, "0")} · ${find("trips", id)?.destination}`;
    if (type === "audit-detail") title = "Evento de auditoria";
    if (type === "benefit-advance")
      title =
        {
          Calculado: "Aprovar benefício",
          Aprovado: "Encaminhar à contabilidade",
          Contabilidade: "Registrar pagamento",
        }[find("benefits", id)?.status] || title;
  }
  return (
    <dialog
      id="modal"
      ref={ref}
      aria-labelledby="modal-title"
      onCancel={(event) => {
        event.preventDefault();
        if (!busy) close();
      }}
    >
      {dialog && (
        <React.Fragment key={dialog.key}>
          <div className="modal-head">
            <h2 id="modal-title">{title}</h2>
            <button
              type="button"
              className="icon-btn"
              data-act="close"
              aria-label="Fechar"
              disabled={busy}
              onClick={close}
            >
              <Icon name="close" />
            </button>
          </div>
          {Content ? (
            <div className="modal-body">
              <Content id={dialog.id} />
            </div>
          ) : (
            <BusinessForm type={dialog.type} id={dialog.id} />
          )}
        </React.Fragment>
      )}
    </dialog>
  );
}

function Shell() {
  const { S, page, can, allowed, handle, busy } = React.useContext(AppContext),
    label = navigation.find((n) => n[0] === page)?.[1],
    Page = pages[page];
  return (
    <>
      <aside className="sidebar">
        <Brand />
        <div className="nav-label">Área de trabalho</div>
        <nav className="nav" aria-label="Menu principal">
          {navigation
            .filter((n) => allowed(n[0]) && n[0] !== "help")
            .map(([id, label, icon]) => (
              <a
                href={"#" + id}
                key={id}
                className={page === id ? "active" : ""}
                aria-current={page === id ? "page" : undefined}
              >
                <Icon name={icon} />
                {label}
                {id === "requests" &&
                  S.requests.filter((r) => r.status === "Em análise").length >
                    0 && (
                    <span className="count">
                      {
                        S.requests.filter((r) => r.status === "Em análise")
                          .length
                      }
                    </span>
                  )}
              </a>
            ))}
        </nav>
        <div className="side-bottom">
          <nav className="nav">
            <a href="#help" className={page === "help" ? "active" : ""}>
              <Icon name="help" />
              Entrega acadêmica
            </a>
          </nav>
          <div className="pilot">
            <strong>
              <span className="dot" />
              Ambiente de demonstração
            </strong>
            <p>Dados fictícios. Preparado para explorar o fluxo municipal.</p>
          </div>
          <div className="side-footer">
            <span className="avatar">{initials(S.user.name)}</span>
            <div>
              <strong>{S.user.name}</strong>
              <small>{roles[S.user.role]}</small>
            </div>
            <button
              className="icon-btn"
              data-act="logout"
              title="Sair"
              aria-label="Sair"
              disabled={busy}
              onClick={() => handle("logout")}
            >
              <Icon name="logout" />
            </button>
          </div>
        </div>
      </aside>
      <main className="main">
        <header className="topbar">
          <button
            className="icon-btn menu-toggle"
            data-act="menu"
            aria-label="Abrir menu"
            onClick={() => handle("menu")}
          >
            <Icon name="menu" />
          </button>
          <div className="breadcrumbs">
            Secretaria de Saúde <span> / &nbsp; {label}</span>
          </div>
          <div className="top-right">
            <span className="top-date muted">
              {new Date(S.today + "T12:00:00").toLocaleDateString("pt-BR", {
                day: "numeric",
                month: "long",
                year: "numeric",
              })}
            </span>
            <span className="demo-tag">PROJETO ACADÊMICO</span>
            <span className="avatar">{initials(S.user.name)}</span>
          </div>
        </header>
        <div className="content" id="content">
          <Page />
          <div className="footer-note">
            <span>Macaparana Saúde · Gestão integrada de deslocamentos</span>
            <span>React + Python · v1.2 · Dados armazenados localmente</span>
          </div>
        </div>
      </main>
    </>
  );
}

function App() {
  const [S, setS] = useState(null),
    [loading, setLoading] = useState(true),
    [busy, setBusy] = useState(false),
    [route, setRoute] = useState(location.hash.slice(1) || "dashboard"),
    [search, setSearch] = useState(""),
    [month, setMonth] = useState(new Date().toISOString().slice(0, 7)),
    [tripFilter, setTripFilter] = useState(""),
    [dialog, setDialog] = useState(null),
    [notice, setNotice] = useState(null),
    [menuOpen, setMenuOpen] = useState(false);
  const dialogKey = useRef(0),
    toastTimer = useRef(null),
    running = useRef(false);
  const find = (table, id) => S?.[table]?.find((x) => x.id === Number(id));
  const requestFor = (o) => find("requests", o?.request_id),
    patientFor = (o) => find("patients", requestFor(o)?.patient_id),
    facilityFor = (r) => find("facilities", r?.facility_id);
  const can = (...roles) =>
    !!S && (S.user.role === "admin" || roles.includes(S.user.role));
  const allowed = (id) =>
    !S
      ? false
      : S.user.role === "motorista"
        ? ["trips", "segments", "help"].includes(id)
        : id === "production"
          ? can("faturamento", "auditor")
          : id === "pilot"
            ? can("auditor", "financeiro", "transporte")
            : id === "finance"
              ? can("financeiro", "auditor")
              : id === "audit"
                ? can("auditor")
                : true;
  const page =
    pages[route] && allowed(route)
      ? route
      : S?.user.role === "motorista"
        ? "trips"
        : "dashboard";
  const open = (type, id = "") =>
    setDialog({ type, id: Number(id) || "", key: ++dialogKey.current });
  const close = () => setDialog(null);
  function toast(message, error = false) {
    setNotice({ message, error });
    clearTimeout(toastTimer.current);
    toastTimer.current = setTimeout(() => setNotice(null), 6500);
  }
  function authError(error) {
    if (error.status === 401) {
      setS(null);
      close();
    }
    return error;
  }
  async function load() {
    try {
      const data = await api("/api/state");
      setS(data);
      return data;
    } catch (error) {
      throw authError(error);
    }
  }
  useEffect(() => {
    let active = true;
    api("/api/state")
      .then((data) => {
        if (active) setS(data);
      })
      .catch((error) => {
        if (active && error.status !== 401) toast(error.message, true);
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
      clearTimeout(toastTimer.current);
    };
  }, []);
  useEffect(() => {
    const change = () => {
      setRoute(location.hash.slice(1) || "dashboard");
      setSearch("");
      setMenuOpen(false);
      close();
      window.scrollTo(0, 0);
    };
    window.addEventListener("hashchange", change);
    return () => window.removeEventListener("hashchange", change);
  }, []);
  useEffect(() => {
    document.body.classList.toggle("menu-open", menuOpen);
    return () => document.body.classList.remove("menu-open");
  }, [menuOpen]);
  async function login(data) {
    setBusy(true);
    try {
      await api("/api/login", data);
      await load();
    } finally {
      setBusy(false);
    }
  }
  async function run(action, data) {
    if (running.current) throw Error("Aguarde a operação em andamento.");
    running.current = true;
    setBusy(true);
    try {
      const result = await api("/api/action", { action, data });
      await load();
      toast(result.message);
      return result;
    } catch (error) {
      throw authError(error);
    } finally {
      running.current = false;
      setBusy(false);
    }
  }
  function printTrip(id) {
    const t = find("trips", id),
      windowPrint = window.open("", "_blank");
    if (!windowPrint)
      throw Error("Permita a abertura da lista em uma nova aba.");
    const body = (
      <html lang="pt-BR">
        <head>
          <meta charSet="utf-8" />
          <title>Lista operacional · Viagem {id}</title>
          <link rel="stylesheet" href="/style.css" />
        </head>
        <body style={{ padding: 35 }}>
          <h1>Lista operacional · Viagem #V{t.id}</h1>
          <p>
            {dateFmt(t.date)} · {t.departure}–{t.arrival} · {t.destination}
            <br />
            {t.route}
          </p>
          <p>
            Motorista: {find("drivers", t.driver_id)?.name} · Veículo:{" "}
            {find("vehicles", t.vehicle_id)?.plate}
          </p>
          <Table
            headers={[
              "Passageiro",
              "Acompanhante",
              "Embarque",
              "Confirmação",
              "Trecho",
              "Situação",
            ]}
            rows={S.occurrences
              .filter((o) => o.trip_id === t.id)
              .map((o) => [
                cleanName(patientFor(o)?.name),
                requestFor(o)?.companion ? patientFor(o)?.companion : "—",
                patientFor(o)?.boarding,
                o.confirmation,
                S.route_stops.filter((s) => s.trip_id === t.id).length
                  ? S.route_stops
                      .filter((s) => s.trip_id === t.id)
                      .filter((s) =>
                        [o.segment_start, o.segment_end].includes(s.position),
                      )
                      .map((s) => s.name)
                      .join(" → ")
                  : "Percurso integral",
                o.boarding,
              ])}
          />
          <p style={{ marginTop: 25 }}>
            Dados fictícios · use Ctrl+P para imprimir ou salvar em PDF.
          </p>
        </body>
      </html>
    );
    windowPrint.document.write("<!doctype html>" + renderToStaticMarkup(body));
    windowPrint.document.close();
  }
  async function handle(type, id) {
    if (busy) return;
    try {
      if (type === "close") return close();
      if (type === "menu") return setMenuOpen((x) => !x);
      if (type === "logout") {
        setBusy(true);
        await api("/api/logout", {});
        setS(null);
        close();
        setBusy(false);
        return;
      }
      if (type === "trip-print") return printTrip(id);
      if (["confirm", "board", "absent"].includes(type)) {
        const tripId = find("occurrences", id).trip_id;
        await run(
          type === "confirm" ? "occurrence.confirm" : "occurrence.board",
          {
            id: Number(id),
            status: {
              confirm: "Confirmado",
              board: "Embarcou",
              absent: "Ausente",
            }[type],
          },
        );
        return open("trip-detail", tripId);
      }
      if (
        type === "schedule-new" &&
        !S.requests.some((r) => r.status === "Autorizada")
      )
        throw Error("Autorize uma solicitação antes de agendar.");
      if (type === "request-new" && !S.patients.length)
        throw Error("Cadastre um paciente primeiro.");
      if (
        type === "trip-allocate" &&
        !S.occurrences.some(
          (o) => o.date === find("trips", id).date && !o.trip_id,
        )
      )
        throw Error(
          "Não há agendamentos sem viagem nessa data. Cadastre no Calendário.",
        );
      if (titles[type] || detailComponents[type]) open(type, id);
    } catch (error) {
      authError(error);
      toast(error.message, true);
      setBusy(false);
    }
  }
  const value = {
    S,
    busy,
    page,
    search,
    setSearch,
    month,
    setMonth,
    tripFilter,
    setTripFilter,
    dialog,
    open,
    close,
    handle,
    run,
    login,
    find,
    requestFor,
    patientFor,
    facilityFor,
    can,
    allowed,
    seats: (t) =>
      Math.max(
        0,
        ...Array.from(
          {
            length: Math.max(
              1,
              S.route_stops.filter((s) => s.trip_id === t.id).length - 1,
            ),
          },
          (_, i) =>
            S.occurrences
              .filter(
                (o) =>
                  o.trip_id === t.id &&
                  o.segment_start <= i &&
                  i < o.segment_end,
              )
              .reduce((n, o) => n + 1 + (requestFor(o)?.companion || 0), 0),
        ),
      ),
    segmentLabel: (o) => {
      const stops = S.route_stops.filter((s) => s.trip_id === o.trip_id);
      return stops.length
        ? `${stops[o.segment_start]?.name} → ${stops[o.segment_end]?.name}`
        : "Percurso integral";
    },
    matches: (value) =>
      !search ||
      String(value)
        .toLocaleLowerCase("pt-BR")
        .includes(search.toLocaleLowerCase("pt-BR")),
  };
  return (
    <AppContext.Provider value={value}>
      {loading ? (
        <div className="loading">Preparando o ambiente de demonstração…</div>
      ) : S ? (
        <Shell />
      ) : (
        <Login />
      )}
      <Modal />
      <div
        id="toast"
        className={notice ? `show${notice.error ? " error" : ""}` : ""}
        role="status"
        aria-live="polite"
      >
        {notice?.message}
      </div>
    </AppContext.Provider>
  );
}

createRoot(document.getElementById("root")).render(<App />);
