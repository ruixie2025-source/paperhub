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

function getErrorMessage(caughtError: unknown, fallback: string) {
  return caughtError instanceof Error ? caughtError.message : fallback
}

export function usePaper() {
  const [papers, setPapers] = useState<Paper[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [isImporting, setIsImporting] = useState(false)
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

  async function importPaperItem(file: File) {
    setIsImporting(true)
    setError(null)
    try {
      await importPaperPdf(file)
      await refreshPapers()
    } catch (caughtError) {
      setError(getErrorMessage(caughtError, "导入 PDF 失败"))
      throw caughtError
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

  return {
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
  }
}
