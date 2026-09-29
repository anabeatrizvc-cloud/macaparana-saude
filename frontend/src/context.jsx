import { createContext, useContext } from "react";
export const AppContext = createContext(null);
export const useApp = () => useContext(AppContext);
export const roles = {
  admin: "Administrador",
  regulacao: "Regulação",
  transporte: "Transporte",
  motorista: "Motorista",
  financeiro: "Financeiro",
  auditor: "Controle interno",
};
export const navigation = [
  ["dashboard", "Visão geral", "home"],
  ["patients", "Pacientes", "users"],
  ["requests", "Solicitações", "file"],
  ["calendar", "Calendário", "calendar"],
  ["trips", "Viagens", "bus"],
  ["review", "Conferência mensal", "clipboard"],
  ["finance", "Ajudas de custo", "wallet"],
  ["fleet", "Frota e referências", "settings"],
  ["audit", "Auditoria", "shield"],
  ["help", "Entrega acadêmica", "help"],
];
export const money = (cents) =>
  new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" }).format(
    (cents || 0) / 100,
  );
export const dateFmt = (value) =>
  value
    ? new Date(value.slice(0, 10) + "T12:00:00").toLocaleDateString("pt-BR")
    : "—";
export const shortDate = (value) => dateFmt(value).slice(0, 5);
export const timeFmt = (value) =>
  value
    ? new Date(value).toLocaleString("pt-BR", {
        dateStyle: "short",
        timeStyle: "short",
      })
    : "—";
export const cleanName = (value) =>
  String(value || "").replace(/ · fictíci[oa]$/, "");
export const initials = (value) =>
  cleanName(value)
    .split(" ")
    .filter(Boolean)
    .slice(0, 2)
    .map((s) => s[0])
    .join("");

export async function api(path, body) {
  const response = await fetch(path, {
    method: body ? "POST" : "GET",
    headers: body
      ? { "Content-Type": "application/json", "X-App": "macaparana" }
      : {},
    body: body ? JSON.stringify(body) : undefined,
  });
  const result = await response.json();
  if (!response.ok) {
    const error = new Error(result.error || "Não foi possível concluir.");
    error.status = response.status;
    throw error;
  }
  return result;
}
