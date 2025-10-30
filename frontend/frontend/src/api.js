// api.js
import axios from "axios";

const API_BASE = ""; // using Vite proxy -> forward /orgs/* to backend

export const evaluateExpense = async (orgId, expense) => {
  const res = await axios.post(`/orgs/${orgId}/policy/evaluate`, expense);
  return res.data;
};

export const getAudits = async (orgId) => {
  const res = await axios.get(`/orgs/${orgId}/policy/audit`);
  return res.data;
};
