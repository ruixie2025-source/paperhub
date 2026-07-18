import { useCallback, useEffect, useState } from "react"

import {
  createPaper,
  deletePaper,
  importPaperPdf,
  listPapers,
  searchPapers,
  updatePaper,
} from "@/api/paper"
import type { Paper, PaperPayload } from "@/api/paper"

const MAX_IMPORT_FILES = 5
const IMPORT_CONCURRENCY = 2

export type PaperImportStatus = "queued" | "importing" | "success" | "error"

export type PaperImportItem = {
  id: string
  name: string
  status: PaperImportStatus
  error?: string
}

function getErrorMessage(caughtError: unknown, fallback: string) {
  return caughtError instanceof Error ? caughtError.message : fallback
}

export function usePaper() {
  const [papers, setPapers] = useState<Paper[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [isImporting, setIsImporting] = useState(false)
  const [importItems, setImportItems] = useState<PaperImportItem[]>([])
  const [isSaving, setIsSaving] = useState(false)
  const [deletingPaperId, setDeletingPaperId] = useState<number | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [keyword, setKeyword] = useState("")

  const loadPapers = useCallback(async (searchKeyword: string) => {
    setIsLoading(true)
    setError(null)
    try {
      const trimmedKeyword = searchKeyword.trim()
      setPapers(trimmedKeyword ? await searchPapers(trimmedKeyword) : await listPapers())
    } catch (caughtError) {
      setError(getErrorMessage(caughtError, "加载论文失败"))
    } finally {
      setIsLoading(false)
    }
  }, [])

  const refreshPapers = useCallback(async () => {
    await loadPapers(keyword)
  }, [keyword, loadPapers])

  useEffect(() => {
    const timeoutId = window.setTimeout(() => {
      void loadPapers(keyword)
    }, 300)

    return () => window.clearTimeout(timeoutId)
  }, [keyword, loadPapers])

  async function createPaperItem(payload: PaperPayload) {
    setIsSaving(true)
    setError(null)
    try {
      await createPaper(payload)
      await refreshPapers()
    } catch (caughtError) {
      setError(getErrorMessage(caughtError, "新增论文失败"))
      throw caughtError
    } finally {
      setIsSaving(false)
    }
  }

  function updateImportItem(id: string, updates: Partial<PaperImportItem>) {
    setImportItems((currentItems) =>
      currentItems.map((item) => (item.id === id ? { ...item, ...updates } : item)),
    )
  }

  async function importPaperItems(files: File[]) {
    if (files.length === 0) {
      return
    }

    if (files.length > MAX_IMPORT_FILES) {
      setError(`每批最多导入 ${MAX_IMPORT_FILES} 个 PDF。`)
      return
    }

    const queuedItems = files.map((file, index) => ({
      id: `${file.name}-${file.size}-${file.lastModified}-${index}`,
      name: file.name,
      status: "queued" as const,
    }))
    const failedFiles: string[] = []
    let nextFileIndex = 0

    setIsImporting(true)
    setError(null)
    setImportItems(queuedItems)

    async function processQueue() {
      while (nextFileIndex < files.length) {
        const fileIndex = nextFileIndex
        nextFileIndex += 1

        const file = files[fileIndex]
        const item = queuedItems[fileIndex]
        updateImportItem(item.id, { status: "importing", error: undefined })

        try {
          await importPaperPdf(file)
          updateImportItem(item.id, { status: "success" })
        } catch (caughtError) {
          const message = getErrorMessage(caughtError, "导入 PDF 失败")
          failedFiles.push(file.name)
          updateImportItem(item.id, { status: "error", error: message })
        }
      }
    }

    try {
      const workerCount = Math.min(IMPORT_CONCURRENCY, files.length)
      await Promise.all(Array.from({ length: workerCount }, () => processQueue()))
      await refreshPapers()

      if (failedFiles.length > 0) {
        setError(`${failedFiles.length} 个 PDF 导入失败，请查看批量导入记录。`)
      }
    } finally {
      setIsImporting(false)
    }
  }

  async function updatePaperItem(id: number, payload: PaperPayload) {
    setIsSaving(true)
    setError(null)
    try {
      await updatePaper(id, payload)
      await refreshPapers()
    } catch (caughtError) {
      setError(getErrorMessage(caughtError, "更新论文失败"))
      throw caughtError
    } finally {
      setIsSaving(false)
    }
  }

  async function deletePaperItem(id: number) {
    setDeletingPaperId(id)
    setError(null)
    try {
      await deletePaper(id)
      await refreshPapers()
    } catch (caughtError) {
      setError(getErrorMessage(caughtError, "删除论文失败"))
      throw caughtError
    } finally {
      setDeletingPaperId(null)
    }
  }

  function clearError() {
    setError(null)
  }

  function clearImportItems() {
    if (!isImporting) {
      setImportItems([])
    }
  }

  return {
    clearError,
    clearImportItems,
    createPaperItem,
    deletePaperItem,
    deletingPaperId,
    error,
    importItems,
    importPaperItems,
    isImporting,
    isLoading,
    isSaving,
    keyword,
    papers,
    refreshPapers,
    setKeyword,
    updatePaperItem,
  }
}
