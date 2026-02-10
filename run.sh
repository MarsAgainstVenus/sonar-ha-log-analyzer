#!/usr/bin/with-contenv bashio
set -e

bashio::log.info "Starting Sonar Log Analyzer"

# Read options
LOG_MAX_CHARS=$(bashio::config 'log_max_chars')

export HA_URL="${HA_URL:-http://supervisor/core}"
export SUPERVISOR_TOKEN="${SUPERVISOR_TOKEN}"
export LOG_MAX_CHARS="${LOG_MAX_CHARS}"

# Perplexity API key must be set as an add-on secret env var in the UI
if [ -z "${PPLX_API_KEY}" ]; then
  bashio::log.error "PPLX_API_KEY not set. Please configure it in add-on options."
  exit 1
fi

python3 /analyzer.py
bashio::log.info "Sonar Log Analyzer finished"
