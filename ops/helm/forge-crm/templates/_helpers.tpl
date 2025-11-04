{{/*
Expand the name of the chart.
*/}}
{{- define "forge-crm.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "forge-crm.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "forge-crm.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "forge-crm.labels" -}}
helm.sh/chart: {{ include "forge-crm.chart" . }}
{{ include "forge-crm.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "forge-crm.selectorLabels" -}}
app.kubernetes.io/name: {{ include "forge-crm.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "forge-crm.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "forge-crm.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Database host
*/}}
{{- define "forge-crm.databaseHost" -}}
{{- if .Values.postgresql.enabled }}
{{- printf "%s-postgresql" (include "forge-crm.fullname" .) }}
{{- else }}
{{- .Values.externalDatabase.host }}
{{- end }}
{{- end }}

{{/*
Database name
*/}}
{{- define "forge-crm.databaseName" -}}
{{- if .Values.postgresql.enabled }}
{{- .Values.postgresql.auth.database }}
{{- else }}
{{- .Values.externalDatabase.database }}
{{- end }}
{{- end }}

{{/*
Database username
*/}}
{{- define "forge-crm.databaseUsername" -}}
{{- if .Values.postgresql.enabled }}
{{- .Values.postgresql.auth.username }}
{{- else }}
{{- .Values.externalDatabase.username }}
{{- end }}
{{- end }}

{{/*
Database secret name
*/}}
{{- define "forge-crm.databaseSecretName" -}}
{{- if .Values.postgresql.enabled }}
{{- printf "%s-postgresql" (include "forge-crm.fullname" .) }}
{{- else }}
{{- .Values.externalDatabase.existingSecret }}
{{- end }}
{{- end }}

{{/*
Database secret password key
*/}}
{{- define "forge-crm.databaseSecretPasswordKey" -}}
{{- if .Values.postgresql.enabled }}
{{- "postgres-password" }}
{{- else }}
{{- .Values.externalDatabase.existingSecretPasswordKey }}
{{- end }}
{{- end }}

{{/*
Secret name for application secrets
*/}}
{{- define "forge-crm.secretName" -}}
{{- printf "%s-secret" (include "forge-crm.fullname" .) }}
{{- end }}