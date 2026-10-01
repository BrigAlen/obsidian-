import { QuartzConfig } from "./quartz/cfg"
import * as Plugin from "./quartz/plugins"

/**
 * Quartz 4 configuration for the "Developer" vault.
 * CI copies this file over quartz.config.ts at build time (see .github/workflows/deploy.yml).
 */
const config: QuartzConfig = {
  configuration: {
    pageTitle: "Developer",
    pageTitleSuffix: "",
    enableSPA: true,
    enablePopovers: true,
    locale: "ru-RU",
    baseUrl: "brigalen.github.io/obsidian-",
    ignorePatterns: ["private", "_templates", ".obsidian", ".github", "site", "README.md", "Дашборд.md"],
    defaultDateType: "modified",
    theme: {
      fontOrigin: "googleFonts",
      cdnCaching: true,
      typography: {
        // «цифровой» вид: Exo 2 для заголовков, Onest (современная замена Roboto) для текста, JetBrains Mono для подписей и кода.
        // У этих шрифтов нет курсива на Google Fonts, поэтому includeItalic: false.
        header: { name: "Exo 2", weights: [500, 600, 700], includeItalic: false },
        body: { name: "Onest", weights: [400, 500, 600], includeItalic: false },
        code: "JetBrains Mono",
      },
      colors: {
        lightMode: {
          light: "#fbfbfa",
          lightgray: "#e4e4e0",
          gray: "#9b9b96",
          darkgray: "#55555a",
          dark: "#1b1b1d",
          secondary: "#6a43d6",
          tertiary: "#8b6cf6",
          highlight: "rgba(106, 67, 214, 0.08)",
          textHighlight: "#fff23688",
        },
        darkMode: {
          light: "#141414",
          lightgray: "#2a2a2c",
          gray: "#777779",
          darkgray: "#b8b8bc",
          dark: "#ededee",
          secondary: "#b69cff",
          tertiary: "#8b6cf6",
          highlight: "rgba(182, 156, 255, 0.10)",
          textHighlight: "#b69cff40",
        },
      },
    },
  },
  plugins: {
    transformers: [
      Plugin.FrontMatter(),
      Plugin.CreatedModifiedDate({
        priority: ["frontmatter", "git", "filesystem"],
      }),
      Plugin.SyntaxHighlighting({
        theme: {
          light: "github-light",
          dark: "github-dark",
        },
        keepBackground: false,
      }),
      Plugin.ObsidianFlavoredMarkdown({ enableInHtmlEmbed: false }),
      Plugin.GitHubFlavoredMarkdown(),
      Plugin.TableOfContents({ maxDepth: 3, minEntries: 2 }),
      Plugin.CrawlLinks({ markdownLinkResolution: "shortest", lazyLoad: true, externalLinkIcon: true }),
      Plugin.Description(),
      Plugin.Latex({ renderEngine: "katex" }),
    ],
    filters: [Plugin.RemoveDrafts()],
    emitters: [
      Plugin.AliasRedirects(),
      Plugin.ComponentResources(),
      Plugin.ContentPage(),
      Plugin.TagPage(),
      Plugin.ContentIndex({
        enableSiteMap: true,
        enableRSS: true,
      }),
      Plugin.Assets(),
      Plugin.Static(),
      Plugin.Favicon(),
      Plugin.NotFoundPage(),
    ],
  },
}

export default config
