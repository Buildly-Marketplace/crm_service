{{/*
Expand the name of the chart.
*/}}
{{- define "crm-service.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "crm-service.fullname" -}}
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
{{- define "crm-service.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "crm-service.labels" -}}
helm.sh/chart: {{ include "crm-service.chart" . }}
{{ include "crm-service.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "crm-service.selectorLabels" -}}
app.kubernetes.io/name: {{ include "crm-service.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "crm-service.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "crm-service.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Database host
*/}}
{{- define "crm-service.databaseHost" -}}
{{- if .Values.postgresql.enabled }}
{{- printf "%s-postgresql" (include "crm-service.fullname" .) }}
{{- else }}
{{- .Values.externalDatabase.host }}
{{- end }}
{{- end }}

{{/*
Database name
*/}}
{{- define "crm-service.databaseName" -}}
{{- if .Values.postgresql.enabled }}
{{- .Values.postgresql.auth.database }}
{{- else }}
{{- .Values.externalDatabase.database }}
{{- end }}
{{- end }}

{{/*
Database username
*/}}
{{- define "crm-service.databaseUsername" -}}
{{- if .Values.postgresql.enabled }}
{{- .Values.postgresql.auth.username }}
{{- else }}
{{- .Values.externalDatabase.username }}
{{- end }}
{{- end }}

{{/*
Database secret name
*/}}
{{- define "crm-service.databaseSecretName" -}}
{{- if .Values.postgresql.enabled }}
{{- printf "%s-postgresql" (include "crm-service.fullname" .) }}
{{- else }}
{{- .Values.externalDatabase.existingSecret }}
{{- end }}
{{- end }}

{{/*
Database secret password key
*/}}
{{- define "crm-service.databaseSecretPasswordKey" -}}
{{- if .Values.postgresql.enabled }}
{{- "postgres-password" }}
{{- else }}
{{- .Values.externalDatabase.existingSecretPasswordKey }}
{{- end }}
{{- end }}

{{/*
Secret name for application secrets
*/}}
{{- define "crm-service.secretName" -}}
{{- printf "%s-secret" (include "crm-service.fullname" .) }}
{{- end }}