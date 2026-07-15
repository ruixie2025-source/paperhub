import { ArrowLeft, ExternalLink, FileCheck2, Upload } from "lucide-react"
import { lazy, Suspense, useCallback, useEffect, useState } from "react"
import { Link, useParams } from "react-router-dom"

import { getPaper, uploadPaperPdf } from "@/api/paper"
import type { Paper } from "@/api/paper"
import { AppShell } from "@/components/AppShell"
import { Badge } from "@/components/ui/badge"
import { Button, buttonVariants } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { cn } from "@/lib/utils"

const PdfViewer = lazy(() =>
  import("@/components/PdfViewer").then((module) => ({ default: module.PdfViewer })),
)

function DetailRow({ label, value }: { label: string; value: string | number | null }) {
  return (
    <div className="min-w-0">
      <p className="text-xs font-medium text-muted-foreground">{label}</p>
      <p className="mt-1 break-words text-sm">{value || "—"}</p>
    </div>
  )
}

function getPdfFilename(pdfPath: string) {
  return pdfPath.split("/").filter(Boolean).at(-1) ?? pdfPath
}

function splitKeywords(keywords: string) {
  return keywords
    .split(/[；;，,]/)
    .map((keyword) => keyword.trim())
    .filter(Boolean)
}

function PaperDetail() {
  const { id } = useParams()
  const [paper, setPaper] = useState<Paper | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isUploading, setIsUploading] = useState(false)
  const [isAbstractExpanded, setIsAbstractExpanded] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const loadPaper = useCallback(async () => {
    setIsLoading(true)
    setError(null)

    const paperId = Number(id)
    if (!Number.isInteger(paperId)) {
      setError("论文 ID 无效。")
      setIsLoading(false)
      return
    }

    try {
      setPaper(await getPaper(paperId))
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "加载论文失败")
    } finally {
      setIsLoading(false)
    }
  }, [id])

  useEffect(() => {
    void loadPaper()
  }, [loadPaper])

  async function handleUpload(file: File | null) {
    if (file === null || paper === null) {
      return
    }

    setIsUploading(true)
    setError(null)
    try {
      await uploadPaperPdf(paper.id, file)
      await loadPaper()
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "上传 PDF 失败")
    } finally {
      setIsUploading(false)
    }
  }

  const keywords = splitKeywords(paper?.keywords ?? "")
  const shouldCollapseAbstract = (paper?.abstract?.length ?? 0) > 520

  return (
    <AppShell>
      <div className="mx-auto max-w-5xl space-y-5">
        <Link className={cn(buttonVariants({ variant: "ghost" }), "-ml-2")} to="/">
          <ArrowLeft />
          返回论文库
        </Link>

        {isLoading ? (
          <Card>
            <CardContent className="p-10 text-center text-sm text-muted-foreground" role="status">
              正在加载论文...
            </CardContent>
          </Card>
        ) : null}

        {error ? (
          <div
            className="rounded-md border border-destructive/30 bg-destructive/10 p-3 text-sm text-destructive"
            role="alert"
          >
            {error}
          </div>
        ) : null}

        {!isLoading && paper !== null ? (
          <>
            <Card>
              <CardHeader className="border-b">
                <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
                  <div className="min-w-0">
                    <p className="text-sm font-medium text-primary">论文详情</p>
                    <CardTitle className="mt-2 break-words text-xl leading-8 sm:text-2xl">
                      {paper.title}
                    </CardTitle>
                    <p className="mt-2 text-sm text-muted-foreground">
                      {[paper.authors, paper.journal, paper.year].filter(Boolean).join(" · ") ||
                        "暂无完整元数据"}
                    </p>
                  </div>

                  <div className="flex shrink-0 flex-wrap items-center gap-2">
                    {paper.pdf_path ? (
                      <a
                        className={buttonVariants({ variant: "outline" })}
                        href={paper.pdf_path}
                        rel="noreferrer"
                        target="_blank"
                      >
                        <ExternalLink />
                        打开 PDF
                      </a>
                    ) : null}
                    <label
                      className={cn(
                        buttonVariants(),
                        "relative cursor-pointer overflow-hidden focus-within:ring-3 focus-within:ring-ring/50",
                        isUploading && "cursor-not-allowed opacity-50",
                      )}
                    >
                      <Upload />
                      {isUploading ? "处理中..." : paper.pdf_path ? "替换 PDF" : "上传 PDF"}
                      <input
                        accept="application/pdf,.pdf"
                        className="absolute inset-0 cursor-pointer opacity-0 disabled:cursor-not-allowed"
                        disabled={isUploading}
                        onChange={(event) => void handleUpload(event.target.files?.[0] ?? null)}
                        type="file"
                      />
                    </label>
                  </div>
                </div>
              </CardHeader>

              <CardContent className="space-y-6 p-5">
                <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
                  <DetailRow label="作者" value={paper.authors} />
                  <DetailRow label="期刊" value={paper.journal} />
                  <DetailRow label="年份" value={paper.year} />
                  <div>
                    <p className="text-xs font-medium text-muted-foreground">DOI</p>
                    {paper.doi ? (
                      <a
                        className="mt-1 block break-all text-sm text-primary hover:underline"
                        href={`https://doi.org/${paper.doi}`}
                        rel="noreferrer"
                        target="_blank"
                      >
                        {paper.doi}
                      </a>
                    ) : (
                      <p className="mt-1 text-sm">—</p>
                    )}
                  </div>
                </div>

                <div>
                  <p className="text-xs font-medium text-muted-foreground">关键词</p>
                  <div className="mt-2 flex flex-wrap gap-1.5">
                    {keywords.length > 0 ? (
                      keywords.map((keyword) => <Badge key={keyword}>{keyword}</Badge>)
                    ) : (
                      <span className="text-sm">—</span>
                    )}
                  </div>
                </div>

                <div className="border-t pt-5">
                  <p className="text-sm font-semibold">摘要</p>
                  <p
                    className={cn(
                      "mt-2 whitespace-pre-wrap break-words text-sm leading-7 text-muted-foreground",
                      shouldCollapseAbstract && !isAbstractExpanded && "line-clamp-6",
                    )}
                  >
                    {paper.abstract || "暂无摘要"}
                  </p>
                  {shouldCollapseAbstract ? (
                    <Button
                      className="mt-2 px-0"
                      onClick={() => setIsAbstractExpanded((expanded) => !expanded)}
                      type="button"
                      variant="link"
                    >
                      {isAbstractExpanded ? "收起摘要" : "展开完整摘要"}
                    </Button>
                  ) : null}
                </div>

                <div className="flex flex-wrap items-center gap-2 border-t pt-5 text-sm">
                  <FileCheck2 className="size-4 text-primary" />
                  <span className="font-medium">PDF 状态</span>
                  <span className="text-muted-foreground">
                    {paper.pdf_path ? getPdfFilename(paper.pdf_path) : "暂无 PDF"}
                  </span>
                </div>
              </CardContent>
            </Card>

            {paper.pdf_path ? (
              <Suspense
                fallback={
                  <Card>
                    <CardContent
                      className="p-10 text-center text-sm text-muted-foreground"
                      role="status"
                    >
                      正在加载 PDF 阅读器...
                    </CardContent>
                  </Card>
                }
              >
                <PdfViewer fileUrl={paper.pdf_path} />
              </Suspense>
            ) : null}
          </>
        ) : null}
      </div>
    </AppShell>
  )
}

export { PaperDetail }
