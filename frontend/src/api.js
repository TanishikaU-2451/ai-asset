/**
 * api.js — Axios wrapper for the NAAC Compliance Intelligence API.
 */

import axios from "axios";

const API_BASE = process.env.REACT_APP_API_URL || "";

/**
 * Submit a compliance query.
 * @param {string} query  - Natural language question.
 * @param {object} opts   - Optional overrides: { n_naac, n_mvsr, model }
 * @returns {Promise<object>} API response with naac_requirement, mvsr_evidence, etc.
 */
export async function submitQuery(query, opts = {}) {
  const payload = {
    query,
    n_naac: opts.n_naac ?? 4,
    n_mvsr: opts.n_mvsr ?? 4,
    model: opts.model ?? "llama3",
  };
  const response = await axios.post(`${API_BASE}/query`, payload);
  return response.data;
}

/**
 * Trigger a forced NAAC document update.
 * @returns {Promise<object>} Sync statistics.
 */
export async function forceUpdate() {
  const response = await axios.post(`${API_BASE}/force-update`);
  return response.data;
}

/**
 * Get the last NAAC sync information.
 * @returns {Promise<object>} Sync state object.
 */
export async function getLastSync() {
  const response = await axios.get(`${API_BASE}/last-sync`);
  return response.data;
}

/**
 * Get the health status of backend services.
 * @returns {Promise<object>} Health status object.
 */
export async function getHealth() {
  const response = await axios.get(`${API_BASE}/health`);
  return response.data;
}
