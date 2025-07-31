{{/*
Expand the name of the chart.
*/}}
{{- define "notes-app.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "notes-app.fullname" -}}
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
{{- define "notes-app.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "notes-app.labels" -}}
helm.sh/chart: {{ include "notes-app.chart" . }}
{{ include "notes-app.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "notes-app.selectorLabels" -}}
app.kubernetes.io/name: {{ include "notes-app.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Frontend labels
*/}}
{{- define "notes-app.frontend.labels" -}}
{{ include "notes-app.labels" . }}
app.kubernetes.io/component: frontend
{{- end }}

{{/*
Frontend selector labels
*/}}
{{- define "notes-app.frontend.selectorLabels" -}}
{{ include "notes-app.selectorLabels" . }}
app.kubernetes.io/component: frontend
{{- end }}

{{/*
Backend labels
*/}}
{{- define "notes-app.backend.labels" -}}
{{ include "notes-app.labels" . }}
app.kubernetes.io/component: backend
{{- end }}

{{/*
Backend selector labels
*/}}
{{- define "notes-app.backend.selectorLabels" -}}
{{ include "notes-app.selectorLabels" . }}
app.kubernetes.io/component: backend
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "notes-app.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "notes-app.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Create the frontend image name
*/}}
{{- define "notes-app.frontend.image" -}}
{{- $registry := .Values.global.imageRegistry }}
{{- $repository := .Values.frontend.image.repository }}
{{- $tag := .Values.frontend.image.tag | default .Chart.AppVersion }}
{{- if $registry }}
{{- printf "%s/%s:%s" $registry $repository $tag }}
{{- else }}
{{- printf "%s:%s" $repository $tag }}
{{- end }}
{{- end }}

{{/*
Create the backend image name
*/}}
{{- define "notes-app.backend.image" -}}
{{- $registry := .Values.global.imageRegistry }}
{{- $repository := .Values.backend.image.repository }}
{{- $tag := .Values.backend.image.tag | default .Chart.AppVersion }}
{{- if $registry }}
{{- printf "%s/%s:%s" $registry $repository $tag }}
{{- else }}
{{- printf "%s:%s" $repository $tag }}
{{- end }}
{{- end }}

{{/*
Database host
*/}}
{{- define "notes-app.database.host" -}}
{{- if .Values.database.external }}
{{- .Values.database.host }}
{{- else }}
{{- printf "%s-postgresql" (include "notes-app.fullname" .) }}
{{- end }}
{{- end }}

{{/*
Database URL
*/}}
{{- define "notes-app.database.url" -}}
{{- $host := include "notes-app.database.host" . }}
{{- $port := .Values.database.port }}
{{- $name := .Values.database.name }}
{{- $username := .Values.database.username }}
{{- printf "postgresql+asyncpg://%s:password@%s:%v/%s" $username $host $port $name }}
{{- end }}

{{/*
Database secret name
*/}}
{{- define "notes-app.database.secretName" -}}
{{- if .Values.database.existingSecret }}
{{- .Values.database.existingSecret }}
{{- else }}
{{- printf "%s-database" (include "notes-app.fullname" .) }}
{{- end }}
{{- end }}

{{/*
Database password key
*/}}
{{- define "notes-app.database.secretPasswordKey" -}}
{{- if .Values.database.existingSecretPasswordKey }}
{{- .Values.database.existingSecretPasswordKey }}
{{- else }}
{{- "password" }}
{{- end }}
{{- end }} 