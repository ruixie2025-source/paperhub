import { useState } from "react"
import { BarChart3, ChevronRight, Clock3 } from "lucide-react"

import type { PaperAnalysis } from "@/api/paperAnalysis"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"

type AnalysisColumn = {
  key: keyof PaperAnalysis
  label: string
}

type ActiveCell = {
  title: string
  label: string
  value: string
} | null

const analysisColumns: AnalysisColumn[] = [
  { key: "purpose", label: "研究目的" },
  { key: "research_question", label: "研究问题" },
  { key: "value", label: "研究价值" },
  { key: "method", label: "研究方法" },
  { key: "keywords", label: "关键词" },
  { key: "research_design", label: "研究设计" },
  { key: "findings", label: "核心发现" },
  { key: "logic", label: "组织逻辑" },
  { key: "variables", label: "研究变量与关系" },
  { key: "application_value", label: "应用价值" },
]

function truncateText(value: string) {
  const compactValue = value.replace(/\s+/g, " ").trim()
  return compactValue.length > 80 ? `${compactValue.slice(0, 80)}...` : compactValue
}

function formatCreatedAt(value: string | null) {
  if (!value) {
    return null
  }
  return new Intl.DateTimeFormat("zh-CN", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value))
}

type PaperAnalysisTableProps = {
  analyses: PaperAnalysis[]
}

function PaperAnalysisTable({ analyses }: PaperAnalysisTableProps) {
  const [activeCell, setActiveCell] = useState<ActiveCell>(null)

  if (analyses.length === 0) {
    return null
  }

  return (
    <>
      <Card>
        <CardHeader className="border-b">
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="size-5 text-primary" />
            论文结构化分析
          </CardTitle>
          <p className="text-sm text-muted-foreground">
            对比研究目的、方法、变量关系和核心发现。点击任意内容可查看完整分析。
          </p>
        </CardHeader>
        <CardContent className="p-0">
          <div className="hidden overflow-x-auto md:block">
            <Table className="min-w-[2200px]">
              <TableHeader>
                <TableRow>
                  <TableHead className="sticky left-0 z-10 min-w-64 bg-muted/90">论文</TableHead>
                  {analysisColumns.map((column) => (
                    <TableHead className="min-w-48" key={column.key}>
                      {column.label}
                    </TableHead>
                  ))}
                </TableRow>
              </TableHeader>
              <TableBody>
                {analyses.map((analysis) => (
                  <TableRow key={analysis.paper_id}>
                    <TableCell className="sticky left-0 z-10 bg-background align-top">
                      <p className="line-clamp-3 font-medium">{analysis.title}</p>
                      {formatCreatedAt(analysis.created_at) ? (
                        <p className="mt-2 flex items-center gap-1 text-xs text-muted-foreground">
                          <Clock3 className="size-3" />
                          {formatCreatedAt(analysis.created_at)}
                        </p>
                      ) : null}
                    </TableCell>
                    {analysisColumns.map((column) => {
                      const value = String(
                        analysis[column.key] || "论文中没有找到相关内容。",
                      )
                      return (
                        <TableCell className="align-top" key={column.key}>
                          <button
                            className="line-clamp-4 max-w-56 text-left text-sm leading-5 text-muted-foreground hover:text-foreground"
                            onClick={() =>
                              setActiveCell({
                                title: analysis.title,
                                label: column.label,
                                value,
                              })
                            }
                            type="button"
                          >
                            {truncateText(value)}
                          </button>
                        </TableCell>
                      )
                    })}
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>

          <div className="divide-y md:hidden">
            {analyses.map((analysis) => (
              <section className="p-4" key={analysis.paper_id}>
                <p className="font-semibold leading-6">{analysis.title}</p>
                {formatCreatedAt(analysis.created_at) ? (
                  <p className="mt-1 flex items-center gap-1 text-xs text-muted-foreground">
                    <Clock3 className="size-3" />
                    {formatCreatedAt(analysis.created_at)}
                  </p>
                ) : null}
                <div className="mt-3 grid gap-2 sm:grid-cols-2">
                  {analysisColumns.map((column) => {
                    const value = String(
                      analysis[column.key] || "论文中没有找到相关内容。",
                    )
                    return (
                      <button
                        className="flex min-w-0 items-center justify-between gap-3 rounded-md border bg-muted/20 px-3 py-2 text-left"
                        key={column.key}
                        onClick={() =>
                          setActiveCell({
                            title: analysis.title,
                            label: column.label,
                            value,
                          })
                        }
                        type="button"
                      >
                        <span className="min-w-0">
                          <span className="block text-xs font-medium text-muted-foreground">
                            {column.label}
                          </span>
                          <span className="mt-0.5 block truncate text-sm">
                            {truncateText(value)}
                          </span>
                        </span>
                        <ChevronRight className="size-4 shrink-0 text-muted-foreground" />
                      </button>
                    )
                  })}
                </div>
              </section>
            ))}
          </div>
        </CardContent>
      </Card>

      <Dialog onOpenChange={(open) => !open && setActiveCell(null)} open={activeCell !== null}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>{activeCell?.label}</DialogTitle>
            <DialogDescription>{activeCell?.title}</DialogDescription>
          </DialogHeader>
          <div className="max-h-[60vh] overflow-y-auto whitespace-pre-wrap rounded-md border bg-muted/30 p-4 text-sm leading-6">
            {activeCell?.value}
          </div>
          <DialogFooter>
            <Button onClick={() => setActiveCell(null)} type="button" variant="outline">
              关闭
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  )
}

export { PaperAnalysisTable }
