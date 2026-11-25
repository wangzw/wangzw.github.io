{{- /*
  The Markdown rendition (index.md) of a list page: a home page, a section, the tags
  overview or a tag. It lists what the HTML page lists, without pagination, and links
  to the Markdown renditions.
*/ -}}
{{- $lines := slice (printf "# %s" (cond .IsHome site.Title .Title)) "" -}}
{{- $lines = $lines | append (printf "[%s](%s)" (i18n "Canonical URL" | default "Canonical URL") .Permalink) "" -}}
{{- with partial "page-description.html" . | replaceRE `\s+` " " -}}
  {{- $lines = $lines | append (printf "> %s" .) "" -}}
{{- end -}}
{{- if .IsHome -}}
  {{- $nav := slice -}}
  {{- range $item := site.Menus.main -}}
    {{- with $item.Page -}}
      {{- if not .IsHome -}}
        {{- $nav = $nav | append (printf "[%s](%s)" (i18n $item.Name | default $item.Name) (partial "markdown-url.html" .)) -}}
      {{- end -}}
    {{- end -}}
  {{- end -}}
  {{- range .Translations -}}
    {{- $nav = $nav | append (printf "[%s](%s)" .Language.Label (partial "markdown-url.html" .)) -}}
  {{- end -}}
  {{- with $nav -}}
    {{- $lines = $lines | append (delimit . " · ") "" -}}
  {{- end -}}
  {{- if ne .Title site.Title -}}
    {{- $lines = $lines | append (printf "## %s" .Title) "" -}}
  {{- end -}}
{{- end -}}
{{- if eq .Kind "taxonomy" -}}
  {{- range .Data.Terms.ByCount -}}
    {{- $lines = $lines | append (printf "- [%s](%s) (%d)" (.Page.Title | replaceRE `([\[\]])` `\$1`) (partial "markdown-url.html" .Page) .Count) -}}
  {{- end -}}
{{- else -}}
  {{- /* The pages of the theme's list.html; .Paginator lists site.RegularPages on a home page. */ -}}
  {{- range where (cond .IsHome site.RegularPages .Pages) "Type" "!=" "page" -}}
    {{- $notes := "" -}}
    {{- with partial "page-description.html" . | replaceRE `\s+` " " -}}{{- $notes = printf ": %s" . -}}{{- end -}}
    {{- $lines = $lines | append (printf "- [%s](%s) (%s)%s" (.Title | replaceRE `([\[\]])` `\$1`) (partial "markdown-url.html" .) (.PublishDate.Format "2006-01-02") $notes) -}}
  {{- end -}}
{{- end -}}
{{- if .IsHome -}}
  {{- with site.Params.projects -}}
    {{- $lines = $lines | append "" (printf "## %s" (i18n "Projects" | default "Projects")) "" -}}
    {{- range . -}}
      {{- $notes := "" -}}
      {{- with .description -}}{{- $notes = printf ": %s" . -}}{{- end -}}
      {{- $lines = $lines | append (printf "- [%s](%s)%s" (.name | replaceRE `([\[\]])` `\$1`) .url $notes) -}}
    {{- end -}}
  {{- end -}}
{{- end -}}
{{- delimit ($lines | append "") "\n" -}}
