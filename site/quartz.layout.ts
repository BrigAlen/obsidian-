import { PageLayout, SharedLayout } from "./quartz/cfg"
import * as Component from "./quartz/components"

// components shared across all pages
export const sharedPageComponents: SharedLayout = {
  head: Component.Head(),
  header: [],
  afterBody: [],
  footer: Component.Footer({
    links: {
      GitHub: "https://github.com/BrigAlen/obsidian-",
    },
  }),
}

// Граф: без тегов, крупнее расстояния, сильнее отталкивание — кластеры (этапы) читаются отдельно.
const graph = Component.Graph({
  localGraph: {
    depth: 1,
    scale: 1.2,
    repelForce: 1.0,
    centerForce: 0.2,
    linkDistance: 45,
    fontSize: 0.7,
    showTags: false,
    focusOnHover: true,
  },
  globalGraph: {
    depth: 2,
    scale: 0.8,
    repelForce: 1.6,
    centerForce: 0.08,
    linkDistance: 70,
    fontSize: 0.7,
    showTags: false,
    focusOnHover: true,
    enableRadial: false,
  },
})

// Дерево слева: короткие названия, клик по папке только раскрывает её, служебные страницы скрыты
const explorer = Component.Explorer({
  folderClickBehavior: "collapse",
  folderDefaultState: "collapsed",
  filterFn: (node) => {
    const s = node.slugSegment
    if (s === "tags") return false
    // страницы-оглавления (доступны по ссылкам): домены, этапы, «Мои заметки»
    if (/^(BE|FE|DB|DO)-Этап-\d/.test(s)) return false
    if (/^(BE-Backend|FE-Frontend|DB-Базы-данных|DO-DevOps|FS-Fullstack-практика|Мои-заметки)$/.test(s)) return false
    return true
  },
  // разделы верхнего уровня — по номерам в именах папок (01-, 02-, ...), остальное — как по умолчанию
  sortFn: (a, b) => {
    const na = /^\d{2}-/.test(a.slugSegment)
    const nb = /^\d{2}-/.test(b.slugSegment)
    if (na && nb) return a.slugSegment.localeCompare(b.slugSegment)
    if (a.isFolder !== b.isFolder) return a.isFolder ? -1 : 1
    return a.displayName.localeCompare(b.displayName, undefined, { numeric: true, sensitivity: "base" })
  },
  mapFn: (node) => {
    let n = node.displayName
    n = n.replace(/^\d{2}-/, "") // 01-Backend -> Backend
    n = n.replace(/^Мои-заметки$/, "Мои заметки").replace(/^00 /, "")
    n = n.replace(/^(BE|FE|DB|DO|FS) (?=\d)/, "") // BE 1.1 -> 1.1
    const m = n.match(/^Этап (\d+)\s*[—·:-]\s*(.*)$/)
    if (m) n = `${m[1]}. ${m[2].split(/\s+[—:]\s+|:\s+/)[0]}`
    node.displayName = n
  },
})

// components for pages that display a single page (e.g. a single note)
export const defaultContentPageLayout: PageLayout = {
  afterBody: [
    // на главной: недавно обновлённые темы
    Component.ConditionalRender({
      component: Component.RecentNotes({
        title: "Недавно обновлено",
        limit: 8,
        showTags: false,
        filter: (f) => f.frontmatter?.type === "topic",
      }),
      condition: (page) => page.fileData.slug === "index",
    }),
  ],
  beforeBody: [
    Component.ContentMeta({ showReadingTime: false }),
    Component.TagList(),
  ],
  left: [
    Component.PageTitle(),
    Component.MobileOnly(Component.Spacer()),
    Component.Flex({
      components: [
        {
          Component: Component.Search(),
          grow: true,
        },
        { Component: Component.Darkmode() },
        { Component: Component.ReaderMode() },
      ],
    }),
    explorer,
  ],
  right: [graph, Component.DesktopOnly(Component.TableOfContents()), Component.Backlinks()],
}

// components for pages that display lists of pages  (e.g. tags or folders)
export const defaultListPageLayout: PageLayout = {
  beforeBody: [Component.Breadcrumbs(), Component.ArticleTitle(), Component.ContentMeta()],
  left: [
    Component.PageTitle(),
    Component.MobileOnly(Component.Spacer()),
    Component.Flex({
      components: [
        {
          Component: Component.Search(),
          grow: true,
        },
        { Component: Component.Darkmode() },
      ],
    }),
    Component.Explorer(),
  ],
  right: [],
}
