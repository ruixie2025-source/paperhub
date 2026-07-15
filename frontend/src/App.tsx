import { FlaskConical, Plus, ShieldCheck, Trash2, Upload, X } from "lucide-react"
import { useEffect, useState, type ChangeEvent } from "react"
import { Route, Routes } from "react-router-dom"

import type { Paper, PaperPayload } from "@/api/paper"
import {
  analyzePapers,
  cleanupOldPaperAnalyses,
  getLatestPaperAnalyses,
  type PaperAnalysis,
} from "@/api/paperAnalysis"
import { AIChat } from "@/components/AIChat"
import { AppShell } from "@/components/AppShell"
import { DeleteDialog } from "@/components/DeleteDialog"
import { PaperAnalysisTable } from "@/components/PaperAnalysisTable"
import { PaperForm } from "@/components/PaperForm"
import { PaperList } from "@/components/PaperList"
import { PaperToolbar } from "@/components/PaperToolbar"
import { Button, buttonVariants } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { usePaper } from "@/hooks/usePaper"
import { cn } from "@/lib/utils"
import { AIChatPage } from "@/pages/AIChatPage"
import { PaperDetail } from "@/pages/PaperDetail"

function PaperListPage() {
  const {
    clearError,
    createPaperItem,
    deletePaperItem,
    deletingPaperId,
    error,
    importPaperItem,
    isImporting,
    isLoading,
    isSaving,
    keyword,
    papers,
    refreshPapers,
    setKeyword,
    updatePaperItem,
  } = usePaper()
  const [editingPaper, setEditingPaper] = useState<Paper | null>(null)
  const [isPaperFormOpen, setIsPaperFormOpen] = useState(false)
  const [paperToDelete, setPaperToDelete] = useState<Paper | null>(null)
  const [selectedPaperIds, setSelectedPaperIds] = useState<number[]>([])
  const [analyses, setAnalyses] = useState<PaperAnalysis[]>([])
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [isCleaningAnalyses, setIsCleaningAnalyses] = useState(false)
  const [analysisError, setAnalysisError] = useState<string | null>(null)
  const [analysisMessage, setAnalysisMessage] = useState<string | null>(null)

  useEffect(() => {
    const paperIds = papers.map((paper) => paper.id)
    setSelectedPaperIds((currentIds) =>
      currentIds.filter((paperId) => paperIds.includes(paperId)),
    )

    if (paperIds.length === 0) {
      setAnalyses([])
      return
    }

    let shouldIgnore = false
    async function loadLatestAnalyses() {
      try {
        const latestAnalyses = await getLatestPaperAnalyses(paperIds)
        if (!shouldIgnore) {
          setAnalyses(latestAnalyses)
          setAnalysisError(null)
        }
      } catch {
        if (!shouldIgnore) {
          setAnalysisError("加载历史分析记录失败")
        }
      }
    }

    void loadLatestAnalyses()
    return () => {
      shouldIgnore = true
    }
  }, [papers])

  function closePaperForm() {
    setEditingPaper(null)
    setIsPaperFormOpen(false)
  }

  async function handleSubmit(payload: PaperPayload) {
    if (editingPaper === null) {
      await createPaperItem(payload)
    } else {
      await updatePaperItem(editingPaper.id, payload)
    }
    closePaperForm()
  }

  async function handleConfirmDelete() {
    if (paperToDelete === null) {
      return
    }

    await deletePaperItem(paperToDelete.id)
    if (editingPaper?.id === paperToDelete.id) {
      closePaperForm()
    }
    setPaperToDelete(null)
  }

  function handleEdit(paper: Paper) {
    clearError()
    setEditingPaper(paper)
    setIsPaperFormOpen(true)
  }

  function handleCreateManually() {
    clearError()
    setEditingPaper(null)
    setIsPaperFormOpen(true)
  }

  async function handleImport(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0]
    event.target.value = ""
    if (!file) {
      return
    }

    await importPaperItem(file)
  }

  function handleSelectionChange(paperId: number, checked: boolean) {
    setSelectedPaperIds((currentIds) => {
      if (checked) {
        return currentIds.includes(paperId) ? currentIds : [...currentIds, paperId]
      }
      return currentIds.filter((currentId) => currentId !== paperId)
    })
  }

  async function handleAnalyzeSelectedPapers() {
    if (selectedPaperIds.length === 0) {
      setAnalysisError("请先选择至少一篇论文。")
      return
    }

    setIsAnalyzing(true)
    setAnalysisError(null)
    setAnalysisMessage(null)
    try {
      setAnalyses(await analyzePapers(selectedPaperIds))
      setAnalysisMessage("分析完成，最近一次结果已保存。")
    } catch (caughtError) {
      setAnalysisError(caughtError instanceof Error ? caughtError.message : "分析论文失败")
    } finally {
      setIsAnalyzing(false)
    }
  }

  async function handleCleanupOldAnalyses() {
    setIsCleaningAnalyses(true)
    setAnalysisError(null)
    setAnalysisMessage(null)
    try {
      const deletedCount = await cleanupOldPaperAnalyses(30)
      setAnalysisMessage(`已清理 ${deletedCount} 条 30 天前的分析记录。`)
      if (papers.length > 0) {
        setAnalyses(await getLatestPaperAnalyses(papers.map((paper) => paper.id)))
      }
    } catch (caughtError) {
      setAnalysisError(caughtError instanceof Error ? caughtError.message : "清理分析记录失败")
    } finally {
      setIsCleaningAnalyses(false)
    }
  }

  return (
    <AppShell>
      <div className="space-y-6">
        <section className="flex flex-col gap-4 border-b pb-6 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="text-sm font-medium text-primary">研究资料中心</p>
            <h1 className="mt-1 text-2xl font-semibold sm:text-3xl">论文工作台</h1>
            <p className="mt-2 max-w-2xl text-sm leading-6 text-muted-foreground">
              导入 PDF 后自动识别元数据、建立语义索引，并支持结构化研究分析。
            </p>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <Button onClick={handleCreateManually} type="button" variant="outline">
              <Plus />
              手动新增
            </Button>
            <label
              className={cn(
                buttonVariants({ size: "lg" }),
                "relative cursor-pointer overflow-hidden focus-within:ring-3 focus-within:ring-ring/50",
                isImporting && "cursor-not-allowed opacity-50",
              )}
            >
              <Upload />
              {isImporting ? "正在解析 PDF..." : "导入 PDF"}
              <input
                accept="application/pdf,.pdf"
                className="absolute inset-0 cursor-pointer opacity-0 disabled:cursor-not-allowed"
                disabled={isImporting}
                onChange={(event) => void handleImport(event)}
                type="file"
              />
            </label>
          </div>
        </section>

        <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_320px]">
          <section className="min-w-0 space-y-4">
            <PaperToolbar
              count={papers.length}
              isLoading={isLoading}
              keyword={keyword}
              onRefresh={() => void refreshPapers()}
              onSearchChange={setKeyword}
            />

            <div className="flex flex-wrap items-center gap-2 rounded-lg border bg-muted/20 p-3">
              <p className="mr-auto text-sm text-muted-foreground">
                已选择 <span className="font-semibold text-foreground">{selectedPaperIds.length}</span>{" "}
                篇论文
              </p>
              <Button
                disabled={isAnalyzing || selectedPaperIds.length === 0}
                onClick={() => void handleAnalyzeSelectedPapers()}
                type="button"
              >
                <FlaskConical />
                {isAnalyzing ? "分析中..." : "分析所选"}
              </Button>
              <Button
                aria-label="清空论文选择"
                disabled={isAnalyzing || selectedPaperIds.length === 0}
                onClick={() => setSelectedPaperIds([])}
                size="icon"
                title="清空选择"
                type="button"
                variant="ghost"
              >
                <X />
              </Button>
              <Button
                disabled={isCleaningAnalyses}
                onClick={() => void handleCleanupOldAnalyses()}
                type="button"
                variant="ghost"
              >
                <Trash2 />
                {isCleaningAnalyses ? "清理中..." : "清理旧记录"}
              </Button>
            </div>

            {error ? (
              <div
                className="rounded-md border border-destructive/30 bg-destructive/10 p-3 text-sm text-destructive"
                role="alert"
              >
                {error}
              </div>
            ) : null}

            {analysisError ? (
              <div
                className="rounded-md border border-destructive/30 bg-destructive/10 p-3 text-sm text-destructive"
                role="alert"
              >
                {analysisError}
              </div>
            ) : null}

            {analysisMessage ? (
              <div
                className="flex items-center gap-2 rounded-md border border-primary/20 bg-primary/5 p-3 text-sm text-foreground"
                role="status"
              >
                <ShieldCheck className="size-4 text-primary" />
                {analysisMessage}
              </div>
            ) : null}

            <PaperList
              deletingPaperId={deletingPaperId}
              isLoading={isLoading}
              onDeleteRequest={setPaperToDelete}
              onEdit={handleEdit}
              onSelectionChange={handleSelectionChange}
              papers={papers}
              selectedPaperIds={selectedPaperIds}
            />
          </section>

          <aside className="min-w-0 lg:sticky lg:top-20 lg:self-start">
            <AIChat compact />
          </aside>
        </div>

        <PaperAnalysisTable analyses={analyses} />
      </div>

      <Dialog onOpenChange={(open) => !open && closePaperForm()} open={isPaperFormOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader className="mb-5">
            <DialogTitle>{editingPaper === null ? "手动新增论文" : "编辑论文信息"}</DialogTitle>
            <DialogDescription>
              PDF 导入会自动填写这些信息；这里适合手动补充或修正。
            </DialogDescription>
          </DialogHeader>
          <PaperForm
            editingPaper={editingPaper}
            isSaving={isSaving}
            onCancel={closePaperForm}
            onSubmit={handleSubmit}
          />
        </DialogContent>
      </Dialog>

      <DeleteDialog
        isDeleting={paperToDelete !== null && deletingPaperId === paperToDelete.id}
        onCancel={() => setPaperToDelete(null)}
        onConfirm={() => void handleConfirmDelete()}
        paper={paperToDelete}
      />
    </AppShell>
  )
}

function App() {
  return (
    <Routes>
      <Route element={<PaperListPage />} path="/" />
      <Route element={<AIChatPage />} path="/ai-chat" />
      <Route element={<PaperDetail />} path="/papers/:id" />
    </Routes>
  )
}

export default App
